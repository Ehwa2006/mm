#!/usr/bin/env python3
"""Membungkus isi halaman di src/pages dengan tata letak bersama dan menulis situs statis ke docs/.

Untuk menambah halaman: buat src/pages/<slug>.html, tambahkan satu baris di PAGES,
dan (jika ada) sumber resminya di SOURCES.
"""
import html
import json
import os
import re
import shutil
import subprocess
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
# site.json: domain, ID penayang AdSense (ca-pub-...), kode verifikasi Search Console.
with open(os.path.join(ROOT, "site.json"), encoding="utf-8") as _f:
    CONFIG = json.load(_f)
SITE_URL = (f"https://{CONFIG['custom_domain']}/" if CONFIG.get("custom_domain")
            else CONFIG["site_url"])
SITE_NAME = "Hitung Gaji Korea"
ADSENSE_CLIENT = CONFIG.get("adsense_client", "")
REPO_URL = "https://github.com/Ehwa2006/mm"

# Kelompok halaman: dipakai untuk breadcrumb, footer, dan "halaman terkait".
GROUPS = {"kalkulator": "Kalkulator", "panduan": "Panduan", "situs": "Situs"}

# (slug, kelompok, nama menu, <title>, meta description)
PAGES = [
    ("", "situs", "Beranda", f"{SITE_NAME} - Kalkulator Gaji TKI/EPS di Korea 2026",
     "Kalkulator gratis untuk pekerja Indonesia di Korea Selatan: gaji bersih dengan lembur, pesangon (퇴직금), dan pengembalian pensiun (반환일시금). Standar 2026."),
    ("kalkulator-gaji", "kalkulator", "Gaji Bersih", "Kalkulator Gaji Korea 2026 - Gaji Bersih + Lembur untuk TKI EPS",
     "Hitung gaji bersih di Korea 2026 dari upah per jam, lembur, jam malam, dan kerja hari libur. Potongan pensiun, asuransi, pajak, dan asrama. Konversi ke Rupiah."),
    ("pesangon", "kalkulator", "Pesangon", "Kalkulator Pesangon Korea (퇴직금) & Asuransi Kepulangan TKI",
     "Hitung perkiraan pesangon (퇴직금) di Korea dan berapa yang dibayar asuransi kepulangan (출국만기보험) serta selisih dari majikan."),
    ("pengembalian-pensiun", "kalkulator", "Pengembalian Pensiun", "Kalkulator Pengembalian Pensiun Korea (반환일시금) untuk TKI",
     "Perkirakan uang pensiun nasional Korea (국민연금) yang bisa diklaim kembali saat pulang ke Indonesia, termasuk iuran majikan dan bunga."),
    ("kalkulator-tabungan", "kalkulator", "Tabungan", "Kalkulator Tabungan Kerja di Korea: Berapa Uang yang Dibawa Pulang?",
     "Hitung perkiraan tabungan selama kerja di Korea 1 tahun, 3 tahun, atau 4 tahun 10 bulan, termasuk pesangon dan pengembalian pensiun, dalam Won dan Rupiah."),
    ("uang-libur-mingguan", "kalkulator", "Uang Libur Mingguan", "Kalkulator Uang Libur Mingguan Korea (주휴수당) 2026",
     "Hitung uang libur mingguan (주휴수당) di Korea: syarat 15 jam per minggu, rumus, dan contoh dengan upah minimum 2026."),
    ("cuti-tahunan", "kalkulator", "Cuti Tahunan", "Kalkulator Cuti Tahunan Korea (연차) dan Uang Pengganti Cuti",
     "Hitung jumlah hari cuti tahunan berbayar di Korea (maksimal 25 hari) dan uang pengganti cuti yang tidak terpakai (연차수당)."),
    ("tunjangan-pengangguran", "kalkulator", "Tunjangan Pengangguran", "Kalkulator Tunjangan Pengangguran Korea (실업급여) untuk Pekerja E-9 2026",
     "Hitung tunjangan pengangguran (구직급여) di Korea: maksimal ₩68.100 per hari, 120–270 hari. Syarat khusus pekerja E-9 dan cara mendaftar."),
    ("potongan-asrama", "kalkulator", "Potongan Asrama", "Batas Potongan Asrama dan Makan Pekerja Asing di Korea (숙식비 공제) - Kalkulator",
     "Majikan hanya boleh memotong biaya asrama dan makan 8–20% dari upah normal. Cek apakah potongan di slip gaji Anda melebihi batas."),
    ("slip-gaji", "panduan", "Membaca Slip Gaji", "Cara Membaca Slip Gaji Korea (임금명세서) untuk Pekerja Indonesia",
     "Arti setiap baris di slip gaji Korea: gaji pokok, lembur, uang libur, potongan asuransi dan pajak. Daftar hal yang harus dicek setiap bulan."),
    ("upah-minimum", "panduan", "Upah Minimum", "Upah Minimum Korea 2026: ₩10.320 per Jam, Tabel 2020–2026",
     "Upah minimum Korea 2026 adalah ₩10.320 per jam atau ₩2.156.880 per bulan. Tabel upah minimum 2020–2026 dan konversi ke Rupiah."),
    ("pindah-kerja", "panduan", "Pindah Kerja", "Aturan Pindah Tempat Kerja E-9 di Korea (사업장 변경) 2026",
     "Batas 3 kali pindah kerja, alasan yang diizinkan, batas wilayah, dan batas waktu 1 dan 3 bulan untuk pekerja EPS/E-9 di Korea."),
    ("gaji-tidak-dibayar", "panduan", "Gaji Tidak Dibayar", "Gaji Tidak Dibayar di Korea (임금체불): Cara Melapor untuk Pekerja Asing",
     "Langkah melapor gaji, lembur, atau pesangon yang tidak dibayar di Korea, bunga 20%, dan bantuan pemerintah sampai ₩10 juta (간이대지급금)."),
    ("kecelakaan-kerja", "panduan", "Kecelakaan Kerja", "Kecelakaan Kerja di Korea (산재): Hak Pekerja Asing dan Cara Klaim",
     "Semua pekerja asing di Korea dilindungi asuransi kecelakaan kerja (산재보험): biaya pengobatan, 70% upah selama tidak bisa kerja, dan cara klaim sendiri."),
    ("asuransi-kesehatan", "panduan", "Asuransi Kesehatan", "Asuransi Kesehatan Korea (건강보험) untuk Pekerja E-9 2026",
     "Potongan asuransi kesehatan Korea 2026 (3,595%), manfaat, dan pengembalian premi saat pindah kerja atau pulang ke Indonesia."),
    ("asuransi-khusus-eps", "panduan", "4 Asuransi EPS", "4 Asuransi Khusus Pekerja EPS di Korea (외국인 전용보험)",
     "Asuransi kepulangan, jaminan upah, biaya pulang, dan kecelakaan untuk pekerja E-9: siapa yang bayar, batas waktu daftar, dan cara klaim saat pulang."),
    ("pekerja-setia", "panduan", "Pekerja Setia", "Program Pekerja Setia E-9: Kembali ke Korea Setelah 1 Bulan (성실근로자 재입국)",
     "Syarat dan langkah program pekerja setia (성실근로자) untuk kembali bekerja di Korea tanpa EPS-TOPIK, total sampai 9 tahun 8 bulan."),
    ("alur-eps", "panduan", "Alur EPS", "Alur Kerja ke Korea Lewat EPS: EPS-TOPIK Sampai Mulai Bekerja",
     "Tahapan program EPS G to G ke Korea: ujian EPS-TOPIK, tes keterampilan, job roster, kontrak, visa, pendidikan, dan hal yang perlu diurus setelah tiba."),
    ("kartu-arc", "panduan", "Kartu ARC", "Kartu Registrasi Orang Asing Korea (ARC): Registrasi, Pindah Alamat, Kartu Hilang",
     "Batas waktu registrasi orang asing di Korea (90 hari), lapor pindah alamat (15 hari), dan ganti kartu ARC hilang (14 hari, ₩35.000)."),
    ("perpanjangan-kerja", "panduan", "Perpanjangan Kerja", "Perpanjangan Masa Kerja E-9 di Korea: 3 Tahun Menjadi 4 Tahun 10 Bulan (재고용)",
     "Cara memperpanjang masa kerja pekerja E-9 sampai 1 tahun 10 bulan: pengajuan majikan 60–7 hari sebelum habis dan perpanjangan izin tinggal."),
    ("aplikasi-penting", "panduan", "Aplikasi Penting", "Aplikasi Penting untuk Pekerja Indonesia di Korea: Chat, Penerjemah, Peta, Taksi",
     "Aplikasi yang wajib dipunya pekerja asing di Korea: KakaoTalk, Papago, Naver Map, Kakao T, HiKorea, dan tips menghindari penipuan."),
    ("nomor-penting", "panduan", "Nomor Penting", "Nomor Telepon Penting untuk Pekerja Indonesia di Korea (Bahasa Indonesia)",
     "Nomor darurat dan layanan bantuan di Korea yang melayani bahasa Indonesia: 1577-0071, 1345, serta 1350, 1355, dan nomor kecelakaan kerja."),
    ("tentang", "situs", "Tentang", f"Tentang {SITE_NAME}",
     f"Tentang {SITE_NAME}: kalkulator gratis dalam bahasa Indonesia untuk pekerja di Korea Selatan, sumber data, dan cara kami memperbarui informasi."),
    ("kontak", "situs", "Kontak", f"Kontak - {SITE_NAME}",
     f"Cara menghubungi {SITE_NAME} untuk melaporkan kesalahan data atau mengusulkan kalkulator baru."),
    ("syarat-ketentuan", "situs", "Syarat & Disclaimer", f"Syarat Penggunaan dan Disclaimer - {SITE_NAME}",
     f"Syarat penggunaan dan batasan tanggung jawab {SITE_NAME}. Hasil kalkulator adalah perkiraan, bukan nasihat hukum atau pajak."),
    ("kebijakan-privasi", "situs", "Kebijakan Privasi", f"Kebijakan Privasi - {SITE_NAME}",
     f"Kebijakan privasi {SITE_NAME}: data yang tidak kami kumpulkan, cookie, iklan Google AdSense, dan pilihan persetujuan Anda."),
]

