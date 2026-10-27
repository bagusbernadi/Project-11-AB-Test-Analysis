# Tahap 3: menulis README.md (root repo) dengan angka dari results/. Angka tidak diketik manual.
import sys, pathlib, csv
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from common import RES_ANA, ROOT
ROOT_REPO = ROOT.parent

tr = {r["uji"]: r for r in csv.DictReader(open(RES_ANA / "test_results.csv", encoding="utf-8"))}
grp = {r["group"]: r for r in csv.DictReader(open(RES_ANA / "group_summary.csv", encoding="utf-8"))}
qt = list(csv.DictReader(open(RES_ANA / "segment_ads_quartile.csv", encoding="utf-8")))
srm = tr["SRM chi-square (50:50)"]
Z = tr["Z dua proporsi (ad vs psa)"]
p_txt = lambda v: "< 0,0001" if float(v) < 0.0001 else f"{float(v):.4f}".replace(".", ",")
pc = lambda v, d=2: f"{float(v) * 100:.{d}f}".replace(".", ",") + "%"
pt = lambda v: f"{float(v) * 100:.2f}".replace(".", ",")
n_ad, n_psa = int(grp["ad"]["n"]), int(grp["psa"]["n"])
share_ad = n_ad / (n_ad + n_psa)
est = f"{float(Z['diff']) * 1e6:,.0f}".replace(",", ".")
q4 = qt[3]

readme = f"""[← Back to portfolio](https://bagusbernadi.github.io/)

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
- Grup: ad {n_ad:,} user ({pc(share_ad, 1)}), psa {n_psa:,} user.

## 3. Analysis
- CR ad **{pc(grp['ad']['conv_rate'])}**, CR psa **{pc(grp['psa']['conv_rate'])}**. Selisih **{pt(Z['diff'])} poin** (95% CI {pt(Z['ci_low'])} s.d. {pt(Z['ci_high'])}), p {p_txt(Z['p_value'])}.
- **SRM gagal:** chi-square = {float(srm['z']):,.0f}, p {p_txt(srm['p_value'])}. Pembagian grup tidak 50:50.
- Efek hanya terlihat di kuartil teratas total ads (selisih {pt(q4['diff'])} poin, p {p_txt(q4['p_value'])}). Tiga kuartil lainnya tidak berbeda.
- Cohen's h = {float(Z['cohens_h']):.3f} (kecil).

## 4. Recommendation
Jangan rollout dari angka ini saja. Pastikan dulu alokasi grup dengan pemilik data, lalu uji ulang dengan alokasi acak 50:50.

## 5. Impact
- *Estimated:* sekitar {est} konversi tambahan per 1 juta user (CI 95% dari hasil uji).
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
"""
(ROOT_REPO / "README.md").write_text(readme, encoding="utf-8")
print("ditulis:", ROOT_REPO / "README.md")
