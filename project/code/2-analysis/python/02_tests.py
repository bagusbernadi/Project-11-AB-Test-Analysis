# Tahap 2: uji statistik, SRM, segmen, bootstrap, sensitivitas. Membaca tabel users dari DuckDB.
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np, pandas as pd, duckdb
from scipy import stats
from common import DB_PATH, RES_ANA, ALPHA, POWER, MDE, SEED, BOOT_REPS, P99_PERCENTILE
from abtest import two_prop_test, srm_test, sample_size_per_group

con = duckdb.connect(str(DB_PATH), read_only=True)
df = con.execute("""SELECT user_id, grp AS "group", converted, total_ads, most_ads_day, most_ads_hour
                    FROM users ORDER BY src_row""").df()
con.close()


def prop_test(d):
    g = d.groupby("group")["converted"].agg(["count", "sum"])
    r = two_prop_test(int(g.loc["ad", "sum"]), int(g.loc["ad", "count"]), int(g.loc["psa", "sum"]), int(g.loc["psa", "count"]), alpha=ALPHA)
    return dict(n_ad=int(g.loc["ad", "count"]), n_psa=int(g.loc["psa", "count"]), conv_ad=r["cr_a"], conv_psa=r["cr_b"],
                diff=r["diff"], ci_low=r["ci_low"], ci_high=r["ci_high"], rel_lift=r["rel_lift"], z=r["z"],
                p_value=r["p_value"], cohens_h=r["cohens_h"])


main = prop_test(df)
rows = [dict(uji="Z dua proporsi (ad vs psa)", **main)]

ad = df.loc[df.group == "ad", "converted"].to_numpy(); ps = df.loc[df.group == "psa", "converted"].to_numpy()
rng = np.random.default_rng(SEED)
bs = np.array([rng.choice(ad, ad.size).mean() - rng.choice(ps, ps.size).mean() for _ in range(BOOT_REPS)])
boot_lo, boot_hi = np.percentile(bs, [2.5, 97.5])
rows.append(dict(uji=f"Bootstrap {BOOT_REPS}x (selisih)", diff=main["diff"], ci_low=boot_lo, ci_high=boot_hi))

p0 = main["conv_psa"]; n_ad, n_psa = main["n_ad"], main["n_psa"]
se0 = np.sqrt(p0 * (1 - p0) * (1 / n_ad + 1 / n_psa))
pw = stats.norm.cdf(MDE / se0 - stats.norm.ppf(1 - ALPHA / 2))
n_req = sample_size_per_group(p0, MDE, alpha=ALPHA, power=POWER)
rows.append(dict(uji="Daya post-hoc (MDE 0,5 poin, n observasi)", diff=MDE, p_value=pw))
rows.append(dict(uji="Ukuran sampel per grup (Cohen h, 80%, alpha 0,05)", n_ad=n_req, n_psa=n_req))

srm = srm_test(n_ad, n_psa)
rows.append(dict(uji="SRM chi-square (50:50)", z=srm["chi2"], p_value=srm["p_value"], n_ad=n_ad, n_psa=n_psa))

order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
seg = pd.DataFrame([dict(segmen=d, **prop_test(sub)) for d, sub in df.groupby("most_ads_day")]).set_index("segmen").loc[order].reset_index()
seg["p_bonferroni"] = (seg["p_value"] * len(seg)).clip(upper=1.0)
seg.to_csv(RES_ANA / "segment_day.csv", index=False)

pd.DataFrame([dict(jam=h, **prop_test(sub)) for h, sub in df.groupby("most_ads_hour")]).sort_values("jam").to_csv(RES_ANA / "segment_hour.csv", index=False)

df["ads_q"] = pd.qcut(df["total_ads"].rank(method="first"), 4, labels=["Q1", "Q2", "Q3", "Q4"])
pd.DataFrame([dict(kuartil_total_ads=k, **prop_test(sub)) for k, sub in df.groupby("ads_q", observed=True)]).to_csv(RES_ANA / "segment_ads_quartile.csv", index=False)

p99 = df["total_ads"].quantile(P99_PERCENTILE)
sens = prop_test(df[df.total_ads <= p99])
rows.append(dict(uji=f"Sensitivitas: buang total_ads > P99 ({p99:.0f})", **sens))
pd.DataFrame(rows).to_csv(RES_ANA / "test_results.csv", index=False)

summ = df.groupby("group").agg(n=("converted", "size"), konversi=("converted", "sum"), conv_rate=("converted", "mean"),
                               median_total_ads=("total_ads", "median"), mean_total_ads=("total_ads", "mean")).reset_index()
summ.to_csv(RES_ANA / "group_summary.csv", index=False)
print("tahap 2 selesai:", len(rows), "uji utama")
