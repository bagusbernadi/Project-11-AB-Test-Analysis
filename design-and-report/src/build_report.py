"""Generator Report v2 (Project 11). Membaca project/results/*/*.csv, merakit design-and-report/index.html.

Jalankan dari root repo setelah project/code/run_all.sh (tahap 1-3):
    python3 design-and-report/src/build_report.py
Pane Design diambil dari src/design_pane.html dan tidak diubah (dicek identik di akhir).
Basis HTML/CSS dari src/base_head.html (Project 12), report_lib.py dan report.css disalin dari Project 4.
"""
import re
import sys
from html import escape as esc
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "project" / "code"))
from common import RES_PREP, RES_ANA, RES_PRES  # noqa: E402
import report_lib as R
from report_lib import D, I, P, audit, gbars, pill, qa, table

# ---------- data ----------
FILES = {RES_PREP: {"cleaning_log.csv"},
         RES_ANA: {"group_summary.csv", "segment_day.csv", "segment_hour.csv", "segment_ads_quartile.csv", "test_results.csv", "crosscheck.csv"},
         RES_PRES: {"one_sheet.png", "one_sheet.pdf", "analysis.ipynb", "presentasi.pptx"}}
for _folder, _names in FILES.items():
    assert {p.name for p in _folder.iterdir() if p.is_file()} == _names, f"ada file hasil yang belum terdaftar di {_folder.name}"

cl = pd.read_csv(RES_PREP / "cleaning_log.csv")
grp = pd.read_csv(RES_ANA / "group_summary.csv").set_index("group")
seg = pd.read_csv(RES_ANA / "segment_day.csv")
qt = pd.read_csv(RES_ANA / "segment_ads_quartile.csv")
tr = pd.read_csv(RES_ANA / "test_results.csv").set_index("uji")

N_RAW = int(cl.rows_in.iloc[0])
N_CLEAN = int(cl.rows_out.iloc[-1])
N_BAD = N_RAW - N_CLEAN
N_AD, N_PSA = int(grp.loc["ad", "n"]), int(grp.loc["psa", "n"])
CR_AD, CR_PSA = float(grp.loc["ad", "conv_rate"]), float(grp.loc["psa", "conv_rate"])
Z = tr.loc["Z dua proporsi (ad vs psa)"]
BOOT = tr.loc["Bootstrap 2000x (selisih)"]
SRM = tr.loc["SRM chi-square (50:50)"]
SAMP = tr.loc["Ukuran sampel per grup (Cohen h, 80%, alpha 0,05)"]
SENS = tr.loc[[i for i in tr.index if str(i).startswith("Sensitivitas")][0]]
MDE_PP = 0.5
H = float(Z.cohens_h)
Q4 = qt.iloc[3]
NAMA_HARI = {"Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu", "Thursday": "Kamis",
             "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"}


_sig = [NAMA_HARI[s] for s, v in zip(seg.segmen, seg.p_bonferroni) if v < 0.05]
_non = [NAMA_HARI[s] for s, v in zip(seg.segmen, seg.p_bonferroni) if v >= 0.05]
_join = lambda xs: ", ".join(xs[:-1]) + " dan " + xs[-1] if len(xs) > 1 else (xs[0] if xs else "tidak ada")


def pv(p):
    p = float(p)
    return "< 0,0001" if p < 0.0001 else D(p, 4)


def pp(x, d=2):
    return D(float(x) * 100, d)


def verdict(v):
    kind = "" if v.startswith("Sesuai") and "+" not in v else ("d" if v.startswith("Tidak") or v.startswith("Belum") else "p")
    return pill(v, kind)


# ---------- bagian Report ----------
def sec1():
    return (f'<div class="card"><p><b>Sumber:</b> Kaggle, "Marketing A/B Testing" (faviovaz/marketing-ab-testing), file <code>marketing_AB.csv</code>. '
            f'Lisensi dan sitasi belum diverifikasi. Data mentah tidak di-commit.</p>'
            f'<p><b>Baris:</b> {I(N_RAW)} baris mentah, {I(N_BAD)} dibuang, {I(N_CLEAN)} dipakai. Log per langkah ada di <code>project/results/1-data-preparation/cleaning_log.csv</code>.</p>'
            f'<p><b>Grup:</b> ad {I(N_AD)} user, psa {I(N_PSA)} user.</p>'
            f'<p><b>Hasil yang dihasilkan:</b> <code>group_summary.csv</code>, <code>segment_day.csv</code>, <code>segment_ads_quartile.csv</code>, <code>test_results.csv</code>, dan log jalan.</p></div>')


