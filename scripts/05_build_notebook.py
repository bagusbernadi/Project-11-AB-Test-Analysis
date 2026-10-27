# Membangun notebooks/analysis.ipynb (sel kode + penjelasan). Lalu dijalankan dengan nbconvert agar output tersimpan.
import pathlib, nbformat as nbf
ROOT = pathlib.Path(__file__).resolve().parents[1]
nb = nbf.v4.new_notebook()
C, M = nbf.v4.new_code_cell, nbf.v4.new_markdown_cell
nb.cells = [
M("# Project 11: Analisis A/B test iklan vs PSA\n\n"
  "Notebook ini menjawab Q1–Q14 dari rancangan dengan dataset `marketing_AB.csv`. "
  "Angka dihitung ulang dengan modul `src/abtest.py` dan dicocokkan dengan `outputs/`.\n\n"
  "Aturan uji ditetapkan sebelum melihat hasil: alpha 0,05 dua arah, power 80%, MDE 0,5 poin."),
M("## Q1 · Kualitas data\nGrup valid, tidak ada user ganda, tidak ada nilai hilang."),
C("import sys, pandas as pd\nsys.path.insert(0, '..')\nfrom src.abtest import two_prop_test, srm_test, sample_size_per_group, cohens_h\n"
  "raw = pd.read_csv('../data/raw/marketing_AB.csv', index_col=0)\n"
  "print('baris:', len(raw), '| grup:', raw['test group'].value_counts().to_dict())\n"
  "print('user ganda:', raw['user id'].duplicated().sum(), '| nilai hilang:', int(raw.isna().sum().sum()))\n"
  "print(pd.read_csv('../outputs/cleaning_log.csv').to_string(index=False))"),
M("## Q2 · SRM (pembagian grup 50:50)\nChi-square terhadap rasio rencana. Jika gagal, kesimpulan kausal perlu batasan."),
C("g = raw.groupby('test group')['converted'].agg(['count', 'sum'])\n"
  "n_ad, n_psa = int(g.loc['ad', 'count']), int(g.loc['psa', 'count'])\n"
  "srm = srm_test(n_ad, n_psa)\n"
  "print(f\"ad {n_ad} ({n_ad/(n_ad+n_psa):.1%}), psa {n_psa} ({n_psa/(n_ad+n_psa):.1%})\")\n"
  "print('chi2 =', round(srm['chi2'], 1), '| p =', srm['p_value'], '| SRM gagal:', srm['srm'])"),
M("## Q4–Q6 · Conversion rate, uji z, dan CI\nUji z dua proporsi dan CI selisih 95%."),
C("x_ad, x_psa = int(g.loc['ad', 'sum']), int(g.loc['psa', 'sum'])\n"
  "r = two_prop_test(x_ad, n_ad, x_psa, n_psa)\n"
  "print(f\"CR ad {r['cr_a']:.2%}, CR psa {r['cr_b']:.2%}\")\n"
  "print(f\"selisih {r['diff']*100:.2f} poin, CI 95% {r['ci_low']*100:.2f} s.d. {r['ci_high']*100:.2f}\")\n"
  "print(f\"lift relatif {r['rel_lift']:.1%}, z = {r['z']:.2f}, p = {r['p_value']:.2e}\")"),
M("## Q7 · Cohen's h dan power\nCohen's h kecil. Daya untuk MDE 0,5 poin dari baseline PSA dihitung dengan ukuran sampel."),
C("print('Cohen h =', round(r['cohens_h'], 4))\n"
  "print('ukuran sampel per grup untuk MDE 0,5 poin:', sample_size_per_group(r['cr_b'], 0.005))"),
M("## Q8–Q9 · Segmen hari dan intensitas iklan\nSegmen hari memakai `most ads day`. Kuartil memakai `total ads`."),
C("import numpy as np\nday = raw.assign(grp=raw['test group']).groupby(['most ads day', 'test group'])['converted'].agg(['count', 'sum']).unstack()\n"
  "rows = []\nfor d in day.index:\n    a = two_prop_test(int(day.loc[d, ('sum','ad')]), int(day.loc[d, ('count','ad')]), int(day.loc[d, ('sum','psa')]), int(day.loc[d, ('count','psa')]))\n"
  "    rows.append((d, round(a['diff']*100, 2), f\"{a['p_value']:.2e}\"))\n"
  "pd.DataFrame(rows, columns=['hari', 'selisih (poin)', 'p (sebelum Holm)'])"),
C("q = raw.assign(kuartil=pd.qcut(raw['total ads'].rank(method='first'), 4, labels=['Q1','Q2','Q3','Q4']))\n"
  "rows = []\nfor k, sub in q.groupby('kuartil', observed=True):\n"
  "    gg = sub.groupby('test group')['converted'].agg(['count', 'sum'])\n"
  "    a = two_prop_test(int(gg.loc['ad','sum']), int(gg.loc['ad','count']), int(gg.loc['psa','sum']), int(gg.loc['psa','count']))\n"
  "    rows.append((k, round(a['diff']*100, 2), f\"{a['p_value']:.2e}\"))\n"
  "pd.DataFrame(rows, columns=['kuartil total ads', 'selisih (poin)', 'p'])"),
M("## Q12–Q13 · Bootstrap dan sensitivitas\nBootstrap 2.000 resample. Sensitivitas: buang user dengan total ads di atas P99."),
C("from src.abtest import bootstrap_diff\nprint('bootstrap:', bootstrap_diff(x_ad, n_ad, x_psa, n_psa, reps=2000))\n"
  "p99 = raw['total ads'].quantile(0.99)\nsub = raw[raw['total ads'] <= p99]\n"
  "gs = sub.groupby('test group')['converted'].agg(['count','sum'])\n"
  "s = two_prop_test(int(gs.loc['ad','sum']), int(gs.loc['ad','count']), int(gs.loc['psa','sum']), int(gs.loc['psa','count']))\n"
  "print(f'P99 = {p99}; selisih tanpa outlier = {s[\"diff\"]*100:.2f} poin, p = {s[\"p_value\"]:.2e}')"),
M("## Q10 · Estimasi dampak (estimated)\nTambahan konversi per 1 juta user. Estimasi per bulan tidak bisa dihitung karena tidak ada data trafik per bulan."),
C("print(f\"estimated: {r['diff']*1e6:,.0f} konversi per 1 juta user (CI {r['ci_low']*1e6:,.0f} s.d. {r['ci_high']*1e6:,.0f})\".replace(',', '.'))"),
M("## Q14 · Cek silang SQL vs Python\nHasil DuckDB dibandingkan dengan Python. Tabel lengkap di `outputs/crosscheck.csv`."),
C("import duckdb\nf = pd.read_csv('../outputs/crosscheck.csv')\nprint(f['hasil'].value_counts().to_dict())\n"
  "con = duckdb.connect('../abtest.duckdb', read_only=True)\nprint(con.sql('SELECT * FROM v_group_summary').df())"),
M("## Kesimpulan\n"
  "- Iklan menghasilkan conversion rate lebih tinggi dibanding PSA (selisih 0,77 poin, signifikan).\n"
  "- Pembagian grup gagal SRM (96% vs 4%). Kesimpulan kausal perlu batasan.\n"
  "- Efek hanya terlihat di kuartil total ads teratas.\n"
  "- Belum rollout berdasarkan angka ini. Pastikan alokasi grup, lalu uji ulang dengan 50:50.\n\n"
  "Lihat [Report](../design-and-report/index.html) dan [README](../README.md) untuk ringkasan lengkap."),
]
for i, c in enumerate(nb.cells, 1):
    c.id = f"cell-{i:02d}"  # id tetap agar byte-identik antar jalan
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
path = ROOT / "notebooks" / "analysis.ipynb"
nbf.write(nb, path)
print("ditulis:", path)

