# ========== IMPLEMENTASI ELECTRE ========== #

import numpy as np
import pandas as pd
from utils.preprocess import prep_dm

def norm(matrix):
    """
    Normalisasi matriks keputusan
    """
    normalized = np.zeros_like(matrix, dtype=float)
    
    for j in range(matrix.shape[1]):
        col = matrix[:, j]
        normalized[:, j] = col / np.sqrt(np.sum(col**2))
    
    return normalized

def calculate_electre(data, criteria_columns, weights, benefit_criteria=None, threshold_c=0.6, threshold_d=0.8):
    """
    Implementasi metode ELECTRE
    
    Parameters:
    - data: DataFrame kandidat
    - criteria_columns: list nama kolom kriteria
    - weights: array bobot kriteria
    - benefit_criteria: list index kriteria benefit
    - threshold_c: ambang batas concordance
    - threshold_d: ambang batas discordance
    
    Returns:
    - DataFrame hasil ranking ELECTRE
    """
    
    # 1. Siapkan matriks keputusan
    decision_matrix, alternatives = prepare_decision_matrix(data, criteria_columns)
    
    # 2. Normalisasi matriks
    normalized_matrix = normalize_matrix(decision_matrix, benefit_criteria)
    
    # 3. Matriks terbobot
    weighted_matrix = normalized_matrix * weights
    
    n_alternatives = len(alternatives)
    
    # 4. Hitung matriks concordance
    concordance_matrix = np.zeros((n_alternatives, n_alternatives))
    
    for i in range(n_alternatives):
        for j in range(n_alternatives):
            if i != j:
                concordance_set = []
                for k in range(len(criteria_columns)):
                    if weighted_matrix[i, k] >= weighted_matrix[j, k]:
                        concordance_set.append(weights[k])
                concordance_matrix[i, j] = np.sum(concordance_set)
    
    # 5. Hitung matriks discordance
    discordance_matrix = np.zeros((n_alternatives, n_alternatives))
    
    for i in range(n_alternatives):
        for j in range(n_alternatives):
            if i != j:
                max_diff = 0
                max_range = 0
                
                for k in range(len(criteria_columns)):
                    diff = abs(weighted_matrix[i, k] - weighted_matrix[j, k])
                    if diff > max_diff:
                        max_diff = diff
                    
                    col_range = np.max(weighted_matrix[:, k]) - np.min(weighted_matrix[:, k])
                    if col_range > max_range:
                        max_range = col_range
                
                if max_range != 0:
                    discordance_matrix[i, j] = max_diff / max_range
    
    # 6. Matriks dominan concordance dan discordance
    concordance_dominant = concordance_matrix >= threshold_c
    discordance_dominant = discordance_matrix <= threshold_d
    
    # 7. Aggregate dominant matrix
    aggregate_dominant = concordance_dominant & discordance_dominant
    
    # 8. Hitung skor ELECTRE (jumlah dominasi)
    electre_scores = np.sum(aggregate_dominant, axis=1)
    
    # 9. Buat DataFrame hasil
    results = pd.DataFrame({
        'Nama': alternatives,
        'Skor ELECTRE': electre_scores
    })
    
    # 10. Ranking berdasarkan skor (descending)
    results = results.sort_values('Skor ELECTRE', ascending=False)
    results['Ranking'] = range(1, len(alternatives) + 1)
    
    return results[['Nama', 'Skor ELECTRE', 'Ranking']]

# ========== FUNGSI WRAPPER UNTUK STREAMLIT ========== #

def run_vikor_analysis(data, job_position=None):
    """
    Wrapper untuk menjalankan analisis VIKOR
    """
    # Agregasi data ke 5 kriteria
    aggregated_data = aggregate_to_5_criteria(data)
    
    # Definisi kriteria dan bobot
    criteria_columns = ['IST_Score', 'MBTI_Score', 'PAPI_Score', 'DISC_Score', 'Kraepelin_Score']
    weights = np.array([0.25, 0.2, 0.2, 0.2, 0.15])  # Bobot bisa disesuaikan
    benefit_criteria = [0, 1, 2, 3, 4]  # Semua kriteria adalah benefit
    
    # Jalankan VIKOR
    results = calculate_vikor(aggregated_data, criteria_columns, weights, benefit_criteria)
    
    return results

def run_electre_analysis(data, job_position=None):
    """
    Wrapper untuk menjalankan analisis ELECTRE
    """
    # Agregasi data ke 5 kriteria
    aggregated_data = aggregate_to_5_criteria(data)
    
    # Definisi kriteria dan bobot
    criteria_columns = ['IST_Score', 'MBTI_Score', 'PAPI_Score', 'DISC_Score', 'Kraepelin_Score']
    weights = np.array([0.25, 0.2, 0.2, 0.2, 0.15])  # Bobot bisa disesuaikan
    benefit_criteria = [0, 1, 2, 3, 4]  # Semua kriteria adalah benefit
    
    # Jalankan ELECTRE
    results = calculate_electre(aggregated_data, criteria_columns, weights, benefit_criteria)
    
    return results