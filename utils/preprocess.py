# ========== FUNGSI AGREGASI 47 KOLOM KE 5 KRITERIA ========== #
import pandas as pd

def prep_dm(data, criteria):
    """
    Menyiapkan decision matrix & daftar alternatif.
    """
    matrix = data[criteria].values
    alternatives = data['NAMA'].tolist()
    return matrix, alternatives

def agg_to_5(data, job_filter_row):
    result = pd.DataFrame()
    result["Nama"] = data["NAMA"]

    # ===== 1. IST =====
    ist_cols = ['SE', 'WA', 'AN', 'GE', 'ME', 'RA', 'ZR', 'FA', 'WU']
    iq_col = 'IQ'

    # Hindari mengubah data asli
    temp = data.copy()

    # Hitung standar deviasi dari 9 sub-kriteria IST
    temp['std_dev'] = temp[ist_cols].std(axis=1)

    # Ambil threshold (persentil ke-75)
    threshold = temp['std_dev'].quantile(0.75)

    # Jika std rendah -> pakai nilai IQ, kalau tinggi -> IQ * 0.9 (kena penalti)
    result['IST'] = temp[iq_col].where(temp['std_dev'] < threshold, temp[iq_col] * 0.9)

    # ===== 2. PAPI Kostick =====
    papi_pos = ['P_A', 'P_C', 'P_E', 'P_F', 'P_G', 'P_H', 'P_I', 'P_L', 'P_N']
    papi_neg = ['P_B', 'P_D', 'P_J', 'P_K', 'P_M', 'P_O']
    papi_contextual = ['P_B', 'P_O', 'P_R', 'P_D', 'P_Z']

    daya_kerja = data[papi_pos + papi_contextual].sum(axis=1)
    risiko = data[papi_neg].sum(axis=1)
    result['PAPI'] = daya_kerja - risiko

    # ===== 3. MBTI =====
    mbti_code = ['M_I', 'M_E', 'M_S', 'M_N', 'M_T', 'M_F', 'M_J', 'M_P']
    mbti_selected = []

    for col in ['M', 'B', 'T', 'I_M']:
        mbti_selected.append(f"M_{job_filter_row[col]}")

    result['MBTI'] = data[mbti_selected].sum(axis=1)

    # ===== 4. Kraepelin =====
    kraepelin_cols = ['K_C', 'K_T', 'K_A1', 'K_A2', 'K_H']
    kraepelin_weights = [0.25, 0.25, 0.125, 0.125, 0.25]

    kraepelin_agg = data[kraepelin_cols].dot(kraepelin_weights)
    result['Kraepelin'] = kraepelin_agg

    # ===== 5. DISC =====
    disc_cols = ['D_D', 'D_I', 'D_S', 'D_C']
    disc_minmax = data[disc_cols].apply(lambda x: (x - x.min()) / (9 - 0))  # normalisasi manual

    disc_weights = [
        job_filter_row['D'],
        job_filter_row['I_D'],
        job_filter_row['S'],
        job_filter_row['C']
    ]
    result['DISC'] = disc_minmax.dot(disc_weights)

    return result