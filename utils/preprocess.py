# ========== FUNGSI AGREGASI 47 KOLOM KE 5 KRITERIA ========== #
import pandas as pd

def prep_dm(data, criteria):
    """
    Menyiapkan decision matrix & daftar alternatif.
    """
    matrix = data[criteria].values
    alternatives = data['NAMA'].tolist()
    return matrix, alternatives

def agg_to_5(data):
    """
    Mengagregasi 47 kolom menjadi 5 kriteria utama
    """
    aggregated = pd.DataFrame()
    aggregated['Nama'] = data['NAMA']
    
    # 1. IST Score (dari kolom IST)
    ist_cols = ['SE', 'WA', 'AN', 'GE', 'ME', 'RA', 'ZR', 'FA', 'WU', 'IQ']
    ist_cols_exist = [col for col in ist_cols if col in data.columns]
    if ist_cols_exist:
        aggregated['IST_Score'] = data[ist_cols_exist].mean(axis=1)
    
    # 2. MBTI Score (dari kolom M_*)
    mbti_cols = [col for col in data.columns if col.startswith('M_')]
    if mbti_cols:
        aggregated['MBTI_Score'] = data[mbti_cols].mean(axis=1)
    
    # 3. PAPI Score (dari kolom P_*)
    papi_cols = [col for col in data.columns if col.startswith('P_')]
    if papi_cols:
        aggregated['PAPI_Score'] = data[papi_cols].mean(axis=1)
    
    # 4. DISC Score (dari kolom D_*)
    disc_cols = [col for col in data.columns if col.startswith('D_')]
    if disc_cols:
        aggregated['DISC_Score'] = data[disc_cols].mean(axis=1)
    
    # 5. Kraepelin Score (dari kolom K_*)
    kraep_cols = [col for col in data.columns if col.startswith('K_')]
    if kraep_cols:
        aggregated['Kraepelin_Score'] = data[kraep_cols].mean(axis=1)
    
    return aggregated