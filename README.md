# Iscar Label Generator

A warehouse label printing web application built with Django for Iscar South Africa.  
Staff search for a product code, preview the label on screen, and print directly to the network label printer — no browser print dialog, no scaling issues, one click.

---

## How It Works

1. Staff open the app in any browser on the network
2. Type a product code — autocomplete suggests matches as you type
3. The label preview appears on screen (product code, description, bin location, barcode)
4. Click **Print Label** — ZPL is sent directly to the printer over TCP
5. Label prints immediately

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13, Django 5.1.4 |
| Data | Pandas, OpenPyXL — reads from Excel |
| Print | ZPL over TCP port 9100 (no browser dialog) |
| Frontend | Vanilla JS, Barlow font, Iscar dark theme |

---

## Printer

**Honeywell PD45** (replacing Intermec EasyCoder 3400)  
- IP: `10.59.0.34`  
- Port: `9100`  
- Protocol: ZPL via raw TCP socket  
- Label size: 100 × 50 mm, 203 DPI  

---

## Label Format

```
┌─────────────────────────────┐
│         5606001             │  ← Product code (bold)
│   H600 WXCU 05T312T IC808   │  ← Description
│            AK8              │  ← Bin location
│  ▐▌▐▌▌▐▌▌▐▌▐▌▌▐▌▌▐▌▐▌▌▐▌  │  ← Code128 barcode
└─────────────────────────────┘
         100mm × 50mm
```

---

## Project Structure

```
Label-printing-app/
├── labelgen/
│   ├── settings.py        ← Printer IP, Excel path, Django config
│   ├── urls.py
│   └── wsgi.py
├── warehouse/
│   ├── views.py           ← Search, autocomplete, ZPL print endpoints
│   ├── urls.py            ← Routes: / /autocomplete/ /print/ /ping/
│   ├── templates/
│   │   └── warehouse/
│   │       └── search.html  ← Full UI — dark theme, preview, print button
│   └── static/
│       └── warehouse/
│           └── fonts/
│               └── code128.ttf  ← Barcode font for on-screen preview
├── manage.py
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/Divan-99/Label-printing-app.git
cd Label-printing-app
```

### 2. Create virtual environment
```powershell
& "C:\Program Files\Python313\python.exe" -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```powershell
python -m pip install -r requirements.txt
```

### 4. Add your Excel data file
Place your `data.xlsx` file in the `warehouse/` folder.  
The file must have a sheet named **`Data`** with these columns:

| Product Code | Product Description | Bin Location |
|---|---|---|
| 600446 | O-RING 10X2 NBR | HF8 |
| 1204169 | BIT SOCKET T25 3/8" DRIVE | HH6 |

> The Excel file is excluded from Git (see `.gitignore`) — add it manually on each machine.

### 5. Run the server
```powershell
python manage.py runserver 0.0.0.0:8000
```

---

## Access

| Where | URL |
|---|---|
| This machine | http://localhost:8000 |
| Any network PC | http://10.59.0.5:8000 |
| Domain | https://label.sa.iscar.com |

---

## Configuration

All settings are in `labelgen/settings.py`:

```python
# Printer
LABEL_PRINTER_IP   = '10.59.0.34'
LABEL_PRINTER_PORT = 9100

# Excel file (None = use warehouse/data.xlsx relative to project)
DATA_XLSX_PATH = None

# Or set an absolute path:
# DATA_XLSX_PATH = r"C:\path\to\your\data.xlsx"
```

---

## API Endpoints

| Method | URL | Description |
|---|---|---|
| GET | `/` | Main search page |
| GET | `/autocomplete/?q=<term>` | Returns up to 10 matching product codes as JSON |
| POST | `/print/` | Sends ZPL label to printer, returns `{"ok": true}` |
| GET | `/ping/` | TCP reachability check on printer, returns `{"online": true/false}` |

---

## Daily Use

```powershell
cd "C:\Users\divan\OneDrive\Desktop\Label-printing-app"
venv\Scripts\activate
python manage.py runserver 0.0.0.0:8000
```

---

## Test Printer Connection

```powershell
python -c "
import socket
s = socket.create_connection(('10.59.0.34', 9100), timeout=3)
print('Printer reachable on port 9100')
s.close()
"
```

---

## Notes

- Excel data is cached in memory and only reloads when the file changes on disk — no performance hit on each search
- The `.gitignore` excludes `data.xlsx`, `venv/`, `__pycache__/`, and `db.sqlite3`
- ZPL is sent as a raw TCP byte stream — the printer must be reachable on port 9100
- Cortex XDR may flag raw TCP scripts run from the command line — use the web app's Print button instead, which sends ZPL internally through Django

---

## Author

Divan Immelman — Iscar South Africa  
[Divan@iscarsa.co.za](mailto:Divan@iscarsa.co.za)
