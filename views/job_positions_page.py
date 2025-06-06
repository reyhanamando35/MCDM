# Di views/job_positions_page.py

import streamlit as st
import pandas as pd
import re
import numpy as np # Diperlukan untuk np.nan jika digunakan

# Kolom yang diharapkan SEKARANG HANYA 10 KOLOM
EXPECTED_JOB_COLUMNS_JP = [
    'Job Position', 'PAPI context', 'M', 'B', 'T', 'I_M', 
    'D', 'I_D', 'S', 'C'
]

def render_page(app_job_positions_csv_path): 
    st.title("💼 Input Posisi Pekerjaan")
    st.subheader("➕ Tambah Posisi Pekerjaan Baru")

    if 'job_positions_df' not in st.session_state:
        try:
            df_temp = pd.read_csv(app_job_positions_csv_path)
            if not all(col in df_temp.columns for col in EXPECTED_JOB_COLUMNS_JP) or len(df_temp.columns) != len(EXPECTED_JOB_COLUMNS_JP):
                st.warning(f"File {app_job_positions_csv_path} memiliki struktur kolom yang tidak diharapkan. Memuat ulang dari default mungkin diperlukan jika masalah berlanjut.")
                st.session_state.job_positions_df = pd.DataFrame(columns=EXPECTED_JOB_COLUMNS_JP) # Fallback
            else:
                st.session_state.job_positions_df = df_temp
        except (FileNotFoundError, pd.errors.EmptyDataError):
            st.info(f"File {app_job_positions_csv_path} tidak ditemukan atau kosong. Membuat DataFrame baru untuk sesi ini.")
            st.session_state.job_positions_df = pd.DataFrame(columns=EXPECTED_JOB_COLUMNS_JP)
        except Exception as e:
            st.error(f"Gagal memuat {app_job_positions_csv_path}: {e}")
            st.session_state.job_positions_df = pd.DataFrame(columns=EXPECTED_JOB_COLUMNS_JP) # Fallback

    # Pastikan st.session_state.job_positions_df ada, meskipun kosong, dengan kolom yang benar
    if 'job_positions_df' not in st.session_state or not isinstance(st.session_state.job_positions_df, pd.DataFrame):
        st.session_state.job_positions_df = pd.DataFrame(columns=EXPECTED_JOB_COLUMNS_JP)
    elif not all(col in st.session_state.job_positions_df.columns for col in EXPECTED_JOB_COLUMNS_JP):
         # Jika ada tapi kolomnya salah, re-inisialisasi dengan kolom yang benar
        temp_data_for_reinit = st.session_state.job_positions_df.to_dict(orient='list')
        st.session_state.job_positions_df = pd.DataFrame(columns=EXPECTED_JOB_COLUMNS_JP)
        for col in EXPECTED_JOB_COLUMNS_JP: # Coba isi kembali data yang mungkin ada
            if col in temp_data_for_reinit:
                st.session_state.job_positions_df[col] = temp_data_for_reinit[col]


    with st.form("job_position_form_ui"):
        job_position_input_nama = st.text_input("Nama Posisi Pekerjaan", placeholder="Contoh: Software Engineer")
        st.markdown("---")

        st.markdown("### 🎯 PAPI Context (pilih salah satu preferensi utama)")
        papi_context_options = {
            "O - Betah terhadap Kelompok": "O", "B - Empati / relasi pribadi": "B",
            "R - Tipe teoritis": "R", "D - Suka detail": "D", "Z - Suka perubahan": "Z"
        }
        selected_papi_context_label = st.selectbox(
            "Pilih salah satu preferensi utama PAPI:",
            options=list(papi_context_options.keys()), index=None, # index=None agar awalnya kosong
            placeholder="Pilih salah satu (O, B, R, D, Z)", key="papi_context_selector"
        )
        st.markdown("---")
        
        st.markdown("### 🎭 MBTI Letters (M, B, T, I_M)")
        st.write("Pilih satu preferensi dari setiap pasangan MBTI untuk mengisi kolom M, B, T, I_M:")
        mbti_dichotomies = [
            {"label": "Orientasi Energi (E/I) -> M", "options": ["Extroverted (E)", "Introverted (I)"], "key_suffix": "ei"},
            {"label": "Fungsi Informasi (S/N) -> B", "options": ["Sensing (S)", "Intuition (N)"], "key_suffix": "sn"},
            {"label": "Fungsi Keputusan (T/F) -> T", "options": ["Thinking (T)", "Feeling (F)"], "key_suffix": "tf"},
            {"label": "Gaya Hidup (J/P) -> I_M", "options": ["Judging (J)", "Perceiving (P)"], "key_suffix": "jp"}
        ]
        selected_mbti_letters = []
        cols_mbti = st.columns(len(mbti_dichotomies))
        for i, dichotomy in enumerate(mbti_dichotomies):
            with cols_mbti[i]:
                selected_choice = st.selectbox(
                    label=dichotomy["label"], options=dichotomy["options"],
                    index=0, key=f"job_mbti_select_{dichotomy['key_suffix']}"
                )
                match = re.search(r"\((\w)\)", selected_choice)
                selected_mbti_letters.append(match.group(1).upper() if match else "")
        st.markdown("---")

        st.markdown("### 🔢 Skor DISC (D, I_D, S, C)")
        st.write("Masukkan skor untuk setiap komponen DISC (total harus 1.0):")
        col1_disc, col2_disc = st.columns(2)
        with col1_disc:
            val_D = st.number_input("D (Dominance)", min_value=0.0, max_value=1.0, value=0.25, step=0.01, key="score_D_job")
            val_ID = st.number_input("I_D (Influence)", min_value=0.0, max_value=1.0, value=0.25, step=0.01, key="score_ID_job")
        with col2_disc:
            val_S = st.number_input("S (Steadiness)", min_value=0.0, max_value=1.0, value=0.25, step=0.01, key="score_S_job")
            val_C = st.number_input("C (Conscientiousness)", min_value=0.0, max_value=1.0, value=0.25, step=0.01, key="score_C_job")

        submitted_button_job = st.form_submit_button("💾 Simpan Posisi Pekerjaan")

        if submitted_button_job:
            total_disc = val_D + val_ID + val_S + val_C
            actual_papi_value = papi_context_options.get(selected_papi_context_label)

            # Validasi input
            if not job_position_input_nama:
                st.error("Nama Posisi Pekerjaan tidak boleh kosong.")
            elif not selected_papi_context_label: # <<<--- VALIDASI TAMBAHAN DI SINI
                st.error("Preferensi utama PAPI harus dipilih.")
            elif abs(total_disc - 1.0) > 0.01: 
                st.error(f"❌ Total skor D+I_D+S+C harus = 1.0. Saat ini: {total_disc:.2f}")
            elif len(selected_mbti_letters) != 4 or any(not letter for letter in selected_mbti_letters):
                st.error("Semua 4 preferensi MBTI harus dipilih.")
            else:
                # Lanjutkan jika semua validasi lolos
                new_job_data = {
                    'Job Position': job_position_input_nama,
                    'PAPI context': actual_papi_value,
                    'M': selected_mbti_letters[0], 'B': selected_mbti_letters[1],
                    'T': selected_mbti_letters[2], 'I_M': selected_mbti_letters[3],
                    'D': val_D, 'I_D': val_ID, 'S': val_S, 'C': val_C,
                }
                new_job_entry_df = pd.DataFrame([new_job_data], columns=EXPECTED_JOB_COLUMNS_JP)
                
                # Pastikan st.session_state.job_positions_df adalah DataFrame
                if not isinstance(st.session_state.job_positions_df, pd.DataFrame):
                    st.session_state.job_positions_df = pd.DataFrame(columns=EXPECTED_JOB_COLUMNS_JP)

                current_df = st.session_state.job_positions_df.copy()
                
                # Pastikan current_df memiliki semua kolom yang diharapkan sebelum concat
                for col in EXPECTED_JOB_COLUMNS_JP:
                    if col not in current_df.columns:
                        current_df[col] = np.nan if col in ['D', 'I_D', 'S', 'C'] else None
                current_df = current_df[EXPECTED_JOB_COLUMNS_JP] # Reorder jika perlu

                if job_position_input_nama in current_df['Job Position'].tolist():
                    st.warning(f"Posisi '{job_position_input_nama}' sudah ada. Data tidak ditambahkan.")
                else:
                    st.session_state.job_positions_df = pd.concat(
                        [current_df, new_job_entry_df], ignore_index=True
                    )
                    try:
                        st.session_state.job_positions_df[EXPECTED_JOB_COLUMNS_JP].to_csv(
                            app_job_positions_csv_path, index=False
                        )
                        st.success(f"✅ Posisi '{job_position_input_nama}' berhasil ditambahkan!")
                        # Pertimbangkan untuk st.rerun() jika ingin form di-reset atau update langsung terlihat
                        # st.rerun() 
                    except Exception as e:
                        st.error(f"Gagal menyimpan: {e}")
                
                # Tampilkan ringkasan (opsional, bisa di luar blok else jika selalu ingin ditampilkan setelah submit)
                # st.write(f"**Posisi:** {job_position_input_nama}")
                # st.write(f"**PAPI Context:** {actual_papi_value}")
                # ... (ringkasan lainnya)