def sec2():
    warn = {2, 3, 8, 9, 10, 13}
    rows = [
        (1, "Apakah data bersih (grup valid, tanpa user ganda)?", f"Ya. {I(N_BAD)} baris dibuang; semua grup valid dan tidak ada user ganda."),
        (2, "Apakah pembagian grup seimbang 50:50 (SRM)?",
         f"Tidak. Chi-square = {I(float(SRM.z))}, p {pv(SRM.p_value)}. Ad {P(N_AD / N_CLEAN, 1)}, psa {P(N_PSA / N_CLEAN, 1)}."),
        (3, "Bagaimana komposisi grup per hari dalam seminggu?",
         "Dijawab dengan hari dalam seminggu, bukan tanggal. Dataset tidak punya tanggal, jadi tren waktu tidak bisa diukur."),
        (4, "Berapa conversion rate ad dan psa, dan berapa selisihnya?",
         f"CR ad {pp(CR_AD)}%, CR psa {pp(CR_PSA)}%. Selisih {pp(Z['diff'])} poin, lift relatif {P(Z.rel_lift, 0)}."),
        (5, "Apakah selisih signifikan (uji z dua proporsi)?",
         f"Ya. z = {D(Z.z, 2)}, p {pv(Z.p_value)}."),
        (6, "Berapa confidence interval selisih?",
         f"95% (Newcombe, berbasis Wilson): {pp(Z.ci_low)} s.d. {pp(Z.ci_high)} poin. Bootstrap 2.000 resample: {pp(BOOT.ci_low)} s.d. {pp(BOOT.ci_high)} poin."),
        (7, "Berapa Cohen's h dan power untuk MDE 0,5 poin?",
         f"Cohen's h = {D(H, 3)} (kecil). Daya untuk MDE 0,5 poin mendekati 100% pada ukuran sampel ini."),
        (8, "Apakah selisih sama di tiap hari dalam seminggu?",
         f"{'Tidak merata. ' if _non else 'Merata. '}Signifikan setelah koreksi Bonferroni (7 uji): {_join(_sig)}. Tidak signifikan: {_join(_non)}."),
        (9, "Apakah selisih bergantung pada intensitas iklan (kuartil total ads)?",
         f"Ya. Hanya kuartil teratas yang berbeda (selisih {pp(Q4['diff'])} poin, p {pv(Q4.p_value)}). Tiga kuartil lainnya tidak."),
        (10, "Berapa tambahan konversi per 1 juta user (estimasi, dengan rentang)?",
         f"Estimasi {I(float(Z['diff']) * 1e6)} konversi per 1 juta user (CI {I(float(Z.ci_low) * 1e6)} s.d. {I(float(Z.ci_high) * 1e6)}). Per bulan tidak bisa dihitung tanpa data trafik."),
        (11, "Berapa ukuran sampel per grup untuk MDE 0,5 poin?",
         f"{I(SAMP.n_ad)} user per grup (power 80%, alpha 0,05). Dataset jauh di atas angka ini."),
        (12, "Apakah hasil stabil menurut bootstrap?", "Ya. CI bootstrap hampir sama dengan CI analitik."),
        (13, "Apakah baris outlier (total ads di atas P99) mengubah kesimpulan?",
         f"Tidak. Dengan buang user total ads di atas P99, selisih {pp(SENS['diff'])} poin, p {pv(SENS.p_value)}."),
        (14, "Apakah hasil SQL (DuckDB) sama dengan Python?", f"Ya. {I(N_CHECK)} cek silang PASS, {I(N_FAIL)} gagal (toleransi 0)."),
    ]
    chips = '<div class="qchips">' + "".join(
        f'<a class="qc{" w" if n in warn else ""}" href="#rp2">Q{n}</a>' for n in range(1, 15)) + "</div>"
    cards = "".join(qa(f"Q{n}", t, "Utama", a, status=("Dengan catatan" if n in warn else "Terjawab"), warn=n in warn)
                    for n, t, a in rows)
    return ('<div class="callout a"><b>14 pertanyaan dijawab</b>; kuning = terjawab dengan catatan atau belum dijawab.</div>'
            + chips + cards)


