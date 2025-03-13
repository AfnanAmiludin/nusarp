from django.core.management.base import BaseCommand
from django.db import transaction
from importlib import import_module
from django.apps import apps

class Command(BaseCommand):
    help = "Menjalankan semua seeders untuk mengisi data dummy dari semua aplikasi"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("🔄 Menjalankan semua seeders dari semua aplikasi..."))

        seeders = []

        for app in apps.get_app_configs():
            try:
                seeder_module = import_module(f"{app.name}.seeders")
                if hasattr(seeder_module, 'SEEDERS'):
                    seeders.extend(seeder_module.SEEDERS)
                else:
                    self.stdout.write(self.style.WARNING(f"⚠️ Modul seeder ditemukan di {app.name} tapi tidak memiliki SEEDERS."))
            except ModuleNotFoundError:
                continue 
            except AttributeError as e:
                self.stdout.write(self.style.WARNING(f"⚠️ Error pada seeder {app.name}: {e}"))

        if not seeders:
            self.stdout.write(self.style.WARNING("⚠️ Tidak ada seeder yang ditemukan."))
            return

        try:
            with transaction.atomic():
                for seeder in seeders:
                    seeder()
            self.stdout.write(self.style.SUCCESS("🎉 Semua data dummy berhasil diisi!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Seeder gagal: {e}"))