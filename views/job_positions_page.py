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

        st.markdown("### 🎯 PAPI Context (pilih salah satu preferensi utama)")

        papi_context_options = {
            "O - Betah terhadap Kelompok": "O",
            "B - Empati / relasi pribadi": "B",
            "R - Tipe teoritis": "R",
            "D - Suka detail": "D",
            "Z - Suka perubahan": "Z"
        }

        selected_label = st.selectbox("Pilih PAPI Context:", options=list(papi_context_options.keys()))
        selected_value = papi_context_options[selected_label]

        selected_papi_context_label = st.selectbox(
        "Pilih salah satu preferensi utama PAPI:", 
        list(papi_context_options.keys()),
        index=None,
        placeholder="Pilih salah satu (O, B, R, D, Z)"
    )
        all_input_values = {}
        for col in ["P_O", "P_B", "P_R", "P_D", "P_Z"]:
            if selected_papi_context_label and papi_context_options[selected_papi_context_label] == col:
                all_input_values[col] = 1
            else:
                all_input_values[col] = 0



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



        st.markdown("### 🔢 Skor DISC")
        st.write("Masukkan skor untuk setiap komponen DISC (total harus 1.0):")
        col1, col2 = st.columns(2)
        with col1:
            val_D = st.number_input("D (Dominance)", min_value=0.0, max_value=1.0, step=0.01, key="score_D")
            val_ID = st.number_input("I_D (Influence)", min_value=0.0, max_value=1.0, step=0.01, key="score_ID")
        with col2:
            val_S = st.number_input("S (Steadiness)", min_value=0.0, max_value=1.0, step=0.01, key="score_S")
            val_C = st.number_input("C (Conscientiousness)", min_value=0.0, max_value=1.0, step=0.01, key="score_C")

        submitted_button_job = st.form_submit_button("💾 Simpan Posisi Pekerjaan")

        if submitted_button_job:
            total_disc = val_D + val_ID + val_S + val_C
            if not job_position_input_nama:
                st.error("Nama Posisi Pekerjaan tidak boleh kosong.")
            elif not selected_papi_context_label:
                st.error("Silakan pilih satu preferensi utama PAPI (O, B, R, D, atau Z).")
            elif abs(total_disc - 1.0) > 0.01:
                st.error(f"❌ Total D+I+S+C harus = 1.0. Saat ini: {total_disc:.2f}")
            elif job_position_input_nama in st.session_state.job_positions_df['Job Position'].tolist():
                st.warning(f"Posisi '{job_position_input_nama}' sudah ada dalam daftar.")
            else:
                mbti_preferences_string = ", ".join(selected_mbti_list_input) if selected_mbti_list_input else "Tidak ada preferensi MBTI dipilih"
                
                new_job_entry_df = pd.DataFrame([{
                    'PAPI context' : selected_value,
                    'Job Position': job_position_input_nama,
                    "D": val_D,
                    "I_D": val_ID,
                    "S": val_S,
                    "C": val_C
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