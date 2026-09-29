# 월급계산소

2026년 4대보험 요율과 최저임금을 반영한 무료 급여 계산기 사이트예요. 검색 유입을 받아 광고(Google AdSense)로 수익을 내는 것이 목표예요.

- 연봉 실수령액 계산기 (`/salary/`)
- 주휴수당 계산기 (`/weekly-holiday-pay/`)
- 퇴직금 계산기 (`/severance/`)
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

## 수익화 순서 (직접 하셔야 하는 일)

1. **공개하기**: 이 브랜치를 `main` 에 병합한 뒤, GitHub 저장소 Settings → Pages 에서 Source 를 `main` 브랜치의 `/docs` 폴더로 지정해요. 몇 분 뒤 `https://ehwa2006.github.io/mm/` 에서 열려요.
2. **도메인 연결 (약 1~2만 원/년)**: AdSense 는 `github.io` 같은 남의 도메인을 승인하지 않아서 직접 소유한 도메인이 필요해요. 도메인을 사서 Pages 설정의 Custom domain 에 입력하고, `SITE_URL=https://내도메인/ npm run build` 로 다시 빌드해요.
3. **검색 등록**: [Google Search Console](https://search.google.com/search-console)과 [네이버 서치어드바이저](https://searchadvisor.naver.com)에 사이트를 등록하고 `sitemap.xml` 을 제출해요. 한국 검색 유입의 상당 부분이 네이버라서 둘 다 해야 해요.
4. **AdSense 신청**: [AdSense](https://adsense.google.com)에 사이트를 등록해요. 승인되면 받은 게시자 ID로 `ADSENSE_CLIENT=ca-pub-XXXXXXXX SITE_URL=https://내도메인/ npm run build` 를 실행해 광고 스크립트와 `ads.txt` 를 넣고 커밋해요.
5. **정산 정보**: AdSense 에 지급 계좌와 세금 정보를 입력해요. 누적 수익이 100달러를 넘으면 지급돼요.

## 현실적인 기대치

- 검색엔진에 색인되고 순위가 오르기까지 보통 1~3개월 걸려요.
- 급여 계산기는 경쟁이 심한 분야라서 처음에는 방문자가 적어요. 계산기 종류를 계속 늘려서 롱테일 키워드를 잡는 전략이에요.
- 한국 트래픽 기준으로 방문 1,000회당 광고 수익은 대략 1~5천 원 수준이에요. 월 10만 원을 벌려면 월 수만 회 방문이 필요해요.

## 다음에 추가할 계산기 후보

실업급여, 연차 일수·연차수당, 야간·연장근로수당, 4대보험(사업주 부담 포함), 프리랜서 3.3% 환급, 연말정산 환급 예상, 육아휴직 급여, 전월세 전환율, 중도상환수수료.
