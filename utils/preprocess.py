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
    papi_pos = ['P_C', 'P_F', 'P_W', 'P_N', 'P_G', 'P_A', 'P_P', 'P_I', 'P_V']
    papi_neg = ['P_S', 'P_X', 'P_E', 'P_K', 'P_L', 'P_T']

    # Ambil huruf dari kolom 'PAPI context' di job_filter_row (misal 'R')
    context_letter = job_filter_row['PAPI context'].strip().upper()
    context_col = f'P_{context_letter}'

    # Pastikan kolom tersebut memang ada di data
    if context_col not in data.columns:
        raise ValueError(f"Kolom kontekstual {context_col} tidak ditemukan di data kandidat.")

    # Hitung skor
    daya_kerja = data[papi_pos].sum(axis=1) + data[context_col]
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

    # Normalisasi min-max per kolom
    disc_minmax = (data[disc_cols] - data[disc_cols].min()) / (data[disc_cols].max() - data[disc_cols].min())

    disc_weights = [
        job_filter_row['D'],
        job_filter_row['I_D'],
        job_filter_row['S'],
        job_filter_row['C']
    ]
    result['DISC'] = disc_minmax.dot(disc_weights)
    
    return result