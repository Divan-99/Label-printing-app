from pathlib import Path
from django.shortcuts import render
from django import forms
from django.conf import settings
import pandas as pd


class SearchForm(forms.Form):
    product_code = forms.CharField(
        label='Product code',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter product code...'})
    )


def encode_code128(value: str) -> str:
    """
    Encode text for a typical Code128B TrueType font.

    Rules:
    Start B  code 104 -> char(204)
    Stop    code 106 -> char(206)
    Checksum 0..94   -> char(code + 32)
    Checksum 95..102 -> char(code + 100)
    """
    value = str(value)

    start_char = chr(204)   # Start B
    stop_char = chr(206)    # Stop

    checksum = 104
    for i, ch in enumerate(value):
        checksum += (ord(ch) - 32) * (i + 1)

    checksum = checksum % 103

    if checksum <= 94:
        check_char = chr(checksum + 32)
    else:
        # For 95..102 the font expects chars 195..202
        check_char = chr(checksum + 100)

    return start_char + value + check_char + stop_char


def get_excel_path():
    explicit = getattr(settings, 'DATA_XLSX_PATH', None)
    if explicit:
        p = Path(explicit)
    else:
        p = Path(settings.BASE_DIR) / 'warehouse' / 'data.xlsx'
    if not p.exists():
        raise FileNotFoundError(f"Excel file not found at: {p}")
    return p


def read_data_sheet():
    p = get_excel_path()
    df = pd.read_excel(str(p), sheet_name='Data', dtype=str)

    col_map = {}
    for col in df.columns:
        lc = col.strip().lower()
        if 'product' in lc and 'code' in lc:
            col_map[col] = 'Product Code'
        elif 'description' in lc:
            col_map[col] = 'Product Description'
        elif 'bin' in lc:
            col_map[col] = 'Bin Location'
    if col_map:
        df = df.rename(columns=col_map)

    cols = list(df.columns)
    mapping = {}
    if len(cols) >= 1:
        mapping[cols[0]] = 'Product Code'
    if len(cols) >= 2:
        mapping[cols[1]] = 'Product Description'
    if len(cols) >= 3:
        mapping[cols[2]] = 'Bin Location'
    df = df.rename(columns=mapping)

    for expected in ('Product Code', 'Product Description', 'Bin Location'):
        if expected not in df.columns:
            df[expected] = ''

    return df


def search_view(request):
    form = SearchForm(request.GET or None)
    result = None
    message = None

    if form.is_valid():
        code = form.cleaned_data['product_code'].strip()

        try:
            df = read_data_sheet()
        except FileNotFoundError as e:
            message = str(e)
        else:
            df['_pclean'] = df['Product Code'].astype(str).str.strip().str.lower()
            matches = df[df['_pclean'] == code.lower()]

            if matches.empty:
                message = f"Product code '{code}' not found in the Excel sheet."
            else:
                row = matches.iloc[0]
                product = str(row['Product Code']).strip()

                encoded = encode_code128(product)

                result = {
                    'product_code': product,
                    'description': str(row.get('Product Description', '')).strip(),
                    'bin_location': str(row.get('Bin Location', '')).strip(),
                    'encoded': encoded,
                }

    return render(request, 'warehouse/search.html', {
        'form': form,
        'result': result,
        'message': message
    })
