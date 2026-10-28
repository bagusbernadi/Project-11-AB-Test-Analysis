# Data

- **Sumber:** Kaggle, "Marketing A/B Testing" (faviovaz/marketing-ab-testing), file `marketing_AB.csv`.
- **Versi:** 1. **Tanggal akses:** 28 Oktober 2026 (dikonfirmasi saat berkas diarsipkan di repo DataCenter; akses pertama 23 Oktober 2026).
- **Lisensi:** [CC0: Public Domain](https://creativecommons.org/publicdomain/zero/1.0/) (label di halaman Kaggle, dicek 28 Oktober 2026). Label diberikan uploader (Favio Vázquez); halaman Kaggle tidak menyebut asal data awal, jadi tidak ada sitasi lain. Cantumkan tautan Kaggle sebagai sumber.
- **Cara mendapatkan:** unduh dari Kaggle, ekstrak, lalu simpan sebagai `project/data/raw/marketing_AB.csv`. File ini tidak di-commit.
- **Isi:** 588.101 baris, satu baris per user. Kolom: `user id`, `test group` (ad / psa), `converted` (True/False), `total ads`, `most ads day`, `most ads hour`. Kolom indeks pertama tidak dipakai.
- **Tidak ada kolom negara dan tidak ada kolom tanggal.** Karena itu pertanyaan negara tidak bisa dijawab dari dataset ini, dan tren harian diganti segmen hari dalam seminggu.
