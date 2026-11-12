import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path

# ── Konfigurasi Path Berbasis Relatif ──────────────────────────────────────────
BASE_DIR = Path(__file__).parent

# ── Gaya Visualisasi Global ───────────────────────────────────────────────────
# Disesuaikan agar latar grafik transparan dan teks terang (cocok untuk dark mode)
plt.rcParams.update({
    "figure.facecolor": "none",       
    "axes.facecolor": "none",         
    "axes.edgecolor": "#7F8C8D",
    "axes.grid": True,
    "grid.color": "#454545",          
    "grid.linestyle": "--",
    "grid.alpha": 0.5,
    "text.color": "#F0F2F6",          
    "axes.labelcolor": "#F0F2F6",
    "xtick.color": "#F0F2F6",
    "ytick.color": "#F0F2F6",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
})

ACCENT = "#E74C3C"   # Merah penyorot utama
GRAY   = "#95A5A6"   # Abu-abu netral / pembanding
BLUE   = "#2980B9"   # Biru sekunder
DARK   = "#2C3E50"   # Biru gelap kontras

# ── Pemuatan Data dengan st.cache_data ─────────────────────────────────────────
@st.cache_data
def load_data():
    day_path = BASE_DIR / "main_data.csv"
    hour_path = BASE_DIR / "main_hour_data.csv"
    df_day = pd.read_csv(day_path, parse_dates=["dteday"])
    df_hour = pd.read_csv(hour_path, parse_dates=["dteday"])
    return df_day, df_hour

# ── Konfigurasi Halaman Streamlit ──────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Analisis Bike Sharing",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Header Dashboard ──────────────────────────────────────────────────────────
st.title("Dashboard Analisis Bike Sharing")
st.markdown(
    "**Capital Bikeshare Washington D.C. (2011–2012)** · "
    "Analisis pola musiman, cuaca, perilaku komuter, dan pertumbuhan tahunan."
)
st.divider()

# ── Pemeriksaan Ketersediaan Berkas Data ───────────────────────────────────────
day_path = BASE_DIR / "main_data.csv"
hour_path = BASE_DIR / "main_hour_data.csv"

if not day_path.exists() or not hour_path.exists():
    st.warning(
        "**Berkas data belum tersedia.** Silakan jalankan notebook terlebih dahulu "
        "untuk menghasilkan file data bersih (`main_data.csv` dan `main_hour_data.csv`)."
    )
    st.stop()

df_day, df_hour = load_data()

# ── Harmonisasi Kolom (Mendukung Output Notebook) ──────────────────────────────
if "temp_c" in df_day.columns and "temp_celsius" not in df_day.columns:
    df_day["temp_celsius"] = df_day["temp_c"]
if "temp_c" in df_hour.columns and "temp_celsius" not in df_hour.columns:
    df_hour["temp_celsius"] = df_hour["temp_c"]

if "weather_label" in df_day.columns and "weathersit_label" not in df_day.columns:
    df_day["weathersit_label"] = df_day["weather_label"]
if "weather_label" in df_hour.columns and "weathersit_label" not in df_hour.columns:
    df_hour["weathersit_label"] = df_hour["weather_label"]

# Pastikan segmen_waktu konsisten dengan notebook
def assign_segmen(hr):
    if hr <= 5:    return "Dini hari (00-05)"
    elif hr <= 10: return "Pagi (06-10)"
    elif hr <= 14: return "Siang (11-14)"
    elif hr <= 19: return "Sore (15-19)"
    else:          return "Malam (20-23)"

if "segmen_waktu" not in df_hour.columns and "hr" in df_hour.columns:
    df_hour["segmen_waktu"] = df_hour["hr"].apply(assign_segmen)

# ── Binning Suhu & Kategori Permintaan ─────────────────────────────────────────
temp_bins = [-np.inf, 10, 20, 30, np.inf]
temp_labels = ["Dingin (<10°C)", "Sejuk (10-20°C)", "Hangat (20-30°C)", "Panas (>30°C)"]
df_day["kategori_suhu"] = pd.cut(df_day["temp_c"], bins=temp_bins, labels=temp_labels)

