import os
import subprocess
import time
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Start Redis server from Django command on Windows'

    def handle(self, *args, **kwargs):
        # Tentukan path ke redis-server.exe di folder bin/redis/latest
        redis_server_path = os.path.join(os.getcwd(), 'bin', 'redis', 'latest', 'redis-server.exe')

        # Cek apakah redis-server.exe ada di lokasi yang benar
        if not os.path.exists(redis_server_path):
            self.stdout.write(self.style.ERROR(f"Error: redis-server.exe not found at {redis_server_path}."))
            return

        try:
            # Menjalankan Redis server dengan subprocess.Popen untuk menjalankan Redis di background
            self.stdout.write(self.style.SUCCESS(f"Starting Redis server from {redis_server_path}..."))

            # Menjalankan Redis di background (stdout dan stderr di-redirect ke pipe)
            process = subprocess.Popen(
                [redis_server_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,  # Agar Redis menerima input dan tidak berhenti
                shell=True  # Gunakan shell untuk menjalankan perintah
            )

            # Tunggu sejenak agar Redis benar-benar berjalan
            time.sleep(5)  # Menunggu 5 detik agar Redis sempat memulai

            # Periksa apakah Redis berjalan dengan memeriksa output
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                self.stdout.write(self.style.SUCCESS("Redis server is running"))
            else:
                self.stdout.write(self.style.ERROR(f"Redis server failed to start. Error: {stderr.decode('utf-8')}"))

        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f"Error: Unable to start Redis server. {e}"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("Error: redis-server.exe not found. Please ensure Redis is installed correctly."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An unexpected error occurred: {e}"))