# Sumber resmi per halaman: (nama, URL). Ditampilkan di bawah konten.
SOURCES = {
    "kalkulator-gaji": [
        ("Komisi Upah Minimum Korea (최저임금위원회)", "https://www.minimumwage.go.kr/"),
        ("National Health Insurance Service (국민건강보험공단)", "https://www.nhis.or.kr/"),
        ("National Pension Service: batas dasar iuran 2026", "https://www.nps.or.kr/pnsgdnc/newgdnc/getOHAE0001M1.do?menuId=MN24000897&pstId=NE202500000000030479"),
        ("Undang-Undang Standar Ketenagakerjaan (근로기준법)", "https://www.law.go.kr/법령/근로기준법"),
    ],
    "pesangon": [
        ("Undang-Undang Jaminan Pesangon (근로자퇴직급여 보장법)", "https://www.law.go.kr/법령/근로자퇴직급여보장법"),
        ("Asuransi khusus pekerja asing (찾기쉬운 생활법령정보)", "https://easylaw.go.kr/CSP/CnpClsMain.laf?popMenu=ov&csmSeq=2042&ccfNo=3&cciNo=1&cnpClsNo=3"),
    ],
    "pengembalian-pensiun": [
        ("National Pension Service: panduan untuk orang asing (PDF)", "https://www.nps.or.kr/html/download/guide_for_foreigners_3.pdf"),
    ],
    "kalkulator-tabungan": [
        ("National Pension Service: panduan untuk orang asing (PDF)", "https://www.nps.or.kr/html/download/guide_for_foreigners_3.pdf"),
    ],
    "uang-libur-mingguan": [
        ("Undang-Undang Standar Ketenagakerjaan (근로기준법) Pasal 55", "https://www.law.go.kr/법령/근로기준법"),
    ],
    "cuti-tahunan": [
        ("Undang-Undang Standar Ketenagakerjaan (근로기준법) Pasal 60–61", "https://www.law.go.kr/법령/근로기준법"),
    ],
    "tunjangan-pengangguran": [
        ("Kementerian Ketenagakerjaan: asuransi ketenagakerjaan untuk pekerja E-9/H-2", "https://www.moel.go.kr/local/tongyeong/news/notice/noticeView.do?bbs_seq=20201200983"),
        ("Work24 (고용24)", "https://www.work24.go.kr/"),
    ],
    "potongan-asrama": [
        ("Kementerian Ketenagakerjaan: pedoman potongan asrama dan makan", "https://www.moel.go.kr/info/etc/dataroom/view.do?bbs_seq=20200200797"),
        ("HRD Korea: panduan potongan biaya asrama", "https://hrdc.hrdkorea.or.kr/hrdc/185230"),
    ],
    "slip-gaji": [
        ("Undang-Undang Standar Ketenagakerjaan (근로기준법) Pasal 48", "https://www.law.go.kr/법령/근로기준법"),
    ],
    "upah-minimum": [
        ("Komisi Upah Minimum Korea (최저임금위원회)", "https://www.minimumwage.go.kr/"),
    ],
    "pindah-kerja": [
        ("Korea.kr: pembatasan wilayah dan sektor untuk pindah kerja", "https://www.korea.kr/news/policyNewsView.do?newsId=148917291"),
        ("찾기쉬운 생활법령정보: perubahan tempat kerja", "https://easylaw.go.kr/CSP/CnpClsMain.laf?popMenu=ov&csmSeq=2042&ccfNo=3&cciNo=2&cnpClsNo=1"),
    ],
    "gaji-tidak-dibayar": [
        ("Kementerian Ketenagakerjaan: cara menyelesaikan gaji tertunggak", "https://labor.moel.go.kr/minwonSysInfo/wagesolway.do"),
        ("찾기쉬운 생활법령정보: 대지급금", "https://easylaw.go.kr/CSP/CnpClsMain.laf?popMenu=ov&csmSeq=1694&ccfNo=3&cciNo=3&cnpClsNo=1"),
    ],
    "kecelakaan-kerja": [
        ("Korea Workers' Compensation & Welfare Service (근로복지공단)", "https://www.comwel.or.kr/"),
    ],
    "asuransi-kesehatan": [
        ("National Health Insurance Service (국민건강보험공단)", "https://www.nhis.or.kr/"),
    ],
    "asuransi-khusus-eps": [
        ("찾기쉬운 생활법령정보: asuransi khusus pekerja asing", "https://easylaw.go.kr/CSP/CnpClsMain.laf?popMenu=ov&csmSeq=2042&ccfNo=3&cciNo=1&cnpClsNo=3"),
        ("EPS: asuransi dan manfaat", "https://www.eps.go.kr/eo/EmployPerSystem.eo?tabGb=06"),
    ],
    "pekerja-setia": [
        ("Kementerian Ketenagakerjaan: pemendekan masa tunggu masuk kembali", "https://www.moel.go.kr/news/enews/report/enewsView.do?news_seq=12802"),
    ],
    "alur-eps": [
        ("Employment Permit System (EPS)", "https://www.eps.go.kr/"),
    ],
    "kartu-arc": [
        ("찾기쉬운 생활법령정보: registrasi dan laporan perubahan pekerja asing", "https://easylaw.go.kr/CSP/CnpClsMain.laf?popMenu=ov&csmSeq=2042&ccfNo=4&cciNo=1&cnpClsNo=1"),
        ("Gov24: laporan pindah alamat orang asing", "https://www.gov.kr/mw/AA020InfoCappView.do?CappBizCD=12700000026"),
    ],
    "perpanjangan-kerja": [
        ("찾기쉬운 생활법령정보: perpanjangan masa kerja (재고용)", "https://easylaw.go.kr/CSP/CnpClsMain.laf?popMenu=ov&csmSeq=2042&ccfNo=3&cciNo=2&cnpClsNo=2"),
        ("Kementerian Ketenagakerjaan: perpanjangan 1 tahun 10 bulan", "https://www.moel.go.kr/local/uijeongbu/info/dataroom/view.do?bbs_seq=20220700794"),
    ],
    "nomor-penting": [
        ("Imigrasi Korea: Pusat Informasi Orang Asing 1345", "https://www.immigration.go.kr/immigration/1530/subview.do"),
        ("HRD Korea: Pusat Konsultasi Pekerja Asing", "https://www.hrdkorea.or.kr/1/3/3/4"),
    ],
}

SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "docs")

# Halaman yang tampil di menu atas. Halaman lain ditautkan dari beranda dan footer.
NAV = ("kalkulator-gaji", "pesangon", "pengembalian-pensiun", "kalkulator-tabungan")

MONTHS_ID = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
             "Agustus", "September", "Oktober", "November", "Desember"]


def fmt_date(d):
    return f"{d.day} {MONTHS_ID[d.month - 1]} {d.year}"


def last_updated(path):
    """Tanggal commit terakhir file sumber; hari ini jika belum di-commit atau git tidak ada."""
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", path], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--", path], cwd=ROOT,
                               capture_output=True, text=True, check=True).stdout.strip()
        if out and not dirty:
            return date.fromisoformat(out)
    except (OSError, subprocess.CalledProcessError, ValueError):
        pass
    return date.today()


def page_url(slug):
    return SITE_URL + (slug + "/" if slug else "")


def nav(current, prefix):
    links = []
    for slug, _, name, *_ in PAGES:
        if slug not in NAV:
            continue
        cur = ' aria-current="page"' if slug == current else ""
        links.append(f'<a href="{prefix}{slug}/"{cur}>{name}</a>')
    links.append(f'<a href="{prefix}">Semua</a>')
    return "\n    ".join(links)


def footer_links(prefix):
    cols = []
    for key in ("kalkulator", "panduan", "situs"):
        items = [f'<li><a href="{prefix}{slug + "/" if slug else ""}">{name}</a></li>'
                 for slug, group, name, *_ in PAGES if group == key and slug]
        cols.append(f'<div><h3>{GROUPS[key]}</h3><ul>{"".join(items)}</ul></div>')
    return "\n    ".join(cols)


