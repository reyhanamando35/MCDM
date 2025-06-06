# ========== IMPLEMENTASI VIKOR ========== #

import numpy as np
import pandas as pd
from utils.preprocess import prep_dm, agg_to_5

def calc_vikor(data, criteria, weights):
    """
    Implementasi metode VIKOR
    
    Parameters:
    - data: DataFrame kandidat
    - criteria: list nama kolom kriteria
    - weights: array bobot kriteria (harus sum = 1)
    
    Returns:
    - DataFrame hasil ranking VIKOR
    """
    
    # 1. Siapkan matriks keputusan
    dm, alternatives = prep_dm(data, criteria)
    
    # 2. Tentukan nilai ideal positif dan negatif
    f_star = np.max(dm, axis=0)  # Nilai terbaik setiap kriteria
    f_minus = np.min(dm, axis=0)  # Nilai terburuk setiap kriteria

    # norm_matx = 

    weights = np.array([0.2, 0.2, 0.2, 0.2, 0.2])
    weighted = norm_matx * weights
    
    # 3. Hitung nilai S dan R untuk setiap alternatif
    S = np.zeros(len(alternatives))
    R = np.zeros(len(alternatives))
    
    for i in range(len(alternatives)):
        s_values = []
        r_values = []
        
        for j in range(len(criteria)):
            if f_star[j] != f_minus[j]:  # Hindari pembagian dengan 0
                normalized_diff = (f_star[j] - dm[i, j]) / (f_star[j] - f_minus[j])
                weighted_diff = weights[j] * normalized_diff
                
                s_values.append(weighted_diff)
                r_values.append(weighted_diff)
        
        S[i] = np.sum(s_values)
        R[i] = np.max(r_values)
    
    # 4. Hitung nilai Q (VIKOR index)
    S_star = np.min(S)
    S_minus = np.max(S)
    R_star = np.min(R)
    R_minus = np.max(R)
    
    v = 0.5  # Parameter strategy (biasanya 0.5)
    Q = np.zeros(len(alternatives))
    
    for i in range(len(alternatives)):
        if (S_minus - S_star) != 0 and (R_minus - R_star) != 0:
            Q[i] = v * (S[i] - S_star) / (S_minus - S_star) + (1 - v) * (R[i] - R_star) / (R_minus - R_star)
    
    # 5. Buat DataFrame hasil
    results = pd.DataFrame({
        'Nama': alternatives,
        'S_Value': S,
        'R_Value': R,
        'Q_Value': Q,
        'Skor VIKOR': 1 - Q  # Skor VIKOR (semakin tinggi semakin baik)
    })
    
    # 6. Ranking berdasarkan Q value (ascending)
    results = results.sort_values('Q_Value')
    results['Ranking'] = range(1, len(alternatives) + 1)
    
    return results[['Nama', 'Skor VIKOR', 'Ranking']]

def run_vikor(data, job_filter_row):
    """
    Wrapper untuk menjalankan analisis VIKOR
    """
    # Agregasi data ke 5 kriteria
    aggregated_data = agg_to_5(data)
    
    # Definisi kriteria dan bobot
    criteria_columns = ['IST_Score', 'MBTI_Score', 'PAPI_Score', 'DISC_Score', 'Kraepelin_Score']
    weights = np.array([0.25, 0.2, 0.2, 0.2, 0.15])  # Bobot bisa disesuaikan
    benefit_criteria = [0, 1, 2, 3, 4]  # Semua kriteria adalah benefit
    
    # Jalankan VIKOR
    results = calc_vikor(aggregated_data, criteria_columns, weights, benefit_criteria)
    
    return results