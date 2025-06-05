import streamlit as st
import pandas as pd
import numpy as np
import os

# Import fungsi render dari modul views
from views import home_page, input_data_page, job_positions_page

# ---------- Konfigurasi Halaman ---------- #
st.set_page_config(page_title="Seleksi Karyawan", layout="wide")

CSV_COLUMNS = [
    "NAMA", "SE", "WA", "AN", "GE", "ME", "RA", "ZR", "FA", "WU", "IQ",
    "P_C", "P_F", "P_W", "P_N", "P_G", "P_A", "P_P", "P_I", "P_V", "P_S",
    "P_X", "P_E", "P_K", "P_L", "P_T", "P_B", "P_O", "P_R", "P_D", "P_Z",
    "M_E", "M_I", "M_S", "M_N", "M_T", "M_F", "M_J", "M_P",
    "K_C", "K_T", "K_A1", "K_A2", "K_H",
    "D_D", "D_I", "D_S", "D_C"
]

# ---------- Load Dataset Kandidat ---------- #
@st.cache_data
def load_data():
    file_path = "Dataset.csv" # Path relatif sudah cukup jika di direktori yang sama
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        st.error(f"File {file_path} tidak ditemukan!")
        return pd.DataFrame(columns=CSV_COLUMNS)
    except pd.errors.EmptyDataError:
        st.warning(f"File {file_path} kosong. Menginisialisasi DataFrame kosong.")
        return pd.DataFrame(columns=CSV_COLUMNS)

data_kandidat = load_data()


# load Dataset Job_Position
@st.cache_data
def get_default_job_positions_data():
    data = {
        'Job Position': ['Pre-Sales', 'IT Developer', 'Sales Manager', 'Admin', 'Marketing'],
        'MBTI Preferences': ['ENTJ, ENFJ', 'INTJ, INTP', 'ESFJ, ENFJ', 'ISFJ, ISTJ', 'ENFP, ESFP'],
        'PAPI Kostick Preferences': ['Leadership, Assertive', 'Analytical, Detail', 'Social, Persuasive', 'Organized, Stable', 'Creative, Flexible']
    }
    return pd.DataFrame(data)

JOB_POSITIONS_CSV_PATH = "job_positions.csv"

def load_or_initialize_job_positions():
    try:
        df = pd.read_csv(JOB_POSITIONS_CSV_PATH)
        if df.empty:
            st.info(f"{JOB_POSITIONS_CSV_PATH} kosong. Menggunakan data default dan menyimpannya.")
            default_df = get_default_job_positions_data()
            default_df.to_csv(JOB_POSITIONS_CSV_PATH, index=False)
            return default_df
        return df
    except FileNotFoundError:
        st.info(f"{JOB_POSITIONS_CSV_PATH} tidak ditemukan. Membuat file dengan data default.")
        default_df = get_default_job_positions_data()
        default_df.to_csv(JOB_POSITIONS_CSV_PATH, index=False)
        return default_df
    except pd.errors.EmptyDataError: # Menangani jika CSV ada tapi kosong
        st.info(f"{JOB_POSITIONS_CSV_PATH} ada tapi kosong. Menggunakan data default dan menyimpannya.")
        default_df = get_default_job_positions_data()
        default_df.to_csv(JOB_POSITIONS_CSV_PATH, index=False)
        return default_df


if 'job_positions_df' not in st.session_state:
    st.session_state.job_positions_df = load_or_initialize_job_positions()


# ---------- Navbar Navigation ---------- #
# Pastikan navigasi selalu ditampilkan
nav_cols = st.columns([2, 2, 2, 4]) # Memberi nama berbeda dari kolom di page lain
with nav_cols[0]:
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = "Home"
with nav_cols[1]:
    if st.button("📝 Input Data", use_container_width=True):
        st.session_state.page = "Input Data"
with nav_cols[2]:
    if st.button("💼 Job Positions", use_container_width=True):
        st.session_state.page = "Job Positions"

# Initialize session state for page
if 'page' not in st.session_state:
    st.session_state.page = "Home"


# ---------- Page Rendering Logic ---------- #
if st.session_state.page == "Home":
    home_page.render_page(data_kandidat, st.session_state.job_positions_df)
elif st.session_state.page == "Input Data":
    # Kita meneruskan CSV_COLUMNS dan fungsi load_data agar page input bisa clear cache
    input_data_page.render_page(CSV_COLUMNS, load_data)
elif st.session_state.page == "Job Positions":
    # Kita meneruskan JOB_POSITIONS_CSV_PATH
    job_positions_page.render_page(JOB_POSITIONS_CSV_PATH)