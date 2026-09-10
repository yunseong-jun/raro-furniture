# DESIGN.md: Article × Floyd (참조 디자인 시스템)

라로퍼니처 리디자인의 시각 언어를 정하기 위해 두 참조 사이트에서 추출한 디자인 시스템. 관측값과 추정값을 구분해 표기한다.

## Source
- Article: https://www.article.com/ (홈), /category/dining-tables (목록), /product/24178/... (상세)
- Floyd: https://floydhome.com/ (홈), /collections/tables (목록), /products/the-floyd-adjustable-base (상세)
- Capture date: 2026-09-10
- Evidence: Firecrawl `branding` 포맷 JSON, 풀페이지 스크린샷(1920px), 페이지 마크다운
- 원본 파일: `.firecrawl/ref/` (article-branding.json, floyd-branding.json, *-screenshot.png, *-home.md, *-plp.md, *-pdp.md)

## Reference Screenshots
![Article 홈 풀페이지](../../.firecrawl/ref/article-screenshot.png)
![Floyd 홈 풀페이지](../../.firecrawl/ref/floyd-screenshot.png)

레이아웃, 위계, 밀도, 분위기는 스크린샷을 기준으로 삼는다. 아래 토큰은 같은 화면을 기계가 읽을 수 있게 옮긴 것이다.

---

## 1. Article

### Design Summary
흰 바탕, 큰 라이프스타일 사진, 굵은 산세리프 헤드라인, 알약(pill) 버튼. "쇼룸을 사진으로 걷는" 느낌. 상품 카드는 연회색 타일 위에 제품만 놓고 이름·가격을 작게 단다. 카피는 짧은 문장 + 마침표("A lesson in leather.").

### Colors (관측)
| 역할 | 값 | 비고 |
|---|---|---|
| 배경 | `#FFFFFF` | |
| 본문 텍스트 | `#2E2E2E` | 순검정 대신 진회색 |
| 상품 타일 배경 | `#F2F2F2` (추정) | 스크린샷 기준 |
| 보더/인풋 | `#C2C2C2` | |
| 브랜드 액센트 | `#F1655B` (코랄) | 로고의 점, 뉴스레터 버튼에만 사용. 면적 아주 작음 |
| 푸터 | `#2B2B2B` (추정) | 다크 푸터, 흰 글자 |

### Typography (관측)
- 서체: Proxima Nova (Regular/Bold). 폴백 시스템 산세리프.
- 헤드라인 H2 약 48px, 굵기 700, 자간 약간 좁게, 문장 끝 마침표.
- 본문 16~18px, 행간 1.5.
- 상품명 13~14px, 회색 `#5A5A5A` (추정). 가격 같은 크기, 진회색.
- 내비게이션 13px, 대문자 아님.

### Spacing & Layout (관측 + 추정)
- 기본 단위 4px. 컨테이너 최대 약 1760px(거의 풀 폭), 좌우 패딩 80px.
- 섹션 간격 약 96~120px.
- 그리드: 상품 6열(데스크톱), 갭 24px. "Shop by room" 6열 썸네일 행.
- 모서리: 카드 4px, 버튼 500px(완전 알약).
- 그림자 없음. 선(border)도 거의 없음. 여백으로 구획.

### Components
- **히어로**: 풀블리드 사진 + 중앙 정렬 헤드라인/서브카피 + 흰 알약 버튼(대문자, 자간 넓게).
- **Shop By Room**: 작은 가로 썸네일 6개 + 캡션. 진입 동선의 핵심.
- **프로모 2단 카드**: 사진 위 텍스트 오버레이 + 흰 알약 버튼.
- **띠 배너(CTA band)**: 검정 배경 풀폭, "Get a free design plan." + 흰 알약.
- **상품 카드**: 연회색 정사각 타일 안에 제품, 아래 이름·가격 2줄. 하트(찜) 아이콘.
- **UGC 섹션**: "Great style in the wild." 고객 사진 3열.
- **상품 상세**: 좌측 큰 이미지 갤러리, 우측 스티키 구매 패널(이름, 가격, 옵션, 배송 정보, CTA). 아래로 소재·치수·"You might also like"·같은 컬렉션 제품.
- **푸터**: 다크 배경, 4열 링크 + 뉴스레터 인풋 + 코랄 버튼.

### Content Style
- 짧은 헤드라인 + 마침표. 유머 살짝("Your fave just got even better.").
- CTA는 대문자 "SHOP ○○○".

---

## 2. Floyd

### Design Summary
크림색 종이 같은 바탕(`#F8F6ED`), 사진이 화면을 크게 차지하고 텍스트는 작고 절제됨. 아주 작은 대문자 모노스페이스 라벨("SHOP DESIGN SYSTEMS", "NEW ARRIVAL:")이 섹션마다 붙어 편집 디자인 느낌을 만든다. 버튼은 얇은 외곽선 사각형. 푸터에 거대한 워드마크 "FLOYD".

### Colors (관측)
| 역할 | 값 | 비고 |
|---|---|---|
| 배경 | `#F8F6ED` | 크림. 전 페이지 공통 |
| 본문 텍스트 | `#231E1E` | 따뜻한 먹색 |
| 패널/서브 배경 | `#DACCBA` | 탄(모래색). 멤버십·트레이드 섹션 배경 |
| 액센트 | `#1990C6` / `#136F99` | 링크·강조. 면적 작음 |
| 인풋 보더 | `#605F5E` | |
| 푸터 워드마크 | `#8C8A82` (추정) | 회갈색 |

