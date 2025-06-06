import streamlit as st
from views import home_page, input_data_page, job_positions_page

def manage_display(
    data_kandidat, 
    job_positions_df, 
    csv_columns_kandidat, 
    load_data_kandidat_func, 
    job_positions_csv_path
):
    """
    Fungsi utama untuk mengelola semua elemen tampilan:
    1. Inisialisasi state halaman.
    2. Membuat dan menampilkan navbar.
    3. Me-render halaman yang dipilih.
    """
    
    # 1. Inisialisasi state halaman jika belum ada
    if 'page' not in st.session_state:
        st.session_state.page = "Home"

    # 2. Membuat Judul Page
    st.title("📋 Dashboard Seleksi Karyawan Berbasis MCDM")
    st.markdown("---")

    # 2. Membuat dan menampilkan navbar
    st.subheader("Pilih Halaman:")

    # Buat 3 kolom dengan lebar yang sama persis
    nav_cols = st.columns(3)
    with nav_cols[0]:
        if st.button("🏠 Home", use_container_width=True, key="nav_home"):
            st.session_state.page = "Home"
    with nav_cols[1]:
        if st.button("📝 Input Candidate Data", use_container_width=True, key="nav_input_data"):
            st.session_state.page = "Input Data"
    with nav_cols[2]:
        if st.button("💼 Job Positions", use_container_width=True, key="nav_job_positions"):
            st.session_state.page = "Job Positions"
    st.markdown("---")

    # 3. Me-render halaman yang dipilih berdasarkan state
    page = st.session_state.get("page", "Home")

    if page == "Home":
        home_page.render_page(data_kandidat, job_positions_df)
        
    elif page == "Input Data":
        input_data_page.render_page(csv_columns_kandidat, load_data_kandidat_func)
            
    elif page == "Job Positions":
        job_positions_page.render_page(job_positions_csv_path)
            
    else:
        # Jika state tidak valid, kembali ke Home
        st.session_state.page = "Home"
        st.rerun()