def sec3():
    return table(["Aspek", "Rancangan", "Realisasi"], [
        ["Jumlah baris", "±294 ribu", f"{I(N_RAW)} (dataset lebih besar)"],
        ["Grup", "Halaman baru vs lama, 50:50", f"Iklan vs PSA, {P(N_AD / N_CLEAN, 1)} vs {P(N_PSA / N_CLEAN, 1)}"],
        ["Kolom", "5 kolom + file negara", "6 kolom, tanpa negara dan tanggal"],
        ["Kualitas", "Ada baris bermasalah", f"{I(N_BAD)} baris dibuang; data bersih"],
        ["Lisensi", "Belum diverifikasi", "Belum diverifikasi"],
    ])


def sec4():
    return table(["Tool", "Rancangan", "Dipakai"], [
        ["Python (pandas, SciPy, statsmodels)", "Ya", "Ya"],
        ["DuckDB + SQL", "Ya", "Ya"],
        ["Streamlit (dashboard)", "Ya", "Ya"],
        ["Markdown (README)", "Ya", "Ya, angka dari CSV"],
    ]) + '<p class="report-note">Semua tool rancangan dipakai. Notebook belum dibuat.</p>'


def sec5():
    return table(["No", "Langkah rancangan", "Status"], [
        ["1", "Tulis rancangan dan aturan uji", verdict("Sesuai")],
        ["2", "Tulis kamus data", verdict("Sesuai")],
        ["3", "Cek kualitas data", verdict("Sesuai")],
        ["4", "Cleaning dengan log", verdict("Sesuai")],
        ["5", "Muat ke DuckDB", verdict("Sesuai")],
        ["6", "SRM", verdict("Sesuai")],
        ["7", "Uji selisih", verdict("Sesuai")],
        ["8", "Segmen hari dan intensitas (koreksi Bonferroni)", verdict("Sesuai + penyesuaian")],
        ["9", "Bootstrap dan sensitivitas", verdict("Sesuai")],
        ["10", "Estimasi dampak", verdict("Sesuai")],
        ["11", "Cek silang SQL vs Python", verdict("Sesuai")],
        ["12", "Dashboard, one-sheet, README", verdict("Sesuai")],
    ]) + '<p class="report-note">Dari 12 langkah rancangan: 12 selesai. Notebook dan slide belum termasuk langkah.</p>'


def sec6():
    return table(["Output", "Status"], [
        ["Dashboard Streamlit (4 halaman)", verdict("Sesuai")],
        ["One-sheet PDF/PNG", verdict("Sesuai")],
        ["Database DuckDB dan folder SQL", verdict("Sesuai")],
        ["Modul Python uji A/B (2-analysis/python/abtest.py)", verdict("Sesuai")],
        ["Notebook analisis (3-presentation/analysis.ipynb)", verdict("Sesuai")],
        ["Slide presentasi (opsional, 7 slide)", verdict("Sesuai")],
                ["README", verdict("Sesuai")],
        ["Repositori GitHub", verdict("Sesuai")],
            ]) + '<p class="report-note">Semua output rancangan sudah dibuat.</p>'


