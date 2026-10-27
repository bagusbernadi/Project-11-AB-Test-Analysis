# Slide presentasi (6 slide) dari outputs/*.csv. Hasil: slides/presentasi.pptx
import pathlib, csv
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
tr = {r["uji"]: r for r in csv.DictReader(open(OUT / "test_results.csv", encoding="utf-8"))}
grp = {r["group"]: r for r in csv.DictReader(open(OUT / "group_summary.csv", encoding="utf-8"))}
Z = tr["Z dua proporsi (ad vs psa)"]
SRM = tr["SRM chi-square (50:50)"]
pc = lambda v, d=2: f"{float(v) * 100:.{d}f}".replace(".", ",") + "%"
pts = lambda v: f"{float(v) * 100:.2f}".replace(".", ",")
BLUE, DARK = RGBColor(0x17, 0x4E, 0xA6), RGBColor(0x20, 0x21, 0x24)

prs = Presentation(); prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
blank = prs.slide_layouts[6]

def slide(title, bullets, note=None):
    s = prs.slides.add_slide(blank)
    tb = s.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(12.1), Inches(1.0)).text_frame
    tb.text = title; p = tb.paragraphs[0]; p.font.size = Pt(32); p.font.bold = True; p.font.color.rgb = BLUE
    body = s.shapes.add_textbox(Inches(0.6), Inches(1.6), Inches(12.1), Inches(5.2)).text_frame
    body.word_wrap = True
    for i, b in enumerate(bullets):
        para = body.paragraphs[0] if i == 0 else body.add_paragraph()
        para.text = "• " + b; para.font.size = Pt(20); para.font.color.rgb = DARK; para.space_after = Pt(10)
    if note:
        nf = s.shapes.add_textbox(Inches(0.6), Inches(6.8), Inches(12.1), Inches(0.4)).text_frame
        nf.text = note; nf.paragraphs[0].font.size = Pt(12); nf.paragraphs[0].font.color.rgb = RGBColor(0x5F, 0x63, 0x68)
    return s

s = prs.slides.add_slide(blank)
tb = s.shapes.add_textbox(Inches(0.6), Inches(2.4), Inches(12.1), Inches(2.5)).text_frame; tb.word_wrap = True
tb.text = "Project 11: Apakah iklan menaikkan konversi?"; tb.paragraphs[0].font.size = Pt(40); tb.paragraphs[0].font.bold = True; tb.paragraphs[0].font.color.rgb = BLUE
q = tb.add_paragraph(); q.text = "A/B test iklan vs PSA pada 588.101 user (dataset publik)"; q.font.size = Pt(20); q.font.color.rgb = DARK

slide("Masalah dan pertanyaan", [
    "Apakah menampilkan iklan menghasilkan conversion rate lebih tinggi daripada PSA?",
    "Jika ya, apakah selisihnya cukup besar dan stabil untuk keputusan kampanye?",
    "Aturan uji ditetapkan sebelum melihat hasil: alpha 0,05 dua arah, power 80%, MDE 0,5 poin."])

slide("Data dan metode", [
    f"588.101 user, grup ad dan psa. Tidak ada baris yang dibuang.",
    "Uji z dua proporsi, CI 95%, Cohen's h, bootstrap 2.000 resample.",
    "Cek SRM (chi-square terhadap 50:50), segmen hari, kuartil total ads, sensitivitas P99.",
    "Cek silang SQL (DuckDB) vs Python: 36 cek, semua PASS."],
    note="Dataset tidak memiliki tanggal dan negara. Lisensi belum diverifikasi.")

slide("Hasil utama", [
    f"CR ad {pc(grp['ad']['conv_rate'])} vs psa {pc(grp['psa']['conv_rate'])}.",
    f"Selisih {pts(Z['diff'])} poin, 95% CI {pts(Z['ci_low'])} s.d. {pts(Z['ci_high'])}, p < 0,0001.",
    f"Cohen's h = {float(Z['cohens_h']):.3f} (kecil). Lift relatif {float(Z['rel_lift']) * 100:.0f}%.",
    f"Estimasi: sekitar {float(Z['diff']) * 1e6:,.0f} konversi tambahan per 1 juta user (estimated)."
        .replace(",", ".")])

slide("Yang perlu diwaspadai", [
    f"SRM gagal: ad {pc(float(grp['ad']['n']) / 588101, 1)}, psa {pc(float(grp['psa']['n']) / 588101, 1)}. Chi-square p < 0,0001.",
    "Efek hanya terlihat di kuartil total ads teratas. Tiga kuartil lainnya tidak berbeda.",
    "total ads mungkin dipengaruhi perlakuan, jadi bukan kontrol kausal.",
    "Tanpa tanggal, negara, dan nilai pembelian."])

slide("Rekomendasi", [
    "Belum rollout berdasarkan angka ini.",
    "Pastikan dengan pemilik data bagaimana grup dibentuk (penyebab SRM).",
    "Uji ulang dengan alokasi acak 50:50, catat sumber dan tanggal.",
    "Uji apakah efeknya nyata pada intensitas iklan menengah."])

slide("Kesimpulan", [
    "Iklan menghasilkan conversion rate lebih tinggi dibanding PSA pada dataset ini.",
    "Namun bukti kausal belum kuat karena alokasi grup tidak seimbang.",
    "Dashboard, one-sheet, dan notebook tersedia di repositori."])

out = ROOT / "slides"; out.mkdir(exist_ok=True)
import datetime
prs.core_properties.created = datetime.datetime(2026, 10, 27)
prs.core_properties.modified = datetime.datetime(2026, 10, 27)
prs.core_properties.last_modified_by = "project-11"
path = out / "presentasi.pptx"
prs.save(path)
# Samakan timestamp entri zip agar byte-identik antar jalan
import zipfile, io
buf = io.BytesIO()
with zipfile.ZipFile(path) as zin, zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
    for it in sorted(zin.infolist(), key=lambda i: i.filename):
        zout.writestr(zipfile.ZipInfo(it.filename, date_time=(2026, 10, 27, 0, 0, 0)), zin.read(it.filename), compress_type=zipfile.ZIP_DEFLATED)
path.write_bytes(buf.getvalue())
print("ditulis:", path.name, len(prs.slides), "slide")

# Bersihkan metadata waktu eksekusi notebook (nbconvert) agar hasil byte-identik antar jalan.
import nbformat as _nbf
_p = ROOT / "notebooks" / "analysis.ipynb"
if _p.exists():
    _nb = _nbf.read(_p, as_version=4)
    for _c in _nb.cells:
        _c.get("metadata", {}).pop("execution", None)
    _nbf.write(_nb, _p)
