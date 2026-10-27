"""Dashboard Project 11 (Streamlit). Membaca results/2-analysis/*.csv; tidak menghitung ulang.
Jalankan dari folder project/: streamlit run code/3-presentation/streamlit/app.py
"""
import sys, pathlib
import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from common import RES_ANA
OUT = RES_ANA
NAMA = {"Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu", "Thursday": "Kamis",
        "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"}

st.set_page_config(page_title="Project 11: A/B Test", layout="wide")
grp = pd.read_csv(OUT / "group_summary.csv").set_index("group")
seg = pd.read_csv(OUT / "segment_day.csv")
qt = pd.read_csv(OUT / "segment_ads_quartile.csv")
tr = pd.read_csv(OUT / "test_results.csv").set_index("uji")
cc = pd.read_csv(OUT / "crosscheck.csv")
Z = tr.loc["Z dua proporsi (ad vs psa)"]
SRM = tr.loc["SRM chi-square (50:50)"]

page = st.sidebar.radio("Halaman", ["Ringkasan Hasil", "Kualitas Eksperimen", "Segmen & Waktu", "Kalkulator Ukuran Sampel"])

if page == "Ringkasan Hasil":
    st.title("Apakah iklan menaikkan konversi?")
    st.subheader("Keputusan: belum rollout berdasarkan angka ini")
    st.write("Iklan menghasilkan konversi lebih tinggi, tetapi pembagian grup gagal SRM dan efek hanya terlihat di kuartil total ads teratas.")
    c1, c2, c3 = st.columns(3)
    c1.metric("CR ad", f"{grp.loc['ad', 'conv_rate']*100:.2f}%")
    c2.metric("CR psa", f"{grp.loc['psa', 'conv_rate']*100:.2f}%")
    c3.metric("Selisih (poin)", f"{Z['diff']*100:.2f}", f"CI 95% {Z.ci_low*100:.2f} s.d. {Z.ci_high*100:.2f}")
    st.caption(f"p-value {Z.p_value:.2e}. Cohen's h = {Z.cohens_h:.3f} (kecil). Angka dari results/2-analysis/test_results.csv.")
    est = f"{Z['diff']*1e6:,.0f}".replace(",", ".")
    st.info(f"Estimasi: sekitar {est} konversi tambahan per 1 juta user (estimated, tanpa data trafik per bulan).")

elif page == "Kualitas Eksperimen":
    st.title("Kualitas eksperimen")
    st.metric("Chi-square SRM (50:50)", f"{SRM.z:,.0f}", f"p {SRM.p_value:.2e}", delta_color="inverse")
    st.write(f"Ad {int(grp.loc['ad','n']):,} user, psa {int(grp.loc['psa','n']):,} user. Rasio tidak 50:50.".replace(",", "."))
    st.subheader("Cek silang SQL vs Python")
    st.metric("Cek PASS", f"{(cc.hasil == 'PASS').sum()} dari {len(cc)}")
    st.dataframe(cc, width='stretch', hide_index=True)

elif page == "Segmen & Waktu":
    st.title("Segmen hari dan intensitas iklan")
    s = seg.copy()
    s["urut"] = s["segmen"].map({k: i for i, k in enumerate(NAMA)})
    s = s.sort_values("urut")
    s["Hari"] = s["segmen"].map(NAMA)
    s["Selisih (poin %)"] = (s["diff"] * 100).round(2)
    s["Signifikan (Bonferroni)"] = s["p_bonferroni"] < 0.05
    st.bar_chart(s.set_index("Hari")["Selisih (poin %)"])
    st.dataframe(s[["Hari", "n_ad", "n_psa", "conv_ad", "conv_psa", "Selisih (poin %)", "p_bonferroni", "Signifikan (Bonferroni)"]],
                 width='stretch', hide_index=True)
    st.subheader("Kuartil total ads")
    q = qt[["kuartil_total_ads", "conv_ad", "conv_psa", "diff", "p_value"]].copy()
    q["diff"] = q["diff"] * 100
    st.dataframe(q.rename(columns={"diff": "selisih (poin %)"}), width='stretch', hide_index=True)
    st.caption("Tidak ada kolom tanggal di dataset, jadi tren waktu tidak bisa dihitung.")

else:
    st.title("Kalkulator ukuran sampel")
    mde = st.slider("MDE (poin persentase)", 0.1, 2.0, 0.5, 0.1)
    p0 = float(grp.loc["psa", "conv_rate"])
    p1 = min(p0 + mde / 100, 0.999)
    h = 2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p0))
    n = int(np.ceil(((stats.norm.ppf(0.975) + stats.norm.ppf(0.80)) / h) ** 2))
    st.metric("Ukuran sampel per grup", f"{n:,}".replace(",", "."))
    st.caption(f"Baseline CR psa {p0*100:.2f}%. Cohen's h, power 80%, alpha 0,05 dua arah.".replace(".", ",", 1))
