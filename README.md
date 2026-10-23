[← Back to portfolio](https://bagusbernadi.github.io/)

# Project 11: A/B Test Analysis

**Status: Design (rancangan).** Halaman rancangan ada di [`index.html`](index.html). Analisis, dashboard, dan angka hasil belum dikerjakan, sehingga bagian Analysis, Recommendation, dan Impact di bawah masih kosong.

**Tujuan:** membangun analisis eksperimen dan dashboard yang menguji apakah halaman web baru (B) benar-benar menghasilkan konversi lebih tinggi daripada halaman lama (A), sehingga keputusan rollout diambil berdasarkan bukti.

| | |
|---|---|
| Kategori | E-commerce / retail |
| Tingkat | Mudah |
| Data | Dataset publik A/B testing halaman web (Kaggle) |
| Tools | DuckDB + SQL, Python (pandas, SciPy, statsmodels), Streamlit + Plotly |

## 1. Problem

**Pertanyaan utama:** Apakah halaman baru (B) benar-benar menghasilkan conversion rate lebih tinggi daripada halaman lama (A), dan apakah perbedaannya cukup besar untuk di-rollout?

Rancangan memecahnya menjadi 14 pertanyaan (9 Utama, 4 Pendukung, 1 Tambahan) dalam tema data dan randomisasi, hasil utama, segmen dan waktu, keputusan dan dampak, serta validitas. Daftar lengkap ada di bagian 2 halaman rancangan.

## 2. Data

- Sumber data: [here](https://www.kaggle.com/datasets/mostafaelmehy/ab-data) (Versi: 1, Tanggal akses: 23 Oktober 2026)
- Ukuran (perkiraan, **belum diverifikasi**): ±294 ribu baris kunjungan, 5 kolom, ±3 minggu, ditambah file negara.
- Aturan uji ditetapkan sebelum melihat hasil: alpha 0,05 dua arah, power 80%, MDE 0,5 poin.
- Rencana tabel: `visits`, `users`, `daily_summary`, `test_results`.
- Lisensi dan sitasi: dicek di halaman sumber sebelum project dipublikasikan.
- Data mentah tidak di-commit ke repository.

## 3. Analysis

Belum dikerjakan. Rencana langkah (12 langkah, tahap A sampai D) ada di bagian 6 halaman rancangan. Semua angka nanti dihitung dari data dengan SQL dan dicek silang.

Hipotesis yang akan diuji (belum terbukti):
1. Halaman baru tidak meningkatkan conversion rate secara bermakna.
2. Pembagian grup seimbang.
3. Hasil tidak berbeda antar negara.
4. Tidak ada efek kebaruan yang kuat.
5. Baris bermasalah <2% dan tidak mengubah kesimpulan.

## 4. Recommendation

Belum dikerjakan. Output yang direncanakan: keputusan rollout halaman baru.

## 5. Impact

Belum dikerjakan. Rumus yang akan dipakai (semua hasil diberi label `estimated`):

```
Tambahan konversi per bulan = selisih conversion rate × user per bulan (dengan rentang confidence interval)
```

## Batasan yang sudah diketahui

- Signifikan tidak sama dengan penting.
- Analisis memakai data penuh, tidak mengintip di tengah.
- Tidak ada nilai pembelian di dataset.

## Struktur repository

```
index.html   Halaman rancangan project (bisa dibuka di browser atau lewat GitHub Pages)
README.md    Dokumen ini
```

Folder `docs/`, `data/`, `scripts/`, `sql/`, `notebooks/`, `dashboard/`, dan `outputs/` ditambahkan saat pengerjaan dimulai.
