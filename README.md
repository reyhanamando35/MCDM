# Proyek Akhir MCDM (VIKOR & ELECTRE)

## Kelompok 4  
- Alexander Yofilio (C14220071)  
- Reyhan Amando (C14230082)  
- Marcel Hans (C14230099)  
- Yemima Chen (C14230157)

---

## Deskripsi Umum Proyek

Proyek ini merupakan aplikasi web berbasis **Streamlit** yang dirancang untuk membantu proses pengambilan keputusan dalam seleksi karyawan menggunakan pendekatan _Multiple Criteria Decision Making_ (MCDM). Aplikasi ini akan mengolah data hasil psikotes dari kandidat pelamar kerja, yang meliputi berbagai aspek psikologis dan kognitif.

Dua metode utama yang digunakan dalam sistem ini adalah:

- **VIKOR** (VIseKriterijumska Optimizacija I Kompromisno Resenje)  
  Metode kompromi yang digunakan untuk memilih alternatif terbaik berdasarkan kedekatannya dengan solusi ideal.

- **ELECTRE** (ELimination Et Choix Traduisant la REalité)  
  Metode outranking yang digunakan untuk membandingkan alternatif secara berpasangan berdasarkan dominasi preferensi.

---

## Tujuan

- Membantu perusahaan dalam menentukan kandidat terbaik secara objektif.
- Meningkatkan efisiensi dan akurasi dalam proses rekrutmen berbasis data.
- Memberikan fleksibilitas kepada pengguna untuk menyesuaikan bobot kriteria dan melakukan filter berdasarkan kebutuhan posisi kerja.

---

## Fitur Utama

- Upload data hasil psikotes dalam format spreadsheet (.csv).
- Penyesuaian bobot antar kriteria secara dinamis.
- Visualisasi hasil analisis menggunakan metode VIKOR dan ELECTRE.
- Filter kandidat berdasarkan posisi pekerjaan tertentu.

---

## Teknologi yang Digunakan

- **Python**  
- **Pandas & NumPy** (untuk pengolahan data)  
- **Streamlit** (untuk antarmuka pengguna)  
- **Matplotlib / Plotly** (untuk visualisasi)  
- **Scikit-learn** (untuk preprocessing tambahan)

---

## Catatan

Data yang digunakan bersifat simulasi dari hasil tes psikologis (MBTI, DISC, IST, PAPI Kostick, Kraepelin), dan aplikasi ini dapat disesuaikan untuk kebutuhan nyata dengan data sebenarnya.
