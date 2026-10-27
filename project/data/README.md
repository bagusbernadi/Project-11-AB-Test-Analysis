# Data

- **Sumber:** Kaggle, "Marketing A/B Testing" (faviovaz/marketing-ab-testing), file `marketing_AB.csv`.
- **Versi:** 1. **Tanggal akses:** 23 Oktober 2026 (dari rancangan, belum dikonfirmasi ulang).
- **Lisensi dan sitasi:** belum diverifikasi. Halaman Kaggle tidak bisa diakses dari sandbox. Paket pihak ketiga `libuplift` (dokumentasi readthedocs) memuat dataset ini dari Kaggle dan menyebut sumbernya, tetapi tidak menyatakan lisensi maupun sitasi. Sebelum dipublikasikan, cek lisensi di halaman Kaggle lalu tulis sitasi di sini.
- **Cara mendapatkan:** unduh dari Kaggle, ekstrak, lalu simpan sebagai `project/data/raw/marketing_AB.csv`. File ini tidak di-commit.
- **Isi:** 588.101 baris, satu baris per user. Kolom: `user id`, `test group` (ad / psa), `converted` (True/False), `total ads`, `most ads day`, `most ads hour`. Kolom indeks pertama tidak dipakai.
- **Tidak ada kolom negara dan tidak ada kolom tanggal.** Karena itu pertanyaan negara tidak bisa dijawab dari dataset ini, dan tren harian diganti segmen hari dalam seminggu.
