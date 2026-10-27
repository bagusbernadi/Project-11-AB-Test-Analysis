"""Path dan parameter untuk seluruh project. Diimpor oleh semua skrip (sys.path = project/code)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]                      # folder project/
RAW_CSV = ROOT / "data" / "raw" / "marketing_AB.csv"            # tidak di-commit
DB_PATH = ROOT / "abtest.duckdb"                                # dibuat ulang, tidak di-commit
SQL_DIR = ROOT / "code" / "2-analysis" / "sql"
RES_PREP = ROOT / "results" / "1-data-preparation"
RES_ANA = ROOT / "results" / "2-analysis"
RES_PRES = ROOT / "results" / "3-presentation"
for _d in (RES_PREP, RES_ANA, RES_PRES):
    _d.mkdir(parents=True, exist_ok=True)

ALPHA = 0.05
POWER = 0.80
MDE = 0.005          # 0,5 poin persentase (proporsi)
SEED = 20260927
BOOT_REPS = 2000
P99_PERCENTILE = 0.99


def result(name):
    """Cari file hasil di folder tahap mana pun."""
    for d in (RES_PREP, RES_ANA, RES_PRES):
        p = d / name
        if p.exists():
            return p
    raise FileNotFoundError(name)
