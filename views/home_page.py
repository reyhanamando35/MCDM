# home_page.py
import streamlit as st
import pandas as pd
import numpy as np
import re # Import modul regular expression

# Fungsi untuk memformat string MBTI ke akronim atau membiarkannya jika sudah akronim
def format_mbti_for_display(mbti_string):
    if not isinstance(mbti_string, str) or "Tidak ada preferensi MBTI dipilih" in mbti_string or not mbti_string.strip():
        return mbti_string # Menangani non-string, placeholder, dan string kosong

    # Periksa apakah string sudah dalam format akronim (misal, "ENTJ", "E", "ENTJ, ENFJ")
    # Heuristik: terdiri dari grup 1-4 huruf kapital, mungkin dipisah koma
    is_likely_acronym_format = True
    temp_parts_check = mbti_string.split(',')
    for tp_check in temp_parts_check:
        tp_check = tp_check.strip()
        if not re.fullmatch(r"[A-Z]{1,4}", tp_check): # Setiap bagian harus 1-4 huruf kapital
            is_likely_acronym_format = False
            break
    
    if is_likely_acronym_format:
        return mbti_string # Jika sudah mirip akronim, kembalikan apa adanya

    # Jika bukan format akronim, coba parse dari format "Nama Deskripsi (X)"
    parts = mbti_string.split(',')
    extracted_letters = []
    for part in parts:
        part = part.strip()
        match = re.search(r'\(([A-Za-z])\)', part) # Cari (X) atau (x) di dalam string
        if match:
            extracted_letters.append(match.group(1).upper()) # Ambil hurufnya dan ubah ke uppercase

    if extracted_letters:
        return "".join(extracted_letters) # Gabungkan semua huruf yang diekstrak
    else:
        # Fallback: jika tidak ada huruf yang diekstrak dan tidak teridentifikasi sebagai akronim,
        # kembalikan string asli (misalnya, jika formatnya tidak terduga)
        return mbti_string

