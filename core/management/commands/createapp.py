import os
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Create a new app with predefined structure outside the core folder'

    def add_arguments(self, parser):
        parser.add_argument('app_name', type=str, help="Name of the new app")

    def handle(self, *args, **kwargs):
        app_name = kwargs['app_name']
        
        # Tentukan lokasi di mana aplikasi akan dibuat (di luar core)
        app_path = os.path.join(os.getcwd(), app_name)

        # List folder yang harus dibuat
        folders = [
            'apis',
            'apis/serializers',
            'apis/views',
            'apis/tests',
            'constants',
            'fields',
            'fixtures',
            'forms',
            'management',
            'management/commands',
            'middleware',
            'migrations',
            'models',
            'templates',
            'static',
            'static/css',
            'static/js',
            'static/img',
            'views',
            'tests',
            'utils',
        ]
        
        # Buat folder aplikasi dan struktur direktori
        for folder in folders:
            folder_path = os.path.join(app_path, folder)
            os.makedirs(folder_path, exist_ok=True)
            self.stdout.write(self.style.SUCCESS(f"Folder created: {folder_path}"))

        # Membuat file `__init__.py` di dalam folder `models`, `serializers`, dll
        init_files = [
            'apis/__init__.py',
            'apis/serializers/__init__.py',
            'apis/views/__init__.py',
            'apis/tests/__init__.py',
            'apis/urls.py',
            'constants/__init__.py',
            'fields/__init__.py',
            'forms/__init__.py',
            'management/__init__.py',
            'management/commands/__init__.py',
            'middleware/__init__.py',
            'migrations/__init__.py',
            'models/__init__.py',
            'views/__init__.py',
            'tests/__init__.py',
            'utils/__init__.py',    
        ]

        for file_path in init_files:
            full_path = os.path.join(app_path, file_path)
            with open(full_path, 'w') as f:
                f.write('__all__ = []\n')  # Isi dengan __all__
            self.stdout.write(self.style.SUCCESS(f"File created: {full_path}"))

        # Membuat file `apps.py` untuk aplikasi baru
        with open(os.path.join(app_path, 'apps.py'), 'w') as f:
            f.write(f"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ApplicationConfig(AppConfig):
    name = '{app_name}'
    verbose_name = _('Application')

    def ready(self):
        import {app_name}.signals
""")
        self.stdout.write(self.style.SUCCESS(f"File 'apps.py' created in {app_path}"))

        # Membuat file `admin.py` untuk aplikasi baru
        with open(os.path.join(app_path, 'admin.py'), 'w') as f:
            f.write(f"""# Register your models here\n""")
        self.stdout.write(self.style.SUCCESS(f"File 'admin.py' created in {app_path}"))

        # Membuat file `.gitignore` untuk aplikasi baru
        with open(os.path.join(app_path, '.gitignore'), 'w') as f:
            f.write("""\n__pycache__\n*.pyc\n*.pyo\n*.pyd\n*.db\n*.sqlite3\n*.log\n.DS_Store\nenv/\nvenv/\nstatic/\n""")
        self.stdout.write(self.style.SUCCESS(f"File '.gitignore' created in {app_path}"))

        # Membuat file `urls.py` untuk aplikasi baru
        with open(os.path.join(app_path, 'urls.py'), 'w') as f:
            f.write("from django.urls import path\n\n")
            f.write("urlpatterns = [\n    # Tambahkan URL di sini\n]\n")
        self.stdout.write(self.style.SUCCESS(f"File 'urls.py' created in {app_path}"))

        # Membuat file `signals.py` untuk aplikasi baru
        with open(os.path.join(app_path, 'signals.py'), 'w') as f:
            f.write(f"""
from django.db import connection
from django.db.models.signals import pre_migrate
from django.dispatch import receiver
from django.conf import settings

@receiver(pre_migrate)
def create_schema(sender, **kwargs):
    schema_name = getattr(settings, "SCHEMA", "{app_name}")
    with connection.cursor() as cursor:
        cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{{schema_name}}";')
""")
        self.stdout.write(self.style.SUCCESS(f"File 'signals.py' created in {app_path}"))

        # Membuat file `settings.py` untuk aplikasi baru
        with open(os.path.join(app_path, 'settings.py'), 'w') as f:
            f.write(f"""
import logging
import sys
from pathlib import Path

from django.conf import settings as djangosettings
from {app_name}.apps import ApplicationConfig

DEFAULTS = dict(
    SCHEMA=ApplicationConfig.name,
)

SCHEMA = DEFAULTS["SCHEMA"]
""")
        self.stdout.write(self.style.SUCCESS(f"File 'settings.py' created in {app_path}"))

        # Membuat file README.md untuk aplikasi baru
        with open(os.path.join(app_path, 'README.md'), 'w') as f:
            f.write(f"# {app_name.capitalize()} App\n\nThis is the {app_name} app.\n\n## Setup\n\n1. Add the app to `INSTALLED_APPS` in `settings.py`\n")
        self.stdout.write(self.style.SUCCESS(f"File 'README.md' created in {app_path}"))

        # Menambahkan URL ke setup/urls.py
        self._add_url_to_root_urls(app_name)

        self.stdout.write(self.style.SUCCESS(f"App '{app_name}' created successfully"))

    def _add_url_to_root_urls(self, app_name):
        """Menambahkan URL aplikasi yang baru dibuat ke dalam setup/urls.py"""
        root_urls_path = os.path.join(os.getcwd(), 'setup', 'urls.py')

        if os.path.exists(root_urls_path):
            with open(root_urls_path, 'r') as file:
                lines = file.readlines()

            # Cari bagian 'urlpatterns' dan tambahkan URL aplikasi baru
            added = False
            for idx, line in enumerate(lines):
                if 'urlpatterns' in line:
                    # Pastikan tidak menambahkan duplikat
                    for existing_line in lines[idx:]:
                        if f"from {app_name}.urls import urlpatterns as {app_name}_urls" in existing_line:
                            added = True
                            break
                    if not added:
                        # Menambahkan URL di bawah bagian urlpatterns
                        lines.insert(idx + 1, f"from {app_name}.urls import urlpatterns as {app_name}_urls\n")
                        lines.insert(idx + 2, f"urlpatterns += {app_name}_urls\n")
                        break

            if not added:
                # Jika URL belum ada, tambahkan URL baru
                with open(root_urls_path, 'w') as file:
                    file.writelines(lines)
                self.stdout.write(self.style.SUCCESS(f"URL for '{app_name}' added to 'setup/urls.py'"))
            else:
                self.stdout.write(self.style.SUCCESS(f"URL for '{app_name}' already exists in 'setup/urls.py'"))
        else:
            self.stdout.write(self.style.ERROR(f"File 'urls.py' not found in 'setup' directory"))
