import streamlit as st
import pandas as pd
import numpy as np
import re
from utils.preprocess import prep_dm, agg_to_5
from methods.vikor import run_vikor
from methods.electre import run_electre

# Fungsi untuk merender halaman utama
def render_page(data_kandidat, job_positions_df_from_state):

    # Original candidate data
    st.subheader("📋 Data Kandidat Lengkap")
    st.dataframe(data_kandidat, use_container_width=True)

    # Job Positions Table
    st.subheader("📋 Daftar Posisi Pekerjaan")
    if job_positions_df_from_state is not None and not job_positions_df_from_state.empty:
        df_display_jobs = job_positions_df_from_state.copy()
        st.dataframe(df_display_jobs, use_container_width=True)
    else:
        st.info("Belum ada data posisi pekerjaan.")

    st.markdown("---")

    # Candidate Selection Section
    st.subheader("🔍 Seleksi Kandidat")

    col_home_1, col_home_2, col_home_3 = st.columns([2, 2, 2])
    with col_home_1:
        if job_positions_df_from_state is not None and not job_positions_df_from_state.empty:
            if 'Job Position' in job_positions_df_from_state.columns:
                job_options_list = job_positions_df_from_state['Job Position'].dropna().tolist()
                selected_job_index = 0 if job_options_list else None
            else:
                job_options_list = ["Data posisi tidak valid"]
                selected_job_index = 0
        else:
            job_options_list = ["Tidak ada posisi tersedia"]
            selected_job_index = 0
            
        # Dropdown untuk memilih posisi pekerjaan
        selected_job = st.selectbox(
            "Pilih Posisi Pekerjaan:",
            options=job_options_list,
            index=selected_job_index if selected_job_index is not None and job_options_list else 0,
            key="home_selectbox_job"
        )

        # Cari job_filter_row (baris bobot) berdasarkan selected_job
        if (
            job_positions_df_from_state is not None
            and "Job Position" in job_positions_df_from_state.columns
        ):
            mask = job_positions_df_from_state["Job Position"] == selected_job
            if mask.any():
                job_filter_row = job_positions_df_from_state.loc[mask].iloc[0]
            else:
                job_filter_row = None
        else:
            job_filter_row = None

        st.session_state["selected_job"] = job_filter_row

    generate_final = st.button("🚀 Generate Final Data", use_container_width=True)

    if generate_final:
        if (
            selected_job in["Tidak ada posisi tersedia", "Data posisi tidak valid"] 
            or data_kandidat is None
            or data_kandidat.empty
            or job_filter_row is None
        ):
            st.warning("Tidak dapat menganalisis. Pastikan ada data kandidat dan posisi pekerjaan yang valid dipilih.")
        else:
            st.session_state["data_kandidat_raw"] = data_kandidat.copy()
            st.session_state["job_filter_row"] = job_filter_row

            # Panggil fungsi agg_to_5 untuk membuat agregasi 5 kriteria dan simpan di session_state
            agg_data = agg_to_5(
                data_kandidat.copy(),
                job_filter_row
            )
            st.session_state["agg_data"] = agg_data
            st.success(f"Menganalisis kandidat untuk posisi: {selected_job}")

    # Tampilkan data hasil agregasi jika sudah ada
    if "agg_data" in st.session_state:
        st.subheader("📊 Data Hasil Agregasi (5 Kriteria)")
        st.dataframe(st.session_state["agg_data"], use_container_width=True)

        st.markdown("---")

        # Tampilkan pilihan metode MCDM
        st.subheader("🔬 Analisis MCDM")
        col1, col2, col3 = st.columns(3)
        with col1:
            btn_run_all = st.button("▶️ Run All Methods", use_container_width=True)
        with col2:
            btn_run_vikor = st.button("🔍 Run VIKOR Only", use_container_width=True)
        with col3:
            btn_run_electre = st.button("📊 Run ELECTRE Only", use_container_width=True)

        data_for_methods = st.session_state["data_kandidat_raw"]
        job_row_for_methods = st.session_state["job_filter_row"]

        # Jika tombol dijalankan, panggil fungsi yang sesuai
        if btn_run_all:
            col1_mcdm, col2_mcdm = st.columns(2)
            with col1_mcdm:
                st.subheader("🔍 Hasil VIKOR")
                df_vikor = run_vikor(data_for_methods, job_row_for_methods)
                st.dataframe(df_vikor.style.apply(lambda r: ["background-color: green"] * len(r) if r["Ranking"] == 1 else [""] * len(r), axis=1), use_container_width=True)
            with col2_mcdm:
                st.subheader("📊 Hasil ELECTRE")
                df_electre = run_electre(data_for_methods, job_row_for_methods)
                st.dataframe(df_electre.style.apply(lambda r: ["background-color: green"] * len(r) if r["Ranking"] == 1 else [""] * len(r), axis=1), use_container_width=True)
        elif btn_run_vikor:
            st.subheader("🔍 Hasil VIKOR")
            df_vikor = run_vikor(data_for_methods, job_row_for_methods)
            st.dataframe(df_vikor.style.apply(lambda r: ["background-color: green"] * len(r) if r["Ranking"] == 1 else [""] * len(r), axis=1), use_container_width=True)
        elif btn_run_electre:
            st.subheader("📊 Hasil ELECTRE")
            df_electre = run_electre(data_for_methods, job_row_for_methods)
            st.dataframe(df_electre.style.apply(lambda r: ["background-color: green"] * len(r) if r["Ranking"] == 1 else [""] * len(r), axis=1), use_container_width=True)
        
    elif generate_final:
        pass
    else:
        st.info("Tekan tombol **Generate Final Data** untuk melihat Data Hasil Agregasi.")