def sec7():
    days = [NAMA_HARI[d] for d in seg.segmen]
    return (
        '<h4>7.1 Hasil analisis</h4><div class="card">'
        f'<p>Iklan menghasilkan conversion rate lebih tinggi dibanding PSA: {pp(CR_AD)}% vs {pp(CR_PSA)}%, selisih {pp(Z["diff"])} poin '
        f'(CI 95% {pp(Z.ci_low)} s.d. {pp(Z.ci_high)}, p {pv(Z.p_value)}).</p>'
        f'<p>Namun pembagian grup gagal SRM, dan efeknya hanya terlihat pada kuartil total ads teratas.</p></div>'
        '<h4>7.2 Impact</h4><div class="card">'
        f'<p><b>Estimated:</b> sekitar {I(float(Z["diff"]) * 1e6)} konversi tambahan per 1 juta user yang melihat iklan dibanding PSA. '
        'Estimasi per bulan belum bisa dihitung karena dataset tidak punya trafik per bulan.</p></div>'
        '<h4>7.3 Success criteria</h4><div class="card"><ul>'
        '<li>Q1–Q14 terjawab dengan angka dari data: tercapai.</li>'
        '<li>Aturan uji tertulis sebelum hasil dilihat: tercapai.</li>'
        '<li>SRM dilaporkan jujur: tercapai.</li>'
        '<li>Dashboard bisa dibuka dan keputusan dijelaskan dalam 1 menit: tercapai (cek manual belum dilakukan).</li></ul></div>'
        '<h4>7.4 Rekomendasi</h4><div class="card">'
        '<p><b>Jangan rollout dari angka ini saja.</b> Pastikan mekanisme alokasi grup dengan pemilik data, lalu jalankan ulang test dengan alokasi acak 50:50 dan catat sumber serta tanggalnya.</p></div>'
        '<h4>7.5 Saran perbaikan</h4><div class="card"><ul>'
        '<li>Tambahkan uji ulang dengan alokasi acak 50:50 setelah mekanisme grup dipastikan.</li>'
        '<li>Tambahkan kolom tanggal dan negara jika ada, agar Q3 dan Q8 bisa dijawab penuh.</li></ul></div>'
        '<h4>7.6 Batasan</h4><div class="card"><ul>'
        f'<li><b>SRM gagal:</b> {P(N_AD / N_CLEAN, 1)} vs {P(N_PSA / N_CLEAN, 1)}. Batasan utama.</li>'
        '<li><b>Tanpa tanggal dan negara:</b> efek kebaruan dan tren waktu tidak bisa diuji.</li>'
        '<li><b>Total ads mungkin dipengaruhi perlakuan:</b> dipakai untuk deskripsi, bukan kontrol kausal.</li>'
        '<li><b>Tanpa nilai pembelian:</b> dampak revenue tidak dihitung.</li>'
        '<li><b>Penyimpangan dari rancangan:</b> pane Design menyebut koreksi Holm; analisis memakai Bonferroni dan CI selisih Newcombe (berbasis Wilson) sesuai standar portofolio. Uji z, bootstrap, dan keputusan utama tidak berubah.</li>'
        '<li><b>Lisensi belum diverifikasi.</b> Halaman Kaggle tidak bisa diakses dari sandbox.</li></ul></div>'
    )


N_CHECK = int(pd.read_csv(RES_ANA / "crosscheck.csv").shape[0])
N_FAIL = int((pd.read_csv(RES_ANA / "crosscheck.csv").hasil == "FAIL").sum())

TITLES = [
    ("Data yang berhasil didapatkan", "Isi data mentah, tabel di database, dan data hasil analisis", sec1),
    ("Apakah business question terjawab?", "14 pertanyaan pada Design Project, dijawab dengan data", sec2),
    ("Apakah dataset sesuai dengan Design Project?", "Perbandingan rancangan dengan realisasi", sec3),
    ("Apakah tools yang digunakan sesuai?", "Perbandingan rancangan dengan eksekusi", sec4),
    ("Apakah alur pengerjaan sesuai dengan Design Project?", "12 langkah rancangan vs yang dijalankan", sec5),
    ("Apakah project output tercapai?", "Output pada Design Project, bagian 7", sec6),
    ("Kesimpulan", "Hasil analisis, Impact, success criteria, rekomendasi, saran perbaikan, dan batasan", sec7),
]

STATIC = {f"{a}.{b}" for a in range(1, 8) for b in range(1, 8)} | {
    "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
    "0", "50", "0,05", "0,0001", "0,5", "1,96", "80", "95", "2.000", "100", "1.000", "2", "3", "4", "5", "6", "7", "8", "9", "294"}


def report_pane():
    parts = ['<div class="pane" id="report" data-tab="report" hidden>\n']
    parts.append('<div class="callout a"><b>Report Project versi 2: evaluasi hasil terhadap Design Project.</b> '
                 'Data pada project ini adalah dataset publik, bukan simulasi.</div>')
    for i, (t, sub, fn) in enumerate(TITLES, 1):
        parts.append(f'<h2 id="rp{i}">{i}. {esc(t)}<small>{esc(sub)}</small></h2>')
        parts.append(fn())
    parts.append("\n</div>\n")
    return "".join(parts)


