import streamlit as st
import pandas as pd
import numpy as np

# Impor fungsi tunggal dari modul display yang baru kita buat
from utils.display import manage_display

# ---------- Konfigurasi Halaman ---------- #
st.set_page_config(page_title="Seleksi Karyawan", layout="wide")

# ---------- Definisi Kolom Global ---------- #
CSV_COLUMNS_KANDIDAT = [
    "NAMA", "SE", "WA", "AN", "GE", "ME", "RA", "ZR", "FA", "WU", "IQ",
    "P_C", "P_F", "P_W", "P_N", "P_G", "P_A", "P_P", "P_I", "P_V", "P_S",
    "P_X", "P_E", "P_K", "P_L", "P_T", "P_B", "P_O", "P_R", "P_D", "P_Z",
    "M_E", "M_I", "M_S", "M_N", "M_T", "M_F", "M_J", "M_P",
    "K_C", "K_T", "K_A1", "K_A2", "K_H",
    "D_D", "D_I", "D_S", "D_C"
]

EXPECTED_JOB_COLUMNS = [
    'Job Position', 'PAPI context', 'M', 'B', 'T', 'I_M',
    'D', 'I_D', 'S', 'C'
]
JOB_POSITIONS_CSV_PATH = "job_positions.csv"

# ---------- Fungsi-Fungsi Load Data (Logika Bisnis) ---------- #
@st.cache_data
def load_data_kandidat():
    file_path = "dataset.csv"
    try:
        df = pd.read_csv(file_path)
        for col in CSV_COLUMNS_KANDIDAT:
            if col not in df.columns:
                df[col] = np.nan
        return df[CSV_COLUMNS_KANDIDAT]
    except FileNotFoundError:
        st.error(f"File {file_path} tidak ditemukan!")
        return pd.DataFrame(columns=CSV_COLUMNS_KANDIDAT)
    except Exception as e:
        st.error(f"Error saat memuat {file_path}: {e}")
        return pd.DataFrame(columns=CSV_COLUMNS_KANDIDAT)

@st.cache_data
def get_default_job_positions_data():
    data = {
        'Job Position': ['Pre-Sales', 'IT Developer', 'Sales Manager', 'Admin', 'Marketing'],
        'PAPI context': ['O', 'R', 'B', 'D', 'Z'], 'M': ['E', 'I', 'E', 'I', 'E'],
        'B': ['N', 'N', 'S', 'S', 'N'], 'T': ['T', 'T', 'F', 'T', 'F'],
        'I_M': ['J', 'P', 'J', 'J', 'P'], 'D': [0.3, 0.1, 0.2, 0.4, 0.25],
        'I_D': [0.4, 0.2, 0.3, 0.1, 0.25], 'S': [0.2, 0.2, 0.3, 0.3, 0.25],
        'C': [0.1, 0.5, 0.2, 0.2, 0.25]
    }
    return pd.DataFrame(data, columns=EXPECTED_JOB_COLUMNS)

def load_or_initialize_job_positions():
    try:
        df = pd.read_csv(JOB_POSITIONS_CSV_PATH)
        if df.empty or not all(col in df.columns for col in EXPECTED_JOB_COLUMNS):
            raise FileNotFoundError # Paksa buat ulang jika kosong atau kolom salah
        return df.copy()
    except (FileNotFoundError, pd.errors.EmptyDataError):
        st.info(f"{JOB_POSITIONS_CSV_PATH} tidak ditemukan/rusak. Membuat file dengan data default.")
        default_df = get_default_job_positions_data()
        default_df.to_csv(JOB_POSITIONS_CSV_PATH, index=False)
        return default_df.copy()

# ---------- "Main" Program Logic ---------- #
def main():
    # 1. Siapkan semua data yang dibutuhkan
    data_kandidat = load_data_kandidat()
    if 'job_positions_df' not in st.session_state:
        st.session_state.job_positions_df = load_or_initialize_job_positions()
    
    # 2. Serahkan semua urusan tampilan ke modul display
    manage_display(
        data_kandidat=data_kandidat,
        job_positions_df=st.session_state.job_positions_df,
        csv_columns_kandidat=CSV_COLUMNS_KANDIDAT,
        load_data_kandidat_func=load_data_kandidat,
        job_positions_csv_path=JOB_POSITIONS_CSV_PATH
    )

if __name__ == "__main__":
    main()