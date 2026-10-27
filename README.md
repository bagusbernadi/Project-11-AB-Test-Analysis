# Project 11: A/B Test Analysis

**Status: semua output rancangan selesai di branch `project-11-build` (belum digabung ke main).** Halaman project: [`design-and-report/index.html`](design-and-report/index.html). Notebook: [`notebooks/analysis.ipynb`](notebooks/analysis.ipynb). Dashboard: `dashboard/app.py`. Slide: [`slides/presentasi.pptx`](slides/presentasi.pptx). Lisensi dataset masih belum diverifikasi.

**Tujuan:** menguji apakah iklan (ad) menghasilkan conversion rate lebih tinggi daripada PSA (layanan masyarakat), dan apakah selisihnya cukup besar dan stabil untuk keputusan kampanye.

| | |
|---|---|
| Kategori | Marketing |
| Tingkat | Menengah |
| Data | Dataset publik `marketing_AB.csv` (588.101 user) |
| Tools | Python (pandas, SciPy, statsmodels) |

## Hasil
- CR ad 2,55% vs psa 1,79%. Selisih 0,77 poin (95% CI 0,60 s.d. 0,94), p < 0,0001.
- **SRM gagal:** ad 96%, psa 4%. Pembagian grup tidak 50:50, dan mekanismenya tidak diketahui.
- Efek hanya terlihat di kuartil teratas total ads. Tiga kuartil lainnya tidak berbeda.
- Rekomendasi: jangan rollout dari angka ini saja. Pastikan alokasi grup, lalu uji ulang dengan alokasi acak 50:50.

## Batasan
- SRM gagal, dan mekanisme alokasi tidak diketahui.
- Dataset tanpa tanggal dan negara. Efek kebaruan dan segmen negara tidak bisa diuji.
- `total ads` mungkin dipengaruhi perlakuan. Dipakai untuk deskripsi, bukan kontrol kausal.
- Tanpa nilai pembelian, dampak revenue tidak dihitung.
- Lisensi dan sitasi dataset belum diverifikasi. Halaman Kaggle tidak bisa diakses dari sandbox (lihat `data/README.md`).

## Menjalankan
```bash
pip install -r requirements.txt
# letakkan marketing_AB.csv di data/raw/ (tidak di-commit)
sh scripts/run_all.sh                 # semua pipeline, notebook, slide, dan report
streamlit run dashboard/app.py        # dashboard
```
Pipeline sudah dijalankan dua kali dan hasilnya identik (byte-for-byte).

## Struktur
```
index.html                        pengalihan ke design-and-report/
README.md
requirements.txt
design-and-report/
  index.html                      halaman project (Design + Report v2), dibangun ulang
  src/                            design_pane.html (pane Design), build_report.py,
                                  report_lib.py, report.css, base_head.html, page_v1.html (rancangan lama)
scripts/
  01_analysis.py                  cleaning, uji, SRM, segmen, sensitivitas
  02_load_duckdb.py               muat ke abtest.duckdb (tidak di-commit) dan view SQL
  03_crosscheck.py                cek silang SQL vs Python (Q14): 36 cek PASS
  04_one_sheet.py                 one-sheet PNG dan PDF
  05_build_notebook.py            bangun notebooks/analysis.ipynb (dieksekusi oleh run_all.sh)
  06_slides.py                    slides/presentasi.pptx (7 slide)
src/abtest.py                     modul uji A/B yang bisa dipakai ulang
notebooks/analysis.ipynb          analisis Q1–Q14 dengan output tersimpan
slides/presentasi.pptx            slide presentasi (opsional)
dashboard/app.py                  dashboard Streamlit (4 halaman, membaca outputs/)
  run_all.sh
outputs/                          CSV hasil, log cleaning, dan crosscheck.csv
sql/01_group_views.sql            view v_group_summary dan v_day_summary
docs/definitions.md               definisi, asumsi berlabel, uji sensitivitas
docs/data_dictionary.md           kamus data (mentah, bersih, view, file hasil)
data/README.md                    sumber, versi, dan lisensi (belum diverifikasi)
```
