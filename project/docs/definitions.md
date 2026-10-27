# Definisi dan asumsi

## Metrik
- **Conversion rate (CR)**: jumlah `converted = True` dibagi jumlah user di grup.
- **Selisih**: CR ad dikurangi CR psa, dalam poin persentase.
- **Lift relatif**: selisih dibagi CR psa.

## Asumsi (berlabel)
- **A1 (aturan uji)**: alpha 0,05 dua arah, power 80%, MDE 0,5 poin persentase. Ditetapkan di rancangan sebelum melihat hasil.
- **A2 (user ganda)**: jika satu user_id muncul dua kali, kunjungan pertama dipakai. Pada data ini tidak ada user ganda.
- **A3 (independensi)**: setiap baris adalah satu user yang independen.
- **A4 (normal approximation)**: uji z dua proporsi valid karena jumlah konversi per grup besar (>5).
- **A5 (dampak)**: tambahan konversi per bulan memakai asumsi trafik sama seperti selama eksperimen. Diberi label *estimated*.
- **A6 (nilai pesanan)**: tidak ada di dataset. Revenue hanya ilustrasi, tidak dihitung.

## Uji sensitivitas
- **S1**: buang user dengan `total ads` di atas P99 (202). Hasil: selisih tetap signifikan (0,79 poin).
- **S2**: segmen per kuartil `total ads`. Efek terlihat hanya di kuartil teratas.
- **S3**: koreksi Bonferroni untuk uji per hari (7 uji): p disesuaikan = min(1, p × 7).

## Catatan
- `total ads` kemungkinan dipengaruhi oleh perlakuan (jumlah iklan yang dilihat). Dipakai untuk deskripsi segmen, bukan sebagai variabel kontrol kausal.