### Typography (관측)
- 헤드라인/본문: Floyd Gothic (자체 서체, 그로테스크 산세리프). 폴백 Arial/Helvetica.
- 라벨: GT America Mono, 10~11px, 대문자, 자간 0.08em.
- H1 약 64px(히어로), H2 28px, 본문 12~14px. 텍스트가 전반적으로 작고 사진이 크다.
- 브랜드 스테이트먼트 단락: 24~28px, 중앙 정렬, 최대 폭 약 720px.

### Spacing & Layout (관측 + 추정)
- 기본 단위 12px. 컨테이너 풀폭, 좌우 패딩 48px.
- 섹션 간격 120~160px. 여백이 매우 넉넉함.
- 그리드: 컬렉션 카드 3열(갭 24px). 상품 목록 3~4열.
- 모서리: 2~3px. 거의 직각.
- 50/50 분할 섹션(사진 반, 텍스트 반)이 반복. 텍스트 쪽은 라벨 → 제목 → 2~3줄 설명 → 외곽선 버튼.
- 그림자 없음.

### Components
- **히어로**: 풀블리드 사진, 좌상단에 작은 H1(2줄) + 외곽선 버튼. 텍스트가 사진을 가리지 않음.
- **스테이트먼트**: 배경색 그대로, 중앙에 브랜드 문장 1개(창립 스토리).
- **컬렉션 카드 3열**: 사진 + 밑줄 링크 텍스트("The Bed Frame →").
- **50/50 피처**: 라벨 + 제목 + 설명 + 버튼 / 사진.
- **탄 색 패널**: 멤버십, 파트너 섹션. 배경 `#DACCBA`.
- **상품 상세**: 이름, 옵션(Size), Subtotal, CTA. 아래로 "Seamlessly integrated comfort." 같은 피처 섹션 3~4개.
- **푸터**: 거대 워드마크 + 4열 링크 + 뉴스레터.

### Content Style
- 브랜드 목소리 강함("We make furniture for keeping.").
- 섹션 라벨은 대문자 모노 + 콜론("NEW ARRIVAL:").
- 헤드라인은 문장형, 마침표.

---

## 3. 라로퍼니처에 적용할 혼합 원칙 (제안)

1. **바탕은 Floyd의 크림, 상품 타일은 Article의 연회색.** 크림 배경이 원목·세라믹 사진의 따뜻함을 살리고, 상품 타일은 밝은 회색으로 제품을 또렷하게.
2. **라벨은 Floyd, 헤드라인은 Article.** 작은 대문자 라벨("BEST SELLERS", "NEW ARRIVAL:")로 편집 느낌을 주고, 헤드라인은 크고 굵게 문장형으로.
3. **버튼**: 방향 시안에서 알약(Article) vs 외곽선 사각(Floyd)을 사용자에게 고르게 한다.
4. **정보 구조는 Article**: 카테고리 썸네일 행(거실/식탁/의자/침실), 베스트셀러 그리드, 상품 상세의 스티키 구매 패널.
5. **섹션 리듬은 Floyd**: 50/50 분할 피처(브랜드 스토리, 친환경 소재, 쇼룸 안내), 넉넉한 세로 여백.
6. **한글 서체**: Pretendard(본문·UI), 헤드라인은 Pretendard 700 또는 세리프(Noto Serif KR) 중 시안으로 결정. 라벨은 JetBrains Mono 또는 Pretendard 대문자 자간 넓게.
7. **액센트 색은 하나만, 작게**: 라로퍼니처 상품군에 맞춰 월넛/테라코타 계열 후보. 세일·뱃지에만.

## Agent Build Instructions
- 정적 HTML/CSS/JS. CSS 변수로 토큰 정의(`--bg`, `--tile`, `--ink`, `--accent`, `--panel`).
- 폰트: Pretendard(jsdelivr), 필요 시 Noto Serif KR(Google Fonts).
- 그림자 금지, 보더 최소화, 여백으로 구획. 섹션 간격 96px 이상.
- 상품 카드: 1:1 타일, 이미지 `object-fit: contain`, 이름 2줄 말줄임, 가격 굵게.
- 상품 상세: 데스크톱 2단(갤러리 7 : 패널 5), 패널 `position: sticky`.
- 모바일: 1열/2열 그리드, 하단 고정 구매 바.

## 권리 고지
Article, Floyd의 로고·사진·카피는 각 사의 자산이다. 이 문서는 레이아웃·색·타이포 패턴만 참조하며, 어떤 자산도 복제하지 않는다. 라로퍼니처의 상품 이미지와 문구는 (주)퍼니우스의 자산이며, 실제 사이트 적용 목적의 시안에서만 사용한다.

## Rerun Inputs
workflow: firecrawl-website-design-clone
source_url: https://www.article.com/, https://floydhome.com/
target_stack: static HTML/CSS/JS (고도몰 스킨 이식 전제)
output: docs/reference/DESIGN-article-floyd.md
