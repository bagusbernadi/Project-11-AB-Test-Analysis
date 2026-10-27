# Project 11: A/B Test Analysis

**Status: sedang dikerjakan di branch `project-11-build`.** Belum digabung ke main. Revisi halaman Design dan Report v2 belum selesai, dashboard, notebook, dan one-sheet belum dibuat.

**Tujuan:** menguji apakah iklan (ad) menghasilkan conversion rate lebih tinggi dibanding PSA (public service announcement), dan apakah perbedaannya cukup besar untuk keputusan rollout.

## Hasil awal (dari `outputs/test_results.csv`)
- CR ad 2,55% vs psa 1,79%. Selisih 0,77 poin (95% CI 0,60 s.d. 0,94). p < 0,001.
- **SRM gagal:** user dibagi 564.577 (ad) dan 23.524 (psa), jauh dari 50:50. Hipotesis pembagian seimbang ditolak. Perbandingan ini perlu kehati-hatian.
- Efek hanya terlihat di kuartil teratas `total ads` (CR 8,3% vs 5,3%). Kuartil lain tidak berbeda.
- Daya cukup untuk MDE 0,5 poin. Ukuran sampel yang dibutuhkan 6.237 per grup.

## Data
Dataset publik `marketing_AB.csv` (588.101 baris). Tidak ada kolom negara dan tanggal. Lihat `data/README.md`.

## Menjalankan
```bash
pip install -r requirements.txt
# letakkan marketing_AB.csv di data/raw/
python3 -I scripts/01_analysis.py
```

## Struktur
```
scripts/01_analysis.py      cleaning, uji, SRM, segmen, sensitivitas
outputs/                    CSV hasil dan log
docs/definitions.md         definisi, asumsi berlabel, uji sensitivitas
data/README.md              sumber dan lisensi (belum diverifikasi)
```
