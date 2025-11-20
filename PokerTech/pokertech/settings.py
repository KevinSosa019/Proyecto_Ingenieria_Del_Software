import os
from pathlib import Path

# Base directory del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------
# CONFIGURACIÓN PRINCIPAL
# ---------------------------------------------------------

SECRET_KEY = 'replace-this-key'   # Cambiar en producción
DEBUG = True                      # Desactivar en producción
ALLOWED_HOSTS = []                # Añadir dominios/servidores reales


# ---------------------------------------------------------
# APLICACIONES INSTALADAS
# ---------------------------------------------------------
# Nota:
# Se usa SOLO lo necesario para tu proyecto sin Django Admin.

INSTALLED_APPS = [
    'django.contrib.staticfiles',   # Archivos estáticos
    'django.contrib.sessions',      # Manejo de sesiones

    # Apps del proyecto
    'accounts',
    'dashboard',
]


# ---------------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',

    # Sesiones necesarias para login
    'django.contrib.sessions.middleware.SessionMiddleware',

    # Protección CSRF
    'django.middleware.csrf.CsrfViewMiddleware',
]


# ---------------------------------------------------------
# URL PRINCIPAL
# ---------------------------------------------------------

ROOT_URLCONF = 'pokertech.urls'


# ---------------------------------------------------------
# TEMPLATES
# ---------------------------------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        # Carpeta global de templates: /pokertech/templates/
        'DIRS': [BASE_DIR / 'templates'],

        # Permite que Django busque templates dentro de apps
        'APP_DIRS': True,

        'OPTIONS': {
            # Sin context processors extra (tu proyecto no usa request, auth, etc.)
            'context_processors': [],
        },
    },
]


# ---------------------------------------------------------
# WSGI (Servidor Python)
# ---------------------------------------------------------

WSGI_APPLICATION = 'pokertech.wsgi.application'


# ---------------------------------------------------------
# BASE DE DATOS MSSQL (PYODBC / django-mssql)
# ---------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'mssql',

        # Conexión a tu SQL Server
        'NAME': 'MaquinasDePoker',
        'USER': 'log_darkgrepher',
        'PASSWORD': 'Pokemon_1',
        'HOST': 'DARKGREPHER',
        'PORT': '',   # Vacío = valor por defecto

        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    }
}


# ---------------------------------------------------------
# REGIONAL / IDIOMA
# ---------------------------------------------------------

LANGUAGE_CODE = 'es-HN'
TIME_ZONE = 'America/Tegucigalpa'
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------
# STATIC FILES
# ---------------------------------------------------------

STATIC_URL = '/static/'

# Carpeta opcional para archivos (si no existe, no pasa nada)
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]


# ---------------------------------------------------------
# ID DE CAMPOS AUTOMÁTICOS
# ---------------------------------------------------------

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
