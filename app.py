import streamlit as st
import pandas as pd
import numpy as np

# ---------- Konfigurasi Halaman ---------- #
st.set_page_config(page_title="Seleksi Karyawan", layout="wide")

# ---------- Load Dataset Kandidat ---------- #
@st.cache_data
def load_data():
    df = pd.read_csv("Dataset.csv")
    return df

@st.cache_data
def load_job_positions():
    # Sample job positions data - nanti bisa diganti dengan data dari file/database
    data = {
        'Job Position': ['Pre-Sales', 'IT Developer', 'Sales Manager', 'Admin', 'Marketing'],
        'MBTI Preferences': ['ENTJ, ENFJ', 'INTJ, INTP', 'ESFJ, ENFJ', 'ISFJ, ISTJ', 'ENFP, ESFP'],
        'PAPI Kostick Preferences': ['Leadership, Assertive', 'Analytical, Detail', 'Social, Persuasive', 'Organized, Stable', 'Creative, Flexible']
    }
    return pd.DataFrame(data)

data = load_data()
job_positions_data = load_job_positions()

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
with col4:
    if st.button("📊 Analysis", use_container_width=True):
        st.session_state.page = "Analysis"

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
    st.subheader("📋 Daftar Posisi Pekerjaan")
    st.dataframe(job_positions_data, use_container_width=True)

    st.markdown("---")

    # Candidate Selection Section
    st.subheader("🔍 Seleksi Kandidat")
    
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        selected_job = st.selectbox(
            "Pilih Posisi Pekerjaan:",
            options=job_positions_data['Job Position'].tolist(),
            index=0
        )
    
    with col2:
        generate_final = st.button("🚀 Generate Final Data", use_container_width=True)
    
    with col3:
        st.write("")  # Empty space for alignment

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
elif st.session_state.page == "Input Data":
    st.title("📝 Input Data Kandidat")

    st.subheader("📥 Input Data Calon Baru")

    with st.form("input_form"):
        nama = st.text_input("Nama Calon")
        st.markdown("---")
        
        # IST Section
        st.markdown("### 🧠 IST (Intelligence Structure Test)")
        col_ist = st.columns(5)
        ist_fields = ["SE", "WA", "AN", "GE", "ME", "RA", "ZR", "FA", "WU", "IQ"]
        ist_values = []
        for i, field in enumerate(ist_fields):
            with col_ist[i % 5]:
                ist_values.append(st.number_input(f"{field}", 0, 100, key=f"ist_{field}"))

        st.markdown("---")
        
        # PAPI Kostick Section
        st.markdown("### 📊 PAPI Kostick")
        papi_fields = [col for col in data.columns if col.startswith("P_")]
        col_papi = st.columns(6)
        papi_values = []
        for i, field in enumerate(papi_fields):
            with col_papi[i % 6]:
                papi_values.append(st.number_input(f"{field}", 0, 9, key=f"papi_{field}"))

        st.markdown("---")
        
        # MBTI Section
        st.markdown("### 🎭 MBTI")
        mbti_fields = [col for col in data.columns if col.startswith("M_")]
        col_mbti = st.columns(4)
        mbti_values = []
        for i, field in enumerate(mbti_fields):
            with col_mbti[i % 4]:
                mbti_values.append(st.number_input(f"{field}", 0, 100, key=f"mbti_{field}"))

        st.markdown("---")
        
        # Kraepelin Section
        st.markdown("### ⏱️ Kraepelin")
        kraep_fields = [col for col in data.columns if col.startswith("K_")]
        col_kraep = st.columns(4)
        kraep_values = []
        for i, field in enumerate(kraep_fields):
            with col_kraep[i % 4]:
                kraep_values.append(st.number_input(f"{field}", 0, 100, key=f"kraep_{field}"))

        st.markdown("---")
        
        # DISC Section
        st.markdown("### 🎯 DISC")
        disc_fields = [col for col in data.columns if col.startswith("D_")]
        col_disc = st.columns(4)
        disc_values = []
        for i, field in enumerate(disc_fields):
            with col_disc[i % 4]:
                disc_values.append(st.number_input(f"{field}", 0, 9, key=f"disc_{field}"))

        submitted = st.form_submit_button("➕ Tambahkan ke Data Kandidat")

        if submitted and nama:
            new_row = pd.DataFrame([[nama] + ist_values + papi_values + mbti_values + kraep_values + disc_values], columns=data.columns)
            # Note: In real implementation, you would save this to the actual dataset
            st.success(f"Data untuk {nama} berhasil ditambahkan!")
            st.info("Note: Dalam implementasi nyata, data akan disimpan ke database/file CSV.")

