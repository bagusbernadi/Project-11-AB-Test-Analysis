"""Modul uji A/B yang bisa dipakai ulang: cek SRM, uji z dua proporsi, CI, Cohen's h, ukuran sampel, bootstrap.

Contoh:
    from src.abtest import two_prop_test
    r = two_prop_test(x_a=14423, n_a=564577, x_b=420, n_b=23524)
"""
import math
import numpy as np
from scipy import stats


def srm_test(n_a, n_b, ratio=(0.5, 0.5)):
    """Chi-square: apakah pembagian grup sesuai rasio rencana (SRM)."""
    total = n_a + n_b
    exp = [ratio[0] * total, ratio[1] * total]
    res = stats.chisquare([n_a, n_b], exp)
    return dict(chi2=float(res.statistic), p_value=float(res.pvalue), srm=bool(res.pvalue < 0.05))


def two_prop_test(x_a, n_a, x_b, n_b, alpha=0.05):
    """Uji z dua proporsi (dua arah), CI selisih (Wald), relative lift, Cohen's h."""
    p_a, p_b = x_a / n_a, x_b / n_b
    pooled = (x_a + x_b) / (n_a + n_b)
    se0 = math.sqrt(pooled * (1 - pooled) * (1 / n_a + 1 / n_b))
    z = (p_a - p_b) / se0
    p_value = 2 * stats.norm.sf(abs(z))
    se = math.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)
    crit = stats.norm.ppf(1 - alpha / 2)
    diff = p_a - p_b
    return dict(cr_a=p_a, cr_b=p_b, diff=diff, ci_low=diff - crit * se, ci_high=diff + crit * se,
                rel_lift=diff / p_b if p_b > 0 else float("nan"), z=z, p_value=p_value,
                cohens_h=cohens_h(p_a, p_b))


def cohens_h(p1, p2):
    return 2 * math.asin(math.sqrt(p1)) - 2 * math.asin(math.sqrt(p2))


def sample_size_per_group(p_base, mde, alpha=0.05, power=0.80):
    """Ukuran sampel per grup untuk mendeteksi selisih mde (proporsi, bukan poin persen) dengan Cohen's h."""
    h = abs(cohens_h(p_base + mde, p_base))
    z_a = stats.norm.ppf(1 - alpha / 2)
    z_b = stats.norm.ppf(power)
    return int(math.ceil(((z_a + z_b) / h) ** 2))


def bootstrap_diff(x_a, n_a, x_b, n_b, reps=2000, seed=20260927):
    """Bootstrap percentile CI untuk selisih proporsi."""
    rng = np.random.default_rng(seed)
    a = np.r_[np.ones(x_a), np.zeros(n_a - x_a)]
    b = np.r_[np.ones(x_b), np.zeros(n_b - x_b)]
    d = np.array([rng.choice(a, a.size).mean() - rng.choice(b, b.size).mean() for _ in range(reps)])
    lo, hi = np.percentile(d, [2.5, 97.5])
    return dict(ci_low=float(lo), ci_high=float(hi))
