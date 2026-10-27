# Muat data mentah ke DuckDB, buat tabel users bersih, lalu jalankan view SQL.
# python3 -I scripts/02_load_duckdb.py  -> abtest.duckdb (tidak di-commit, dibuat ulang)
import pathlib, duckdb
ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "marketing_AB.csv"
DB = ROOT / "abtest.duckdb"
if DB.exists():
    DB.unlink()
con = duckdb.connect(str(DB))
con.execute(f"""
CREATE TABLE raw_visits AS
SELECT column0 AS src_row, "user id" AS user_id, "test group" AS grp, converted,
       "total ads" AS total_ads, "most ads day" AS most_ads_day, "most ads hour" AS most_ads_hour
FROM read_csv('{RAW.as_posix()}', header=true)
""")
# Cleaning: grup valid; user ganda -> ambil baris pertama (src_row terkecil)
con.execute("""
CREATE TABLE users AS
SELECT user_id, grp, CAST(converted AS INTEGER) AS converted, total_ads, most_ads_day, most_ads_hour
FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY src_row) AS rn
  FROM raw_visits
  WHERE grp IN ('ad', 'psa')
) WHERE rn = 1
ORDER BY user_id
""")
con.execute((ROOT / "sql" / "01_group_views.sql").read_text(encoding="utf-8"))
counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ["raw_visits", "users"]}
print(counts)
con.close()