# ---------- JOB POSITIONS PAGE ---------- #
elif st.session_state.page == "Job Positions":
    st.title("💼 Input Posisi Pekerjaan")

    st.subheader("➕ Tambah Posisi Pekerjaan Baru")

    with st.form("job_position_form"):
        # Job Position Input
        job_position = st.text_input("Nama Posisi Pekerjaan", placeholder="Contoh: Software Engineer, Sales Manager, dll.")
        
        st.markdown("---")
        
        # MBTI Preferences (8 checkboxes)
        st.markdown("### 🎭 MBTI Preferences")
        st.write("Pilih tipe MBTI yang sesuai untuk posisi ini:")
        
        mbti_types = ["Extroverted (E)", "Introverted (I)", "Sensing (S)", "iNtuition (N)", "Thinking (T)", "Feeling (F)", "Judging (J)", "Percieving (P)"]
        col_mbti1, col_mbti2 = st.columns(2)
        
        selected_mbti = []
        for i, mbti_type in enumerate(mbti_types):
            if i < 4:
                with col_mbti1:
                    if st.checkbox(mbti_type, key=f"mbti_{mbti_type}"):
                        selected_mbti.append(mbti_type)
            else:
                with col_mbti2:
                    if st.checkbox(mbti_type, key=f"mbti_{mbti_type}"):
                        selected_mbti.append(mbti_type)

        st.markdown("---")
        
        # PAPI Kostick Preferences (5 radio buttons)
        st.markdown("### 📊 PAPI Kostick Primary Preference")
        st.write("Pilih karakteristik utama yang diperlukan:")
        
        papi_options = [
            "Leadership & Dominance",
            "Analytical & Detail-Oriented", 
            "Social & People-Oriented",
            "Organized & Systematic",
            "Creative & Flexible"
        ]
        
        selected_papi = st.radio(
            "Pilih satu karakteristik utama:",
            papi_options,
            key="papi_primary"
        )

        st.markdown("---")
        
        # Additional PAPI characteristics (checkboxes for secondary traits)
        st.markdown("### 📋 PAPI Kostick Secondary Preferences (Opsional)")
        st.write("Pilih karakteristik tambahan yang diinginkan:")
        
        secondary_papi = []
        col_papi1, col_papi2 = st.columns(2)
        
        secondary_options = [
            "High Energy", "Aggressive", "Competitive", "Outgoing", "Social"
        ]
        
        for i, option in enumerate(secondary_options):
            if i < 3:
                with col_papi1:
                    if st.checkbox(option, key=f"secondary_{option}"):
                        secondary_papi.append(option)
            else:
                with col_papi2:
                    if st.checkbox(option, key=f"secondary_{option}"):
                        secondary_papi.append(option)

        # Submit button
        submitted = st.form_submit_button("💾 Simpan Posisi Pekerjaan")

        if submitted and job_position:
            st.success(f"✅ Posisi '{job_position}' berhasil ditambahkan!")
            
            # Display summary
            st.markdown("### 📋 Ringkasan Posisi:")
            st.write(f"**Posisi:** {job_position}")
            st.write(f"**MBTI Preferences:** {', '.join(selected_mbti) if selected_mbti else 'Tidak ada yang dipilih'}")
            st.write(f"**Primary PAPI:** {selected_papi}")
            st.write(f"**Secondary PAPI:** {', '.join(secondary_papi) if secondary_papi else 'Tidak ada yang dipilih'}")
            
            st.info("Note: Dalam implementasi nyata, data akan disimpan ke database/file.")

# ---------- ANALYSIS PAGE ---------- #
elif st.session_state.page == "Analysis":
    st.title("📊 Analisis Data")
    st.info("Halaman ini akan berisi analisis mendalam dari hasil MCDM dan visualisasi data kandidat.")
    
    # Placeholder untuk analisis lebih lanjut
    st.subheader("📈 Statistik Kandidat")
    if len(data) > 0:
        st.write(f"Total Kandidat: {len(data)}")
        st.write(f"Total Posisi Pekerjaan: {len(job_positions_data)}")
    
    st.subheader("🔍 Filter dan Pencarian")
    st.info("Fitur filter berdasarkan kriteria tertentu akan ditambahkan di sini.")