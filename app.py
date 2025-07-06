import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
import os
import base64

# Konfigurasi halaman
st.set_page_config(page_title="GempaLog.ID", layout="wide")

# Fungsi untuk set background image sesuai halaman
def set_background(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
    """, unsafe_allow_html=True)

# CSS transparan elegan
def add_transparent_css():
    st.markdown("""
        <style>
        .transparent-box {
            background-color: rgba(255, 255, 255, 0.85);
            padding: 2.5rem;
            border-radius: 20px;
            max-width: 1000px;
            margin: 2rem auto;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.25);
        }
        .transparent-box h2, .transparent-box h3 {
            text-align: center;
            color: #1f2937;
        }
        </style>
    """, unsafe_allow_html=True)

# Inisialisasi data jika belum ada
DATA_PATH = "data/bantuan.csv"
os.makedirs("data", exist_ok=True)
if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=["Nama", "Jenis Bantuan", "Jumlah", "Lokasi", "Waktu"]).to_csv(DATA_PATH, index=False)

# Fungsi ambil data gempa BMKG
def ambil_data_gempa_terkini():
    try:
        r = requests.get("https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.json", timeout=5)
        return pd.DataFrame(r.json()["Infogempa"]["gempa"])
    except:
        return pd.DataFrame()

def ambil_data_gempa_dirasakan():
    try:
        r = requests.get("https://data.bmkg.go.id/DataMKG/TEWS/gempadirasakan.json", timeout=5)
        return pd.DataFrame(r.json()["Infogempa"]["gempa"])
    except:
        return pd.DataFrame()

# Sidebar menu
menu = st.sidebar.radio("📌 Navigasi", ["🌍 Info Gempa", "📝 Formulir Bantuan", "📊 Data Bantuan"])

# Background sesuai halaman
if menu == "🌍 Info Gempa":
    set_background("assets/gempa.jpg")
elif menu == "📝 Formulir Bantuan":
    set_background("assets/bantuan.jpg")
elif menu == "📊 Data Bantuan":
    set_background("assets/statistik.jpg")

# Tambahkan CSS transparan
add_transparent_css()

# Header Umum
with st.container():
    st.markdown('<div class="transparent-box">', unsafe_allow_html=True)
    st.title("🌐 GempaLog.ID")
    st.subheader("Sistem Bantuan Logistik Bencana Gempa")
    st.markdown('</div>', unsafe_allow_html=True)

# ====================== 🌍 Info Gempa ======================
if menu == "🌍 Info Gempa":
    with st.container():
        st.markdown('<div class="transparent-box">', unsafe_allow_html=True)

        st.header("📡 Informasi Gempa Real-time dari BMKG")

        df_terkini = ambil_data_gempa_terkini()
        if not df_terkini.empty:
            st.subheader("📄 Gempa Terkini")
            st.dataframe(df_terkini[["Tanggal", "Jam", "Wilayah", "Magnitude", "Kedalaman", "Potensi"]].head(10), use_container_width=True)
        else:
            st.warning("Gagal mengambil data gempa terkini.")

        df_dirasakan = ambil_data_gempa_dirasakan()
        if not df_dirasakan.empty:
            st.subheader("🌐 Gempa Dirasakan (Dengan Peta)")
            df_map = df_dirasakan.copy()
            df_map["latitude"] = df_map["Lintang"].str.replace("LS", "").str.replace("LU", "").astype(float)
            df_map["longitude"] = df_map["Bujur"].str.replace("BT", "").astype(float) * -1
            st.map(df_map[["latitude", "longitude"]], zoom=4)

            kolom = ["Tanggal", "Jam", "Wilayah", "Magnitude", "Kedalaman", "Dirasakan"]
            st.dataframe(df_map[kolom], use_container_width=True)
        else:
            st.warning("Gagal mengambil data gempa dirasakan.")

        st.markdown('</div>', unsafe_allow_html=True)

# ====================== 📝 Formulir Bantuan ======================
elif menu == "📝 Formulir Bantuan":
    with st.container():
        st.markdown('<div class="transparent-box">', unsafe_allow_html=True)

        st.header("📦 Formulir Pengiriman Bantuan")
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

        st.markdown('</div>', unsafe_allow_html=True)

# ====================== 📊 Data Bantuan ======================
elif menu == "📊 Data Bantuan":
    with st.container():
        st.markdown('<div class="transparent-box">', unsafe_allow_html=True)

        st.header("📊 Rekap Data Bantuan Masuk")
        if os.path.exists(DATA_PATH):
            df = pd.read_csv(DATA_PATH)
            st.dataframe(df, use_container_width=True)
            st.markdown("### 📈 Statistik Bantuan per Jenis")
            st.bar_chart(df["Jenis Bantuan"].value_counts())
        else:
            st.info("Belum ada data bantuan.")

        st.markdown('</div>', unsafe_allow_html=True)
