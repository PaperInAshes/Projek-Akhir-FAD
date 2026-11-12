# Bike Sharing Data Analysis

Proyek ini berisi analisis data pada dataset Bike Sharing. Fokus utamanya adalah memahami pola penggunaan sepeda harian dan per jam berdasarkan berbagai kondisi (seperti musim, cuaca, dan hari libur), serta menyajikan temuan tersebut melalui *dashboard* interaktif.

## Struktur Proyek

- `dashboard/`: Berisi skrip `dashboard.py` dan dataset hasil pembersihan (`main_data.csv`, `main_hour_data.csv`) yang digunakan untuk merender antarmuka aplikasi.
- `notebook.ipynb`: Alur kerja utama yang mendokumentasikan proses *data wrangling*, *exploratory data analysis* (EDA), hingga pembuatan visualisasi.
- `day.csv` & `hour.csv`: Dataset mentah yang menjadi sumber analisis awal.
- `requirements.txt`: Daftar pustaka Python yang wajib diinstal.
- `url.txt`: Informasi tautan akses *dashboard* yang telah dipublikasikan.

## Persiapan Lingkungan

Sebelum menjalankan proyek ini, pastikan Python sudah terinstal di sistem Anda. Sangat disarankan untuk menggunakan *virtual environment* agar tidak mengganggu dependensi proyek lain.

### Menggunakan venv

```bash
# Buka terminal dan arahkan ke direktori proyek
python -m venv env

# Aktifkan virtual environment
# Untuk Windows:
env\Scripts\activate
# Untuk macOS/Linux:
source env/bin/activate

# Instal seluruh dependensi
pip install -r requirements.txt
