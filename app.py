
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import os

# Path untuk menyimpan data bantuan
DATA_PATH = "data/bantuan.csv"
os.makedirs("data", exist_ok=True)
if not os.path.exists(DATA_PATH):
    df_init = pd.DataFrame(columns=["Nama", "Jenis Bantuan", "Jumlah", "Lokasi", "Waktu"])
    df_init.to_csv(DATA_PATH, index=False)

# Fungsi ambil data gempa dari BMKG
def ambil_data_gempa_terkini():
    try:
        url = "https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.json"
        response = requests.get(url)
        data = response.json()
        return pd.DataFrame(data["Infogempa"]["gempa"])
    except Exception as e:
        st.error("Gagal mengambil data gempa dari BMKG.")
        return pd.DataFrame()

# Konfigurasi Streamlit
st.set_page_config(page_title="GempaLog.ID", layout="wide")
st.title("🌐 GempaLog.ID - Sistem Bantuan Logistik Bencana Gempa")

# Sidebar navigasi
menu = st.sidebar.radio("Navigasi", ["🌍 Info Gempa Real-time", "📝 Formulir Bantuan", "📊 Data Bantuan Masuk"])

# Halaman 1: Info Gempa Real-time
if menu == "🌍 Info Gempa Real-time":
    st.header("🌍 Daftar 5 Gempa Terbaru - Real-time dari BMKG")
    df_gempa = ambil_data_gempa_terkini()

    if not df_gempa.empty:
        df_display = df_gempa[["Tanggal", "Jam", "Wilayah", "Magnitude", "Kedalaman", "Potensi"]].head(5)
        st.dataframe(df_display, use_container_width=True)
    else:
        st.warning("Belum ada data gempa tersedia saat ini.")

# Halaman 2: Formulir Bantuan
elif menu == "📝 Formulir Bantuan":
    st.header("📝 Formulir Pengisian Bantuan Logistik")
    with st.form("form_bantuan"):
        nama = st.text_input("Nama Pengirim")
        jenis = st.selectbox("Jenis Bantuan", ["Makanan", "Obat-obatan", "Pakaian", "Tenda", "Lainnya"])
        jumlah = st.number_input("Jumlah", min_value=1)
        lokasi = st.text_input("Lokasi Tujuan")
        submit = st.form_submit_button("Kirim Bantuan")

        if submit:
            waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = pd.DataFrame([[nama, jenis, jumlah, lokasi, waktu]],
                                   columns=["Nama", "Jenis Bantuan", "Jumlah", "Lokasi", "Waktu"])
            new_row.to_csv(DATA_PATH, mode='a', header=False, index=False)
            st.success("✅ Data bantuan berhasil dikirim.")

# Halaman 3: Data Bantuan Masuk
elif menu == "📊 Data Bantuan Masuk":
    st.header("📊 Data Bantuan yang Telah Masuk")
    if os.path.exists(DATA_PATH):
        df_bantuan = pd.read_csv(DATA_PATH)
        st.dataframe(df_bantuan, use_container_width=True)
    else:
        st.info("Belum ada data bantuan masuk.")