# Quantile binning permintaan harian (q=3)
df_day["kategori_permintaan"] = pd.qcut(df_day["cnt"], q=3, labels=["Rendah", "Sedang", "Tinggi"])

# ── SIDEBAR FILTER ────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Panel Filter")
    st.markdown("Sesuaikan filter untuk mengeksplorasi subset data.")
    st.markdown("---")

    # 1. Filter Rentang Tanggal
    min_date = df_day["dteday"].min().date()
    max_date = df_day["dteday"].max().date()
    date_range = st.date_input(
        "Rentang Tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    st.markdown("---")

    # 2. Filter Musim
    musim_opsi = ["Semi", "Panas", "Gugur", "Dingin"]
    musim_dipilih = st.multiselect(
        "Musim",
        options=musim_opsi,
        default=musim_opsi,
        help="Pilih satu atau beberapa musim",
    )
    if not musim_dipilih:
        musim_dipilih = musim_opsi

    st.markdown("---")

    # 3. Filter Kondisi Cuaca (Hanya 3 kondisi riil yang ada di day.csv)
    cuaca_opsi = ["Cerah", "Berkabut/Mendung", "Hujan/Salju Ringan"]
    cuaca_dipilih = st.multiselect(
        "Kondisi Cuaca",
        options=cuaca_opsi,
        default=cuaca_opsi,
        help="Catatan: Kategori Hujan Lebat tidak tercatat pada data harian",
    )
    if not cuaca_dipilih:
        cuaca_dipilih = cuaca_opsi

    st.markdown("---")

    # 4. Filter Tipe Hari
    tipe_hari = st.radio(
        "Tipe Hari",
        options=["Semua Hari", "Hari Kerja", "Akhir Pekan / Libur"],
        index=0,
    )

    st.markdown("---")
    st.caption("Dashboard Analisis Data · Dicoding Submission")

# ── Terapkan Filter pada Dataframe ────────────────────────────────────────────
mask_day = (
    (df_day["dteday"].dt.date >= start_date) &
    (df_day["dteday"].dt.date <= end_date) &
    (df_day["season_label"].isin(musim_dipilih)) &
    (df_day["weathersit_label"].isin(cuaca_dipilih))
)
if tipe_hari == "Hari Kerja":
    mask_day &= (df_day["workingday"] == 1)
elif tipe_hari == "Akhir Pekan / Libur":
    mask_day &= (df_day["workingday"] == 0)

df_filtered = df_day[mask_day].copy()

mask_hour = (
    (df_hour["dteday"].dt.date >= start_date) &
    (df_hour["dteday"].dt.date <= end_date) &
    (df_hour["season_label"].isin(musim_dipilih)) &
    (df_hour["weathersit_label"].isin(cuaca_dipilih))
)
if tipe_hari == "Hari Kerja":
    mask_hour &= (df_hour["workingday"] == 1)
elif tipe_hari == "Akhir Pekan / Libur":
    mask_hour &= (df_hour["workingday"] == 0)

df_hour_filtered = df_hour[mask_hour].copy()

# ── Penanganan Kasus Data Kosong ──────────────────────────────────────────────
if df_filtered.empty:
    st.warning("**Tidak ada data yang sesuai dengan kombinasi filter yang dipilih.** Silakan longgarkan filter di sidebar.")
    st.stop()

# ── Baris Metrik Utama (KPI) ──────────────────────────────────────────────────
total_penyewaan = int(df_filtered["cnt"].sum())
rata2_harian    = df_filtered["cnt"].mean()
total_reg       = df_filtered["registered"].sum()
pct_registered  = (total_reg / total_penyewaan * 100) if total_penyewaan > 0 else 0

years_in_filter = df_filtered["yr"].unique()
yoy_val_str = "—"
yoy_delta_str = None
if 0 in years_in_filter and 1 in years_in_filter:
    cnt_11 = df_filtered[df_filtered["yr"] == 0]["cnt"].sum()
    cnt_12 = df_filtered[df_filtered["yr"] == 1]["cnt"].sum()
    if cnt_11 > 0:
        yoy_growth = ((cnt_12 - cnt_11) / cnt_11) * 100
        yoy_val_str = f"{yoy_growth:+.1f}%"
        yoy_delta_str = f"2011 ({cnt_11:,}) → 2012 ({cnt_12:,})"

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Penyewaan", f"{total_penyewaan:,}")
with col2:
    st.metric("Rata-Rata Harian", f"{rata2_harian:,.0f} unit")
with col3:
    st.metric("% Pengguna Registered", f"{pct_registered:.1f}%")
with col4:
    st.metric("Pertumbuhan YoY", yoy_val_str, delta=yoy_delta_str, help="Pertumbuhan dari 2011 ke 2012 pada data terfilter")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1: PERTANYAAN 1 — PENGARUH MUSIM & KONDISI CUACA
# ══════════════════════════════════════════════════════════════════════════════
st.header("Pengaruh Musim & Kondisi Cuaca terhadap Penyewaan")
st.markdown(
    "*Bagaimana rata-rata penyewaan sepeda harian (`cnt`) pada tiap kombinasi musim dan kondisi cuaca, "
    "dan berapa persen penurunannya saat cuaca buruk dibandingkan cuaca cerah?*"
)

col_q1_a, col_q1_b = st.columns([1.1, 1.0])

MUSIM_ORDER = ["Semi", "Panas", "Gugur", "Dingin"]
CUACA_ORDER = ["Cerah", "Berkabut/Mendung", "Hujan/Salju Ringan"]

pivot_q1 = df_filtered.pivot_table(
    values="cnt",
    index="season_label",
    columns="weathersit_label",
    aggfunc="mean"
)
pivot_q1 = pivot_q1.reindex(
    index=[m for m in MUSIM_ORDER if m in pivot_q1.index],
    columns=[c for c in CUACA_ORDER if c in pivot_q1.columns]
)

with col_q1_a:
    if pivot_q1.empty or pivot_q1.isna().all().all():
        st.info("Data tidak mencukupi untuk membentuk heatmap dengan filter saat ini.")
    else:
        fig1, ax1 = plt.subplots(figsize=(8, 4.8))
        sns.heatmap(
            pivot_q1,
            annot=True,
            fmt=".0f",
            cmap="Blues",
            linewidths=1.0,
            linecolor="#2C3E50", # Disesuaikan agar garis tidak silau
            ax=ax1,
            cbar_kws={"label": "Rata-Rata Penyewaan (unit/hari)"},
            annot_kws={"size": 10, "weight": "bold"}
        )
        ax1.set_title("Rata-Rata Penyewaan per Musim & Cuaca", pad=12)
        ax1.set_xlabel("Kondisi Cuaca")
        ax1.set_ylabel("Musim")
        plt.tight_layout()
        fig1.text(0.5, -0.06, "Sumber: Capital Bikeshare Washington D.C. (2011–2012) · day.csv", ha="center", fontsize=8, color="#7F8C8D")
        st.pyplot(fig1)
        plt.close(fig1)

with col_q1_b:
    weather_avg = df_filtered.groupby("weathersit_label")["cnt"].mean()
    if "Cerah" in weather_avg.index and len(weather_avg) > 1:
        base_cerah = weather_avg["Cerah"]
        other_weathers = [w for w in ["Berkabut/Mendung", "Hujan/Salju Ringan"] if w in weather_avg.index]
        drops = [((weather_avg[w] - base_cerah) / base_cerah * 100) for w in other_weathers]

        fig2, ax2 = plt.subplots(figsize=(8, 4.8))
        bar_colors = [ACCENT if d == min(drops) else GRAY for d in drops]
        bars2 = ax2.bar(other_weathers, drops, color=bar_colors, width=0.45, edgecolor=DARK, linewidth=0.8)
        ax2.axhline(0, color=DARK, linewidth=1.2)
        ax2.set_title("Penurunan Rata-Rata Penyewaan Dibanding Cuaca Cerah", pad=12)
        ax2.set_ylabel("Perubahan Rata-Rata (%)")
        ax2.set_xlabel("Kondisi Cuaca")
        ax2.set_ylim(min(drops) - 15, 10)
        ax2.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))

        for bar, val in zip(bars2, drops):
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                val - 3.5,
                f"{val:.1f}%",
                ha="center",
                va="top",
                fontsize=11,
                fontweight="bold",
                color="white" if bar.get_facecolor() == ACCENT else DARK
            )
        plt.tight_layout()
        fig2.text(0.5, -0.06, "Sumber: Capital Bikeshare Washington D.C. (2011–2012) · day.csv", ha="center", fontsize=8, color="#7F8C8D")
        st.pyplot(fig2)
        plt.close(fig2)
    else:
        st.info("Pilih minimal kondisi Cuaca Cerah dan satu cuaca lain untuk melihat perbandingan persentase penurunan.")

