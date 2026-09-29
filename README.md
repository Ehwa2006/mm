# 월급계산소

2026년 4대보험 요율과 최저임금을 반영한 무료 급여 계산기 사이트예요. 검색 유입을 받아 광고(Google AdSense)로 수익을 내는 것이 목표예요.

- 연봉 실수령액 계산기 (`/salary/`)
- 주휴수당 계산기 (`/weekly-holiday-pay/`)
- 퇴직금 계산기 (`/severance/`)
- 실업급여 계산기 (`/unemployment/`)
- 연차 계산기 (`/annual-leave/`)
- 시급·월급·연봉 변환기 (`/wage-converter/`)

서버 없이 동작하는 정적 사이트라서 호스팅 비용이 없어요. 계산은 모두 브라우저에서 이루어져요.

## 구조

```
src/assets/calc.js   계산 로직 (브라우저와 Node 테스트에서 함께 사용)
src/pages/*.html     페이지 본문
build.py             공통 레이아웃을 입혀 docs/ 에 사이트를 생성
docs/                배포용 결과물 (GitHub Pages가 이 폴더를 서비스)
tests/               계산 로직 테스트
```

```
npm run build   # docs/ 재생성
npm test        # 계산 로직 테스트
```

`src/` 를 고친 뒤에는 반드시 `npm run build` 를 실행해서 `docs/` 까지 함께 커밋해야 해요.

## 설정 (`site.json`)

| 키 | 내용 |
| --- | --- |
| `custom_domain` | 연결한 도메인 (예: `wolgeup.kr`). 채우면 `CNAME` 이 생성되고 모든 주소가 이 도메인으로 바뀐다 |
| `adsense_client` | AdSense 게시자 ID (`ca-pub-...`). 채우면 광고 스크립트와 `ads.txt` 가 생성된다 |
| `google_site_verification` | Google Search Console HTML 태그 소유확인 코드 |
| `naver_site_verification` | 네이버 서치어드바이저 HTML 태그 소유확인 코드 |

값을 바꾼 뒤 `npm run build` 하고 `docs/` 까지 커밋한다.

## 수익화 순서

사람이 직접 해야 하는 일(계정·본인인증·결제·계좌)만 ☐ 로 표시했다. 나머지는 코드로 처리한다.

1. ☐ 저장소를 공개(public)로 전환하고 Settings → Pages 에서 Source 를 기본 브랜치의 `/docs` 로 지정 (비공개 저장소는 유료 플랜에서만 Pages 사용 가능)
2. ☐ 도메인 구입 (연 1~2만 원). AdSense 는 `github.io` 주소를 승인하지 않는다
3. ☐ 도메인 업체 DNS 에 GitHub Pages 레코드 입력: A 레코드 `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` / `www` CNAME `ehwa2006.github.io`
4. `site.json` 의 `custom_domain` 설정 후 빌드
5. ☐ Google Search Console·네이버 서치어드바이저 가입 후 HTML 태그 소유확인 코드 발급
6. `site.json` 에 소유확인 코드 입력 후 빌드, 두 곳에 `sitemap.xml` 제출
7. ☐ AdSense 가입, 본인인증, 게시자 ID 발급
8. `site.json` 의 `adsense_client` 설정 후 빌드
9. ☐ AdSense 승인 후 지급 계좌·세금 정보 등록. 누적 100달러부터 지급

## 현실적인 기대치

- 검색엔진에 색인되고 순위가 오르기까지 보통 1~3개월 걸려요.
- 급여 계산기는 경쟁이 심한 분야라서 처음에는 방문자가 적어요. 계산기 종류를 계속 늘려서 롱테일 키워드를 잡는 전략이에요.
- 한국 트래픽 기준으로 방문 1,000회당 광고 수익은 대략 1~5천 원 수준이에요. 월 10만 원을 벌려면 월 수만 회 방문이 필요해요.

## 다음에 추가할 계산기 후보

야간·연장근로수당, 4대보험(사업주 부담 포함), 프리랜서 3.3% 환급, 연말정산 환급 예상, 육아휴직 급여, 전월세 전환율, 중도상환수수료.
