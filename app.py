# app.py

import streamlit as st
import pandas as pd
import numpy as np
import os

# Import fungsi render dari modul views
# Pastikan nama file di folder 'views' sesuai:
# views/home_page.py
# views/input_data_page.py
# views/job_positions_page.py
from views import home_page, input_data_page, job_positions_page

# ---------- Konfigurasi Halaman ---------- #
st.set_page_config(page_title="Seleksi Karyawan", layout="wide")

# ---------- Definisi Kolom Global ---------- #
# Kolom untuk dataset.csv (Kandidat)
CSV_COLUMNS_KANDIDAT = [
    "NAMA", "SE", "WA", "AN", "GE", "ME", "RA", "ZR", "FA", "WU", "IQ",
    "P_C", "P_F", "P_W", "P_N", "P_G", "P_A", "P_P", "P_I", "P_V", "P_S",
    "P_X", "P_E", "P_K", "P_L", "P_T", "P_B", "P_O", "P_R", "P_D", "P_Z",
    "M_E", "M_I", "M_S", "M_N", "M_T", "M_F", "M_J", "M_P",
    "K_C", "K_T", "K_A1", "K_A2", "K_H",
    "D_D", "D_I", "D_S", "D_C"
]

# Kolom untuk job_positions.csv (sudah 10 kolom)
EXPECTED_JOB_COLUMNS = [
    'Job Position', 'PAPI context', 'M', 'B', 'T', 'I_M',
    'D', 'I_D', 'S', 'C'
]
JOB_POSITIONS_CSV_PATH = "job_positions.csv"

# ---------- Load Dataset Kandidat (dataset.csv) ---------- #
@st.cache_data
def load_data_kandidat(): # Mengganti nama fungsi agar lebih spesifik
    file_path = "dataset.csv" # Path relatif biasanya cukup
    try:
        df = pd.read_csv(file_path)
        # Pastikan semua kolom yang diharapkan ada, tambahkan jika tidak ada
        for col in CSV_COLUMNS_KANDIDAT:
            if col not in df.columns:
                df[col] = np.nan # atau nilai default lainnya
        return df[CSV_COLUMNS_KANDIDAT] # Pastikan urutan kolom
    except FileNotFoundError:
        st.error(f"File {file_path} tidak ditemukan!")
        return pd.DataFrame(columns=CSV_COLUMNS_KANDIDAT)
    except pd.errors.EmptyDataError:
        st.warning(f"File {file_path} kosong. Menginisialisasi DataFrame kosong.")
        return pd.DataFrame(columns=CSV_COLUMNS_KANDIDAT)
    except Exception as e:
        st.error(f"Error saat memuat {file_path}: {e}")
        return pd.DataFrame(columns=CSV_COLUMNS_KANDIDAT)

# ---------- Load/Initialize Job Positions (job_positions.csv) ---------- #
@st.cache_data
def get_default_job_positions_data():
    data = {
        'Job Position': ['Pre-Sales', 'IT Developer', 'Sales Manager', 'Admin', 'Marketing'],
        'PAPI context': ['O', 'R', 'B', 'D', 'Z'],
        'M': ['E', 'I', 'E', 'I', 'E'],
        'B': ['N', 'N', 'S', 'S', 'N'],
        'T': ['T', 'T', 'F', 'T', 'F'],
        'I_M': ['J', 'P', 'J', 'J', 'P'],
        'D': [0.3, 0.1, 0.2, 0.4, 0.25],
        'I_D': [0.4, 0.2, 0.3, 0.1, 0.25],
        'S': [0.2, 0.2, 0.3, 0.3, 0.25],
        'C': [0.1, 0.5, 0.2, 0.2, 0.25]
    }
    default_df = pd.DataFrame(data)
    for col in EXPECTED_JOB_COLUMNS:
        if col not in default_df.columns:
            if col in ['D', 'I_D', 'S', 'C']:
                default_df[col] = np.nan
            else:
                default_df[col] = None
    return default_df[EXPECTED_JOB_COLUMNS]

