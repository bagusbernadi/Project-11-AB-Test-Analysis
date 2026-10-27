# One-sheet infografik (PNG dan PDF) dari outputs/*.csv. Jalankan dari root repo.
import pathlib, csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
tr = {r["uji"]: r for r in csv.DictReader(open(OUT / "test_results.csv", encoding="utf-8"))}
grp = {r["group"]: r for r in csv.DictReader(open(OUT / "group_summary.csv", encoding="utf-8"))}
seg = list(csv.DictReader(open(OUT / "segment_day.csv", encoding="utf-8")))
Z = tr["Z dua proporsi (ad vs psa)"]
pct = lambda v: f"{float(v) * 100:.2f}%".replace(".", ",")
pts = lambda v: f"{float(v) * 100:.2f}".replace(".", ",")

fig = plt.figure(figsize=(11, 8.5), dpi=150)
fig.text(0.05, 0.93, "Iklan vs PSA: apakah iklan menaikkan konversi?", fontsize=22, weight="bold", color="#174EA6")
fig.text(0.05, 0.895, "Project 11 · A/B test pada 588.101 user (dataset publik)", fontsize=12, color="#5F6368")

# Kartu angka
cards = [
    (pct(grp["ad"]["conv_rate"]), "CR ad"),
    (pct(grp["psa"]["conv_rate"]), "CR psa"),
    (f"+{pts(Z['diff'])} poin", f"Selisih (CI 95% {pts(Z['ci_low'])} s.d. {pts(Z['ci_high'])})"),
]
for i, (big, lab) in enumerate(cards):
    x = 0.05 + i * 0.32
    ax = fig.add_axes([x, 0.66, 0.28, 0.18]); ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color="#E8F0FE" if i < 2 else "#188038", transform=ax.transAxes))
    ax.text(0.5, 0.6, big, ha="center", fontsize=22, weight="bold", color="#174EA6" if i < 2 else "white")
    ax.text(0.5, 0.2, lab, ha="center", fontsize=10, color="#202124" if i < 2 else "white")

# Grafik segmen hari
ax = fig.add_axes([0.08, 0.14, 0.55, 0.42])
HARI = {"Monday": "Sen", "Tuesday": "Sel", "Wednesday": "Rab", "Thursday": "Kam", "Friday": "Jum", "Saturday": "Sab", "Sunday": "Min"}
names = [HARI[s["segmen"]] for s in seg]
vals = [float(s["diff"]) * 100 for s in seg]
colors = ["#188038" if float(s["p_holm"]) < 0.05 else "#9AA0A6" for s in seg]
ax.bar(names, vals, color=colors)
ax.set_title("Selisih CR ad − psa per hari (poin %; hijau = signifikan setelah Holm)", fontsize=10, loc="left")
ax.set_ylabel("poin %"); ax.spines[["top", "right"]].set_visible(False)

# Keputusan
ax2 = fig.add_axes([0.68, 0.14, 0.28, 0.42]); ax2.axis("off")
txt = ("Keputusan\n\n"
       "Belum rollout berdasarkan angka ini.\n\n"
       "• SRM gagal: ad 96%, psa 4%.\n"
       "• Efek terlihat di kuartil total ads teratas saja.\n"
       "• Estimasi: +" + f"{float(Z['diff']) * 1e6:,.0f}".replace(",", ".") + " konversi per 1 juta user (estimated).\n\n"
       "Langkah: pastikan alokasi grup, lalu uji ulang dengan 50:50.")
ax2.text(0, 1, txt, va="top", fontsize=10.5, color="#202124", wrap=True)
fig.text(0.05, 0.05, "Data: marketing_AB.csv (Kaggle, faviovaz/marketing-ab-testing). Lisensi belum diverifikasi. Angka dari outputs/test_results.csv.",
         fontsize=8.5, color="#5F6368")

png, pdf = OUT / "one_sheet.png", OUT / "one_sheet.pdf"
fig.savefig(png, metadata={"Software": "matplotlib"}); fig.savefig(pdf, metadata={"CreationDate": None, "Creator": "matplotlib"})
print("ditulis:", png.name, pdf.name)
