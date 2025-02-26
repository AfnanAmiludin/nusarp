# ERP Nusantara - README

## Deskripsi Aplikasi

ERP Nusantara adalah aplikasi **Enterprise Resource Planning (ERP)** yang dirancang untuk membantu pengelolaan berbagai aspek dalam sebuah organisasi. Aplikasi ini menyediakan berbagai fitur untuk mendukung operasional, seperti pengelolaan inventaris, keuangan, manajemen sumber daya manusia, dan lainnya. ERP Nusantara dibangun menggunakan **Django**, **PostgreSQL**, dan **Redis** untuk memberikan performa dan keandalan yang optimal.

## Persyaratan Sistem

Sebelum memulai, pastikan sistem Anda memenuhi persyaratan berikut:

### **1. PostgreSQL**
Aplikasi ini menggunakan PostgreSQL sebagai database utama. Pastikan Anda memiliki PostgreSQL yang sudah terinstal dan berjalan di sistem Anda.

#### Instalasi PostgreSQL:
- **Windows**: Unduh dan instal PostgreSQL dari [situs resmi PostgreSQL](https://www.postgresql.org/download/windows/).
- **Linux**: Gunakan `apt` (Ubuntu/Debian) untuk menginstal PostgreSQL:
  ```bash
  sudo apt update
  sudo apt install postgresql postgresql-contrib
  ```
- **macOS**: Gunakan `brew` untuk menginstal PostgreSQL:
  ```bash
  brew install postgresql
  ```

Setelah PostgreSQL terinstal, pastikan service PostgreSQL sudah berjalan dengan perintah:
```bash
sudo service postgresql start
```

### **2. Python 3.8+**
Aplikasi ini dibangun menggunakan Python. Pastikan Python versi 3.8 atau lebih baru terinstal.

#### Instalasi Python:
- **Windows/Mac/Linux**: Unduh Python dari [situs resmi Python](https://www.python.org/downloads/).
- **Linux**: Install Python menggunakan package manager:
  ```bash
  sudo apt install python3 python3-pip
  ```

### **3. Redis**
Aplikasi ini juga menggunakan Redis untuk caching dan task queue. Redis harus diinstal dan berjalan pada sistem Anda.

#### Instalasi Redis:
- **Windows**: Unduh dan instal Redis dari [Redis Windows Releases](https://github.com/microsoftarchive/redis/releases).
- **Linux**: Gunakan `apt` untuk menginstal Redis:
  ```bash
  sudo apt update
  sudo apt install redis-server
  ```
- **macOS**: Gunakan `brew` untuk menginstal Redis:
  ```bash
  brew install redis
  ```

Pastikan Redis sudah berjalan di background di port default `6379`:
```bash
redis-server
```

### **4. Menginstal Dependencies**
Aplikasi ini menggunakan berbagai pustaka Python. Anda bisa menginstal dependensi yang dibutuhkan dengan menggunakan `pip` dan file `requirements.txt`.

---

## Langkah-langkah untuk Menjalankan Aplikasi

Ikuti langkah-langkah berikut untuk menjalankan aplikasi ERP Nusantara di lokal Anda:

### **1. Clone Repository**
Pertama, clone repository ini ke mesin lokal Anda.

```bash
git clone https://github.com/username/erp-nusantara.git
cd erp-nusantara
```

### **2. Buat Virtual Environment**
Buat dan aktifkan virtual environment untuk proyek ini.

#### Di Windows:
```bash
python -m venv env
.\env\Scripts\activate
```

#### Di Linux/Mac:
```bash
python3 -m venv env
source env/bin/activate
```

### **3. Instal Dependencies**
Instal semua dependensi yang diperlukan dengan menjalankan perintah berikut di dalam virtual environment:

```bash
pip install -r requirements.txt
```

### **4. Salin File `.env`**
Salin file `.env.sample` menjadi `.env` dengan perintah berikut:

```bash
cp .env.sample .env
```

Lalu buka file `.env` dan ubah konfigurasi database sesuai dengan pengaturan PostgreSQL Anda:

```env
DATABASE_POSTGRESQL_NAME=postgres
DATABASE_POSTGRESQL_USER=postgres
DATABASE_POSTGRESQL_PASSWORD=1234560
DATABASE_POSTGRESQL_HOST=localhost
DATABASE_POSTGRESQL_PORT=5432
```

### **5. Jalankan Redis**
Pastikan Redis sudah berjalan di background. Anda bisa menjalankan Redis dengan perintah berikut di terminal:

```bash
redis-server
```

### **6. Menjalankan Aplikasi**
Setelah semua dependensi terinstal dan Redis berjalan, jalankan server Django dengan perintah:

```bash
python manage.py runserver
```

Aplikasi akan berjalan di `http://127.0.0.1:8000`.
---

## Fitur Aplikasi

1. **Pengelolaan Inventaris**: Manajemen produk dan stok barang.
2. **Keuangan**: Mengelola transaksi dan laporan keuangan.
3. **Sumber Daya Manusia**: Pengelolaan karyawan, gaji, dan absensi.
4. **Penyimpanan dan Akses Data**: Menggunakan Redis untuk caching data dan mempercepat akses.
5. **Laporan**: Membuat laporan keuangan dan statistik lainnya.

---

## Catatan

- **Redis**: Aplikasi ini menggunakan Redis untuk caching dan task queue. Jika Anda tidak memerlukan Redis, Anda bisa menonaktifkan caching di `settings.py`.
- **Pengaturan Database**: Pastikan PostgreSQL sudah berjalan sebelum menjalankan aplikasi.
- **Pengujian**: Pastikan semua migrasi berjalan dengan lancar dan tidak ada error saat aplikasi dijalankan.

---

Jika Anda membutuhkan bantuan lebih lanjut atau ada pertanyaan lainnya, silakan buka [issue](https://github.com/username/erp-nusantara/issues) di repository ini.

---