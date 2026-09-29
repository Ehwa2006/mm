#!/usr/bin/env python3
"""Membungkus isi halaman di src/pages dengan tata letak bersama dan menulis situs statis ke docs/.

Untuk menambah kalkulator: buat src/pages/<slug>.html lalu tambahkan satu baris di PAGES.
"""
import html
import json
import os
import shutil
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
# site.json: domain, ID penayang AdSense (ca-pub-...), kode verifikasi Search Console.
with open(os.path.join(ROOT, "site.json"), encoding="utf-8") as _f:
    CONFIG = json.load(_f)
SITE_URL = (f"https://{CONFIG['custom_domain']}/" if CONFIG.get("custom_domain")
            else CONFIG["site_url"])
SITE_NAME = "Hitung Gaji Korea"
ADSENSE_CLIENT = CONFIG.get("adsense_client", "")

# (slug, nama menu, <title>, meta description)
PAGES = [
    ("", "Beranda", f"{SITE_NAME} - Kalkulator Gaji TKI/EPS di Korea 2026",
     "Kalkulator gratis untuk pekerja Indonesia di Korea Selatan: gaji bersih dengan lembur, pesangon (퇴직금), dan pengembalian pensiun (반환일시금). Standar 2026."),
    ("kalkulator-gaji", "Gaji Bersih", "Kalkulator Gaji Korea 2026 - Gaji Bersih + Lembur untuk TKI EPS",
     "Hitung gaji bersih di Korea 2026 dari upah per jam, lembur, jam malam, dan kerja hari libur. Potongan pensiun, asuransi, pajak, dan asrama. Konversi ke Rupiah."),
    ("pesangon", "Pesangon", "Kalkulator Pesangon Korea (퇴직금) & Asuransi Kepulangan TKI",
     "Hitung perkiraan pesangon (퇴직금) di Korea dan berapa yang dibayar asuransi kepulangan (출국만기보험) serta selisih dari majikan."),
    ("pengembalian-pensiun", "Pengembalian Pensiun", "Kalkulator Pengembalian Pensiun Korea (반환일시금) untuk TKI",
     "Perkirakan uang pensiun nasional Korea (국민연금) yang bisa diklaim kembali saat pulang ke Indonesia, termasuk iuran majikan dan bunga."),
    ("uang-libur-mingguan", "Uang Libur Mingguan", "Kalkulator Uang Libur Mingguan Korea (주휴수당) 2026",
     "Hitung uang libur mingguan (주휴수당) di Korea: syarat 15 jam per minggu, rumus, dan contoh dengan upah minimum 2026."),
    ("cuti-tahunan", "Cuti Tahunan", "Kalkulator Cuti Tahunan Korea (연차) dan Uang Pengganti Cuti",
     "Hitung jumlah hari cuti tahunan berbayar di Korea (maksimal 25 hari) dan uang pengganti cuti yang tidak terpakai (연차수당)."),
    ("pindah-kerja", "Pindah Kerja", "Aturan Pindah Tempat Kerja E-9 di Korea (사업장 변경) 2026",
     "Batas 3 kali pindah kerja, alasan yang diizinkan, batas wilayah, dan batas waktu 1 dan 3 bulan untuk pekerja EPS/E-9 di Korea."),
    ("upah-minimum", "Upah Minimum", "Upah Minimum Korea 2026: ₩10.320 per Jam, Tabel 2020–2026",
     "Upah minimum Korea 2026 adalah ₩10.320 per jam atau ₩2.156.880 per bulan. Tabel upah minimum 2020–2026 dan konversi ke Rupiah."),
    ("tunjangan-pengangguran", "Tunjangan Pengangguran", "Kalkulator Tunjangan Pengangguran Korea (실업급여) untuk Pekerja E-9 2026",
     "Hitung tunjangan pengangguran (구직급여) di Korea: maksimal ₩68.100 per hari, 120–270 hari. Syarat khusus pekerja E-9 dan cara mendaftar."),
    ("kecelakaan-kerja", "Kecelakaan Kerja", "Kecelakaan Kerja di Korea (산재): Hak Pekerja Asing dan Cara Klaim",
     "Semua pekerja asing di Korea dilindungi asuransi kecelakaan kerja (산재보험): biaya pengobatan, 70% upah selama tidak bisa kerja, dan cara klaim sendiri."),
    ("asuransi-kesehatan", "Asuransi Kesehatan", "Asuransi Kesehatan Korea (건강보험) untuk Pekerja E-9 2026",
     "Potongan asuransi kesehatan Korea 2026 (3,595%), manfaat, dan pengembalian premi saat pindah kerja atau pulang ke Indonesia."),
    ("asuransi-khusus-eps", "4 Asuransi EPS", "4 Asuransi Khusus Pekerja EPS di Korea (외국인 전용보험)",
     "Asuransi kepulangan, jaminan upah, biaya pulang, dan kecelakaan untuk pekerja E-9: siapa yang bayar, batas waktu daftar, dan cara klaim saat pulang."),
    ("tentang", "Tentang", f"Tentang {SITE_NAME}",
     f"Tentang {SITE_NAME}: kalkulator gratis dalam bahasa Indonesia untuk pekerja di Korea Selatan."),
    ("kebijakan-privasi", "Kebijakan Privasi", f"Kebijakan Privasi - {SITE_NAME}",
     f"Kebijakan privasi {SITE_NAME}."),
]

SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "docs")


# Halaman yang tampil di menu atas. Halaman lain ditautkan dari beranda.
NAV = ("kalkulator-gaji", "pesangon", "pengembalian-pensiun", "tunjangan-pengangguran")


def nav(current, depth):
    prefix = "../" * depth
    links = []
    for slug, name, *_ in PAGES:
        if slug not in NAV:
            continue
        cur = ' aria-current="page"' if slug == current else ""
        links.append(f'<a href="{prefix}{slug}/"{cur}>{name}</a>')
    links.append(f'<a href="{prefix}">Semua</a>')
    return "\n    ".join(links)


def render(slug, title, desc, body):
    depth = 1 if slug else 0
    prefix = "../" * depth
    url = SITE_URL + (slug + "/" if slug else "")
    head_extra = ""
    if CONFIG.get("google_site_verification"):
        head_extra += (f'<meta name="google-site-verification" '
                       f'content="{html.escape(CONFIG["google_site_verification"])}">\n')
    if ADSENSE_CLIENT:
        head_extra += (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
                       f'?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>')
    return f"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:locale" content="id_ID">
<link rel="stylesheet" href="{prefix}assets/style.css">
{head_extra}
</head>
<body>
<header>
  <a class="logo" href="{prefix}">{SITE_NAME}</a>
  <nav>
    {nav(slug, depth)}
  </nav>
</header>
<main>
{body.replace("{{prefix}}", prefix)}
</main>
<footer>
  <p>Hasil perhitungan adalah perkiraan dan bisa berbeda dari slip gaji atau pembayaran resmi. Berdasarkan aturan Korea tahun 2026.</p>
  <p><a href="{prefix}tentang/">Tentang</a> · <a href="{prefix}kebijakan-privasi/">Kebijakan Privasi</a> · &copy; {date.today().year} {SITE_NAME}</p>
</footer>
<script src="{prefix}assets/calc.js"></script>
<script src="{prefix}assets/ui.js"></script>
</body>
</html>
"""


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(os.path.join(SRC, "assets"), os.path.join(OUT, "assets"))
    for slug, _, title, desc in PAGES:
        name = slug or "index"
        with open(os.path.join(SRC, "pages", name + ".html"), encoding="utf-8") as f:
            body = f.read()
        target = os.path.join(OUT, slug) if slug else OUT
        os.makedirs(target, exist_ok=True)
        with open(os.path.join(target, "index.html"), "w", encoding="utf-8") as f:
            f.write(render(slug, title, desc, body))

    today = date.today().isoformat()
    urls = "\n".join(
        f"  <url><loc>{SITE_URL}{slug + '/' if slug else ''}</loc><lastmod>{today}</lastmod></url>"
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
    print(f"built {len(PAGES)} pages -> {OUT}")


if __name__ == "__main__":
    main()
