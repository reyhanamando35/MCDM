# ========== IMPLEMENTASI VIKOR ========== #

import numpy as np
import pandas as pd
from utils.preprocess import prep_dm, agg_to_5

def calc_vikor(data, criteria):
    """
    Implementasi metode VIKOR
    
    Parameters:
    - data: DataFrame kandidat
    - criteria: list nama kolom kriteria
    
    Returns:
    - DataFrame hasil ranking VIKOR
    """
    
    # 1. Siapkan matriks keputusan
    dm, alt = prep_dm(data, criteria)
    
    # 2. Tentukan nilai ideal positif dan negatif
    f_star = np.max(dm, axis=0)
    f_minus = np.min(dm, axis=0)

    # 3. Normalisasi matriks keputusan
    n_rows, n_cols = dm.shape
    norm_matx = np.zeros((n_rows, n_cols))
    
    for i in range(n_rows):
        for j in range(n_cols):
            if f_star[j] != f_minus[j]:  # Hindari pembagian dengan 0
                norm_matx[i, j] = (f_star[j] - dm[i, j]) / (f_star[j] - f_minus[j])
            else:
                norm_matx[i, j] = 0

    # 4. Matriks terbobot (semua bobot = 0.2)
    weights = np.array([0.2, 0.2, 0.2, 0.2, 0.2])
    weighted = norm_matx * weights
    
    # 5. Hitung nilai S dan R untuk setiap alternatif
    S = np.zeros(n_rows)
    R = np.zeros(n_rows)

    for i in range(n_rows):
        # S_i = sum dari semua F_ij untuk alternatif i
        S[i] = np.sum(weighted[i, :])
        
        # R_i = max dari semua F_ij untuk alternatif i
        R[i] = np.max(weighted[i, :])
    
    # 4. Hitung nilai Q (VIKOR index)
    S_star = np.min(S)
    S_minus = np.max(S)
    R_star = np.min(R)
    R_minus = np.max(R)
    
    v = 0.5  # Parameter strategy (biasanya 0.5)
    Q = np.zeros(n_rows)
    
    for i in range(n_rows):
        s_val = 0
        r_val = 0
        
        if (S_minus - S_star) != 0:
            s_val = v * ((S[i] - S_minus) / (S_star - S_minus))
        
        if (R_minus - R_star) != 0:
            r_val = (1 - v) * ((R[i] - R_minus) / (R_star - R_minus))
        
        Q[i] = s_val + r_val
    
    # 5. Buat DataFrame hasil
    results = pd.DataFrame({
        'Nama': alt,
        'Skor VIKOR': Q 
    })
    
    # 6. Ranking berdasarkan Q value
    results = results.sort_values('Skor VIKOR', ascending=True) # Nilai Q semakin rendah semakin baik
    results['Ranking'] = range(1, len(alt) + 1)
    
    return results[['Nama', 'Skor VIKOR', 'Ranking']]

# ========== FUNGSI WRAPPER UNTUK STREAMLIT ========== #

def run_vikor(data, job_filter_row):
    """
    Wrapper untuk menjalankan analisis VIKOR
    """
    # Agregasi data ke 5 kriteria
    aggregated_data = agg_to_5(data, job_filter_row)
    aggregated_data = aggregated_data.rename(columns={'Nama': 'NAMA'})
    
    # Definisi kriteria dan bobot
    criteria = ['IST', 'PAPI', 'MBTI', 'Kraepelin', 'DISC']
    
    # Jalankan VIKOR
    results = calc_vikor(aggregated_data, criteria)
    
    return results