def related(slug, group, prefix):
    """Maksimal 4 halaman lain dari kelompok yang sama, dimulai setelah halaman ini."""
    same = [p for p in PAGES if p[1] == group and p[0] and p[0] != slug]
    if group == "situs" or not same:
        return ""
    idx = [p[0] for p in PAGES].index(slug)
    ordered = [p for p in same if [q[0] for q in PAGES].index(p[0]) > idx] + \
              [p for p in same if [q[0] for q in PAGES].index(p[0]) < idx]
    items = "".join(f'<a class="card" href="{prefix}{p[0]}/"><strong>{p[2]}</strong><br>{html.escape(p[4][:110])}…</a>'
                    for p in ordered[:4])
    return f'<h2>Halaman terkait</h2>\n<div class="tools">{items}</div>'


def sources_block(slug):
    src = SOURCES.get(slug)
    if not src:
        return ""
    items = "".join(f'<li><a href="{html.escape(u)}" rel="nofollow noopener" target="_blank">{html.escape(n)}</a></li>'
                    for n, u in src)
    return f'<div class="sources"><h2>Sumber resmi</h2><ul>{items}</ul></div>'


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


def faq_schema(body):
    """Ambil pasangan tanya-jawab dari bagian 'Pertanyaan umum' (<p><strong>Q</strong><br>A</p>)."""
    m = re.search(r"<h2>Pertanyaan umum</h2>(.*?)(?=<h2>|<script|$)", body, re.S)
    if not m:
        return None
    pairs = re.findall(r"<p><strong>(.*?)</strong><br>(.*?)</p>", m.group(1), re.S)
    if not pairs:
        return None
    return {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": strip_tags(q),
                        "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in pairs],
    }


