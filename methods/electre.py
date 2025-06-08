# ========== IMPLEMENTASI ELECTRE ========== #

import numpy as np
import pandas as pd
from utils.preprocess import prep_dm, agg_to_5

def norm(matrix):
    """
    Normalisasi matriks keputusan
    """
    normalized = np.zeros_like(matrix, dtype=float)
    
    for j in range(matrix.shape[1]):
        col = matrix[:, j]
        normalized[:, j] = col / np.sqrt(np.sum(col**2))
    
    return normalized

def calc_electre(data, criteria):
    """
    Implementasi metode ELECTRE
    
    Parameters:
    - data: DataFrame kandidat
    - criteria: list nama kolom kriteria
    
    Returns:
    - DataFrame hasil ranking ELECTRE
    """
    
    # 1. Siapkan matriks keputusan
    dm, alt = prep_dm(data, criteria)
    
    # 2. Normalisasi matriks
    norm_matx = norm(dm)
    
    # 3. Matriks terbobot (semua bobot = 0.2)
    weights = np.array([0.2, 0.2, 0.2, 0.2, 0.2])
    weighted = norm_matx * weights
    
    n = len(alt)
    
    # 4. Hitung matriks concordance
    concordance = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            if i != j:
                concordance_set = []
                for k in range(len(criteria)):
                    if weighted[i, k] >= weighted[j, k]:
                        concordance_set.append(weights[k])
                concordance[i, j] = np.sum(concordance_set)
    
    # 5. Hitung matriks discordance
    discordance = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            if i != j:
                # Hitung maksimum selisih pada kriteria discordance
                max_diff_discord = 0
                for k in range(len(criteria)):
                    # Discordance terjadi ketika weighted[j,k] > weighted[i,k]
                    if weighted[j, k] > weighted[i, k]:
                        diff = abs(weighted[j, k] - weighted[i, k])
                        if diff > max_diff_discord:
                            max_diff_discord = diff
                
                # Hitung maksimum selisih dari seluruh kriteria
                max_diff_all = 0
                for k in range(len(criteria)):
                    diff = abs(weighted[i, k] - weighted[j, k])
                    if diff > max_diff_all:
                        max_diff_all = diff
                
                if max_diff_all != 0:
                    discordance[i, j] = max_diff_discord / max_diff_all
    
    # 6. Hitung threshold concordance dan discordance
                    
    # Threshold concordance: rata-rata dari elemen non-diagonal matrix concordance
    concordance_sum = 0
    count = 0
    for i in range(n):
        for j in range(n):
            if i != j:
                concordance_sum += concordance[i, j]
                count += 1
    threshold_c = concordance_sum / count
    
    # Threshold discordance: rata-rata dari elemen non-diagonal matrix discordance
    discordance_sum = 0
    count = 0
    for i in range(n):
        for j in range(n):
            if i != j:
                discordance_sum += discordance[i, j]
                count += 1
    threshold_d = discordance_sum / count
    
     # 7. Matriks dominan concordance dan discordance
    con_dom = (concordance >= threshold_c).astype(int)
    discon_dom = (discordance <= threshold_d).astype(int)
    
    # Set diagonal menjadi 0 (alternatif tidak membandingkan dengan dirinya sendiri)
    np.fill_diagonal(con_dom, 0)
    np.fill_diagonal(discon_dom, 0)
    
    # 8. Aggregate dominant matrix
    aggregate = con_dom & discon_dom
    
    # 9. Hitung skor ELECTRE
    electre_scores = np.sum(aggregate, axis=1)
    
    # 10. Buat DataFrame hasil
    results = pd.DataFrame({
        'Nama': alt,
        'Skor ELECTRE': electre_scores
    })
    
    # 11. Ranking berdasarkan skor (descending)
    results = results.sort_values('Skor ELECTRE', ascending=False)
    results['Ranking'] = range(1, len(alt) + 1)
    
    return results[['Nama', 'Skor ELECTRE', 'Ranking']]

# ========== FUNGSI WRAPPER UNTUK STREAMLIT ========== #

def run_electre(data, job_filter_row):
    """
    Wrapper untuk menjalankan analisis ELECTRE
    """
    # Agregasi data ke 5 kriteria
    aggregated_data = agg_to_5(data, job_filter_row)
    aggregated_data = aggregated_data.rename(columns={'Nama': 'NAMA'})
    
    # Definisi kriteria dan bobot
    criteria = ['IST', 'PAPI', 'MBTI', 'Kraepelin', 'DISC']
    
    # Jalankan ELECTRE
    results = calc_electre(aggregated_data, criteria)
    
    return results