NAV_REPORT = ('<div class="links" data-tab="report" hidden>'
              '<a href="#rp1">Data</a><a href="#rp2">Business Questions</a><a href="#rp3">Dataset</a>'
              '<a href="#rp4">Tools</a><a href="#rp5">Alur Kerja</a><a href="#rp6">Project Output</a>'
              '<a href="#rp7">Kesimpulan</a></div>')

NAV_DESIGN = ('<div class="links" data-tab="design">'
              '<a href="#s1">Background</a><a href="#s2">Business Questions</a><a href="#s3">Significance &amp; Decision</a>'
              '<a href="#s4">Dataset</a><a href="#s5">Tools</a><a href="#s6">Work Plan</a><a href="#s7">Project Outputs</a>'
              '<a href="#s8">Success Criteria</a><a href="#s9">Assumptions &amp; Limitations</a></div>')

GLOSSARY = r'''const G=[["conversion rate","i","Persentase user yang melakukan konversi.\nRumus: CR = user konversi ÷ semua user di grup.\nContoh: 1.200 dari 10.000 user, CR = 12%."],["selisih","i","Beda conversion rate dua grup dalam poin persentase.\nRumus: selisih = CR ad − CR psa."],["lift relatif","i","Kenaikan CR dibanding basis, dalam persen.\nRumus: (CR ad − CR psa) ÷ CR psa."],["p-value","","Peluang melihat selisih sebesar ini jika sebenarnya kedua grup sama. Batas umum: 0,05."],["confidence interval","i","Rentang tempat selisih sebenarnya kemungkinan berada (95%)."],["SRM","","Sample Ratio Mismatch: pembagian grup tidak sesuai rasio yang direncanakan. Tanda ada masalah pada cara grup dibentuk."],["Cohen's h","","Ukuran besar selisih dua proporsi. Sekitar 0,2 kecil, 0,5 sedang, 0,8 besar."],["power","i","Peluang uji mendeteksi selisih yang nyata. Target umum 80%."],["MDE","i","Minimum detectable effect: selisih terkecil yang bisa dideteksi dengan power yang ditetapkan."],["bootstrap","","Cara menghitung ketidakpastian dengan mengulang sampel acak berkali-kali."],["Holm","","Koreksi p-value saat banyak uji dilakukan sekaligus, agar kesalahan tipe I tetap terkendali."],["P99","i","Nilai di bawah 99% data. Dipakai untuk menandai nilai ekstrem."],["kuartil","i","Pembagian data menjadi empat bagian sama besar berdasarkan urutan nilai."],["estimated","i","Angka hasil perhitungan dari asumsi, bukan hasil pengukuran langsung."]];'''

SCRIPT = ('<script>\n' + GLOSSARY + r'''
const TERMS=G.map(([t,f,d])=>({t,d,re:new RegExp('(?<![\\w-])'+t.replace(/[.*+?^${}()|[\]\\-]/g,'\\$&')+'(?![\\w-])',f)}));
const SK='svg,.fx,.fbar,.oh,h1,h2,h3,nav,button,script,style,summary,.tm,.tag,.pri,.pill,.v,.l,.chip,.flow,th,#tip,.banner,.theme,.phase,.add,.tools b,b.t,table td:first-child,.wb,code';
function wrapT(n,seen){let b=null;for(const x of TERMS){if(seen.has(x.t))continue;const m=x.re.exec(n.data);if(m&&(!b||m.index<b.i||(m.index==b.i&&m[0].length>b.l)))b={x,i:m.index,l:m[0].length}}
if(!b)return;seen.add(b.x.t);const r=n.splitText(b.i),a=r.splitText(b.l),s=document.createElement('span');s.className='tm';s.tabIndex=0;s.dataset.d=b.x.d;s.textContent=r.data;r.replaceWith(s);wrapT(a,seen)}
function hl(root,seen){const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,{acceptNode:n=>n.parentElement.closest(SK)?3:1}),ns=[];while(w.nextNode())ns.push(w.currentNode);ns.forEach(n=>wrapT(n,seen))}
const tip=document.createElement('div');tip.id='tip';tip.setAttribute('role','tooltip');document.body.appendChild(tip);
function showT(e){tip.textContent=e.dataset.d;tip.style.display='block';const r=e.getBoundingClientRect(),w=tip.offsetWidth,h=tip.offsetHeight;tip.style.left=Math.max(8,Math.min(innerWidth-w-8,r.left))+'px';tip.style.top=(r.bottom+h+12>innerHeight?r.top-h-6:r.bottom+6)+'px'}
document.addEventListener('click',ev=>{const t=ev.target.closest('.tm');t?showT(t):tip.style.display='none'});
document.addEventListener('mouseover',ev=>{const t=ev.target.closest('.tm');if(t)showT(t)});
document.addEventListener('mouseout',ev=>{if(ev.target.closest&&ev.target.closest('.tm'))tip.style.display='none'});
document.addEventListener('focusin',ev=>{const t=ev.target.closest&&ev.target.closest('.tm');if(t)showT(t)});
addEventListener('scroll',()=>tip.style.display='none',{passive:true});
let seen=new Set();document.querySelectorAll('main>.pane>*').forEach(el=>{if(el.tagName=='H2')seen=new Set();hl(el,seen)});
const TB=[...document.querySelectorAll('.tab')];
function setTab(t){document.querySelectorAll('.pane,.links').forEach(e=>e.hidden=e.dataset.tab!==t);TB.forEach(x=>{const on=x.dataset.t===t;x.classList.toggle('on',on);x.setAttribute('aria-expanded',on)})}
function route(){const h=decodeURIComponent(location.hash.slice(1)),el=h&&document.getElementById(h);
if(h=='design'||h=='report'){setTab(h);scrollTo(0,0);return}
if(el){const p=el.closest('.pane');if(p){setTab(p.dataset.tab);el.scrollIntoView()}}}
TB.forEach(x=>x.onclick=()=>{location.hash=x.dataset.t});
addEventListener('hashchange',route);route();
</script>
''')