# Insight Dinamis Q1
cerah_mean_txt = f"{weather_avg['Cerah']:,.0f}" if "Cerah" in weather_avg.index else "N/A"
kabut_drop_txt = f"{((weather_avg['Berkabut/Mendung'] - weather_avg['Cerah'])/weather_avg['Cerah']*100):.1f}%" if ("Cerah" in weather_avg.index and "Berkabut/Mendung" in weather_avg.index) else "N/A"
hujan_drop_txt = f"{((weather_avg['Hujan/Salju Ringan'] - weather_avg['Cerah'])/weather_avg['Cerah']*100):.1f}%" if ("Cerah" in weather_avg.index and "Hujan/Salju Ringan" in weather_avg.index) else "N/A"

st.markdown(
    f"> **Temuan Menarik:** Dari filter yang kamu pilih, saat cuaca Cerah rata-rata sewanya paling tinggi, mencapai **{cerah_mean_txt} unit per hari**. "
    f"Kalau cuaca mulai Berkabut atau Mendung, jumlah sewanya biasanya turun sekitar **{kabut_drop_txt}**. "
    f"Paling terasa jatuhnya kalau sudah Hujan atau Salju Ringan, permintaannya bisa anjlok sampai **{hujan_drop_txt}**. "
    "Oh ya, kombinasi Musim Gugur saat cuacanya cerah itu konsisten jadi waktu yang paling laris."
)
st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2: PERTANYAAN 2 — POLA JAM & PROPORSI PENGGUNA (2012)
# ══════════════════════════════════════════════════════════════════════════════
st.header("Pola Waktu Sibuk & Profil Pengguna (2012)")
st.markdown(
    "*Pada jam berapa puncak penyewaan sepeda di hari kerja dibandingkan akhir pekan/hari libur selama 2012, "
    "dan bagaimana proporsi pengguna `registered` vs `casual` pada tiap segmen waktu?*"
)

