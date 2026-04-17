import json
import socket
import threading
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
import pandas as pd


# ─────────────────────────────────────────────────────────────────────────────
# Excel cache
# ─────────────────────────────────────────────────────────────────────────────
_lock  = threading.Lock()
_cache = {'df': None, 'mtime': None}


def _excel_path():
    explicit = getattr(settings, 'DATA_XLSX_PATH', None)
    if explicit:
        p = Path(explicit)
    else:
        p = Path(settings.BASE_DIR) / 'warehouse' / 'data.xlsx'
    if not p.exists():
        raise FileNotFoundError(
            f"data.xlsx not found at: {p}  —  "
            "place your Excel file there or set DATA_XLSX_PATH in settings.py"
        )
    return p


def _get_df():
    path  = _excel_path()
    mtime = path.stat().st_mtime
    with _lock:
        if _cache['df'] is None or _cache['mtime'] != mtime:
            df = pd.read_excel(str(path), sheet_name='Data', dtype=str)
            df.columns = [c.strip() for c in df.columns]
            rename = {}
            for col in df.columns:
                lc = col.lower()
                if 'product' in lc and 'code' in lc:
                    rename[col] = 'Product Code'
                elif 'description' in lc:
                    rename[col] = 'Description'
                elif 'bin' in lc:
                    rename[col] = 'Bin'
            df = df.rename(columns=rename)
            for col in ('Product Code', 'Description', 'Bin'):
                if col not in df.columns:
                    df[col] = ''
                df[col] = df[col].astype(str).str.strip()
            df = df[df['Product Code'].str.len() > 0].reset_index(drop=True)
            _cache['df']    = df
            _cache['mtime'] = mtime
    return _cache['df']


def _encode_code128(value):
    value    = str(value)
    checksum = 104
    for i, ch in enumerate(value):
        checksum += (ord(ch) - 32) * (i + 1)
    checksum %= 103
    check = chr(checksum + 32) if checksum <= 94 else chr(checksum + 100)
    return chr(204) + value + check + chr(206)


def _build_zpl(code, desc, bin_loc):
    desc = desc[:48]
    return (
        "^XA\n^MMT\n^PW800\n^LL400\n^LS0\n"
        f"^FO0,20^FB800,1,,C^A0N,56,54^FD{code}^FS\n"
        f"^FO0,88^FB800,2,,C^A0N,28,26^FD{desc}^FS\n"
        f"^FO0,150^FB800,1,,C^A0N,32,30^FD{bin_loc}^FS\n"
        "^FO100,195^BY2,3,95^BCN,95,N,N\n"
        f"^FD{code}^FS\n"
        "^PQ1\n^XZ\n"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Views
# ─────────────────────────────────────────────────────────────────────────────
def search_view(request):
    query   = request.GET.get('q', '').strip()
    result  = None
    message = None
    if query:
        try:
            df = _get_df()
        except FileNotFoundError as e:
            message = str(e)
        else:
            mask = df['Product Code'].str.lower() == query.lower()
            if df[mask].empty:
                message = f"'{query}' not found."
            else:
                row = df[mask].iloc[0]
                result = {
                    'product_code': row['Product Code'],
                    'description':  row['Description'],
                    'bin_location': row['Bin'],
                    'encoded':      _encode_code128(row['Product Code']),
                }
    return render(request, 'warehouse/search.html', {
        'query': query, 'result': result, 'message': message,
    })


def autocomplete_view(request):
    term = request.GET.get('q', '').strip().lower()
    if len(term) < 2:
        return JsonResponse({'results': []})
    try:
        df = _get_df()
    except FileNotFoundError:
        return JsonResponse({'results': []})
    mask = df['Product Code'].str.lower().str.startswith(term)
    hits = df[mask].head(10)
    return JsonResponse({
        'results': [{'code': r['Product Code'], 'desc': r['Description']}
                    for _, r in hits.iterrows()]
    })


@require_POST
def print_label_view(request):
    try:
        code = json.loads(request.body).get('product_code', '').strip()
    except Exception:
        return JsonResponse({'ok': False, 'error': 'Bad request.'}, status=400)
    if not code:
        return JsonResponse({'ok': False, 'error': 'No product code.'}, status=400)
    try:
        df = _get_df()
    except FileNotFoundError as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)
    mask = df['Product Code'].str.lower() == code.lower()
    if df[mask].empty:
        return JsonResponse({'ok': False, 'error': f"'{code}' not found."}, status=404)
    row = df[mask].iloc[0]
    zpl = _build_zpl(row['Product Code'], row['Description'], row['Bin'])
    ip   = getattr(settings, 'LABEL_PRINTER_IP',   '10.59.0.34')
    port = getattr(settings, 'LABEL_PRINTER_PORT',  9100)
    try:
        with socket.create_connection((ip, port), timeout=5) as s:
            s.sendall(zpl.encode('utf-8'))
    except OSError as e:
        return JsonResponse({'ok': False, 'error': f"Printer unreachable: {e}"}, status=502)
    return JsonResponse({'ok': True})


def ping_printer_view(request):
    ip   = getattr(settings, 'LABEL_PRINTER_IP',   '10.59.0.34')
    port = getattr(settings, 'LABEL_PRINTER_PORT',  9100)
    try:
        with socket.create_connection((ip, port), timeout=2):
            pass
        return JsonResponse({'online': True,  'ip': ip})
    except OSError:
        return JsonResponse({'online': False, 'ip': ip})
