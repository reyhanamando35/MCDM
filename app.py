import streamlit as st
import pandas as pd
import numpy as np
import os 

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
# @st.cache_data
def load_data():
    file_path = os.path.abspath("dataset.csv")
    try:
        df = pd.read_csv("dataset.csv")
        return df
    except FileNotFoundError:
        st.error(f"File dataset.csv tidak ditemukan di {file_path}!")
        return pd.DataFrame(columns=CSV_COLUMNS)
data_kandidat = load_data()


# load Dataset Job_Position
@st.cache_data
def get_default_job_positions_data(): # Ini benar, untuk menyediakan data default
    data = {
        'Job Position': ['Pre-Sales', 'IT Developer', 'Sales Manager', 'Admin', 'Marketing'],
        'MBTI Preferences': ['ENTJ, ENFJ', 'INTJ, INTP', 'ESFJ, ENFJ', 'ISFJ, ISTJ', 'ENFP, ESFP'],
        'PAPI Kostick Preferences': ['Leadership, Assertive', 'Analytical, Detail', 'Social, Persuasive', 'Organized, Stable', 'Creative, Flexible']
    }
    return pd.DataFrame(data)
data= load_data()

JOB_POSITIONS_CSV_PATH = "job_positions.csv"
# Fungsi baru untuk memuat data posisi pekerjaan dari CSV atau menginisialisasi jika tidak ada
def load_or_initialize_job_positions():
    try:
        df = pd.read_csv(JOB_POSITIONS_CSV_PATH)
        # Jika file CSV ada tapi kosong
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
# ... (load_data() untuk data kandidat tetap sama) ...

# Inisialisasi atau muat data posisi pekerjaan dari session_state (dan CSV)
if 'job_positions_df' not in st.session_state:
    st.session_state.job_positions_df = load_or_initialize_job_positions()


# ---------- Navbar Navigation ---------- #
col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 4])
with col1:
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = "Home"
with col2:
    if st.button("📝 Input Data", use_container_width=True):
        st.session_state.page = "Input Data"
with col3:
    if st.button("💼 Job Positions", use_container_width=True):
        st.session_state.page = "Job Positions"

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "Home"


# ---------- HOME PAGE ---------- #
if st.session_state.page == "Home":
    st.title("📋 Dashboard Seleksi Karyawan Berbasis MCDM")
    
    # Original candidate data
    st.subheader("📋 Data Kandidat Lengkap")
    st.dataframe(data, use_container_width=True)

    # Job Positions Table
     # Job Positions Table - sekarang mengambil dari session_state
    st.subheader("📋 Daftar Posisi Pekerjaan")
    st.dataframe(st.session_state.job_positions_df, use_container_width=True) # Menggunakan session_state

    st.markdown("---")

    # Candidate Selection Section
    st.subheader("🔍 Seleksi Kandidat")
    
    col_home_1, col_home_2, col_home_3 = st.columns([2, 2, 2]) # Ganti nama var agar tidak konflik
    with col_home_1:
        # Opsi diambil dari session_state
        job_options_list = st.session_state.job_positions_df['Job Position'].tolist()
        selected_job_index = 0 if job_options_list else None # Handle jika daftar kosong

        selected_job = st.selectbox(
            "Pilih Posisi Pekerjaan:",
            options=job_options_list,
            index=selected_job_index, # Menggunakan selected_job_index
            key="home_selectbox_job" # Tambahkan key unik
        )

    generate_final = st.button("🚀 Generate Final Data", use_container_width=True)
    if generate_final:
        st.success(f"Menganalisis kandidat untuk posisi: {selected_job}")
        
        # Generate 5 kriteria umum dari 47 kolom
        st.subheader("📊 Data Hasil Agregasi (5 Kriteria)")
        
        # Dummy aggregation - nanti bisa diganti dengan logic sebenarnya
        np.random.seed(42)
        aggregated_data = pd.DataFrame({
            'Nama': data['NAMA'],
            'IST_Score': np.random.randint(60, 100, len(data)),
            'MBTI_Score': np.random.randint(60, 100, len(data)),
            'PAPI_Score': np.random.randint(60, 100, len(data)),
            'DISC_Score': np.random.randint(60, 100, len(data)),
            'Kraepelin_Score': np.random.randint(60, 100, len(data))
        })
        
        st.dataframe(aggregated_data, use_container_width=True)

    st.markdown("---")
   


    # MCDM Analysis Buttons
    st.subheader("🔬 Analisis MCDM")
    col1, col2, col3 = st.columns(3)
    with col1:
        run_all = st.button("▶️ Run All Methods", use_container_width=True)
    with col2:
        run_vikor = st.button("🔍 Run VIKOR Only", use_container_width=True)
    with col3:
        run_electre = st.button("📊 Run ELECTRE Only", use_container_width=True)

    def dummy_scores(method_name):
        np.random.seed(42)
        scores = np.random.rand(len(data))
        ranked = sorted(zip(data['NAMA'], scores), key=lambda x: -x[1])
        df_rank = pd.DataFrame(ranked, columns=["Nama", f"Skor {method_name}"])
        df_rank['Ranking'] = df_rank[f"Skor {method_name}"].rank(ascending=False).astype(int)
        return df_rank

    if run_all:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🔍 Hasil VIKOR")
            df_vikor = dummy_scores("VIKOR")
            st.dataframe(df_vikor.style.apply(lambda x: ['background-color: lightgreen' if r == 1 else '' for r in x['Ranking']], axis=1), use_container_width=True)
        with col2:
            st.markdown("### 📊 Hasil ELECTRE")
            df_electre = dummy_scores("ELECTRE")
            st.dataframe(df_electre.style.apply(lambda x: ['background-color: lightgreen' if r == 1 else '' for r in x['Ranking']], axis=1), use_container_width=True)

    elif run_vikor:
        st.markdown("### 🔍 Hasil VIKOR")
        df_vikor = dummy_scores("VIKOR")
        st.dataframe(df_vikor.style.apply(lambda x: ['background-color: lightgreen' if r == 1 else '' for r in x['Ranking']], axis=1), use_container_width=True)

    elif run_electre:
        st.markdown("### 📊 Hasil ELECTRE")
        df_electre = dummy_scores("ELECTRE")
        st.dataframe(df_electre.style.apply(lambda x: ['background-color: lightgreen' if r == 1 else '' for r in x['Ranking']], axis=1), use_container_width=True)