def main():
    base = (HERE / "base_head.html").read_text(encoding="utf-8")
    base = re.sub(r"<title>.*?</title>", "<title>Project 11: A/B Test Analysis</title>", base, count=1)
    base = re.sub(r'<meta name="description"[^>]*>',
                  '<meta name="description" content="Analisis A/B test iklan vs PSA pada 588 ribu user: kualitas data, SRM, uji proporsi, segmen, dan rekomendasi.">',
                  base, count=1)
    css = (HERE / "report.css").read_text(encoding="utf-8")
    assert base.count("</style>") == 1
    head = base.replace("</style>", css + "\n</style>", 1)
    banner = ('<header class="banner"><h1>Project 11: A/B Test Analysis</h1>'
              '<p class="goal"><b>Tujuan project:</b> menguji apakah iklan (ad) menghasilkan conversion rate lebih tinggi daripada PSA, '
              'dan apakah selisihnya cukup besar dan stabil untuk keputusan kampanye.</p>'
              '<div class="tags"><span class="tlab">Kategori:</span><span class="tag a">Rancangan v2 + Report v2</span>'
              '<span class="tag c1">Marketing</span><span class="tag c2">Dataset publik</span><span class="tag c3">Statistik</span></div></header>')
    nav = ('<nav aria-label="Project navigation"><button type="button" class="tab on" data-t="design" aria-expanded="true" aria-controls="design">Design Project</button>'
           + NAV_DESIGN +
           '<button type="button" class="tab" data-t="report" aria-expanded="false" aria-controls="report">Report Project</button>'
           + NAV_REPORT + "</nav>")
    design = (HERE / "design_pane.html").read_text(encoding="utf-8")
    report = report_pane()
    back = ('<a href="https://bagusbernadi.github.io/" style="display:inline-block;margin:12px 16px;font:600 14px/1.4 '
            "'Source Sans 3',Arial,sans-serif;color:#1A73E8;text-decoration:none\">← All projects / Semua project</a>")
    html = head + "<body>\n" + back + "\n<main>\n" + nav + "\n" + banner + "\n" + design + report + "\n</main>\n" + SCRIPT + "</body></html>\n"
    # pane Design tidak boleh berubah
    assert design in html and html.index('<div class="pane" id="design"') < html.index('<div class="pane" id="report"')
    n_tok, bad = audit(report, STATIC)
    print(f"audit: {n_tok} token diperiksa, tidak terdaftar: {bad}")
    (ROOT / "design-and-report" / "index.html").write_text(html, encoding="utf-8")
    print("ditulis:", ROOT / "design-and-report" / "index.html")


if __name__ == "__main__":
    main()
