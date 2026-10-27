# Kamus data

Sumber: `project/data/raw/marketing_AB.csv` (tidak di-commit). Database: `project/abtest.duckdb` (dibuat ulang oleh `project/code/1-data-preparation/python/01_clean_load.py`).

## Data mentah (`raw_visits`)
| Kolom asli | Kolom DuckDB | Tipe | Arti |
|---|---|---|---|
| (kolom indeks tanpa nama) | `src_row` | BIGINT | nomor baris sumber, dipakai sebagai tie-breaker |
| `user id` | `user_id` | BIGINT | ID user |
| `test group` | `grp` | VARCHAR | `ad` (iklan) atau `psa` (layanan masyarakat) |
| `converted` | `converted` | BOOLEAN | `True` jika user melakukan konversi |
| `total ads` | `total_ads` | BIGINT | jumlah iklan yang dilihat user (bisa dipengaruhi perlakuan) |
| `most ads day` | `most_ads_day` | VARCHAR | hari dalam seminggu dengan iklan terbanyak |
| `most ads hour` | `most_ads_hour` | BIGINT | jam dengan iklan terbanyak (0–23) |

## Data bersih (`users`)
1 baris = 1 user. Sama seperti data mentah, dengan `converted` sebagai 0/1 dan tanpa `src_row`.
- Baris dengan `grp` selain `ad`/`psa` dibuang (0 baris).
- User ganda: ambil baris dengan `src_row` terkecil (0 baris ganda).
- Hasil: 588.101 baris.

## View (`project/code/2-analysis/sql/01_group_views.sql`)
- `v_group_summary`: n, konversi, conv_rate, median dan rata-rata total_ads per grup.
- `v_day_summary`: n_ad, n_psa, cr_ad, cr_psa per hari dalam seminggu.

## File hasil (`project/results/`)
| File | Isi |
|---|---|
| `cleaning_log.csv` | jumlah baris per langkah cleaning |
| `group_summary.csv` | ringkasan per grup |
| `segment_day.csv` | uji per hari, dengan p_bonferroni |
| `segment_hour.csv` | ringkasan per jam |
| `segment_ads_quartile.csv` | uji per kuartil total ads |
| `test_results.csv` | semua uji statistik dan sensitivitas |
| `crosscheck.csv` | hasil cek silang SQL vs Python |
| `one_sheet.png`, `one_sheet.pdf` | one-sheet |