def json_ld(slug, group, name, title, desc, body, updated):
    blocks = []
    if not slug:
        blocks.append({"@context": "https://schema.org", "@type": "WebSite", "name": SITE_NAME,
                       "url": SITE_URL, "inLanguage": "id-ID", "description": desc})
    else:
        blocks.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": SITE_NAME, "item": SITE_URL},
            {"@type": "ListItem", "position": 2, "name": name, "item": page_url(slug)}]})
        blocks.append({"@context": "https://schema.org", "@type": "WebPage", "name": title,
                       "description": desc, "url": page_url(slug), "inLanguage": "id-ID",
                       "dateModified": updated.isoformat(),
                       "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL}})
    faq = faq_schema(body)
    if faq:
        blocks.append(faq)
    return "\n".join(f'<script type="application/ld+json">{json.dumps(b, ensure_ascii=False)}</script>'
                     for b in blocks)


def render(slug, group, name, title, desc, body, updated, prefix=None):
    if prefix is None:
        prefix = "../" if slug else ""
    url = page_url(slug)
    head_extra = ""
    if CONFIG.get("google_site_verification"):
        head_extra += (f'<meta name="google-site-verification" '
                       f'content="{html.escape(CONFIG["google_site_verification"])}">\n')
    if ADSENSE_CLIENT:
        head_extra += (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
                       f'?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>\n')
    crumb = ""
    meta_line = ""
    if slug:
        crumb = (f'<nav class="crumb" aria-label="breadcrumb"><a href="{prefix}">Beranda</a> › '
                 f'<span>{GROUPS[group]}</span> › <span>{html.escape(name)}</span></nav>\n')
        meta_line = f'<p class="updated">Terakhir diperbarui: <time datetime="{updated.isoformat()}">{fmt_date(updated)}</time></p>\n'
    body = body.replace("{{prefix}}", prefix)
    # Tanggal diperbarui diletakkan tepat setelah <h1>.
    body = re.sub(r"(</h1>\n)", r"\1" + meta_line.replace("\\", "\\\\"), body, count=1)
    return f"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{url}">
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{prefix}assets/apple-touch-icon.png">
<meta name="theme-color" content="#0b7a5b">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:locale" content="id_ID">
<meta property="og:image" content="{SITE_URL}assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="{prefix}assets/style.css">
{json_ld(slug, group, name, title, desc, body, updated)}
{head_extra}</head>
<body>
<header>
  <a class="logo" href="{prefix}"><img src="{prefix}assets/favicon.svg" alt="" width="24" height="24">{SITE_NAME}</a>
  <nav>
    {nav(slug, prefix)}
  </nav>
</header>
<main>
{crumb}{body}
{sources_block(slug)}
{related(slug, group, prefix)}
</main>
<footer>
  <div class="footer-cols">
    {footer_links(prefix)}
  </div>
  <p>Hasil perhitungan adalah perkiraan dan bisa berbeda dari slip gaji atau pembayaran resmi. Situs ini bukan situs resmi pemerintah Korea atau Indonesia. Berdasarkan aturan Korea tahun 2026.</p>
  <p>&copy; {date.today().year} {SITE_NAME}</p>
</footer>
<script src="{prefix}assets/calc.js"></script>
<script src="{prefix}assets/ui.js"></script>
</body>
</html>
"""


def render_404():
    body = """<h1>Halaman tidak ditemukan</h1>
<p class="lead">Maaf, halaman yang Anda cari tidak ada atau sudah dipindahkan.</p>
<p><a href="/">Kembali ke beranda</a> untuk melihat semua kalkulator dan panduan.</p>"""
    # Halaman 404 dilayani dari path apa pun, jadi pakai path absolut dan jangan diindeks.
    page = render("", "situs", "404", f"Halaman tidak ditemukan - {SITE_NAME}",
                  "Halaman tidak ditemukan.", body, date.today(), prefix="/")
    page = page.replace('content="index, follow, max-image-preview:large"', 'content="noindex"')
    page = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', "", page)
    page = re.sub(r'<link rel="canonical"[^>]*>\n', "", page)
    return page


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(os.path.join(SRC, "assets"), os.path.join(OUT, "assets"))
    lastmods = {}
    for slug, group, name, title, desc in PAGES:
        src = os.path.join(SRC, "pages", (slug or "index") + ".html")
        with open(src, encoding="utf-8") as f:
            body = f.read()
        updated = last_updated(src)
        lastmods[slug] = updated
        target = os.path.join(OUT, slug) if slug else OUT
        os.makedirs(target, exist_ok=True)
        with open(os.path.join(target, "index.html"), "w", encoding="utf-8") as f:
            f.write(render(slug, group, name, title, desc, body, updated))
    with open(os.path.join(OUT, "404.html"), "w", encoding="utf-8") as f:
        f.write(render_404())

    urls = "\n".join(
        f"  <url><loc>{page_url(slug)}</loc><lastmod>{lastmods[slug].isoformat()}</lastmod></url>"
        for slug, *_ in PAGES)
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                f"{urls}\n</urlset>\n")
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n")
    if ADSENSE_CLIENT:
        pub = ADSENSE_CLIENT.replace("ca-", "")
        with open(os.path.join(OUT, "ads.txt"), "w", encoding="utf-8") as f:
            f.write(f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n")
    if CONFIG.get("custom_domain"):
        with open(os.path.join(OUT, "CNAME"), "w", encoding="utf-8") as f:
            f.write(CONFIG["custom_domain"] + "\n")
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    print(f"built {len(PAGES)} pages + 404 -> {OUT}")


if __name__ == "__main__":
    main()