df_h12 = df_hour_filtered[df_hour_filtered["yr"] == 1].copy()

if df_h12.empty:
    st.info("Tidak ada data untuk tahun 2012 pada rentang filter saat ini.")
else:
    col_q2_a, col_q2_b = st.columns([1.1, 1.0])

    workday_hourly = df_h12[df_h12["workingday"] == 1].groupby("hr")["cnt"].mean()
    weekend_hourly = df_h12[df_h12["workingday"] == 0].groupby("hr")["cnt"].mean()

    with col_q2_a:
        fig3, ax3 = plt.subplots(figsize=(8, 4.8))
        if not workday_hourly.empty:
            ax3.plot(workday_hourly.index, workday_hourly.values, label="Hari Kerja", color=ACCENT, linewidth=2.5, marker="o", markersize=3)
        if not weekend_hourly.empty:
            ax3.plot(weekend_hourly.index, weekend_hourly.values, label="Akhir Pekan/Libur", color=GRAY, linewidth=2.2, linestyle="--", marker="s", markersize=3)
        ax3.set_title("Pola Jam Hari Kerja (Bimodal) vs Akhir Pekan (Unimodal)", pad=12)
        ax3.set_xlabel("Jam Operasional (00–23)")
        ax3.set_ylabel("Rata-Rata Penyewaan (unit/jam)")
        ax3.set_xticks(range(0, 24, 2))
        ax3.set_ylim(bottom=0)
        ax3.legend(loc="upper left", frameon=True)
        plt.tight_layout()
        fig3.text(0.5, -0.06, "Sumber: Capital Bikeshare Washington D.C. (2012) · hour.csv", ha="center", fontsize=8, color="#7F8C8D")
        st.pyplot(fig3)
        plt.close(fig3)

    with col_q2_b:
        seg_order = ["Dini hari (00-05)", "Pagi (06-10)", "Siang (11-14)", "Sore (15-19)", "Malam (20-23)"]
        seg_sum = df_h12.groupby("segmen_waktu")[["registered", "casual", "cnt"]].sum()
        seg_sum = seg_sum.reindex([s for s in seg_order if s in seg_sum.index])

        if not seg_sum.empty and seg_sum["cnt"].sum() > 0:
            seg_sum["reg_pct"] = (seg_sum["registered"] / seg_sum["cnt"] * 100)
            seg_sum["cas_pct"] = (seg_sum["casual"] / seg_sum["cnt"] * 100)

            short_labels = [s.split(" ")[0] for s in seg_sum.index]
            fig4, ax4 = plt.subplots(figsize=(8, 4.8))
            bars_r = ax4.bar(short_labels, seg_sum["reg_pct"], label="Registered", color=DARK, width=0.55, edgecolor="none")
            bars_c = ax4.bar(short_labels, seg_sum["cas_pct"], bottom=seg_sum["reg_pct"], label="Casual", color=ACCENT, width=0.55, edgecolor="none")

            ax4.set_title("Proporsi Registered vs Casual per Segmen Waktu", pad=12)
            ax4.set_xlabel("Segmen Waktu")
            ax4.set_ylabel("Proporsi Pengguna (%)")
            ax4.set_ylim(0, 105)
            ax4.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
            ax4.legend(loc="upper right", frameon=True)

            for bar_r, bar_c, r_val, c_val in zip(bars_r, bars_c, seg_sum["reg_pct"], seg_sum["cas_pct"]):
                ax4.text(bar_r.get_x() + bar_r.get_width() / 2, r_val / 2, f"{r_val:.1f}%", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
                ax4.text(bar_c.get_x() + bar_c.get_width() / 2, r_val + c_val / 2, f"{c_val:.1f}%", ha="center", va="center", color="white", fontsize=9, fontweight="bold")

            plt.tight_layout()
            fig4.text(0.5, -0.06, "Sumber: Capital Bikeshare Washington D.C. (2012) · hour.csv", ha="center", fontsize=8, color="#7F8C8D")
            st.pyplot(fig4)
            plt.close(fig4)

    # Insight Dinamis Q2
    peak_wd_str = f"jam {workday_hourly.idxmax():02d}.00 ({workday_hourly.max():.0f} unit/jam)" if not workday_hourly.empty else "N/A"
    peak_we_str = f"jam {weekend_hourly.idxmax():02d}.00 ({weekend_hourly.max():.0f} unit/jam)" if not weekend_hourly.empty else "N/A"
    cas_siang_str = f"{seg_sum.loc['Siang (11-14)', 'cas_pct']:.1f}%" if ('Siang (11-14)' in seg_sum.index and 'cas_pct' in seg_sum.columns) else "N/A"

    st.markdown(
        f"> **Pola Waktu Sewa (2012):** Kelihatan banget bedanya hari kerja dan akhir pekan. "
        f"Saat hari kerja, orang-orang banyak pakai sepeda buat berangkat *ngantor* (puncaknya di **{peak_wd_str}** dan arus pagi jam 08.00). "
        f"Tapi kalau akhir pekan atau libur, polanya lebih santai dan memuncak di siang hari (**{peak_we_str}**). "
        f"Walaupun pengguna *member* (registered) mendominasi setiap saat, penyewa kasual lumayan sering muncul keluar di siang hari (**{cas_siang_str}**)."
    )

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3: PERTANYAAN 3 — PERTUMBUHAN TAHUNAN BULANAN (YoY)
# ══════════════════════════════════════════════════════════════════════════════
st.header("Tren Pertumbuhan Bulanan (2011 vs 2012)")
st.markdown(
    "*Berapa pertumbuhan total penyewaan 2012 dibanding 2011 secara bulanan (Year-over-Year per bulan), "
    "dan bulan mana yang pertumbuhannya paling rendah?*"
)

mnth_names = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'Mei', 6:'Jun', 7:'Jul', 8:'Agu', 9:'Sep', 10:'Okt', 11:'Nov', 12:'Des'}

