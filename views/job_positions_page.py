import streamlit as st
import pandas as pd

# Fungsi ini akan dipanggil dari app.py
# Kita perlu meneruskan JOB_POSITIONS_CSV_PATH
def render_page(app_job_positions_csv_path):
    st.title("💼 Input Posisi Pekerjaan")
    st.subheader("➕ Tambah Posisi Pekerjaan Baru")

    with st.form("job_position_form_ui"):
        job_position_input_nama = st.text_input("Nama Posisi Pekerjaan", placeholder="Contoh: Software Engineer")
        st.markdown("---")

        st.markdown("### 🎭 MBTI Preferences")
        st.write("Pilih tipe MBTI yang sesuai untuk posisi ini:")
        mbti_types_options = ["Extroverted (E)", "Introverted (I)", "Sensing (S)", "iNtuition (N)", "Thinking (T)", "Feeling (F)", "Judging (J)", "Percieving (P)"]
        col_mbti_job_1, col_mbti_job_2 = st.columns(2)
        selected_mbti_list_input = []
        for i, mbti_option_text in enumerate(mbti_types_options):
            target_col = col_mbti_job_1 if i < 4 else col_mbti_job_2
            with target_col:
                if st.checkbox(mbti_option_text, key=f"job_mbti_input_{mbti_option_text.replace(' ', '_').replace('(', '').replace(')', '')}"):
                    selected_mbti_list_input.append(mbti_option_text)
        st.markdown("---")

        st.markdown("### 📊 PAPI Kostick Primary Preference")
        st.write("Pilih karakteristik utama yang diperlukan:")
        papi_primary_options_list = [
            "Leadership & Dominance", "Analytical & Detail-Oriented", 
            "Social & People-Oriented", "Organized & Systematic", "Creative & Flexible"
        ]
        selected_papi_primary_input = st.radio(
            "Pilih satu karakteristik utama:",
            papi_primary_options_list,
            key="job_papi_primary_input"
        )
        st.markdown("---")

        st.markdown("### 📋 PAPI Kostick Secondary Preferences (Opsional)")
        st.write("Pilih karakteristik tambahan yang diinginkan:")
        selected_secondary_papi_list_input = []
        col_papi_sec_1, col_papi_sec_2 = st.columns(2)
        secondary_papi_options_list = ["High Energy", "Aggressive", "Competitive", "Outgoing", "Social"]
        for i, papi_sec_option_text in enumerate(secondary_papi_options_list):
            target_col_sec = col_papi_sec_1 if i < (len(secondary_papi_options_list) / 2) else col_papi_sec_2
            with target_col_sec:
                if st.checkbox(papi_sec_option_text, key=f"job_papi_sec_input_{papi_sec_option_text.replace(' ', '_')}"):
                    selected_secondary_papi_list_input.append(papi_sec_option_text)

        submitted_button_job = st.form_submit_button("💾 Simpan Posisi Pekerjaan")

        if submitted_button_job:
            if not job_position_input_nama:
                st.error("Nama Posisi Pekerjaan tidak boleh kosong.")
            elif job_position_input_nama in st.session_state.job_positions_df['Job Position'].tolist():
                st.warning(f"Posisi '{job_position_input_nama}' sudah ada dalam daftar.")
            else:
                mbti_preferences_string = ", ".join(selected_mbti_list_input) if selected_mbti_list_input else "Tidak ada preferensi MBTI dipilih"
                papi_kostick_string = selected_papi_primary_input
                if selected_secondary_papi_list_input:
                    papi_kostick_string += f" ({', '.join(selected_secondary_papi_list_input)})"
                
                new_job_entry_df = pd.DataFrame([{
                    'Job Position': job_position_input_nama,
                    'MBTI Preferences': mbti_preferences_string,
                    'PAPI Kostick Preferences': papi_kostick_string
                }])
                
                st.session_state.job_positions_df = pd.concat(
                    [st.session_state.job_positions_df, new_job_entry_df],
                    ignore_index=True
                )
                
                try:
                    st.session_state.job_positions_df.to_csv(app_job_positions_csv_path, index=False)
                    st.success(f"✅ Posisi '{job_position_input_nama}' berhasil ditambahkan ke daftar dan disimpan secara permanen ke file {app_job_positions_csv_path}!")
                except Exception as e:
                    st.error(f"Gagal menyimpan data posisi pekerjaan ke CSV: {e}")
                    st.warning(f"Posisi '{job_position_input_nama}' telah ditambahkan ke daftar sesi ini, tetapi gagal disimpan secara permanen.")
                
                st.markdown("### 📋 Ringkasan Posisi yang Ditambahkan (Sesi Ini):")
                st.write(f"**Posisi:** {job_position_input_nama}")
                st.write(f"**MBTI Preferences:** {mbti_preferences_string}")
                st.write(f"**Primary PAPI:** {selected_papi_primary_input}")
                if selected_secondary_papi_list_input:
                    st.write(f"**Secondary PAPI:** {', '.join(selected_secondary_papi_list_input)}")
                else:
                    st.write(f"**Secondary PAPI:** Tidak ada yang dipilih")