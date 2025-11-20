import os
from django.core.wsgi import get_wsgi_application

# Indica qué archivo de configuración debe usar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pokertech.settings')

# Punto de entrada WSGI para servidores como Gunicorn / Apache
application = get_wsgi_application()
