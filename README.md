# Iscar Label Generator

Warehouse label printing web app built with Django.  
Searches product data from an Excel file and sends labels directly to a network label printer via ZPL over TCP port 9100.

## Stack
- Python 3.13
- Django 5.1.4
- Pandas / OpenPyXL
- ZPL over TCP (no browser print dialog)

## Printer
Honeywell PD45 — IP `10.59.0.34`, port `9100`

## Label Size
100 × 50 mm — Product code, description, bin location, Code128 barcode

## Setup

```bash
# Create and activate venv
& "C:\Program Files\Python313\python.exe" -m venv venv
venv\Scripts\activate

# Install dependencies
python -m pip install django==5.1.4 pandas==2.2.3 openpyxl==3.1.5

# Add your data file
# Copy data.xlsx into warehouse/data.xlsx
# Sheet must be named: Data
# Columns: Product Code | Product Description | Bin Location

# Run
python manage.py runserver 0.0.0.0:8000
```

## Config
Edit `labelgen/settings.py` to change:
- `LABEL_PRINTER_IP` — printer IP address
- `LABEL_PRINTER_PORT` — default 9100
- `DATA_XLSX_PATH` — absolute path to Excel file (optional, defaults to warehouse/data.xlsx)

## Access
- Local: http://localhost:8000
- Network: http://10.59.0.5:8000
- Domain: https://label.sa.iscar.com
