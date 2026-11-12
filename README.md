# 🚲 Dashboard Analisis Bike Sharing - Capital Bikeshare (2011–2012)

Proyek akhir analisis data berbasis Python untuk program Dicoding **"Belajar Analisis Data dengan Python"**. Analisis dilakukan pada dataset Capital Bikeshare di Washington D.C. periode 2011–2012, dilengkapi dengan dashboard interaktif berbasis Streamlit.

---

## 📋 Deskripsi Proyek & Pertanyaan Bisnis (SMART)

Analisis ini dirancang menggunakan kerangka kerja **SMART** (*Specific, Measurable, Action-Oriented, Relevant, Time-bound*) untuk menjawab tiga pertanyaan bisnis utama:

1. **Pertanyaan 1 (Pengaruh Musim & Cuaca):**
   *Bagaimana rata-rata penyewaan sepeda harian (`cnt`) pada tiap kombinasi musim dan kondisi cuaca selama 2011–2012, dan berapa persen penurunannya saat cuaca buruk dibandingkan cuaca cerah?*
   - **Tindakan:** Menentukan aturan penyesuaian armada aktif saat cuaca buruk serta menjadwalkan servis besar tahunan pada musim sepi.

2. **Pertanyaan 2 (Pola Jam & Tipe Pengguna 2012):**
   *Pada jam berapa puncak penyewaan sepeda di hari kerja dibandingkan akhir pekan/hari libur selama 2012, dan bagaimana proporsi pengguna `registered` vs `casual` pada tiap segmen waktu?*
   - **Tindakan:** Mengatur jadwal rute logistik reposisi sepeda sebelum jam sibuk pagi dan sore, serta merancang kampanye promosi konversi member bagi pengguna kasual siang/akhir pekan.

3. **Pertanyaan 3 (Pertumbuhan Tahunan Bulanan / YoY):**
   *Berapa pertumbuhan total penyewaan 2012 dibanding 2011 secara bulanan (Year-over-Year per bulan), dan bulan mana yang pertumbuhannya paling rendah?*
   - **Tindakan:** Memfokuskan kampanye pemasaran musiman pada bulan-bulan berlaju pertumbuhan rendah (Juni, Desember, Juli) dan merencanakan penambahan kapasitas docking station.

---

## 🔬 Teknik Analisis Lanjutan (Non-Machine Learning)

Sesuai saran penilaian, proyek ini menerapkan teknik segmentasi data tanpa machine learning:
1. **Binning Suhu (Temperature Binning):** Mengelompokkan suhu kontinu ke dalam 4 kategori kenyamanan termal manusia menggunakan `pd.cut`: Dingin ($<10^\circ\text{C}$), Sejuk ($10–20^\circ\text{C}$), Hangat ($20–30^\circ\text{C}$), dan Panas ($>30^\circ\text{C}$).
2. **Pengelompokan Segmen Waktu (Time-of-Day Binning):** Mengelompokkan 24 jam ke dalam 5 fase aktivitas perkotaan: Dini hari (00–05), Pagi (06–10), Siang (11–14), Sore (15–19), dan Malam (20–23).
3. **Kategori Permintaan Harian (Quantile Binning - `pd.qcut`):** Mengklasifikasikan beban permintaan harian menjadi 3 kelompok berimbang ($q=3$ / *terciles*): Rendah ($22–3.740$ unit), Sedang ($3.744–5.312$ unit), dan Tinggi ($5.315–8.714$ unit).

---

## 📁 Struktur Berkas

```text
submission/
├── dashboard/
│   ├── dashboard.py          # Aplikasi Streamlit interaktif
│   ├── main_data.csv         # Data harian bersih (731 baris)
│   └── main_hour_data.csv    # Data per jam bersih (17.379 baris)
├── data/
│   ├── day.csv               # Data mentah harian
│   └── hour.csv              # Data mentah per jam
├── notebook.ipynb            # Jupyter Notebook lengkap & tereksekusi
├── README.md                 # Panduan proyek dan instalasi
├── requirements.txt          # Dependensi Python kompatibel
└── url.txt                   # Tautan deploy Streamlit Cloud
```

---

## 🛠️ Panduan Menjalankan Secara Lokal

### 1. Setup Virtual Environment

Menggunakan **venv** (disarankan):
```bash
# Masuk ke direktori submission
cd submission

# Buat virtual environment
python -m venv venv

# Aktivasi di Linux / macOS:
source venv/bin/activate

# Aktivasi di Windows:
venv\Scripts\activate

# Install dependensi yang dibutuhkan
pip install -r requirements.txt
```

Menggunakan **Conda**:
```bash
conda create -n bike-sharing python=3.10
conda activate bike-sharing
pip install -r requirements.txt
```

### 2. Menjalankan Dashboard Streamlit
```bash
# Pastikan berada di dalam folder submission/
streamlit run dashboard/dashboard.py
```
Aplikasi akan terbuka otomatis di browser lokal pada alamat `http://localhost:8501`.

### 3. Menjalankan Jupyter Notebook
```bash
jupyter notebook notebook.ipynb
# atau
jupyter lab notebook.ipynb
```

---

## 🌐 Panduan Deploy ke Streamlit Cloud (Langkah demi Langkah)

Agar `dashboard/dashboard.py` dan `requirements.txt` terbaca dengan benar oleh Streamlit Cloud, **seluruh isi folder `submission/` harus berada di *root* repositori GitHub**:

1. **Masuk ke folder `submission/` dan inisialisasi Git:**
   ```bash
   cd submission
   git init
   git add .
   git commit -m "feat: initial commit submission bike sharing"
   git branch -M main
   git remote add origin https://github.com/<username-kamu>/<nama-repo>.git
   git push -u origin main
   ```
   *(Pastikan file `requirements.txt` dan folder `dashboard/` berada langsung di halaman utama repositori GitHub).*

2. **Deploy di Streamlit Cloud:**
   - Kunjungi [share.streamlit.io](https://share.streamlit.io) dan masuk dengan akun GitHub kamu.
   - Klik tombol **"New app"**.
   - Pilih repositori GitHub yang baru kamu buat.
   - Pada kolom **Main file path**, masukkan: `dashboard/dashboard.py`.
   - Klik **"Deploy!"** dan tunggu proses instalasi selesai.

3. **Salin URL Aplikasi:**
   - Setelah aplikasi berhasil tayang, salin tautan URL aplikasi (format: `https://<nama-app>.streamlit.app`).
   - Tempelkan URL tersebut ke dalam berkas `url.txt`.

---

## 📌 Tautan Aplikasi

Silakan periksa berkas `url.txt` untuk tautan langsung aplikasi Streamlit Cloud.

---
*Dataset: Capital Bikeshare Washington D.C. (2011–2012) · UCI Machine Learning Repository*  
*Proyek Akhir: Belajar Analisis Data dengan Python — Dicoding Indonesia*
