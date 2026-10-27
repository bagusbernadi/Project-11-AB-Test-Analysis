# Analisis A/B: cleaning, uji, SRM, segmen, sensitivitas. Jalankan dari root repo.
# python3 -I scripts/01_analysis.py  (input: data/raw/marketing_AB.csv, tidak di-commit)
import pathlib, numpy as np, pandas as pd
from scipy import stats
ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "marketing_AB.csv"
OUT = ROOT / "outputs"; OUT.mkdir(exist_ok=True)
ALPHA, POWER, MDE = 0.05, 0.80, 0.005
SEED = 20260927

raw = pd.read_csv(RAW, index_col=0)
log = []
def note(step, n_in, n_out, detail):
    log.append(dict(step=step, rows_in=n_in, rows_out=n_out, detail=detail))

n0 = len(raw)
df = raw.rename(columns={"user id": "user_id", "test group": "group", "total ads": "total_ads",
                         "most ads day": "most_ads_day", "most ads hour": "most_ads_hour"})
df["converted"] = df["converted"].astype(int)
note("baca", n0, n0, "kolom indeks dibuang")
bad_grp = ~df["group"].isin(["ad", "psa"]); n1 = len(df)
df = df[~bad_grp]; note("grup tidak valid", n1, len(df), "grup selain ad/psa")
dup = df.duplicated("user_id", keep="first"); n2 = len(df)
df = df[~dup]; note("user ganda (ambil kunjungan pertama)", n2, len(df), "user_id duplikat")
df = df.reset_index(drop=True)
pd.DataFrame(log).to_csv(OUT / "cleaning_log.csv", index=False)

def prop_test(d):
    g = d.groupby("group")["converted"].agg(["count", "sum"])
    a, p = g.loc["ad"], g.loc["psa"]
    p1, p2 = a["sum"] / a["count"], p["sum"] / p["count"]
    pp = (a["sum"] + p["sum"]) / (a["count"] + p["count"])
    se0 = np.sqrt(pp * (1 - pp) * (1 / a["count"] + 1 / p["count"]))
    z = (p1 - p2) / se0; pval = 2 * stats.norm.sf(abs(z))
    se = np.sqrt(p1 * (1 - p1) / a["count"] + p2 * (1 - p2) / p["count"])
    diff = p1 - p2
    h = 2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p2))
    return dict(n_ad=int(a["count"]), n_psa=int(p["count"]), conv_ad=p1, conv_psa=p2,
                diff=diff, ci_low=diff - 1.96 * se, ci_high=diff + 1.96 * se,
                rel_lift=(diff / p2) if p2 > 0 else np.nan, z=z, p_value=pval, cohens_h=h)

main = prop_test(df)
rows = [dict(uji="Z dua proporsi (ad vs psa)", **{k: v for k, v in main.items()})]

# Bootstrap CI selisih (Q12)
rng = np.random.default_rng(SEED)
ad = df.loc[df.group == "ad", "converted"].to_numpy(); ps = df.loc[df.group == "psa", "converted"].to_numpy()
B = 2000
bs = np.array([rng.choice(ad, ad.size).mean() - rng.choice(ps, ps.size).mean() for _ in range(B)])
boot_lo, boot_hi = np.percentile(bs, [2.5, 97.5])

# Power dan ukuran sampel (Q7, Q11) untuk MDE 0.5 poin dari baseline PSA
p0 = main["conv_psa"]; p1t = p0 + MDE
h_ = 2 * np.arcsin(np.sqrt(p1t)) - 2 * np.arcsin(np.sqrt(p0))
n_req = int(np.ceil(((stats.norm.ppf(1 - ALPHA / 2) + stats.norm.ppf(POWER)) / h_) ** 2))
n_power_obs = (main["diff"] / np.sqrt(p0 * (1 - p0) * (1 / main["n_ad"] + 1 / main["n_psa"])))
pw = stats.norm.cdf(abs(MDE) / np.sqrt(p0*(1-p0)*(1/main["n_ad"]+1/main["n_psa"])) - stats.norm.ppf(1-ALPHA/2))
rows.append(dict(uji="Bootstrap 2000x (selisih)", diff=main["diff"], ci_low=boot_lo, ci_high=boot_hi))
rows.append(dict(uji="Daya post-hoc (MDE 0,5 poin, n observasi)", diff=MDE, p_value=pw))
rows.append(dict(uji="Ukuran sampel per grup (Cohen h, 80%, alpha 0,05)", n_ad=n_req, n_psa=n_req))

# SRM (Q2)
exp_split = np.array([0.5, 0.5]) * (main["n_ad"] + main["n_psa"])
chi = stats.chisquare([main["n_ad"], main["n_psa"]], exp_split)
rows.append(dict(uji="SRM chi-square (50:50)", z=chi.statistic, p_value=chi.pvalue,
                 n_ad=main["n_ad"], n_psa=main["n_psa"]))

# Segmen hari (Q9 tren, Q3 proxy) - uji per hari, koreksi Holm 7 hari
day_rows = []
order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
for dname, sub in df.groupby("most_ads_day"):
    r = prop_test(sub)
    day_rows.append(dict(segmen=dname, **r))
seg = pd.DataFrame(day_rows).set_index("segmen").loc[order].reset_index()
from statsmodels.stats.multitest import multipletests
seg["p_holm"] = multipletests(seg["p_value"], method="holm")[1]
seg.to_csv(OUT / "segment_day.csv", index=False)

# Segmen jam (Q9-Q10 tren waktu): 24 jam
hr_rows = []
for hh, sub in df.groupby("most_ads_hour"):
    r = prop_test(sub); hr_rows.append(dict(jam=hh, **r))
pd.DataFrame(hr_rows).sort_values("jam").to_csv(OUT / "segment_hour.csv", index=False)

# Interaksi frekuensi iklan (kuartil total_ads) - efek kebaruan / intensitas
df["ads_q"] = pd.qcut(df["total_ads"].rank(method="first"), 4, labels=["Q1","Q2","Q3","Q4"])
q_rows = []
for qn, sub in df.groupby("ads_q", observed=True):
    r = prop_test(sub); q_rows.append(dict(kuartil_total_ads=qn, **r))
pd.DataFrame(q_rows).to_csv(OUT / "segment_ads_quartile.csv", index=False)

# Tren harian: "most_ads_hour" bukan tanggal -> tidak ada kolom tanggal; tren tidak bisa dihitung (dicatat)

# Sensitivitas: buang outlier total_ads di atas P99
p99 = df["total_ads"].quantile(0.99)
sens = prop_test(df[df.total_ads <= p99])
rows.append(dict(uji=f"Sensitivitas: buang total_ads > P99 ({p99:.0f})", **sens))
# Sensitivitas: Mann-Whitney tidak relevan (biner). Sensitivitas: hanya kuartil bawah
rows_df = pd.DataFrame(rows)
rows_df.to_csv(OUT / "test_results.csv", index=False)

# Ringkasan per grup
summ = df.groupby("group").agg(n=("converted", "size"), konversi=("converted", "sum"),
                               conv_rate=("converted", "mean"), median_total_ads=("total_ads", "median"),
                               mean_total_ads=("total_ads", "mean")).reset_index()
summ.to_csv(OUT / "group_summary.csv", index=False)
print(pd.DataFrame(log).to_string(index=False))
print(summ.to_string(index=False)); print(rows_df.to_string(index=False))
print("sample_size", n_req, "power_at_MDE", round(pw, 3), "p99", p99)
print(seg[["segmen","n_ad","n_psa","conv_ad","conv_psa","diff","p_value"]].to_string(index=False))
