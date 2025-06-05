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
    file_path = os.path.abspath("dataset.csv")
    try:
        df = pd.read_csv("dataset.csv")
        return df
    except FileNotFoundError:
        st.error(f"File dataset.csv tidak ditemukan di {file_path}!")
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
    st.title("📝 Input Data Kandidat")
    st.subheader("📥 Input Data Calon Baru")

    with st.form("input_form_kandidat"): # Beri nama form yang unik
        nama = st.text_input("Nama Calon")
        st.markdown("---")
        
        all_input_values = {} # Dictionary untuk menyimpan semua nilai input

        # IST Section (10 fields + IQ = 10 fields)
        st.markdown("### 🧠 IST (Intelligence Structure Test)")
        ist_fields = [col for col in CSV_COLUMNS if col in ["SE", "WA", "AN", "GE", "ME", "RA", "ZR", "FA", "WU", "IQ"]]
        cols_ist = st.columns(5)
        for i, field in enumerate(ist_fields):
            with cols_ist[i % 5]:
                all_input_values[field] = st.number_input(f"{field}", value=0, min_value=0, max_value=150, key=f"input_ist_{field}") # IQ bisa > 100
        st.markdown("---")
        
        # PAPI Kostick Section (20 fields)
        st.markdown("### 📊 PAPI Kostick")
        papi_fields = [col for col in CSV_COLUMNS if col.startswith("P_")]
        # Layout PAPI: 5 fields per row
        num_papi_cols_ui = 5
        for i in range(0, len(papi_fields), num_papi_cols_ui):
            cols_papi = st.columns(num_papi_cols_ui)
            for j, field in enumerate(papi_fields[i : i + num_papi_cols_ui]):
                with cols_papi[j]:
                    all_input_values[field] = st.number_input(f"{field}", value=0, min_value=0, max_value=9, key=f"input_papi_{field}")
        st.markdown("---")
        
        # MBTI Section (8 fields)
        st.markdown("### 🎭 MBTI")
        mbti_fields = [col for col in CSV_COLUMNS if col.startswith("M_")]
        cols_mbti = st.columns(4)
        for i, field in enumerate(mbti_fields):
            with cols_mbti[i % 4]:
                all_input_values[field] = st.number_input(f"{field}", value=0, min_value=0, max_value=100, key=f"input_mbti_{field}")
        st.markdown("---")
        
        # Kraepelin Section (5 fields)
        st.markdown("### ⏱️ Kraepelin")
        kraep_fields = [col for col in CSV_COLUMNS if col.startswith("K_")]
        cols_kraep = st.columns(len(kraep_fields) if len(kraep_fields) > 0 else 1)
        for i, field in enumerate(kraep_fields):
            with cols_kraep[i % len(kraep_fields) if len(kraep_fields) > 0 else 0]:
                 all_input_values[field] = st.number_input(f"{field}", value=0, min_value=0, max_value=100, key=f"input_kraep_{field}") # Sesuaikan max_value jika perlu
        st.markdown("---")
        
        # DISC Section (4 fields)
        st.markdown("### 🎯 DISC")
        disc_fields = [col for col in CSV_COLUMNS if col.startswith("D_")]
        cols_disc = st.columns(len(disc_fields) if len(disc_fields) > 0 else 1)
        for i, field in enumerate(disc_fields):
            with cols_disc[i % len(disc_fields) if len(disc_fields) > 0 else 0]:
                all_input_values[field] = st.number_input(f"{field}", value=0, min_value=0, max_value=9, key=f"input_disc_{field}")

        submitted_kandidat = st.form_submit_button("➕ Tambahkan ke Data Kandidat")

        if submitted_kandidat:
                if not nama:
                    st.error("Nama Calon tidak boleh kosong.")
                else:
                    # Siapkan data untuk baris baru sesuai urutan CSV_COLUMNS
                    new_row_data = [nama] # NAMA adalah kolom pertama
                    for col_name in CSV_COLUMNS[1:]: # Mulai dari kolom kedua setelah NAMA
                        new_row_data.append(all_input_values.get(col_name, np.nan))

                    new_row_df = pd.DataFrame([new_row_data], columns=CSV_COLUMNS)
                    
                    try:
                        file_exists = os.path.exists("Dataset.csv")
                        is_empty = False
                        if file_exists:
                            try:
                                df_check = pd.read_csv("Dataset.csv")
                                if df_check.empty:
                                    is_empty = True
                            except pd.errors.EmptyDataError:
                                is_empty = True
                        
                        write_header = not file_exists or is_empty
                        new_row_df.to_csv("Dataset.csv", mode='a', header=write_header, index=False)
                        st.session_state.candidate_success_message = f"Data untuk {nama} berhasil ditambahkan ke Dataset.csv!"
                        
                        # Hanya jalankan ini jika penyimpanan berhasil
                        if hasattr(load_data, 'clear'): 
                            load_data.clear() 
                        st.rerun()  # Rerun setelah sukses dan clear cache
                    except Exception as e:
                        st.error(f"Gagal menyimpan data ke CSV: {e}")
        
# ---------- JOB POSITIONS PAGE ---------- #
elif st.session_state.page == "Job Positions":
    # Kita meneruskan JOB_POSITIONS_CSV_PATH
    job_positions_page.render_page(JOB_POSITIONS_CSV_PATH)