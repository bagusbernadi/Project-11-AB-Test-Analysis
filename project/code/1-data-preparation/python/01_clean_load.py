# Tahap 1: cek kualitas, cleaning dengan log, muat ke DuckDB, lalu buat view SQL.
# Jalankan dari mana saja: python3 -I project/code/1-data-preparation/python/01_clean_load.py
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import duckdb, pandas as pd
from common import RAW_CSV, DB_PATH, SQL_DIR, RES_PREP

if DB_PATH.exists():
    DB_PATH.unlink()
con = duckdb.connect(str(DB_PATH))
con.execute(f"""
CREATE TABLE raw_visits AS
SELECT column0 AS src_row, "user id" AS user_id, "test group" AS grp, converted,
       "total ads" AS total_ads, "most ads day" AS most_ads_day, "most ads hour" AS most_ads_hour
FROM read_csv('{RAW_CSV.as_posix()}', header=true)
""")
n_raw = con.execute("SELECT COUNT(*) FROM raw_visits").fetchone()[0]
con.execute("CREATE TABLE valid AS SELECT * FROM raw_visits WHERE grp IN ('ad', 'psa')")
n_valid = con.execute("SELECT COUNT(*) FROM valid").fetchone()[0]
# User ganda: ambil baris dengan src_row terkecil. Urutan tetap berdasarkan src_row (tie-breaker).
con.execute("""
CREATE TABLE users AS
SELECT user_id, grp, CAST(converted AS INTEGER) AS converted, total_ads, most_ads_day, most_ads_hour, src_row
FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY src_row) AS rn FROM valid)
WHERE rn = 1
ORDER BY src_row
""")
n_users = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
con.execute((SQL_DIR / "01_group_views.sql").read_text(encoding="utf-8"))
con.close()

log = pd.DataFrame([
    dict(step="baca", rows_in=n_raw, rows_out=n_raw, detail="kolom indeks dibuang"),
    dict(step="grup tidak valid", rows_in=n_raw, rows_out=n_valid, detail="grup selain ad/psa"),
    dict(step="user ganda (ambil kunjungan pertama)", rows_in=n_valid, rows_out=n_users, detail="user_id duplikat"),
])
log.to_csv(RES_PREP / "cleaning_log.csv", index=False)
print(f"raw {n_raw}, valid {n_valid}, users {n_users}")
