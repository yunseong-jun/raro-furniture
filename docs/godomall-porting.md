# 고도몰 스킨 이식 가이드

이 프로토타입은 고도몰(NHN커머스) 스킨 구조에 맞춰 만들었다. 관리자 권한이 생기면 아래 순서로 옮긴다. 현재 스킨 이름은 `mplshop`(기본 제공 스킨 커스텀본)이다.

## 0. 준비
1. 관리자 > 디자인 > 디자인 스킨 관리에서 현재 스킨을 **복사**해 작업용 스킨을 만든다. 라이브 스킨을 직접 고치지 않는다.
2. `assets/style.css` → 스킨의 `css/raro.css`, `assets/app.js` → `js/raro.js`, `assets/logo-header.png`·`company-story.jpg`·`banner-interior.jpg` → `img/` 로 업로드.
3. `layout/header.html`의 `<head>`에 Pretendard·JetBrains Mono 링크와 `raro.css`를, `layout/footer.html` 끝에 `raro.js`를 추가한다. 기존 스킨 CSS와 충돌하는 규칙은 `raro.css`가 나중에 로드되도록 순서를 맞춘다.

## 1. 블록 → 스킨 파일 대응
| 프로토타입 블록 | 스킨 파일 | 옮기는 방법 |
|---|---|---|
| 헤더(로고·검색·유틸·카테고리 메뉴·드로어) | `layout/header.html` | `RARO.headerHTML()` 출력 마크업을 그대로 붙이고, 카테고리 `<li>` 반복부만 고도몰 카테고리 변수(`{{category}}`) 루프로 교체. 검색 폼 `action`은 `../goods/goods_search.php`, 인풋 `name="keyword"`. |
| 푸터 | `layout/footer.html` | `RARO.footerHTML()` 마크업. 사업자 정보는 고도몰 기본 정보 변수(`{{gGlobal.info}}`)로 교체. 운영시간 문구는 실제 값으로. |
| 메인 히어로 | `main/index.html` | 메인 배너 위젯(관리자 > 디자인 > 배너)으로 슬라이드 2장 등록. 마크업은 `.hero__slide` 유지. |
| 메인 공간별 둘러보기 | `main/index.html` | 정적 HTML. 카테고리 코드 링크 그대로. |
| 메인 특가 / 베스트 / 신제품 | `main/index.html` | 메인 상품 진열 위젯 3개(타임세일·베스트·신상품). 반복부 `<li>` 안을 `RARO.cardHTML()` 마크업으로 교체하고 이미지·이름·가격을 위젯 변수(`{{goods.goodsNm}}`, `{{goods.goodsPrice}}`, `{{goods.fixedPrice}}`)로. 할인율은 `raro.js`의 `discountRate`로 계산. |
| 메인 브랜드 띠 | `main/index.html` | 정적 HTML. |
| 메인 고객의 공간 | `main/index.html` | 리뷰 게시판 위젯(`_board_article.html`) 반복부를 `.review` 마크업으로 교체. 룩북은 룩북 게시판 최신 1건. |
| 목록 카테고리 헤더 | `goods/goods_list.html` | 카테고리명 `{{cateNm}}`. 설명·가이드 문구는 관리자 카테고리 설명란에 넣고 변수로 출력. |
| 목록 필터·정렬·그리드 | `goods/goods_list.html` | 정렬은 고도몰 `sort` 파라미터 링크로 교체(추천 `sort=g.sortNo desc`, 인기 `g.orderCnt desc`, 가격 `g.goodsPrice asc/desc`, 상품평 `g.reviewCnt desc`, 최신 `g.regDt desc`). 필터는 1차 이식에서는 소분류 칩만 서버 링크로 두고, 사이즈·소재 필터는 클라이언트 필터(`raro.js` `applyFilters`)로 현재 페이지 상품에만 적용. 완전한 서버 필터는 2단계. 프로토타입의 "판매인기순/상품평순"은 리뷰 수 기준 근사치이므로 서버 정렬로 대체한다. |
| 목록 가이드 띠 | `goods/goods_list.html` | 정적 HTML, 카테고리 코드별 분기. |
| 상세 갤러리·구매 패널 | `goods/goods_view.html` | 갤러리는 고도몰 `detailKeyID` 이미지 배열 유지, 썸네일 마크업만 `.gallery__thumbs`. 구매 패널은 **고도몰 옵션 스크립트(`goodsViewController`)와 hidden input을 그대로 두고** 마크업만 교체. 카드형 라디오는 `<select name="optionNo_0">`/`optionSnoInput`를 숨기고 클릭 시 `select.value`를 바꾼 뒤 `change` 이벤트를 발생시켜 고도몰 가격 계산을 그대로 쓴다. |
| 상세 탭 | `goods/goods_view.html` | 기존 `.item_goods_tab` 마크업을 `.ptabs`로. 프로토타입은 상세정보·사양·배송(교환·반품 포함)·리뷰·Q&A 5개 탭으로 앵커가 `#sec-detail` `#sec-spec` `#sec-ship` `#sec-review` `#sec-qna`다. 원본 스킨 탭 수(보통 4개: 상세정보/상품평/상품문의/교환반품)와 다르면 배송·교환·반품을 한 탭으로 합치거나 스킨 탭 위젯 구조에 맞춰 앵커 이름을 다시 매핑한다. |
| 상세 특징 / 사양 | `goods/goods_view.html` | 특징 3개는 카테고리별 기본 문구(`data/build.py`의 `FEATURES`)를 상품 요약 설명 필드로 옮긴다. 사양 표는 상품정보고시 변수 출력에서 "상세페이지 참조" 값을 `raro.js`가 숨긴다. |
| 상세 이미지 | `goods/goods_view.html` | 기존 상세 설명 영역(`{{goodsDescription}}`)을 `.detail-imgs`로 감싼다. |
| 상세 리뷰·함께 보기 | `goods/goods_view.html` | 리뷰 위젯 + 관련상품 위젯(`RELATED ITEMS`) 반복부를 카드 마크업으로. 별점 평균은 리뷰 위젯 변수로 표시. |
| 브랜드 | `service/company.html` | 정적 HTML. 쇼룸 지도는 카카오맵 JavaScript API 키 발급 후 `.map`에 삽입. `company2.html`(HISTORY)은 메뉴에서 제거, `company3.html`(오시는 길)은 `company.html#showroom`으로 리다이렉트. |

