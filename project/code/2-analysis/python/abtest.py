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


def wilson_ci(x, n, alpha=0.05):
    """Interval Wilson untuk satu proporsi."""
    z = stats.norm.ppf(1 - alpha / 2)
    p = x / n
    denom = 1 + z ** 2 / n
    center = (p + z ** 2 / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / denom
    return center - half, center + half


def two_prop_test(x_a, n_a, x_b, n_b, alpha=0.05):
    """Uji z dua proporsi (dua arah), CI selisih (Newcombe, berbasis Wilson), relative lift, Cohen's h."""
    p_a, p_b = x_a / n_a, x_b / n_b
    pooled = (x_a + x_b) / (n_a + n_b)
    se0 = math.sqrt(pooled * (1 - pooled) * (1 / n_a + 1 / n_b))
    z = (p_a - p_b) / se0
    p_value = 2 * stats.norm.sf(abs(z))
    l_a, u_a = wilson_ci(x_a, n_a, alpha)
    l_b, u_b = wilson_ci(x_b, n_b, alpha)
    diff = p_a - p_b
    ci_low = diff - math.sqrt((p_a - l_a) ** 2 + (u_b - p_b) ** 2)
    ci_high = diff + math.sqrt((u_a - p_a) ** 2 + (p_b - l_b) ** 2)
    return dict(cr_a=p_a, cr_b=p_b, diff=diff, ci_low=ci_low, ci_high=ci_high,
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
