import streamlit as st
import pandas as pd
import numpy as np
import os

# Fungsi untuk merender halaman input data kandidat
def render_page(app_csv_columns, load_data_callback_for_clear):
    """
    Fungsi untuk menampilkan halaman input data kandidat.
    """

    # Inisialisasi session state untuk pesan sukses jika belum ada
    if 'candidate_success_message' in st.session_state and st.session_state.candidate_success_message:
        st.success(st.session_state.candidate_success_message)
        del st.session_state.candidate_success_message

    st.title("📝 Input Data Kandidat")
    st.subheader("📥 Input Data Calon Baru")

    with st.form("input_form_kandidat"):
        # Inisialisasi dictionary untuk menyimpan semua input & nilai
        all_input_values = {}

        # Input untuk nama calon
        nama = st.text_input("Nama Calon")
        st.markdown("---")

        # Input untuk hasil IST
        st.markdown("### 🧠 IST (Intelligence Structure Test)")
        ist_fields = [col for col in app_csv_columns if col in ["SE", "WA", "AN", "GE", "ME", "RA", "ZR", "FA", "WU", "IQ"]]
        cols_ist = st.columns(5)
        for i, field in enumerate(ist_fields):
            with cols_ist[i % 5]:
                all_input_values[field] = st.number_input(f"{field}", value=0, min_value=0, max_value=150, key=f"input_ist_{field}")
        st.markdown("---")

        # Input untuk PAPI Kostick
        st.markdown("### 📊 PAPI Kostick")
        papi_fields = [col for col in app_csv_columns if col.startswith("P_")]
        num_papi_cols_ui = 5
        for i in range(0, len(papi_fields), num_papi_cols_ui):
            cols_papi = st.columns(num_papi_cols_ui)
            for j, field in enumerate(papi_fields[i : i + num_papi_cols_ui]):
                with cols_papi[j]:
                    all_input_values[field] = st.number_input(f"{field}", value=0, min_value=0, max_value=9, key=f"input_papi_{field}")
        st.markdown("---")

        # Input untuk MBTI
        st.markdown("### 🎭 MBTI")
        mbti_fields = [col for col in app_csv_columns if col.startswith("M_")]
        cols_mbti = st.columns(4)
        for i, field in enumerate(mbti_fields):
            with cols_mbti[i % 4]:
                all_input_values[field] = st.number_input(f"{field}", value=0, min_value=0, max_value=100, key=f"input_mbti_{field}")
        st.markdown("---")

        # Input untuk Kraepelin
        st.markdown("### ⏱️ Kraepelin")
        kraep_fields = [col for col in app_csv_columns if col.startswith("K_")]
        cols_kraep = st.columns(len(kraep_fields) if len(kraep_fields) > 0 else 1)
        for i, field in enumerate(kraep_fields):
            with cols_kraep[i % len(kraep_fields) if len(kraep_fields) > 0 else 0]:
                all_input_values[field] = st.number_input(f"{field}", value=0, min_value=0, max_value=5, key=f"input_kraep_{field}")
        st.markdown("---")

        # Input untuk DISC
        st.markdown("### 🎯 DISC")
        disc_fields = [col for col in app_csv_columns if col.startswith("D_")]
        cols_disc = st.columns(len(disc_fields) if len(disc_fields) > 0 else 1)
        for i, field in enumerate(disc_fields):
            with cols_disc[i % len(disc_fields) if len(disc_fields) > 0 else 0]:
                all_input_values[field] = st.number_input(f"{field}", value=0, min_value=0, max_value=9, key=f"input_disc_{field}")

        submitted_kandidat = st.form_submit_button("➕ Tambahkan ke Data Kandidat")

        # Validasi input sebelum menyimpan
        if submitted_kandidat:
            if not nama:
                st.error("Nama Calon tidak boleh kosong.")
            else:
                new_row_data = [nama]
                for col_name in app_csv_columns[1:]:
                    new_row_data.append(all_input_values.get(col_name, np.nan))

                new_row_df = pd.DataFrame([new_row_data], columns=app_csv_columns)

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
                    st.session_state.candidate_success_message = f"Data untuk {nama} berhasil ditambahkan ke Dataset.csv!"
                    
                    if hasattr(load_data_callback_for_clear, 'clear'): 
                        load_data_callback_for_clear.clear() 
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menyimpan data ke CSV: {e}")