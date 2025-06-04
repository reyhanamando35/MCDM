# ========== IMPLEMENTASI ELECTRE ========== #

import numpy as np
import pandas as pd
from utils.preprocess import prep_dm

def calculate_vikor(data, criteria, weights):
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
    decision_matrix, alternatives = prep_dm(data, criteria)
    
    # 2. Tentukan nilai ideal positif dan negatif
    f_star = np.max(decision_matrix, axis=0)  # Nilai terbaik setiap kriteria
    f_minus = np.min(decision_matrix, axis=0)  # Nilai terburuk setiap kriteria
    
    # 3. Hitung nilai S dan R untuk setiap alternatif
    S = np.zeros(len(alternatives))
    R = np.zeros(len(alternatives))
    
    for i in range(len(alternatives)):
        s_values = []
        r_values = []
        
        for j in range(len(criteria)):
            if f_star[j] != f_minus[j]:  # Hindari pembagian dengan 0
                normalized_diff = (f_star[j] - decision_matrix[i, j]) / (f_star[j] - f_minus[j])
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