# ---------- INPUT DATA PAGE ---------- #
if 'candidate_success_message' in st.session_state and st.session_state.candidate_success_message:
          st.success(st.session_state.candidate_success_message)
          del st.session_state.candidate_success_message

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
                        file_exists = os.path.exists("dataset.csv")
                        is_empty = False
                        if file_exists:
                            try:
                                df_check = pd.read_csv("dataset.csv")
                                if df_check.empty:
                                    is_empty = True
                            except pd.errors.EmptyDataError:
                                is_empty = True
                        
                        write_header = not file_exists or is_empty
                        new_row_df.to_csv("dataset.csv", mode='a', header=write_header, index=False)
                        st.session_state.candidate_success_message = f"Data untuk {nama} berhasil ditambahkan ke dataset.csv!"
                        
                        # Hanya jalankan ini jika penyimpanan berhasil
                        if hasattr(load_data, 'clear'): 
                            load_data.clear() 
                        st.rerun()  # Rerun setelah sukses dan clear cache
                    except Exception as e:
                        st.error(f"Gagal menyimpan data ke CSV: {e}")
        
# ---------- JOB POSITIONS PAGE ---------- #
elif st.session_state.page == "Job Positions":
    st.title("💼 Input Posisi Pekerjaan")
    st.subheader("➕ Tambah Posisi Pekerjaan Baru")

    # Menggunakan form yang sudah Anda definisikan sebelumnya
    with st.form("job_position_form_ui"): # Beri key unik untuk form ini
        # Job Position Input (sesuaikan dengan variabel Anda)
        job_position_input_nama = st.text_input("Nama Posisi Pekerjaan", placeholder="Contoh: Software Engineer")
        
        st.markdown("---")
        
        # MBTI Preferences (menggunakan UI checkboxes Anda)
        st.markdown("### 🎭 MBTI Preferences")
        st.write("Pilih tipe MBTI yang sesuai untuk posisi ini:")
        
        mbti_types_options = ["Extroverted (E)", "Introverted (I)", "Sensing (S)", "iNtuition (N)", "Thinking (T)", "Feeling (F)", "Judging (J)", "Percieving (P)"]
        col_mbti_job_1, col_mbti_job_2 = st.columns(2)
        
        selected_mbti_list_input = [] 
        for i, mbti_option_text in enumerate(mbti_types_options):
            target_col = col_mbti_job_1 if i < 4 else col_mbti_job_2
            with target_col:
                # Pastikan key untuk setiap checkbox unik
                if st.checkbox(mbti_option_text, key=f"job_mbti_input_{mbti_option_text.replace(' ', '_').replace('(', '').replace(')', '')}"):
                    selected_mbti_list_input.append(mbti_option_text)

        st.markdown("---")
        
        # PAPI Kostick Primary Preference (menggunakan UI radio buttons Anda)
        st.markdown("### 📊 PAPI Kostick Primary Preference")
        st.write("Pilih karakteristik utama yang diperlukan:")
        
        papi_primary_options_list = [
            "Leadership & Dominance", "Analytical & Detail-Oriented", 
            "Social & People-Oriented", "Organized & Systematic", "Creative & Flexible"
        ]
        selected_papi_primary_input = st.radio(
            "Pilih satu karakteristik utama:",
            papi_primary_options_list,
            key="job_papi_primary_input" # Key unik
        )

        st.markdown("---")
        
        # Additional PAPI characteristics (menggunakan UI checkboxes Anda)
        st.markdown("### 📋 PAPI Kostick Secondary Preferences (Opsional)")
        st.write("Pilih karakteristik tambahan yang diinginkan:")
        
        selected_secondary_papi_list_input = []
        col_papi_sec_1, col_papi_sec_2 = st.columns(2)
        
        secondary_papi_options_list = ["High Energy", "Aggressive", "Competitive", "Outgoing", "Social"]
        for i, papi_sec_option_text in enumerate(secondary_papi_options_list):
            target_col_sec = col_papi_sec_1 if i < (len(secondary_papi_options_list) / 2) else col_papi_sec_2
            with target_col_sec:
                 # Pastikan key untuk setiap checkbox unik
                if st.checkbox(papi_sec_option_text, key=f"job_papi_sec_input_{papi_sec_option_text.replace(' ', '_')}"):
                    selected_secondary_papi_list_input.append(papi_sec_option_text)

        # Submit button
        submitted_button_job = st.form_submit_button("💾 Simpan Posisi Pekerjaan")

        # Logika setelah tombol submit ditekan
        if submitted_button_job:
            if not job_position_input_nama: # Menggunakan variabel input nama posisi
                st.error("Nama Posisi Pekerjaan tidak boleh kosong.")
            # Cek apakah posisi sudah ada di session_state DataFrame
            elif job_position_input_nama in st.session_state.job_positions_df['Job Position'].tolist():
                st.warning(f"Posisi '{job_position_input_nama}' sudah ada dalam daftar.")
            else:
                # Jika valid dan nama posisi belum ada:
                
                # 1. Format string MBTI dari list pilihan
                mbti_preferences_string = ", ".join(selected_mbti_list_input) if selected_mbti_list_input else "Tidak ada preferensi MBTI dipilih"
                
                # 2. Format string PAPI dari pilihan primer dan sekunder
                papi_kostick_string = selected_papi_primary_input # Menggunakan variabel input PAPI primer
                if selected_secondary_papi_list_input: # Menggunakan variabel input PAPI sekunder
                    papi_kostick_string += f" ({', '.join(selected_secondary_papi_list_input)})"
                
                # 3. Buat DataFrame baru untuk entri posisi pekerjaan ini
                new_job_entry_df = pd.DataFrame([{
                    'Job Position': job_position_input_nama, # Menggunakan variabel input nama posisi
                    'MBTI Preferences': mbti_preferences_string,
                    'PAPI Kostick Preferences': papi_kostick_string
                }])
                
                # 4. Tambahkan entri baru ke DataFrame di session_state
                st.session_state.job_positions_df = pd.concat(
                    [st.session_state.job_positions_df, new_job_entry_df],
                    ignore_index=True
                )
                
                # ----- INI BAGIAN B YANG DIMAKSUD (MODIFIKASI UNTUK MENYIMPAN KE CSV) -----
                # 5. SIMPAN DataFrame yang sudah diupdate ke CSV
                try:
                    st.session_state.job_positions_df.to_csv(JOB_POSITIONS_CSV_PATH, index=False)
                    # Pesan sukses yang lebih informatif
                    st.success(f"✅ Posisi '{job_position_input_nama}' berhasil ditambahkan ke daftar dan disimpan secara permanen ke file {JOB_POSITIONS_CSV_PATH}!")
                except Exception as e:
                    st.error(f"Gagal menyimpan data posisi pekerjaan ke CSV: {e}")
                    st.warning(f"Posisi '{job_position_input_nama}' telah ditambahkan ke daftar sesi ini, tetapi gagal disimpan secara permanen.")
                # ----- AKHIR DARI BAGIAN B -----
                
                #RINGKASAN
                st.markdown("### 📋 Ringkasan Posisi yang Ditambahkan (Sesi Ini):")
                st.write(f"**Posisi:** {job_position_input_nama}")
                st.write(f"**MBTI Preferences:** {mbti_preferences_string}")
                st.write(f"**Primary PAPI:** {selected_papi_primary_input}")
                if selected_secondary_papi_list_input:
                    st.write(f"**Secondary PAPI:** {', '.join(selected_secondary_papi_list_input)}")
                else:
                    st.write(f"**Secondary PAPI:** Tidak ada yang dipilih")
