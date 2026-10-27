# Cek silang: hasil SQL (DuckDB) vs hasil Python (outputs/*.csv). Menjawab Q14.
# Menulis outputs/crosscheck.csv; gagal (exit 1) jika ada selisih di atas toleransi.
import pathlib, sys, duckdb, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
TOL = 1e-9
con = duckdb.connect(str(ROOT / "abtest.duckdb"), read_only=True)
rows = []
def chk(nama, sql_val, py_val):
    ok = abs(float(sql_val) - float(py_val)) <= TOL
    rows.append(dict(cek=nama, sql=float(sql_val), python=float(py_val), hasil="PASS" if ok else "FAIL"))

g_py = pd.read_csv(OUT / "group_summary.csv").set_index("group")
for grp, n, k, cr, med in con.execute(
        "SELECT grp, n, konversi, conv_rate, median_total_ads FROM v_group_summary ORDER BY grp").fetchall():
    chk(f"n {grp}", n, g_py.loc[grp, "n"])
    chk(f"konversi {grp}", k, g_py.loc[grp, "konversi"])
    chk(f"conv_rate {grp}", cr, g_py.loc[grp, "conv_rate"])
    chk(f"median total ads {grp}", med, g_py.loc[grp, "median_total_ads"])

d_py = pd.read_csv(OUT / "segment_day.csv").set_index("segmen")
for seg, na, npsa, cra, crp in con.execute(
        "SELECT segmen, n_ad, n_psa, cr_ad, cr_psa FROM v_day_summary ORDER BY segmen").fetchall():
    chk(f"n_ad {seg}", na, d_py.loc[seg, "n_ad"])
    chk(f"n_psa {seg}", npsa, d_py.loc[seg, "n_psa"])
    chk(f"cr_ad {seg}", cra, d_py.loc[seg, "conv_ad"])
    chk(f"cr_psa {seg}", crp, d_py.loc[seg, "conv_psa"])

df = pd.DataFrame(rows)
df.to_csv(OUT / "crosscheck.csv", index=False)
n_fail = int((df.hasil == "FAIL").sum())
print(f"cek silang: {len(df)} cek, PASS {int((df.hasil == 'PASS').sum())}, FAIL {n_fail}")
sys.exit(1 if n_fail else 0)