## 2. 제거할 기존 요소
`layout/header.html`의 공지 티커·즐겨찾기·회원가입 포인트, 좌측 퀵메뉴(`quickLogo`·`quickNotice`·배송조회·택배사 링크), `main/index.html`의 HIT PRODUCT·추천상품 배너·Youtube_Movie·INSTAGRAM 섹션, 인트로 팝업, 비밀번호 인증 레이어(주문조회 페이지로 이동).

## 3. 데이터 연결 규칙
- 프로토타입 `data/site.json`의 필드와 고도몰 변수 대응: `no`↔`goodsNo`, `name`↔`goodsNm`, `price`↔`goodsPrice`, `listPrice`↔`fixedPrice`, `image`↔`goods.image` 400px, `imageLarge`↔1000px 상세 이미지, `reviewCount`↔`reviewCnt`, `colors`↔상품 색상 옵션, `tags`(무료배송·품절)↔상품 아이콘/품절 상태, `cates`↔상품이 속한 모든 카테고리.
- `raro.js`는 `data/site.json`을 fetch하지 않도록 `loadData`를 서버 렌더 값으로 대체한다: 각 페이지에서 `window.RARO_DATA = {...}`를 템플릿이 출력하고 `loadData`는 이 객체를 반환하게 한 줄만 바꾼다.
- 프로토타입에서 "실제 사이트 연동 시 표시"로 표기한 값(옵션 2단계, 리뷰 별점 평균, 치수 도면)은 이식 시 해당 고도몰 변수로 채운다.

## 4. 확인이 필요한 사실
쇼룸 운영시간·주차, 고객센터 운영시간, 교환·반품 정책 문구, 설치 서비스 범위는 사이트에서 확인되지 않아 프로토타입에 넣지 않았다. 이식 전에 담당자에게 확인해 채운다.

## 5. 검증
스킨 미리보기 URL로 `tools/screenshot.ps1`을 `BASE=<미리보기 URL>` 환경변수로 실행해 같은 12장을 찍고 프로토타입 스크린샷(`docs/screenshots/`)과 비교한다.
