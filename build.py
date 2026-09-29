#!/usr/bin/env python3
"""src/ 의 페이지 본문을 공통 레이아웃으로 감싸 docs/ 에 정적 사이트를 생성한다.

새 계산기를 추가하려면 src/pages/<slug>.html 을 만들고 PAGES 에 한 줄 추가하면 된다.
"""
import html
import os
import shutil
from datetime import date

SITE_URL = os.environ.get("SITE_URL", "https://ehwa2006.github.io/mm/")
SITE_NAME = "월급계산소"
# 애드센스 승인 후 게시자 ID(ca-pub-...)를 넣으면 모든 페이지에 광고 스크립트가 들어간다.
ADSENSE_CLIENT = os.environ.get("ADSENSE_CLIENT", "")

# (slug, 메뉴 이름, <title>, meta description)
PAGES = [
    ("", "홈", f"{SITE_NAME} - 2026 연봉 실수령액·주휴수당·퇴직금 계산기",
     "2026년 4대보험 요율과 최저임금을 반영한 무료 급여 계산기 모음. 연봉 실수령액, 주휴수당, 퇴직금, 시급·월급 변환을 한 곳에서."),
    ("salary", "연봉 실수령액", "2026 연봉 실수령액 계산기 - 4대보험·소득세 공제 후 월급",
     "연봉을 입력하면 2026년 국민연금 4.75%, 건강보험 3.595%, 장기요양, 고용보험, 소득세를 공제한 월 실수령액을 바로 계산합니다."),
    ("weekly-holiday-pay", "주휴수당", "2026 주휴수당 계산기 - 알바 주휴수당 조건과 계산법",
     "주 15시간 이상 근무하면 받는 주휴수당을 시급과 주 근무시간으로 계산합니다. 2026년 최저시급 10,320원 기준."),
    ("severance", "퇴직금", "퇴직금 계산기 - 평균임금으로 예상 퇴직금 계산",
     "입사일, 마지막 근무일, 최근 3개월 급여를 입력하면 1일 평균임금과 예상 퇴직금을 계산합니다."),
    ("wage-converter", "시급·월급 변환", "시급 월급 연봉 변환기 - 2026 최저임금 확인",
     "시급, 월급, 연봉을 서로 변환하고 2026년 최저임금(시급 10,320원, 월 2,156,880원) 미달 여부를 확인합니다."),
    ("privacy", "개인정보처리방침", f"개인정보처리방침 - {SITE_NAME}",
     f"{SITE_NAME}의 개인정보처리방침입니다."),
]

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "docs")


def nav(current, depth):
    prefix = "../" * depth
    links = []
    for slug, name, *_ in PAGES:
        if slug in ("", "privacy"):
            continue
        cur = ' aria-current="page"' if slug == current else ""
        links.append(f'<a href="{prefix}{slug}/"{cur}>{name}</a>')
    return "\n    ".join(links)


def render(slug, title, desc, body):
    depth = 1 if slug else 0
    prefix = "../" * depth
    url = SITE_URL + (slug + "/" if slug else "")
    ads = ""
    if ADSENSE_CLIENT:
        ads = (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
               f'?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>')
    return f"""<!doctype html>
<html lang="ko">
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
<link rel="stylesheet" href="{prefix}assets/style.css">
{ads}
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
  <p>계산 결과는 참고용 추정치이며 실제 급여·세액과 다를 수 있습니다. 2026년 요율 기준.</p>
  <p><a href="{prefix}privacy/">개인정보처리방침</a> · &copy; {date.today().year} {SITE_NAME}</p>
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
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    print(f"built {len(PAGES)} pages -> {OUT}")


if __name__ == "__main__":
    main()
