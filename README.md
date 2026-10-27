[← Back to portfolio](https://bagusbernadi.github.io/)

# Project 11: A/B Test Analysis

**Status: semua output rancangan selesai di branch `project-11-build` (belum digabung ke main).** Halaman project: [`design-and-report/index.html`](design-and-report/index.html). Notebook: [`project/results/3-presentation/analysis.ipynb`](project/results/3-presentation/analysis.ipynb). Dashboard: `project/code/3-presentation/streamlit/app.py`. Slide: [`project/results/3-presentation/presentasi.pptx`](project/results/3-presentation/presentasi.pptx). Lisensi dataset masih belum diverifikasi.

**Tujuan:** menguji apakah iklan (ad) menghasilkan conversion rate lebih tinggi daripada PSA (layanan masyarakat), dan apakah selisihnya cukup besar dan stabil untuk keputusan kampanye.

| | |
|---|---|
| Kategori | Marketing |
| Tingkat | Menengah |
| Data | Dataset publik `marketing_AB.csv` (588.101 user) |
| Tools | Python (pandas, SciPy), DuckDB + SQL, Streamlit |

## 1. Problem
Apakah menampilkan iklan menghasilkan conversion rate lebih tinggi daripada PSA, dan apakah selisihnya cukup besar dan stabil untuk keputusan kampanye?

## 2. Data
- Sumber: Kaggle, "Marketing A/B Testing" (faviovaz/marketing-ab-testing), file `marketing_AB.csv`. Lisensi dan sitasi belum diverifikasi.
- 588.101 baris, satu baris per user. Tidak ada user ganda dan tidak ada nilai hilang. Data mentah tidak di-commit.
- Grup: ad 564,577 user (96,0%), psa 23,524 user.

## 3. Analysis
- CR ad **2,55%**, CR psa **1,79%**. Selisih **0,77 poin** (95% CI 0,59 s.d. 0,94), p < 0,0001.
- **SRM gagal:** chi-square = 497,769, p < 0,0001. Pembagian grup tidak 50:50.
- Efek hanya terlihat di kuartil teratas total ads (selisih 3,01 poin, p < 0,0001). Tiga kuartil lainnya tidak berbeda.
- Cohen's h = 0.053 (kecil).

## 4. Recommendation
Jangan rollout dari angka ini saja. Pastikan dulu alokasi grup dengan pemilik data, lalu uji ulang dengan alokasi acak 50:50.

## 5. Impact
- *Estimated:* sekitar 7.692 konversi tambahan per 1 juta user (CI 95% dari hasil uji).
- Estimasi per bulan belum bisa dihitung karena dataset tidak punya data trafik per bulan. Revenue tidak dihitung karena tidak ada nilai pesanan.

## Batasan
- **SRM gagal**, dan mekanisme alokasi grup tidak diketahui. Ini batasan utama.
- Tidak ada kolom tanggal dan negara. Efek kebaruan dan segmen negara tidak bisa diuji.
- `total ads` mungkin dipengaruhi perlakuan. Dipakai untuk deskripsi, bukan kontrol kausal.
- Tidak ada nilai pembelian.
- Lisensi dan sitasi dataset belum diverifikasi (lihat `project/data/README.md`).

## Menjalankan
Dari root repo:
```bash
pip install -r project/requirements.txt
# letakkan marketing_AB.csv di project/data/raw/ (tidak di-commit)
sh project/code/run_all.sh          # semua tahap, notebook, slide, README, dan report
streamlit run project/code/3-presentation/streamlit/app.py   # dashboard
```

## Struktur repository
```
index.html                        pengalihan ke design-and-report/
README.md                         dokumen ini (dibuat ulang oleh 07_build_readme.py)
design-and-report/
  index.html                      halaman project (Design + Report v2)
  src/                            page_v1.html, report.css, report_lib.py, build_report.py
project/
  code/
    common.py                     path dan parameter
    run_all.sh
    1-data-preparation/python/    01_clean_load.py
    2-analysis/python/            02_tests.py, 03_crosscheck.py, abtest.py
    2-analysis/sql/               01_group_views.sql
    3-presentation/python/        04_one_sheet.py, 05_build_notebook.py, 06_slides.py, 07_build_readme.py
    3-presentation/streamlit/     app.py
  results/
    1-data-preparation/           cleaning_log.csv
    2-analysis/                   test_results.csv, group_summary.csv, segment_*.csv, crosscheck.csv
    3-presentation/               one_sheet.png/pdf, analysis.ipynb, presentasi.pptx
  data/                           raw/ (tidak di-commit), README.md
  docs/                           definitions.md, data_dictionary.md
  requirements.txt
```
