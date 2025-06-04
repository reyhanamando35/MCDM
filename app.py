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

data = load_data()

# ---------- Sidebar Navigasi ---------- #
page = st.sidebar.selectbox("Navigasi", ["Home", "Input Data"])

# ---------- HOME PAGE ---------- #
if page == "Home":
    st.title("📋 Dashboard Seleksi Karyawan Berbasis MCDM")

    st.subheader("Data Kandidat")
    st.dataframe(data, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        run_all = st.button("▶️ Run All")
    with col2:
        run_vikor = st.button("🔍 Run VIKOR Only")
    with col3:
        run_electre = st.button("📊 Run ELECTRE Only")

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
            st.markdown("### Hasil VIKOR")
            df_vikor = dummy_scores("VIKOR")
            st.dataframe(df_vikor.style.apply(lambda x: ['background-color: lightgreen' if r == 1 else '' for r in x['Ranking']], axis=1), use_container_width=True)
        with col2:
            st.markdown("### Hasil ELECTRE")
            df_electre = dummy_scores("ELECTRE")
            st.dataframe(df_electre.style.apply(lambda x: ['background-color: lightgreen' if r == 1 else '' for r in x['Ranking']], axis=1), use_container_width=True)

    elif run_vikor:
        st.markdown("### Hasil VIKOR")
        df_vikor = dummy_scores("VIKOR")
        st.dataframe(df_vikor.style.apply(lambda x: ['background-color: lightgreen' if r == 1 else '' for r in x['Ranking']], axis=1), use_container_width=True)

    elif run_electre:
        st.markdown("### Hasil ELECTRE")
        df_electre = dummy_scores("ELECTRE")
        st.dataframe(df_electre.style.apply(lambda x: ['background-color: lightgreen' if r == 1 else '' for r in x['Ranking']], axis=1), use_container_width=True)

# ---------- INPUT DATA PAGE ---------- #
elif page == "Input Data":
    st.title("📝 Input Data Kandidat dan Posisi")

    tab1, tab2 = st.tabs(["📥 Input Data Calon", "💼 Input Posisi Kerja"])

    with tab1:
        st.subheader("Input Data Calon Baru")

        with st.form("input_form"):
            nama = st.text_input("Nama Calon")
            st.markdown("---")
            st.markdown("### IST")
            col_ist = st.columns(10)
            ist_fields = ["SE", "WA", "AN", "GE", "ME", "RA", "ZR", "FA", "WU", "IQ"]
            ist_values = [col.number_input(f"{f}", 0, 200, key=f) for col, f in zip(col_ist, ist_fields)]

            st.markdown("---")
            st.markdown("### PAPI Kostik")
            papi_fields = [col for col in data.columns if col.startswith("P_")]
            col_papi = st.columns(6)
            papi_values = [col.number_input(f"{f}", 0, 9, key=f) for col, f in zip(col_papi * (len(papi_fields)//6 + 1), papi_fields)]

            st.markdown("---")
            st.markdown("### MBTI")
            mbti_fields = [col for col in data.columns if col.startswith("M_")]
            col_mbti = st.columns(4)
            mbti_values = [col.number_input(f"{f}", 0, 100, key=f) for col, f in zip(col_mbti * (len(mbti_fields)//4 + 1), mbti_fields)]

            st.markdown("---")
            st.markdown("### Kraepelin")
            kraep_fields = [col for col in data.columns if col.startswith("K_")]
            col_kraep = st.columns(4)
            kraep_values = [col.number_input(f"{f}", 0, 5, key=f) for col, f in zip(col_kraep * (len(kraep_fields)//4 + 1), kraep_fields)]

            st.markdown("---")
            st.markdown("### DISC")
            disc_fields = [col for col in data.columns if col.startswith("D_")]
            col_disc = st.columns(4)
            disc_values = [col.number_input(f"{f}", 0, 15, key=f) for col, f in zip(col_disc, disc_fields)]

            submitted = st.form_submit_button("➕ Tambahkan ke Data Kandidat")

            if submitted:
                new_row = pd.DataFrame([[nama] + ist_values + papi_values + mbti_values + kraep_values + disc_values], columns=data.columns)
                data = pd.concat([data, new_row], ignore_index=True)
                st.success(f"Data untuk {nama} berhasil ditambahkan!")

    with tab2:
        st.subheader("(To be implemented) Input Posisi Pekerjaan")
        st.info("Fitur ini akan dikembangkan untuk menentukan bobot & filter kriteria berdasarkan posisi (IT, Sales, Admin, dll).")