# Fungsi render_page yang sudah ada, dengan modifikasi pada bagian penampilan tabel job positions
def render_page(data_kandidat, job_positions_df_from_state):
    st.title("📋 Dashboard Seleksi Karyawan Berbasis MCDM")

    # Original candidate data
    st.subheader("📋 Data Kandidat Lengkap")
    st.dataframe(data_kandidat, use_container_width=True)

    # Job Positions Table
    st.subheader("📋 Daftar Posisi Pekerjaan")
    if job_positions_df_from_state is not None and not job_positions_df_from_state.empty:
        df_display_jobs = job_positions_df_from_state.copy() # Buat salinan untuk dimodifikasi
        
        # Bagian ini tidak lagi diperlukan karena kolom 'MBTI Preferences' akan dihapus dari DataFrame sumber
        # if 'MBTI Preferences' in df_display_jobs.columns:
        #     # Terapkan fungsi pemformatan ke kolom 'MBTI Preferences'
        #     df_display_jobs['MBTI Preferences'] = df_display_jobs['MBTI Preferences'].apply(format_mbti_for_display)
            
        st.dataframe(df_display_jobs, use_container_width=True)
    else:
        st.info("Belum ada data posisi pekerjaan.")


    st.markdown("---")

    # Candidate Selection Section
    st.subheader("🔍 Seleksi Kandidat")

    col_home_1, col_home_2, col_home_3 = st.columns([2, 2, 2])
    with col_home_1:
        if job_positions_df_from_state is not None and not job_positions_df_from_state.empty:
            # Pastikan kolom 'Job Position' ada sebelum mencoba mengaksesnya
            if 'Job Position' in job_positions_df_from_state.columns:
                job_options_list = job_positions_df_from_state['Job Position'].dropna().tolist() # dropna untuk menghindari error jika ada NaN
                selected_job_index = 0 if job_options_list else None
            else:
                job_options_list = ["Data posisi tidak valid"]
                selected_job_index = 0
        else:
            job_options_list = ["Tidak ada posisi tersedia"]
            selected_job_index = 0
            
        selected_job = st.selectbox(
            "Pilih Posisi Pekerjaan:",
            options=job_options_list,
            index=selected_job_index if selected_job_index is not None and job_options_list else 0,
            key="home_selectbox_job"
        )

    generate_final = st.button("🚀 Generate Final Data", use_container_width=True)
    if generate_final:
        if selected_job == "Tidak ada posisi tersedia" or selected_job == "Data posisi tidak valid" or data_kandidat.empty:
            st.warning("Tidak dapat menganalisis. Pastikan ada data kandidat dan posisi pekerjaan yang valid dipilih.")
        else:
            st.success(f"Menganalisis kandidat untuk posisi: {selected_job}")

            st.subheader("📊 Data Hasil Agregasi (5 Kriteria)")
            np.random.seed(42)
            aggregated_data = pd.DataFrame({
                'Nama': data_kandidat['NAMA'],
                'IST_Score': np.random.randint(60, 100, len(data_kandidat)),
                'MBTI_Score': np.random.randint(60, 100, len(data_kandidat)),
                'PAPI_Score': np.random.randint(60, 100, len(data_kandidat)),
                'DISC_Score': np.random.randint(60, 100, len(data_kandidat)),
                'Kraepelin_Score': np.random.randint(60, 100, len(data_kandidat))
            })
            st.dataframe(aggregated_data, use_container_width=True)

    st.markdown("---")

    st.subheader("🔬 Analisis MCDM")
    col1, col2, col3 = st.columns(3)
    with col1:
        run_all = st.button("▶️ Run All Methods", use_container_width=True)
    with col2:
        run_vikor = st.button("🔍 Run VIKOR Only", use_container_width=True)
    with col3:
        run_electre = st.button("📊 Run ELECTRE Only", use_container_width=True)

    def dummy_scores(method_name, candidate_names):
        np.random.seed(42) # Konsistensi dummy data
        scores = np.random.rand(len(candidate_names))
        ranked = sorted(zip(candidate_names, scores), key=lambda x: -x[1])
        df_rank = pd.DataFrame(ranked, columns=["Nama", f"Skor {method_name}"])
        df_rank['Ranking'] = df_rank[f"Skor {method_name}"].rank(ascending=False).astype(int)
        return df_rank

    if not data_kandidat.empty and 'NAMA' in data_kandidat.columns: # Pastikan kolom NAMA ada
        candidate_names_for_dummy = data_kandidat['NAMA']
        if run_all:
            col1_mcdm, col2_mcdm = st.columns(2) # Menggunakan nama variabel kolom yang berbeda
            with col1_mcdm:
                st.markdown("### 🔍 Hasil VIKOR")
                df_vikor = dummy_scores("VIKOR", candidate_names_for_dummy)
                st.dataframe(df_vikor.style.apply(lambda x: ['background-color: lightgreen' if r == 1 else '' for r in x['Ranking']], axis=1), use_container_width=True)
            with col2_mcdm:
                st.markdown("### 📊 Hasil ELECTRE")
                df_electre = dummy_scores("ELECTRE", candidate_names_for_dummy)
                st.dataframe(df_electre.style.apply(lambda x: ['background-color: lightgreen' if r == 1 else '' for r in x['Ranking']], axis=1), use_container_width=True)
        elif run_vikor:
            st.markdown("### 🔍 Hasil VIKOR")
            df_vikor = dummy_scores("VIKOR", candidate_names_for_dummy)
            st.dataframe(df_vikor.style.apply(lambda x: ['background-color: lightgreen' if r == 1 else '' for r in x['Ranking']], axis=1), use_container_width=True)
        elif run_electre:
            st.markdown("### 📊 Hasil ELECTRE")
            # df_electre = dummy_scores("ELECTRE", candidate_names_for_dummy)
            # df_electre = run_electre(agg_to_5(data_kandidat, job_positions_df_from_state.loc[job_positions_df_from_state['Job Position'] == selected_job].iloc[0]), selected_job) masih salah inii
            st.dataframe(df_electre.style.apply(lambda x: ['background-color: lightgreen' if r == 1 else '' for r in x['Ranking']], axis=1), use_container_width=True)
    elif generate_final or run_all or run_vikor or run_electre:
        st.warning("Tidak ada data kandidat (atau kolom NAMA tidak ada) untuk diproses. Silakan input data terlebih dahulu.")