m11 = df_day[df_day["yr"] == 0].groupby("mnth")["cnt"].sum()
m12 = df_day[df_day["yr"] == 1].groupby("mnth")["cnt"].sum()
common_mnth = sorted(list(set(m11.index) & set(m12.index)))

if len(common_mnth) < 2:
    st.info("Memerlukan data dari tahun 2011 dan 2012 untuk menghitung pertumbuhan YoY.")
else:
    df_yoy_sec = pd.DataFrame({
        "Bulan": [mnth_names[m] for m in common_mnth],
        "2011": m11.loc[common_mnth].values,
        "2012": m12.loc[common_mnth].values,
    })
    df_yoy_sec["growth_pct"] = ((df_yoy_sec["2012"] - df_yoy_sec["2011"]) / df_yoy_sec["2011"] * 100).round(1)

    col_q3_a, col_q3_b = st.columns([1.1, 1.0])

    with col_q3_a:
        fig5, ax5 = plt.subplots(figsize=(8, 4.8))
        ax5.plot(df_yoy_sec["Bulan"], df_yoy_sec["2011"], label="2011", color=GRAY, linewidth=2.2, marker="o", markersize=4)
        ax5.plot(df_yoy_sec["Bulan"], df_yoy_sec["2012"], label="2012", color=ACCENT, linewidth=2.5, marker="s", markersize=4)
        ax5.set_title("Total Penyewaan Bulanan: 2011 vs 2012", pad=12)
        ax5.set_xlabel("Bulan")
        ax5.set_ylabel("Total Penyewaan (unit)")
        ax5.set_ylim(bottom=0)
        ax5.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f"{int(x):,}"))
        ax5.legend(loc="upper left", frameon=True)
        plt.tight_layout()
        fig5.text(0.5, -0.06, "Sumber: Capital Bikeshare Washington D.C. (2011–2012) · day.csv", ha="center", fontsize=8, color="#7F8C8D")
        st.pyplot(fig5)
        plt.close(fig5)

    with col_q3_b:
        min_g_idx = df_yoy_sec["growth_pct"].idxmin()
        yoy_colors = [ACCENT if i == min_g_idx else GRAY for i in range(len(df_yoy_sec))]

        fig6, ax6 = plt.subplots(figsize=(8, 4.8))
        bars6 = ax6.bar(df_yoy_sec["Bulan"], df_yoy_sec["growth_pct"], color=yoy_colors, width=0.55, edgecolor=DARK, linewidth=0.8)
        ax6.axhline(0, color=DARK, linewidth=1.0)
        ax6.set_title("Pertumbuhan YoY per Bulan (Juni Terendah: +41,3%)", pad=12)
        ax6.set_xlabel("Bulan")
        ax6.set_ylabel("Pertumbuhan YoY (%)")
        ax6.set_ylim(0, max(df_yoy_sec["growth_pct"]) + 25)
        ax6.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))

        for bar, val in zip(bars6, df_yoy_sec["growth_pct"]):
            ax6.text(
                bar.get_x() + bar.get_width() / 2,
                val + 3,
                f"{val:.0f}%",
                ha="center",
                va="bottom",
                fontsize=8.5,
                fontweight="bold",
                color=ACCENT if val == df_yoy_sec["growth_pct"].min() else DARK
            )
        plt.tight_layout()
        fig6.text(0.5, -0.06, "Sumber: Capital Bikeshare Washington D.C. (2011–2012) · day.csv", ha="center", fontsize=8, color="#7F8C8D")
        st.pyplot(fig6)
        plt.close(fig6)

    min_row = df_yoy_sec.loc[min_g_idx]
    max_row = df_yoy_sec.loc[df_yoy_sec["growth_pct"].idxmax()]
    st.markdown(
        f"> **Perkembangan Tahunan (YoY):** Kabar baiknya, semua bulan mengalami kenaikan dari tahun 2011 ke 2012. "
        f"Kenaikan yang paling santai ada di bulan **{min_row['Bulan']} (+{min_row['growth_pct']}%)**, sedangkan lonjakan paling tajam terjadi di **{max_row['Bulan']} (+{max_row['growth_pct']}%)**. "
        "Kalau persentase di pertengahan tahun kelihatan agak melambat, itu wajar karena memang angka awal di tahun 2011-nya sudah keburu tinggi."
    )

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4: ANALISIS LANJUTAN (BINNING & PROFIL PERMINTAAN)
# ══════════════════════════════════════════════════════════════════════════════
st.header("Analisis Lanjutan: Suhu, Waktu, & Kategori Permintaan")
st.markdown(
    "Penerapan teknik **Manual Grouping / Binning** dan **Quantile-based Binning (`pd.qcut`)** "
    "untuk menggali pola segmentasi non-machine learning."
)