def load_or_initialize_job_positions():
    try:
        df = pd.read_csv(JOB_POSITIONS_CSV_PATH)
        if not all(col in df.columns for col in EXPECTED_JOB_COLUMNS) or len(df.columns) != len(EXPECTED_JOB_COLUMNS):
            st.warning(f"Struktur kolom di {JOB_POSITIONS_CSV_PATH} tidak sesuai. Menginisialisasi ulang dengan default.")
            raise FileNotFoundError # Anggap file tidak valid, paksa buat ulang
        if df.empty:
            st.info(f"{JOB_POSITIONS_CSV_PATH} kosong. Menggunakan data default dan menyimpannya.")
            default_df = get_default_job_positions_data()
            default_df.to_csv(JOB_POSITIONS_CSV_PATH, index=False)
            return default_df.copy()
        return df.copy()
    except (FileNotFoundError, pd.errors.EmptyDataError):
        st.info(f"{JOB_POSITIONS_CSV_PATH} tidak ditemukan atau kosong/rusak. Membuat file dengan data default.")
        default_df = get_default_job_positions_data()
        default_df.to_csv(JOB_POSITIONS_CSV_PATH, index=False)
        return default_df.copy()
    except Exception as e:
        st.error(f"Error saat memuat {JOB_POSITIONS_CSV_PATH}: {e}. Menginisialisasi ulang dengan default.")
        default_df = get_default_job_positions_data()
        default_df.to_csv(JOB_POSITIONS_CSV_PATH, index=False)
        return default_df.copy()

# ---------- Inisialisasi Session State & Data ---------- #
if 'job_positions_df' not in st.session_state:
    st.session_state.job_positions_df = load_or_initialize_job_positions()

data_kandidat = load_data_kandidat() # Load data kandidat

if 'page' not in st.session_state:
    st.session_state.page = "Home"

# ---------- Navbar Navigation (INI BAGIAN YANG PENTING!)---------- #
st.markdown("---") # Garis pemisah sebelum navigasi
nav_cols = st.columns([1, 1, 1, 5]) # Sesuaikan rasio jika perlu
with nav_cols[0]:
    if st.button("🏠 Home", use_container_width=True, key="nav_home"):
        st.session_state.page = "Home"
with nav_cols[1]:
    if st.button("📝 Candidate Data", use_container_width=True, key="nav_input_data"): # Ubah nama tombol agar lebih jelas
        st.session_state.page = "Input Data"
with nav_cols[2]:
    if st.button("💼 Job Positions", use_container_width=True, key="nav_job_positions"): # Ubah nama tombol
        st.session_state.page = "Job Positions"
st.markdown("---") # Garis pemisah setelah navigasi

# ---------- Page Rendering Logic ---------- #
if st.session_state.page == "Home":
    home_page.render_page(data_kandidat, st.session_state.job_positions_df)
elif st.session_state.page == "Input Data":
    # Panggil fungsi render dari input_data_page.py
    # Pastikan input_data_page.render_page() didefinisikan dengan benar
    # dan menerima argumen yang sesuai.
    # Misal: input_data_page.render_page(CSV_COLUMNS_KANDIDAT, load_data_kandidat)
    # Untuk sekarang, kita tampilkan placeholder jika belum ada:
    if hasattr(input_data_page, 'render_page'):
         input_data_page.render_page(CSV_COLUMNS_KANDIDAT, load_data_kandidat) # Sesuaikan argumen jika perlu
    else:
         st.error("views/input_data_page.py belum memiliki fungsi render_page atau belum diimport dengan benar.")
elif st.session_state.page == "Job Positions":
    # job_positions_page.render_page HARUS diperbarui untuk menangani 10 kolom
    # dan CSV path yang benar
    if hasattr(job_positions_page, 'render_page'):
        job_positions_page.render_page(JOB_POSITIONS_CSV_PATH) # , EXPECTED_JOB_COLUMNS) # Anda mungkin perlu passing EXPECTED_JOB_COLUMNS jika dibutuhkan oleh page
    else:
        st.error("views/job_positions_page.py belum memiliki fungsi render_page atau belum diimport dengan benar.")
else:
    st.session_state.page = "Home" # Default jika ada state aneh
    home_page.render_page(data_kandidat, st.session_state.job_positions_df) # Tampilkan home