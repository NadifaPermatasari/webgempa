import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
import os

# Konfigurasi halaman
st.set_page_config(page_title="GempaLog.ID", layout="wide")
st.title("🌐 GempaLog.ID")
st.subheader("Sistem Bantuan Logistik Bencana Gempa")

# Path penyimpanan data bantuan
DATA_PATH = "data/bantuan.csv"
os.makedirs("data", exist_ok=True)
if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=["Nama", "Jenis Bantuan", "Jumlah", "Lokasi", "Waktu"]).to_csv(DATA_PATH, index=False)

# Fungsi ambil data gempa terkini
def ambil_data_gempa_terkini():
    url = "https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.json"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()["Infogempa"]["gempa"]
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()

# Fungsi ambil data gempa dirasakan
def ambil_data_gempa_dirasakan():
    url = "https://data.bmkg.go.id/DataMKG/TEWS/gempadirasakan.json"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()["Infogempa"]["gempa"]
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()

# Sidebar menu
menu = st.sidebar.radio("📌 Navigasi", ["🌍 Info Gempa", "📝 Formulir Bantuan", "📊 Data Bantuan"])

# Halaman 1: Info Gempa
if menu == "🌍 Info Gempa":
    st.header("📡 Informasi Gempa Real-time dari BMKG")
    st.image("assets/gempa.jpg", use_container_width=True, caption="Data Gempa Real-time dari BMKG")
    tab1, tab2 = st.tabs(["📄 Gempa Terkini", "🌐 Gempa Dirasakan (Dengan Peta)"])

    # Tab Gempa Terkini
    with tab1:
        df_terkini = ambil_data_gempa_terkini()
        if not df_terkini.empty:
            st.dataframe(df_terkini[["Tanggal", "Jam", "Wilayah", "Magnitude", "Kedalaman", "Potensi"]].head(10), use_container_width=True)
        else:
            st.warning("Gagal mengambil data gempa terkini.")

    # Tab Gempa Dirasakan
    with tab2:
        df_dirasakan = ambil_data_gempa_dirasakan()
        if not df_dirasakan.empty:
            df_map = df_dirasakan.copy()

            # Konversi koordinat
            df_map["latitude"] = df_map["Lintang"].str.replace("LS", "").str.replace("LU", "").astype(float)
            df_map["longitude"] = df_map["Bujur"].str.replace("BT", "").astype(float) * -1

            st.map(df_map[["latitude", "longitude"]], zoom=4)

            # Tampilkan tabel jika kolom tersedia
            kolom_tampilkan = ["Tanggal", "Jam", "Wilayah", "Magnitude", "Kedalaman", "Dirasakan"]
            kolom_ada = [k for k in kolom_tampilkan if k in df_map.columns]

            if kolom_ada:
                st.dataframe(df_map[kolom_ada], use_container_width=True)
            else:
                st.info("Data gempa tidak memuat kolom yang dapat ditampilkan.")
        else:
            st.warning("Gagal mengambil data gempa dirasakan.")

# Halaman 2: Formulir Bantuan
elif menu == "📝 Formulir Bantuan":
    st.header("📦 Formulir Pengiriman Bantuan")
    st.image("assets/bantuan.jpg", use_container_width=True, caption="Bantu saudara kita yang terdampak gempa")
    with st.form("form_bantuan"):
        nama = st.text_input("👤 Nama Pengirim")
        jenis = st.selectbox("📦 Jenis Bantuan", ["Makanan", "Obat-obatan", "Pakaian", "Tenda", "Lainnya"])
        jumlah = st.number_input("🔢 Jumlah", min_value=1)
        lokasi = st.text_input("📍 Lokasi Tujuan")
        submit = st.form_submit_button("📤 Kirim")

        if submit:
            zona_wib = pytz.timezone("Asia/Jakarta")
            waktu = datetime.now(zona_wib).strftime("%Y-%m-%d %H:%M:%S WIB")
            new_entry = pd.DataFrame([[nama, jenis, jumlah, lokasi, waktu]],
                                     columns=["Nama", "Jenis Bantuan", "Jumlah", "Lokasi", "Waktu"])
            new_entry.to_csv(DATA_PATH, mode="a", header=False, index=False)
            st.success("✅ Data bantuan berhasil disimpan.")

# Halaman 3: Data Bantuan Masuk
elif menu == "📊 Data Bantuan":
    st.header("📊 Rekap Data Bantuan Masuk")
    st.image("assets/statistik.jpg", use_container_width=True, caption="Distribusi Bantuan Logistik")
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        st.dataframe(df, use_container_width=True)

        st.markdown("### 📈 Statistik Bantuan per Jenis")
        st.bar_chart(df["Jenis Bantuan"].value_counts())
    else:
        st.info("Belum ada data bantuan.")
