#!/usr/bin/env python
import os
import sys

def main():
    # Define el archivo de configuración de Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pokertech.settings')

    try:
        # Ejecuta los comandos de administración de Django (runserver, migrate, etc.)
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Error amigable si Django no está instalado
        raise ImportError("Couldn't import Django.") from exc

    # Procesa los comandos recibidos por consola
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
