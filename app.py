import streamlit as st
import pandas as pd
import numpy as np

# --- 0. Konfigurasi Halaman Aplikasi ---
st.set_page_config(
    page_title="SPK Rekrutmen Karyawan (Sesuai PDF)",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Helper Function untuk Membuat DataFrame Kosong ---
def create_empty_candidate_df_template():
    # Kolom disesuaikan dengan kebutuhan dari contoh hasil tes dan pra-proses
    columns = [
        'ID Kandidat', 'Nama Kandidat', 'Posisi Lamaran',
        # IST - diasumsikan kita dapatkan IQ total dan StdDev dari subtes
        'IST_IQ_Total', 'IST_StdDev_Subtes_IST', # Diambil dari perhitungan manual/sistem skor IST
        # MBTI - kita butuh skor WS (Weighted Score) untuk setiap dimensi
        'MBTI_WS_E', 'MBTI_WS_I', 'MBTI_WS_S', 'MBTI_WS_N',
        'MBTI_WS_T', 'MBTI_WS_F', 'MBTI_WS_J', 'MBTI_WS_P',
        # Kraepelin - kita butuh skor numerik untuk setiap aspek (hasil konversi BS,B,S,K,KS)
        # Contoh: Kecepatan(BS=5, B=4, S=3, K=2, KS=1), Ketelitian, Keajegan_Tingkat, Keajegan_Variasi, Ketahanan
        'Kraepelin_Kecepatan', 'Kraepelin_Ketelitian',
        'Kraepelin_Keajegan_Tingkat', 'Kraepelin_Keajegan_Variasi', 'Kraepelin_Ketahanan',
        # DISC - kita butuh skor kuantitatif yang merepresentasikan konsistensi atau profil ideal
        'DISC_Konsistensi_Score', # Misalnya, skor 0-1 untuk konsistensi 3 grafik
        # PAPI Kostick - kita butuh skor untuk 20 aspek atau total per kategori
        # Untuk menyederhanakan input file, kita minta total skor per kategori PAPI
        'PAPI_Sum_Atribut_Positif',      # Total dari 9 atribut positif
        'PAPI_Sum_Atribut_Kontekstual',  # Total dari 5 atribut kontekstual
        'PAPI_Sum_Atribut_Negatif'       # Total dari 6 atribut negatif (yang akan jadi 'cost')
    ]
    return pd.DataFrame(columns=columns)

# --- 2. Fungsi Pra-Proses Data (SAW implisit) ---
def preprocess_data_kandidat(df_kandidat, posisi_terpilih, streamlit_logging=False):
    processed_data = []
    if streamlit_logging: st.markdown("### --- Perhitungan Pra-Proses Data (SAW Implisit) ---")

    # Kolom yang dibutuhkan untuk pra-proses dan nilai default jika tidak ada
    required_cols_praproses = {
        'IST_IQ_Total': 100, 'IST_StdDev_Subtes_IST': 1.0,
        'MBTI_WS_E': 50, 'MBTI_WS_I': 50, 'MBTI_WS_S': 50, 'MBTI_WS_N': 50,
        'MBTI_WS_T': 50, 'MBTI_WS_F': 50, 'MBTI_WS_J': 50, 'MBTI_WS_P': 50,
        'Kraepelin_Kecepatan': 3, 'Kraepelin_Ketelitian': 3,
        'Kraepelin_Keajegan_Tingkat': 3, 'Kraepelin_Keajegan_Variasi': 3, 'Kraepelin_Ketahanan': 3,
        'DISC_Konsistensi_Score': 0.5,
        'PAPI_Sum_Atribut_Positif': 45, 'PAPI_Sum_Atribut_Kontekstual': 25, 'PAPI_Sum_Atribut_Negatif': 30
    }

    # Pastikan semua kolom yang dibutuhkan ada di DataFrame input
    for col, default_val in required_cols_praproses.items():
        if col not in df_kandidat.columns:
            df_kandidat[col] = default_val
            if streamlit_logging: st.warning(f"Kolom pra-proses '{col}' tidak ditemukan, menggunakan nilai default: {default_val}")


    for index, row in df_kandidat.iterrows():
        # Ambil Nama dan ID Kandidat dengan aman
        nama_kandidat_log = row.get('Nama Kandidat', f'Kandidat Index {index}')
        id_kandidat_log = row.get('ID Kandidat', f'ID_{index}')
        if streamlit_logging: st.markdown(f"**Mengolah Kandidat: {nama_kandidat_log} (ID: {id_kandidat_log})**")

        # 2.1 IST (sesuai Bab II Latar Belakang Anda)
        # Penalti jika standar deviasi tinggi (misal > 1.5, Anda bisa sesuaikan threshold ini)
        std_dev_ist = row['IST_StdDev_Subtes_IST']
        iq_asli = row['IST_IQ_Total']
        koefisien_ist = 0.9 if std_dev_ist > 1.5 else 1.0
        skor_ist_final = iq_asli * koefisien_ist
        if streamlit_logging:
            st.write(f"  - **IST**: IQ Asli = {iq_asli}, StdDev Subtes IST = {std_dev_ist}")
            st.write(f"    Koefisien penalti IST (StdDev > 1.5 ? 0.9 : 1.0) = {koefisien_ist}")
            st.write(f"    Skor IST Final = {iq_asli} * {koefisien_ist} = **{skor_ist_final:.2f}**")

        # Penjumlahan nilai WS dari dimensi yang dibutuhkan untuk posisi tertentu
        kebutuhan_mbti_scores = {}
        kebutuhan_mbti_display_calc = []
        if posisi_terpilih.upper() == 'IT': # Diasumsikan IT butuh T dan J
            kebutuhan_mbti_scores = {'T': row['MBTI_WS_T'], 'J': row['MBTI_WS_J']}
            kebutuhan_mbti_display_calc = [f"T({row['MBTI_WS_T']})", f"J({row['MBTI_WS_J']})"]
        elif posisi_terpilih.upper() == 'SALES': # Contoh, Sales butuh E
            kebutuhan_mbti_scores = {'E': row['MBTI_WS_E']}
            kebutuhan_mbti_display_calc = [f"E({row['MBTI_WS_E']})"]
        # Tambahkan logika untuk posisi lain sesuai kebutuhan Anda
        else: # Default jika tidak ada definisi spesifik
            kebutuhan_mbti_scores = {'E': row['MBTI_WS_E'], 'N': row['MBTI_WS_N'], 'T':row['MBTI_WS_T'], 'P':row['MBTI_WS_P']} # Contoh default
            kebutuhan_mbti_display_calc = [f"E({row['MBTI_WS_E']})",f"N({row['MBTI_WS_N']})",f"T({row['MBTI_WS_T']})",f"P({row['MBTI_WS_P']})"]


        skor_mbti_final = sum(kebutuhan_mbti_scores.values())
        if streamlit_logging:
            st.write(f"  - **MBTI** (Untuk Posisi: {posisi_terpilih}): Dimensi & Skor WS yang Digunakan = {', '.join(kebutuhan_mbti_display_calc)}")
            skor_values_str = [str(v) for v in kebutuhan_mbti_scores.values()]
            st.write(f"    Skor MBTI Final = Sum({', '.join(skor_values_str)}) = **{skor_mbti_final:.2f}**")

        # 2.3 Kraepelin (SAW - sesuai Bab II Latar Belakang Anda)
        # Aspek: Kecepatan, Ketelitian, Daya Tahan (masing2 25%), Keajegan Tingkat, Keajegan Variasi (masing2 12.5%)
        bobot_kraepelin_saw = {
            'Kraepelin_Kecepatan': 0.25,
            'Kraepelin_Ketelitian': 0.25,
            'Kraepelin_Daya_Tahan': 0.25,
            'Kraepelin_Keajegan_Tingkat': 0.125,
            'Kraepelin_Keajegan_Variasi': 0.125
        }
        skor_kraepelin_final_saw = 0
        kraepelin_saw_calc_display = []
        for aspek_col_name, bobot_val_saw in bobot_kraepelin_saw.items():
            skor_aspek_saw = row[aspek_col_name]
            skor_kraepelin_final_saw += skor_aspek_saw * bobot_val_saw
            kraepelin_saw_calc_display.append(f"{aspek_col_name.replace('Kraepelin_','')}({skor_aspek_saw}) * {bobot_val_saw}")
        if streamlit_logging:
            st.write(f"  - **Kraepelin (SAW)**:")
            for calc_step_saw in kraepelin_saw_calc_display:
                st.write(f"    {calc_step_saw}")
            st.write(f"    Skor Kraepelin Final (SAW) = **{skor_kraepelin_final_saw:.3f}**")

        # Menggunakan skor konsistensi yang sudah ada (misalnya, dari perbandingan 3 grafik)
        skor_disc_final = row['DISC_Konsistensi_Score'] # Ini adalah skor 0-1, semakin tinggi semakin baik
        if streamlit_logging:
            st.write(f"  - **DISC**: Skor Konsistensi (langsung dari data input) = **{skor_disc_final:.2f}**")

        # Rumus Daya Kerja = (Jumlah atribut positif + Jumlah atribut kontekstual) - Jumlah atribut potensi negatif
        sum_papi_positif = row['PAPI_Sum_Atribut_Positif']
        sum_papi_kontekstual = row['PAPI_Sum_Atribut_Kontekstual']
        sum_papi_negatif = row['PAPI_Sum_Atribut_Negatif']
        skor_papi_final = sum_papi_positif + sum_papi_kontekstual - sum_papi_negatif
        if streamlit_logging:
            st.write(f"  - **PAPI Kostick**:")
            st.write(f"    Sum Atribut Positif = {sum_papi_positif}")
            st.write(f"    Sum Atribut Kontekstual = {sum_papi_kontekstual}")
            st.write(f"    Sum Atribut Negatif (Risiko) = {sum_papi_negatif}")
            st.write(f"    Skor PAPI Final (Daya Kerja) = {sum_papi_positif} + {sum_papi_kontekstual} - {sum_papi_negatif} = **{skor_papi_final:.2f}**")

        processed_data.append({
            'ID Kandidat': row.get('ID Kandidat', id_kandidat_log),
            'Nama Kandidat': row.get('Nama Kandidat', nama_kandidat_log),
            'Posisi Lamaran': row.get('Posisi Lamaran', 'N/A'),
            'Kriteria_IST': skor_ist_final,
            'Kriteria_MBTI': skor_mbti_final,
            'Kriteria_Kraepelin': skor_kraepelin_final_saw, # Menggunakan hasil SAW
            'Kriteria_DISC': skor_disc_final,
            'Kriteria_PAPI': skor_papi_final,
        })
        if streamlit_logging: st.write("---") # Pemisah antar kandidat

    df_processed = pd.DataFrame(processed_data)
    kolom_kriteria_mcdm = ['Kriteria_IST', 'Kriteria_MBTI', 'Kriteria_Kraepelin', 'Kriteria_DISC', 'Kriteria_PAPI']
    
    # Pastikan kolom ada sebelum mengambil subset
    kolom_ada = [col for col in kolom_kriteria_mcdm if col in df_processed.columns]
    df_kriteria_subset = df_processed[kolom_ada].copy() if kolom_ada and not df_processed.empty else pd.DataFrame(columns=kolom_kriteria_mcdm)
    
    return df_processed, df_kriteria_subset, kolom_kriteria_mcdm

# --- 3. Fungsi Metode VIKOR (Disesuaikan dengan PDF 10-MCDM-VIKOR.pdf) ---
def vikor_method(df_kriteria, kriteria_types, bobot_vikor, v_param=0.5, streamlit_logging=False):
    if df_kriteria.empty or len(kriteria_types) != df_kriteria.shape[1] or len(bobot_vikor) != df_kriteria.shape[1]:
        st.error("VIKOR: Data kriteria, jenis kriteria, atau bobot tidak valid.")
        return pd.DataFrame(columns=['S', 'R', 'Q', 'Rank_VIKOR']), "N/A"

    if streamlit_logging: st.markdown("### --- Perhitungan VIKOR (sesuai PDF) ---")

    # Langkah 1: Matriks Keputusan Awal (X atau f_ij)
    f_ij_matrix = df_kriteria.copy()
    if streamlit_logging: st.markdown("**1. Matriks Keputusan Awal (X atau $f_{ij}$):**"); st.dataframe(f_ij_matrix.style.format("{:.3f}"))

    # Langkah 2a: Menentukan nilai f_j* (ideal baik) dan f_j- (ideal buruk)
    f_j_star = pd.Series(index=f_ij_matrix.columns, dtype=float)
    f_j_minus = pd.Series(index=f_ij_matrix.columns, dtype=float)

    if streamlit_logging: st.markdown("**2a. Menentukan Solusi Ideal Positif ($f_j^*$) dan Negatif ($f_j^-$):**")
    for idx, col_name_vikor in enumerate(f_ij_matrix.columns):
        if kriteria_types[idx] == 'benefit':
            f_j_star[col_name_vikor] = f_ij_matrix[col_name_vikor].max()
            f_j_minus[col_name_vikor] = f_ij_matrix[col_name_vikor].min()
        elif kriteria_types[idx] == 'cost':
            f_j_star[col_name_vikor] = f_ij_matrix[col_name_vikor].min()
            f_j_minus[col_name_vikor] = f_ij_matrix[col_name_vikor].max()
        if streamlit_logging:
            st.write(f"  Kriteria '{col_name_vikor}' (Tipe: {kriteria_types[idx]}): $f_j^*$ = {f_j_star[col_name_vikor]:.3f}, $f_j^-$ = {f_j_minus[col_name_vikor]:.3f}")

    # Langkah 2b: Normalisasi Matriks Keputusan (N_ij)
    # N_ij = (f_j* - f_ij) / (f_j* - f_j-)
    N_ij_matrix = f_ij_matrix.copy()
    if streamlit_logging: st.markdown("**2b. Matriks Ternormalisasi ($N_{ij} = (f_j^* - f_{ij}) / (f_j^* - f_j^-)$):**")
    for col_name_vikor in f_ij_matrix.columns:
        pembagi = (f_j_star[col_name_vikor] - f_j_minus[col_name_vikor])
        if pembagi == 0:
            N_ij_matrix[col_name_vikor] = 0.0
            if streamlit_logging: st.write(f"  Normalisasi Kriteria '{col_name_vikor}': Pembagi nol, hasil N_ij = 0")
        else:
            N_ij_matrix[col_name_vikor] = (f_j_star[col_name_vikor] - f_ij_matrix[col_name_vikor]) / pembagi
            if streamlit_logging:
                for alt_idx, alt_name in enumerate(N_ij_matrix.index):
                    st.write(f"  $N_{{{alt_name},{col_name_vikor}}} = ({f_j_star[col_name_vikor]:.3f} - {f_ij_matrix.loc[alt_name, col_name_vikor]:.3f}) / ({f_j_star[col_name_vikor]:.3f} - {f_j_minus[col_name_vikor]:.3f}) = {N_ij_matrix.loc[alt_name, col_name_vikor]:.3f}$")
    if streamlit_logging: st.dataframe(N_ij_matrix.style.format("{:.3f}"))


    # Langkah 3: Normalisasi Terbobot (F_ij)
    # F_ij = w_j * N_ij
    F_ij_matrix = N_ij_matrix.copy()
    if streamlit_logging: st.markdown(f"**3. Matriks Normalisasi Terbobot ($F_{{ij}} = w_j \cdot N_{{ij}}$) dengan Bobot (w): {np.round(bobot_vikor,3).tolist()}**")
    for idx, col_name_vikor in enumerate(N_ij_matrix.columns):
        F_ij_matrix[col_name_vikor] = bobot_vikor[idx] * N_ij_matrix[col_name_vikor]
        if streamlit_logging:
            for alt_idx, alt_name in enumerate(F_ij_matrix.index):
                 st.write(f"  $F_{{{alt_name},{col_name_vikor}}} = {bobot_vikor[idx]:.2f} * {N_ij_matrix.loc[alt_name, col_name_vikor]:.3f} = {F_ij_matrix.loc[alt_name, col_name_vikor]:.3f}$")
    if streamlit_logging: st.dataframe(F_ij_matrix.style.format("{:.3f}"))

    # Langkah 4: Menghitung nilai S_i dan R_i
    # S_i = sum(F_ij) for each alternative i
    # R_i = max(F_ij) for each alternative i
    S_i_series = F_ij_matrix.sum(axis=1)
    R_i_series = F_ij_matrix.max(axis=1)
    if streamlit_logging:
        st.markdown("**4. Menghitung Nilai Utility Measure ($S_i$) dan Regret Measure ($R_i$):**")
        temp_df_sr_vikor = pd.DataFrame({'S_i': S_i_series, 'R_i': R_i_series})
        st.dataframe(temp_df_sr_vikor.style.format("{:.3f}"))

    # Langkah 5: Menghitung Indeks VIKOR (Q_i)
    S_star_val = S_i_series.min()
    S_minus_val = S_i_series.max()
    R_star_val = R_i_series.min()
    R_minus_val = R_i_series.max()
    if streamlit_logging:
        st.markdown("**5. Menghitung Indeks VIKOR ($Q_i$):**")
        st.write(f"  $S^*$ (min $S_i$) = {S_star_val:.4f}, $S^-$ (max $S_i$) = {S_minus_val:.4f}")
        st.write(f"  $R^*$ (min $R_i$) = {R_star_val:.4f}, $R^-$ (max $R_i$) = {R_minus_val:.4f}")
        st.write(f"  Parameter $v$ = {v_param}")

    term_S_num_vikor = (S_i_series - S_star_val)
    term_S_den_vikor = (S_minus_val - S_star_val)
    term_S_vikor = term_S_num_vikor / term_S_den_vikor if term_S_den_vikor != 0 else pd.Series(0.0, index=S_i_series.index)

    term_R_num_vikor = (R_i_series - R_star_val)
    term_R_den_vikor = (R_minus_val - R_star_val)
    term_R_vikor = term_R_num_vikor / term_R_den_vikor if term_R_den_vikor != 0 else pd.Series(0.0, index=R_i_series.index)
    
    Q_i_series = v_param * term_S_vikor + (1 - v_param) * term_R_vikor
    if streamlit_logging:
        temp_df_q_calc_vikor = pd.DataFrame({
            '$S_i$': S_i_series, '$(S_i-S^*)/(S^--S^*)$': term_S_vikor,
            '$R_i$': R_i_series, '$(R_i-R^*)/(R^--R^*)$': term_R_vikor,
            '$Q_i$': Q_i_series
        })
        st.markdown("  Detail Perhitungan $Q_i$:")
        st.dataframe(temp_df_q_calc_vikor.style.format("{:.3f}"))

    # Langkah 6: Perankingan alternatif
    df_result_vikor = pd.DataFrame({'S': S_i_series, 'R': R_i_series, 'Q': Q_i_series}, index=df_kriteria.index)
    df_result_vikor['Rank_VIKOR'] = df_result_vikor['Q'].rank(method='min').astype(int) # Semakin kecil Q semakin baik
    df_result_sorted_vikor = df_result_vikor.sort_values(by='Rank_VIKOR')

    # Kondisi Akseptabilitas (Acceptable Advantage)
    acceptable_advantage_status_vikor = "N/A (Kurang dari 2 alternatif)"
    if len(df_result_sorted_vikor) >= 2:
        q_a1_vikor = df_result_sorted_vikor['Q'].iloc[0]
        q_a2_vikor = df_result_sorted_vikor['Q'].iloc[1]
        m_vikor = len(df_kriteria) # Jumlah alternatif
        DQ_vikor = 1 / (m_vikor - 1) if m_vikor > 1 else float('inf')
        
        adv_check = (q_a2_vikor - q_a1_vikor) >= DQ_vikor
        acceptable_advantage_status_vikor = f"Terpenuhi (Q(A2)-Q(A1) = {q_a2_vikor-q_a1_vikor:.4f} >= DQ = {DQ_vikor:.4f})" if adv_check else f"Tidak Terpenuhi (Q(A2)-Q(A1) = {q_a2_vikor-q_a1_vikor:.4f} < DQ = {DQ_vikor:.4f})"
    
    if streamlit_logging:
        st.markdown("**6. Perankingan Alternatif (Semakin kecil Q, semakin baik):**")
        st.dataframe(df_result_sorted_vikor.style.format({'S': '{:.4f}', 'R': '{:.4f}', 'Q': '{:.4f}'}))
        st.write(f"  Kondisi 'Acceptable Advantage': {acceptable_advantage_status_vikor}")

    return df_result_sorted_vikor, acceptable_advantage_status_vikor


# --- 4. Fungsi Metode ELECTRE (Disesuaikan dengan PDF 07-MCDM-ELECTRE.pdf) ---
def electre_method(df_kriteria, bobot_electre, streamlit_logging=False): # Threshold input dihilangkan
    if df_kriteria.empty or len(bobot_electre) != df_kriteria.shape[1]:
        st.error("ELECTRE: Data kriteria atau bobot tidak valid.")
        return pd.DataFrame(columns=['Net_Score_E', 'Rank_ELECTRE']), None, None, None, None, None, None, None

    X_ij_electre = df_kriteria.copy()
    n_alt_electre, n_crit_electre = X_ij_electre.shape

    if streamlit_logging: st.markdown("### --- Perhitungan ELECTRE (sesuai PDF) ---")
    if streamlit_logging: st.markdown("**Matriks Keputusan Awal ($X_{ij}$):**"); st.dataframe(X_ij_electre.style.format("{:.3f}"))

    # Langkah 1: Normalisasi Matriks Keputusan ($r_{ij}$)
    R_ij_electre = X_ij_electre.copy()
    if streamlit_logging: st.markdown("**1. Normalisasi Matriks Keputusan ($r_{ij} = x_{ij} / \sqrt{\sum x_{ij}^2}$ per kolom):**")
    for col_electre in X_ij_electre.columns:
        norm_factor_electre = np.sqrt(np.sum(X_ij_electre[col_electre]**2))
        R_ij_electre[col_electre] = X_ij_electre[col_electre] / norm_factor_electre if norm_factor_electre != 0 else 0
        if streamlit_logging:
             st.write(f"  Normalisasi Kriteria '{col_electre}': Pembagi $\sqrt{{\sum x^2}}$ = {norm_factor_electre:.3f}")
    if streamlit_logging: st.markdown("  **Matriks Ternormalisasi ($R_{ij}$):**"); st.dataframe(R_ij_electre.style.format("{:.4f}"))

    # Langkah 2: Pembobotan pada Matriks Ternormalisasi ($V_{ij}$)
    V_ij_electre = R_ij_electre.copy()
    if streamlit_logging: st.markdown(f"**2. Matriks Normalisasi Terbobot ($V_{{ij}} = r_{{ij}} \cdot w_j$) dengan Bobot (w): {np.round(bobot_electre,3).tolist()}**")
    for j_idx, col_name_electre in enumerate(R_ij_electre.columns):
        V_ij_electre[col_name_electre] = R_ij_electre[col_name_electre] * bobot_electre[j_idx]
    if streamlit_logging: st.markdown("  **Matriks $V_{ij}$ Final:**"); st.dataframe(V_ij_electre.style.format("{:.4f}"))

    # Langkah 3: Menentukan Himpunan Concordance ($C_{kl}$) dan Discordance ($D_{kl}$)
    # (Implisit dalam langkah 4)
    if streamlit_logging: st.markdown("**3. Menentukan Himpunan Concordance dan Discordance (Implisit dalam Langkah 4):**")

    # Langkah 4: Menghitung Matriks Concordance ($c_{kl}$) dan Discordance ($d_{kl}$)
    concordance_matrix_c_electre = pd.DataFrame(np.zeros((n_alt_electre, n_alt_electre)), index=X_ij_electre.index, columns=X_ij_electre.index, dtype=float)
    discordance_matrix_d_electre = pd.DataFrame(np.zeros((n_alt_electre, n_alt_electre)), index=X_ij_electre.index, columns=X_ij_electre.index, dtype=float)

    if streamlit_logging: st.markdown("**4a. Menghitung Matriks Concordance ($c_{kl} = \sum_{j \in C_{kl}} w_j$):**")
    for k_idx_electre, k_alt_name_electre in enumerate(X_ij_electre.index):
        for l_idx_electre, l_alt_name_electre in enumerate(X_ij_electre.index):
            if k_idx_electre == l_idx_electre: continue
            sum_w_concord_electre = 0
            concord_criteria_names_electre = []
            for j_crit_idx_electre, crit_name_electre in enumerate(X_ij_electre.columns):
                if V_ij_electre.iloc[k_idx_electre, j_crit_idx_electre] >= V_ij_electre.iloc[l_idx_electre, j_crit_idx_electre]: # $v_{kj} \ge v_{lj}$
                    sum_w_concord_electre += bobot_electre[j_crit_idx_electre]
                    concord_criteria_names_electre.append(crit_name_electre)
            concordance_matrix_c_electre.iloc[k_idx_electre, l_idx_electre] = sum_w_concord_electre # Formula $c_{kl}$
            if streamlit_logging:
                st.write(f"  $c({k_alt_name_electre},{l_alt_name_electre})$: Kriteria $C_{{kl}}$ ({', '.join(concord_criteria_names_electre)}) -> $\sum w_j$ = {sum_w_concord_electre:.4f}")
    if streamlit_logging: st.markdown("  **Matriks Concordance ($c_{kl}$) Final:**"); st.dataframe(concordance_matrix_c_electre.style.format("{:.4f}"))

    if streamlit_logging: st.markdown("**4b. Menghitung Matriks Discordance ($d_{kl}$):**") #
    for k_idx_electre, k_alt_name_electre in enumerate(X_ij_electre.index):
        for l_idx_electre, l_alt_name_electre in enumerate(X_ij_electre.index):
            if k_idx_electre == l_idx_electre: continue
            max_diff_discord_set_electre = 0
            discord_criteria_names_dkl_electre = [] # Untuk $D_{kl}$
            
            v_k_electre = V_ij_electre.iloc[k_idx_electre]
            v_l_electre = V_ij_electre.iloc[l_idx_electre]
            
            for j_crit_idx_electre, crit_name_electre in enumerate(X_ij_electre.columns):
                if v_k_electre.iloc[j_crit_idx_electre] < v_l_electre.iloc[j_crit_idx_electre]: # $v_{kj} < v_{lj}$ untuk $D_{kl}$
                    diff_electre = abs(v_k_electre.iloc[j_crit_idx_electre] - v_l_electre.iloc[j_crit_idx_electre])
                    if diff_electre > max_diff_discord_set_electre:
                        max_diff_discord_set_electre = diff_electre
                    discord_criteria_names_dkl_electre.append(crit_name_electre)
            
            # Pembagi: max |v_kj - v_lj| untuk SEMUA j (seluruh kriteria) untuk pasangan (k,l)
            v_kj_minus_v_lj_abs_electre = abs(v_k_electre - v_l_electre) # Series of |v_kj - v_lj| for all j
            max_diff_all_criteria_pair_electre = 0
            if not v_kj_minus_v_lj_abs_electre.empty:
                max_diff_all_criteria_pair_electre = v_kj_minus_v_lj_abs_electre.max()

            if max_diff_all_criteria_pair_electre == 0:
                discordance_matrix_d_electre.iloc[k_idx_electre, l_idx_electre] = 0
            else:
                discordance_matrix_d_electre.iloc[k_idx_electre, l_idx_electre] = max_diff_discord_set_electre / max_diff_all_criteria_pair_electre # Formula $d_{kl}$
            
            if streamlit_logging:
                st.write(f"  $d({k_alt_name_electre},{l_alt_name_electre})$: Kriteria $D_{{kl}}$ ({', '.join(discord_criteria_names_dkl_electre)})")
                st.write(f"    Numerator: $\max |v_{{kj}}-v_{{lj}}|_{{j \in D_{{kl}}}}$ = {max_diff_discord_set_electre:.4f}")
                st.write(f"    Denominator: $\max |v_{{kj}}-v_{{lj}}|_{{\forall j}}$ (untuk pasangan {k_alt_name_electre},{l_alt_name_electre}) = {max_diff_all_criteria_pair_electre:.4f}")
                st.write(f"    $d({k_alt_name_electre},{l_alt_name_electre})$ = {discordance_matrix_d_electre.iloc[k_idx_electre, l_idx_electre]:.4f}")
    if streamlit_logging: st.markdown("  **Matriks Discordance ($d_{kl}$) Final:**"); st.dataframe(discordance_matrix_d_electre.style.format("{:.4f}"))

    # Langkah 5: Menentukan Matriks Dominan Concordance (F) dan Discordance (G)
    # Hitung threshold c_bar
    sum_c_kl_electre = concordance_matrix_c_electre.values.sum() - np.diag(concordance_matrix_c_electre.values).sum() # Sum of non-diagonal
    den_c_bar_electre = n_alt_electre * (n_alt_electre - 1) if n_alt_electre > 1 else 1
    c_bar_electre = sum_c_kl_electre / den_c_bar_electre if den_c_bar_electre != 0 else 0.5
    
    F_matrix_electre = (concordance_matrix_c_electre >= c_bar_electre).astype(int)
    np.fill_diagonal(F_matrix_electre.values, 0) # Set diagonal to 0
    if streamlit_logging:
        st.markdown("**5a. Matriks Dominan Concordance (F):**")
        st.write(f"  Threshold Concordance ($\\underline{{c}}$ atau c_bar) = $\sum c_{{kl}} / (m(m-1))$ = {sum_c_kl_electre:.4f} / {den_c_bar_electre} = **{c_bar_electre:.4f}**")
        st.markdown("  **Matriks F Final ($f_{kl}=1$ jika $c_{kl} \ge\\underline{{c}}$, 0 jika sebaliknya):**"); st.dataframe(F_matrix_electre)

    # Hitung threshold d_bar
    sum_d_kl_electre = discordance_matrix_d_electre.values.sum() - np.diag(discordance_matrix_d_electre.values).sum() # Sum of non-diagonal
    den_d_bar_electre = n_alt_electre * (n_alt_electre - 1) if n_alt_electre > 1 else 1
    d_bar_electre = sum_d_kl_electre / den_d_bar_electre if den_d_bar_electre != 0 else 0.5

    # Sesuai PDF: g_kl = 1 jika d_kl >= d_bar
    G_matrix_electre = (discordance_matrix_d_electre >= d_bar_electre).astype(int)
    np.fill_diagonal(G_matrix_electre.values, 0) # Set diagonal to 0
    if streamlit_logging:
        st.markdown("**5b. Matriks Dominan Discordance (G):**")
        st.write(f"  Threshold Discordance ($\\underline{{d}}$ atau d_bar) = $\sum d_{{kl}} / (m(m-1))$ = {sum_d_kl_electre:.4f} / {den_d_bar_electre} = **{d_bar_electre:.4f}**")
        st.markdown("  **Matriks G Final ($g_{kl}=1$ jika $d_{kl} \ge \\underline{{d}}$, 0 jika sebaliknya):**"); st.dataframe(G_matrix_electre)

    # Langkah 6: Menentukan Aggregate Dominance Matrix (E)
    # e_kl = f_kl * g_kl
    E_matrix_electre = F_matrix_electre * G_matrix_electre
    if streamlit_logging: st.markdown("**6. Matriks Agregat Dominan ($E = F \\times G$):**"); st.dataframe(E_matrix_electre)

    # Langkah 7: Eliminasi Alternatif (atau Ranking)
    # Baris dalam matriks E yang memiliki jumlah e_kl=1 paling BANYAK adalah yang terbaik (atau paling sedikit dieliminasi).
    net_score_E_electre = E_matrix_electre.sum(axis=1) # Jumlahkan elemen 1 per baris
    df_result_electre = pd.DataFrame({'Net_Score_E': net_score_E_electre}, index=X_ij_electre.index)
    df_result_electre['Rank_ELECTRE'] = df_result_electre['Net_Score_E'].rank(method='min', ascending=False).astype(int) # Higher score is better
    df_result_sorted_electre = df_result_electre.sort_values(by='Rank_ELECTRE')

    if streamlit_logging:
        st.markdown("**7. Ranking Alternatif (berdasarkan jumlah dominasi $e_{kl}=1$ per baris di E - Semakin banyak, semakin baik):**")
        st.dataframe(df_result_sorted_electre)

    return df_result_sorted_electre, concordance_matrix_c_electre, discordance_matrix_d_electre, F_matrix_electre, G_matrix_electre, E_matrix_electre, c_bar_electre, d_bar_electre

# --- Aplikasi Streamlit Utama ---
def main():
    st.title("📊 Rekrutmen Karyawan")
    st.markdown("Implementasi metode VIKOR dan ELECTRE.")
    st.markdown("---")

    if 'df_kandidat_all' not in st.session_state:
        st.session_state['df_kandidat_all'] = create_empty_candidate_df_template()

    st.sidebar.header("⚙️ Input Data Kandidat")
    input_method = st.sidebar.radio("Metode Input:", ("Unggah File", "Input Manual"), key="input_method_radio")
    df_kandidat_input = None
    # ... (Logika Input File dan Input Manual SAMA seperti jawaban sebelumnya) ...
    if input_method == "Unggah File":
        st.sidebar.subheader("Unggah File Data Kandidat")
        uploaded_file = st.sidebar.file_uploader("Pilih file CSV atau Excel", type=["csv", "xlsx"], key="file_uploader_main")
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'): df_kandidat_input = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith('.xlsx'): df_kandidat_input = pd.read_excel(uploaded_file)
                st.session_state['df_kandidat_all'] = df_kandidat_input
                st.sidebar.success(f"File '{uploaded_file.name}' berhasil diunggah.")
            except Exception as e:
                st.sidebar.error(f"Error membaca file: {e}")
                df_kandidat_input = st.session_state['df_kandidat_all']
        else:
            df_kandidat_input = st.session_state['df_kandidat_all']
            if not df_kandidat_input.empty : st.sidebar.info("Menggunakan data yang ada di memori sesi.")
        st.sidebar.markdown("---")
        st.sidebar.subheader("Contoh Format Kolom File:")
        st.sidebar.code("- ID Kandidat, Nama Kandidat, Posisi Lamaran\n"
                        "- IST_IQ_Total, IST_StdDev_Subtes_IST\n"
                        "- MBTI_WS_E, MBTI_WS_I, ..., MBTI_WS_P\n"
                        "- Kraepelin_Kecepatan, ..., Kraepelin_Ketahanan\n"
                        "- DISC_Konsistensi_Score\n"
                        "- PAPI_Sum_Atribut_Positif, PAPI_Sum_Atribut_Kontekstual, PAPI_Sum_Atribut_Negatif", language="text")
    elif input_method == "Input Manual":
        st.sidebar.subheader("Input Data Kandidat Manual")
        if st.sidebar.button("Hapus Semua Data Manual", key="hapus_manual_btn"):
            st.session_state['df_kandidat_all'] = create_empty_candidate_df_template()
            st.sidebar.success("Data input manual dihapus.")
        with st.sidebar.form("form_input_kandidat_manual", clear_on_submit=True):
            # ... (Form input manual SAMA, pastikan semua kolom di create_empty_candidate_df_template() ada inputnya) ...
            st.write("Data Kandidat Baru:"); id_k = st.text_input("ID"); nama_k = st.text_input("Nama"); pos_k = st.text_input("Posisi Lamaran")
            st.markdown("**IST**"); ist_iq = st.number_input("IQ Total",0,200,110); ist_std = st.number_input("StdDev Subtes IST",0.0,5.0,1.0,0.1,"%.1f")
            st.markdown("**MBTI (WS)**"); m_e,m_i,m_s,m_n = st.columns(4); mb_e=m_e.number_input("Extovert",0,100,50);mb_i=m_i.number_input("Introvert",0,100,50);mb_s=m_s.number_input("Sensing",0,100,50);mb_n=m_n.number_input("iNtuition",0,100,50); m_t,m_f,m_j,m_p = st.columns(4); mb_t=m_t.number_input("Thinking",0,100,50);mb_f=m_f.number_input("Feeling",0,100,50);mb_j=m_j.number_input("Judging",0,100,50);mb_p=m_p.number_input("Perceiving",0,100,50);
            st.markdown("**Kraepelin**"); kr_kec,kr_ket,kr_tah = st.columns(3); kr_1=kr_kec.number_input("Kecepatan",1,5,3);kr_2=kr_ket.number_input("Ketelitian",1,5,3);kr_3=kr_tah.number_input("Daya Tahan",1,5,3); kr_kt,kr_kv=st.columns(2); kr_4=kr_kt.number_input("Kons. Tingkat",1,5,3);kr_5=kr_kv.number_input("Kons. Variasi",1,5,3)
            st.markdown("**DISC**"); disc_s = st.number_input("Konsistensi Score",0.0,1.0,0.7,0.01,"%.2f")
            st.markdown("**PAPI (Sum)**"); pa_pos,pa_kon,pa_neg=st.columns(3); pa_1=pa_pos.number_input("Sum Positif",0,100,60); pa_2=pa_kon.number_input("Sum Kontekstual",0,50,30); pa_3=pa_neg.number_input("Sum Negatif",0,50,20)
            submitted = st.form_submit_button("Tambah Kandidat")
            if submitted:
                if not id_k or not nama_k or not pos_k: st.error("ID, Nama, Posisi wajib diisi!")
                else:
                    new_data_row = {'ID Kandidat':id_k, 'Nama Kandidat':nama_k, 'Posisi Lamaran':pos_k,
                                'IST_IQ_Total':ist_iq, 'IST_StdDev_Subtes_IST':ist_std,
                                'MBTI_WS_E':mb_e, 'MBTI_WS_I':mb_i, 'MBTI_WS_S':mb_s, 'MBTI_WS_N':mb_n, 'MBTI_WS_T':mb_t, 'MBTI_WS_F':mb_f, 'MBTI_WS_J':mb_j, 'MBTI_WS_P':mb_p,
                                'Kraepelin_Kecepatan':kr_1, 'Kraepelin_Ketelitian':kr_2, 'Kraepelin_Daya_Tahan':kr_3, 'Kraepelin_Konsistensi_Tingkat':kr_4, 'Kraepelin_Konsistensi_Variasi':kr_5,
                                'DISC_Konsistensi_Score':disc_s, 'PAPI_Sum_Atribut_Positif':pa_1, 'PAPI_Sum_Atribut_Kontekstual':pa_2, 'PAPI_Sum_Atribut_Negatif':pa_3}
                    st.session_state['df_kandidat_all'] = pd.concat([st.session_state['df_kandidat_all'], pd.DataFrame([new_data_row])], ignore_index=True)
                    st.success(f"Kandidat '{nama_k}' ditambahkan.")
        df_kandidat_input = st.session_state['df_kandidat_all']


    st.subheader("Data Kandidat Tersedia:")
    if df_kandidat_input is not None and not df_kandidat_input.empty:
        st.dataframe(df_kandidat_input)
    else:
        st.info("Belum ada data kandidat. Silakan unggah file atau input manual di sidebar.")
        st.stop()

    st.header("Filter dan Analisis")
    # ... (Logika Filter Posisi sama) ...
    posisi_unik_main_area = df_kandidat_input['Posisi Lamaran'].unique() if 'Posisi Lamaran' in df_kandidat_input.columns and not df_kandidat_input.empty else []
    if not list(posisi_unik_main_area):
        st.warning("Kolom 'Posisi Lamaran' tidak ada atau kosong di data input.")
        st.stop()
    opsi_posisi_main_area = list(posisi_unik_main_area)
    posisi_terpilih_main_area = st.selectbox("Pilih Posisi Lamaran untuk Analisis:", opsi_posisi_main_area, key="posisi_analisis_main_area_sb")
    if not posisi_terpilih_main_area: st.stop()
    df_kandidat_filtered_main_area = df_kandidat_input[df_kandidat_input['Posisi Lamaran'] == posisi_terpilih_main_area].copy()
    if df_kandidat_filtered_main_area.empty:
        st.warning(f"Tidak ada kandidat untuk posisi '{posisi_terpilih_main_area}'.")
        st.stop()
    if 'ID Kandidat' in df_kandidat_filtered_main_area.columns:
        df_kandidat_filtered_main_area.set_index('ID Kandidat', inplace=True)
    else:
        st.error("Kolom 'ID Kandidat' tidak ada di data input.")
        st.stop()
    st.markdown(f"Menganalisis **{len(df_kandidat_filtered_main_area)}** kandidat untuk posisi: **{posisi_terpilih_main_area}**.")


    show_preprocess_details_main = st.checkbox("Tampilkan Detail Perhitungan Pra-Proses", value=False, key="show_praproses_main_cb_detail")
    df_processed_main, df_kriteria_mcdm_main, kolom_kriteria_main = preprocess_data_kandidat(
        df_kandidat_filtered_main_area.reset_index(), posisi_terpilih_main_area, streamlit_logging=show_preprocess_details_main
    )
    
    if not df_processed_main.empty and 'ID Kandidat' in df_processed_main.columns: df_processed_main.set_index('ID Kandidat', inplace=True)
    if not df_kriteria_mcdm_main.empty:
        if 'ID Kandidat' in df_kriteria_mcdm_main.columns: df_kriteria_mcdm_main.set_index('ID Kandidat', inplace=True)
        elif df_processed_main.index.name == 'ID Kandidat': df_kriteria_mcdm_main.index = df_processed_main.index
    else:
        df_kriteria_mcdm_main = pd.DataFrame(columns=kolom_kriteria_main if kolom_kriteria_main else ['Kriteria_IST'])

    if df_kriteria_mcdm_main.empty and not kolom_kriteria_main:
        st.error("Pra-proses gagal menghasilkan kriteria valid. Tidak dapat lanjut.")
        st.stop()
    elif not df_kriteria_mcdm_main.empty and kolom_kriteria_main:
        st.subheader("🔢 Data Kriteria Siap untuk MCDM (Hasil Pra-Proses):")
        kolom_tampil_praproses_main = ['Nama Kandidat'] + [col for col in kolom_kriteria_main if col in df_processed_main.columns]
        st.dataframe(df_processed_main[kolom_tampil_praproses_main])
    elif df_kriteria_mcdm_main.empty and kolom_kriteria_main:
         st.warning("Tidak ada data kriteria untuk posisi ini. Tidak dapat melakukan analisis MCDM.")
         # Lanjutkan untuk setup bobot, tapi MCDM tidak akan jalan


    st.sidebar.subheader("⚖️ Bobot & Jenis Kriteria MCDM")
    bobot_kriteria_input_main = {}
    kriteria_types_input_main = {}
    default_bobot_val_main = 1.0 / len(kolom_kriteria_main) if kolom_kriteria_main else 0.2
    
    for k_col_name_main in kolom_kriteria_main:
        col_label_main = k_col_name_main.replace('Kriteria_', '')
        bobot_kriteria_input_main[k_col_name_main] = st.sidebar.number_input(
            f"Bobot {col_label_main}", min_value=0.0, max_value=1.0, value=default_bobot_val_main, step=0.01, key=f"bobot_main_{k_col_name_main}"
        )
        kriteria_types_input_main[k_col_name_main] = st.sidebar.selectbox(
            f"Jenis {col_label_main} (VIKOR)", ('benefit', 'cost'), key=f"type_main_{k_col_name_main}"
        )

    total_bobot_main = sum(bobot_kriteria_input_main.values()) if bobot_kriteria_input_main else 0
    bobot_kriteria_array_main = np.array([bobot_kriteria_input_main[k] for k in kolom_kriteria_main]) if kolom_kriteria_main and bobot_kriteria_input_main else np.array([])
    kriteria_types_list_main = [kriteria_types_input_main[k] for k in kolom_kriteria_main] if kolom_kriteria_main and kriteria_types_input_main else []

    if not kolom_kriteria_main: st.sidebar.warning("Tidak ada kriteria untuk input bobot.")
    # ... (Logika validasi & normalisasi bobot SAMA) ...
    elif not np.isclose(total_bobot_main, 1.0):
        st.sidebar.warning(f"Total bobot {total_bobot_main:.2f} != 1.0.")
        if total_bobot_main > 0 and len(bobot_kriteria_array_main) > 0:
            bobot_kriteria_array_main = bobot_kriteria_array_main / total_bobot_main
            st.sidebar.info(f"Bobot dinormalisasi: {[f'{b:.2f}' for b in bobot_kriteria_array_main]}")
        elif len(bobot_kriteria_array_main) > 0 :
            st.sidebar.error("Total bobot nol. Menggunakan bobot default rata.")
            bobot_kriteria_array_main = np.full(len(kolom_kriteria_main), default_bobot_val_main)
    else: st.sidebar.success(f"Total bobot: {total_bobot_main:.2f}")


    st.markdown("---")
    tab_vikor_main, tab_electre_main, tab_perbandingan_main = st.tabs(["🥇 VIKOR (PDF)", "🥈 ELECTRE (PDF)", "🥉 Perbandingan"])
    show_mcdm_vikor_details_main = st.sidebar.checkbox("Detail Perhitungan VIKOR", value=False, key="show_vikor_log_main_cb_detail")
    show_mcdm_electre_details_main = st.sidebar.checkbox("Detail Perhitungan ELECTRE", value=False, key="show_electre_log_main_cb_detail")

    with tab_vikor_main:
        st.header("Metode VIKOR (Sesuai PDF)")
        v_vikor_main = st.slider("Parameter 'v' (VIKOR)", 0.0, 1.0, 0.5, 0.01, key="v_vikor_main_slider_pdf")
        if st.button("Hitung VIKOR (PDF)", key="btn_vikor_calc_main_pdf"):
            if not df_kriteria_mcdm_main.empty and \
               len(bobot_kriteria_array_main) == len(df_kriteria_mcdm_main.columns) and \
               len(kriteria_types_list_main) == len(df_kriteria_mcdm_main.columns):
                
                hasil_vikor_pdf, acc_adv_status_pdf = vikor_method(df_kriteria_mcdm_main, kriteria_types_list_main, bobot_kriteria_array_main, v_param=v_vikor_main, streamlit_logging=show_mcdm_vikor_details_main)
                
                if not hasil_vikor_pdf.empty:
                    hasil_vikor_display_pdf = df_processed_main[['Nama Kandidat']].join(hasil_vikor_pdf, how="right")
                    st.subheader("🏆 Peringkat Kandidat (VIKOR - PDF)")
                    st.dataframe(hasil_vikor_display_pdf[['Nama Kandidat', 'S', 'R', 'Q', 'Rank_VIKOR']].sort_values(by="Rank_VIKOR").style.format({'S':'{:.4f}', 'R':'{:.4f}', 'Q':'{:.4f}'}))
                    st.markdown(f"**Kondisi 'Acceptable Advantage':** {acc_adv_status_pdf}")
                    st.session_state['hasil_vikor'] = hasil_vikor_display_pdf # Simpan untuk perbandingan
                else: st.info("Tidak ada hasil VIKOR untuk ditampilkan.")
            else: st.error("Pastikan data kriteria, bobot, dan jenis kriteria valid dan sesuai jumlahnya.")

    with tab_electre_main:
        st.header("Metode ELECTRE (Sesuai PDF)")
        st.info("Threshold Concordance (c_bar) dan Discordance (d_bar) dihitung otomatis berdasarkan PDF.")
        if st.button("Hitung ELECTRE (PDF)", key="btn_electre_calc_main_pdf"):
            if not df_kriteria_mcdm_main.empty and len(bobot_kriteria_array_main) == len(df_kriteria_mcdm_main.columns):
                hasil_electre_pdf, C_pdf, D_pdf, F_pdf, G_pdf, E_pdf, c_bar_pdf, d_bar_pdf = electre_method(
                    df_kriteria_mcdm_main, bobot_kriteria_array_main, streamlit_logging=show_mcdm_electre_details_main
                )
                if not hasil_electre_pdf.empty:
                    hasil_electre_display_pdf = df_processed_main[['Nama Kandidat']].join(hasil_electre_pdf, how="right")
                    st.subheader("🏆 Peringkat Kandidat (ELECTRE - PDF)")
                    st.dataframe(hasil_electre_display_pdf[['Nama Kandidat', 'Net_Score_E', 'Rank_ELECTRE']].sort_values(by="Rank_ELECTRE"))
                    st.session_state['hasil_electre'] = hasil_electre_display_pdf # Simpan untuk perbandingan

                    with st.expander("Lihat Detail Matriks ELECTRE (sesuai PDF)"):
                        st.write(f"**Bobot Kriteria (w):** {dict(zip(df_kriteria_mcdm_main.columns, np.round(bobot_kriteria_array_main,3)))}")
                        st.write(f"**Threshold Concordance ($\\underline{{c}}$) dihitung:** {c_bar_pdf:.4f}")
                        st.write(f"**Threshold Discordance ($\\underline{{d}}$) dihitung:** {d_bar_pdf:.4f}")
                        st.subheader("Matriks Concordance ($c_{kl}$):"); st.dataframe(C_pdf.style.format("{:.4f}"))
                        st.subheader("Matriks Discordance ($d_{kl}$):"); st.dataframe(D_pdf.style.format("{:.4f}"))
                        st.subheader("Matriks Dominan Concordance (F):"); st.dataframe(F_pdf)
                        st.subheader("Matriks Dominan Discordance (G) (Sesuai PDF: 1 jika $d_{kl} \ge \\underline{{d}}$):"); st.dataframe(G_pdf)
                        st.subheader("Matriks Agregat Dominan ($E = F \\times G$):"); st.dataframe(E_pdf)
                else: st.info("Tidak ada hasil ELECTRE untuk ditampilkan.")
            else: st.error("Pastikan data kriteria dan bobot valid dan sesuai jumlahnya.")

    with tab_perbandingan_main:
        # ... (Logika perbandingan SAMA) ...
        st.header("Perbandingan Peringkat VIKOR vs ELECTRE")
        if 'hasil_vikor' in st.session_state and 'hasil_electre' in st.session_state and \
           isinstance(st.session_state['hasil_vikor'], pd.DataFrame) and not st.session_state['hasil_vikor'].empty and \
           isinstance(st.session_state['hasil_electre'], pd.DataFrame) and not st.session_state['hasil_electre'].empty and \
           'Nama Kandidat' in st.session_state['hasil_vikor'].columns and \
           'Nama Kandidat' in st.session_state['hasil_electre'].columns:
            
            df_vikor_ranks_main = st.session_state['hasil_vikor'][['Nama Kandidat', 'Rank_VIKOR']]
            df_electre_ranks_main = st.session_state['hasil_electre'][['Nama Kandidat', 'Rank_ELECTRE']]
            df_comparison_main = pd.merge(df_vikor_ranks_main, df_electre_ranks_main, on="Nama Kandidat", how="outer")
            st.dataframe(df_comparison_main.set_index('Nama Kandidat'))
        else:
            st.info("Hitung VIKOR dan ELECTRE dengan data valid untuk melihat perbandingan.")


    st.sidebar.markdown("---")
    st.sidebar.info("Aplikasi SPK - Implementasi PDF")

if __name__ == '__main__':
    main()