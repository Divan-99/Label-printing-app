from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-iscar-labelgen-change-this-in-production-2026'

DEBUG = True

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://label.sa.iscar.com',
    'http://10.59.0.5:8000',
    'http://localhost:8000',
]

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'warehouse',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'labelgen.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'labelgen.wsgi.application'

STATIC_URL = 'static/'

# ---------------------------------------------------------------------------
# Excel data source
# Place your data.xlsx file in the warehouse/ folder, OR set an absolute path:
# DATA_XLSX_PATH = r"C:\path\to\your\data.xlsx"
# ---------------------------------------------------------------------------
DATA_XLSX_PATH = None   # None = use warehouse/data.xlsx (relative to project)

# ---------------------------------------------------------------------------
# Label printer — Easy-Coder 3400c
# ZPL sent directly via TCP to port 9100, no browser dialog
# ---------------------------------------------------------------------------
LABEL_PRINTER_IP   = '10.59.0.34'
LABEL_PRINTER_PORT = 9100