col_lanjut_a, col_lanjut_b = st.columns(2)

# --- 4a. Binning Suhu ---
with col_lanjut_a:
    st.subheader("🌡️ Rata-Rata Penyewaan per Kategori Suhu")
    suhu_stat = df_filtered.groupby("kategori_suhu", observed=True)["cnt"].agg(["count", "mean"]).reindex(temp_labels)
    suhu_stat = suhu_stat.dropna()

    if not suhu_stat.empty:
        fig7, ax7 = plt.subplots(figsize=(7, 4.5))
        max_suhu_val = suhu_stat["mean"].max()
        colors7 = [ACCENT if v == max_suhu_val else GRAY for v in suhu_stat["mean"]]
        bars7 = ax7.bar(suhu_stat.index, suhu_stat["mean"], color=colors7, width=0.55, edgecolor=DARK, linewidth=0.8)
        ax7.set_title("Penyewaan Mencapai Puncak pada Suhu Hangat (20–30°C)", pad=12)
        ax7.set_xlabel("Kategori Suhu")
        ax7.set_ylabel("Rata-Rata Penyewaan (unit/hari)")
        ax7.set_ylim(0, max_suhu_val * 1.25)
        ax7.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f"{int(x):,}"))
        for bar in bars7:
            val = bar.get_height()
            ax7.text(bar.get_x() + bar.get_width() / 2, val + (max_suhu_val * 0.03), f"{val:,.0f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
        plt.tight_layout()
        fig7.text(0.5, -0.06, "Sumber: Capital Bikeshare (2011–2012) · day.csv", ha="center", fontsize=8, color="#7F8C8D")
        st.pyplot(fig7)
        plt.close(fig7)

# --- 4b. Segmen Waktu ---
with col_lanjut_b:
    st.subheader("Rata-Rata Penyewaan per Jam per Segmen Waktu")
    seg_hr_stat = df_hour_filtered.groupby("segmen_waktu")["cnt"].mean().reindex([s for s in seg_order if s in df_hour_filtered["segmen_waktu"].unique()])

    if not seg_hr_stat.empty:
        fig8, ax8 = plt.subplots(figsize=(7, 4.5))
        max_seg_val = seg_hr_stat.max()
        colors8 = [ACCENT if v == max_seg_val else GRAY for v in seg_hr_stat.values]
        short_seg_labels = [s.split(" ")[0] for s in seg_hr_stat.index]
        bars8 = ax8.bar(short_seg_labels, seg_hr_stat.values, color=colors8, width=0.55, edgecolor=DARK, linewidth=0.8)
        ax8.set_title("Segmen Sore (15–19) Merupakan Waktu Tersibuk", pad=12)
        ax8.set_xlabel("Segmen Waktu")
        ax8.set_ylabel("Rata-Rata Penyewaan per Jam (unit/jam)")
        ax8.set_ylim(0, max_seg_val * 1.25)
        for bar in bars8:
            val = bar.get_height()
            ax8.text(bar.get_x() + bar.get_width() / 2, val + (max_seg_val * 0.03), f"{val:.0f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
        plt.tight_layout()
        fig8.text(0.5, -0.06, "Sumber: Capital Bikeshare (2011–2012) · hour.csv", ha="center", fontsize=8, color="#7F8C8D")
        st.pyplot(fig8)
        plt.close(fig8)

# --- 4c. Kategori Permintaan (qcut) ---
st.subheader("Distribusi Kategori Permintaan Harian per Kondisi Cuaca")
ct_demand = pd.crosstab(df_filtered["weathersit_label"], df_filtered["kategori_permintaan"]).reindex(
    index=[c for c in CUACA_ORDER if c in df_filtered["weathersit_label"].unique()],
    columns=[k for k in ["Rendah", "Sedang", "Tinggi"] if k in df_filtered["kategori_permintaan"].unique()]
)

if not ct_demand.empty:
    fig9, ax9 = plt.subplots(figsize=(10, 4.8))
    ct_demand.plot(kind="bar", ax=ax9, color=[GRAY, BLUE, ACCENT], edgecolor=DARK, width=0.6)
    ax9.set_title("Hari Berpermintaan Tinggi Didominasi oleh Cuaca Cerah", pad=12)
    ax9.set_xlabel("Kondisi Cuaca")
    ax9.set_ylabel("Jumlah Hari")
    ax9.set_xticklabels(ax9.get_xticklabels(), rotation=0)
    ax9.legend(title="Kategori Permintaan", frameon=True)
    ax9.set_ylim(0, ct_demand.values.max() * 1.25)
    plt.tight_layout()
    fig9.text(0.5, -0.06, "Sumber: Capital Bikeshare (2011–2012) · day.csv", ha="center", fontsize=8, color="#7F8C8D")
    st.pyplot(fig9)
    plt.close(fig9)

st.markdown(
    "> **Kesimpulan Tambahan:** Pengguna rata-rata paling antusias menyewa sepeda pas suhunya lagi **Hangat (20–30°C)**. "
    "Jam-jam pulang kerja **(Sore, 15–19)** juga konsisten jadi waktu yang paling padat. "
    "Selain itu, hari-hari dengan pesanan kategori 'Tinggi' itu hampir semuanya terjadi saat cuaca lagi cerah; kalau sudah hujan atau salju ringan, nyaris mustahil bisa menembus target pesanan tinggi."
)

st.divider()
st.caption(
    "**Sumber Data:** Capital Bikeshare System Data (2011–2012) · "
    "UCI Machine Learning Repository · Dicoding Belajar Analisis Data dengan Python"
)