# 라로퍼니처 UI 리디자인 1단계 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 라로퍼니처 사이트의 실제 상품 데이터를 수집해, Article × Floyd 방향(B안 "화이트 쇼룸")으로 다시 설계한 핵심 4페이지(메인·상품목록·상품상세·브랜드)를 정적 HTML/CSS/JS 프로토타입으로 만든다.

**Architecture:** `data/build.py`가 현재 사이트 HTML을 직접 요청해 `data/site.json` 하나로 정리한다. 4개 HTML은 정적 틀(헤더·푸터·섹션)만 갖고, 반복 요소(카드·필터·옵션·갤러리)는 `assets/app.js`가 JSON을 `fetch`해 렌더링한다. 스타일은 `assets/style.css` 한 파일에 CSS 변수 토큰으로 정의한다. 고도몰 스킨의 페이지 구분(main / goods_list / goods_view / company)과 파일을 1:1로 맞춘다.

**Tech Stack:** Python 3.13 표준 라이브러리(urllib, re, json, unittest) · HTML5 · CSS3(변수, grid, sticky) · Vanilla JS(ES2020, fetch) · Pretendard(jsdelivr) · JetBrains Mono(Google Fonts) · Edge 헤드리스 스크린샷 · `python -m http.server`

**Spec:** `docs/superpowers/specs/2026-09-10-raro-furniture-redesign-design.md`

---

## 파일 구조

| 파일 | 책임 |
|---|---|
| `data/build.py` | 사이트 HTML 수집(캐시 `data/raw/`) → 파싱 → 속성 추출 → `data/site.json` 생성. 상수로 카테고리 문구·홈 섹션 구성·회사 정보·특징 문구 보관 |
| `data/site.json` | 페이지가 읽는 유일한 데이터 |
| `tests/test_build.py` | build.py 파서·속성 추출 단위 테스트(unittest, 실제 마크업 조각 픽스처) |
| `assets/style.css` | 토큰 · 리셋 · 공통 컴포넌트(헤더/푸터/버튼/카드/그리드) · 페이지별 섹션 · 반응형 |
| `assets/app.js` | `RARO` 네임스페이스: 데이터 로드, 순수 함수(가격·할인·정렬·필터·옵션 합계), 헤더/푸터 렌더, 페이지별 init |
| `tests/app.test.html` | 브라우저에서 여는 순수 함수 테스트. 결과를 `#result`에 PASS/FAIL로 출력 |
| `index.html` `list.html` `view.html` `brand.html` | 페이지 틀. `<body data-page="home|list|view|brand">` |
| `tools/screenshot.sh` | 로컬 서버 기준 4페이지 × 3폭 스크린샷을 `docs/screenshots/`에 저장 |
| `docs/godomall-porting.md` | 블록 → 고도몰 스킨 파일 대응표 |
| `README.md` | 실행 방법, 구조, 2단계 안내 |

작업 순서: 데이터(Task 1–3) → 스타일·JS 기반(Task 4–5) → 페이지(Task 6–9) → 검증·문서(Task 10–11). 각 Task 끝에 커밋.

커밋 규칙: `git -c user.name="yunseong" -c user.email="happysmile7389@gmail.com" commit -m "..."` 형태로 실행하거나, 처음 한 번 `git config user.name yunseong; git config user.email happysmile7389@gmail.com`을 실행한다. 모든 커밋 메시지 끝에 빈 줄 후 `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`을 붙인다.

실행 위치: 모든 명령은 `c:/Users/전윤성/yunseong/raro-furniture/`에서 실행한다. Windows Git Bash 기준이며 Python 출력 인코딩 문제를 피하려고 `PYTHONIOENCODING=utf-8`을 앞에 붙인다.

---

### Task 1: 프로젝트 골격과 README

**Files:**
- Create: `README.md`
- Create: `data/raw/.gitkeep`, `tests/__init__.py`, `tools/.gitkeep`, `docs/screenshots/.gitkeep`
- Modify: `.gitignore`

- [x] **Step 1: 폴더와 빈 파일 생성**

Run:
```bash
mkdir -p data/raw tests tools docs/screenshots && touch data/raw/.gitkeep tests/__init__.py tools/.gitkeep docs/screenshots/.gitkeep && git config user.name yunseong && git config user.email happysmile7389@gmail.com
```
Expected: 오류 없음. `ls data tests tools docs`에 폴더가 보임.

- [x] **Step 2: .gitignore에 수집 캐시 추가**

`.gitignore`를 다음 내용으로 덮어쓴다:
```
.superpowers/
.firecrawl/
data/raw/*.html
__pycache__/
*.log
```

- [x] **Step 3: README 작성**

`README.md`:
````markdown
# 라로퍼니처 UI 리디자인 프로토타입

rarofurniture.co.kr(고도몰)을 Article × Floyd 방향으로 다시 설계한 정적 프로토타입. 나중에 고도몰 스킨으로 옮기는 것을 전제로 페이지 구분을 고도몰과 1:1로 맞췄다.

## 실행

```bash
# 1) 데이터 생성 (사이트에서 약 35개 페이지를 1초 간격으로 가져온다. 캐시가 있으면 재요청하지 않음)
PYTHONIOENCODING=utf-8 python data/build.py

# 2) 로컬 서버
python -m http.server 8080

# 3) 브라우저
#   http://localhost:8080/            메인
#   http://localhost:8080/list.html?cate=012   상품 목록 (cate = 고도몰 카테고리 코드)
#   http://localhost:8080/view.html?no=1000000491   상품 상세 (no = goodsNo)
#   http://localhost:8080/brand.html  브랜드 + 쇼룸
#   http://localhost:8080/tests/app.test.html  JS 순수 함수 테스트
```

`file://`로 직접 열면 `fetch`가 막혀 상품이 표시되지 않는다. 반드시 서버로 연다.

## 구조

- `data/build.py` → `data/site.json`: 카테고리 · 상품 · 홈 섹션 · 회사 정보
- `assets/style.css`: 디자인 토큰(CSS 변수) + 공통 컴포넌트 + 페이지 섹션
- `assets/app.js`: `RARO` 네임스페이스. 헤더/푸터 렌더, 카드 렌더, 필터·정렬·옵션 계산, 페이지별 init
- `index.html` `list.html` `view.html` `brand.html`
- `docs/superpowers/specs/`: 설계 문서 · `docs/superpowers/plans/`: 구현 계획 · `docs/godomall-porting.md`: 이식 가이드

## 테스트

```bash
PYTHONIOENCODING=utf-8 python -m unittest tests.test_build -v     # 파서
bash tools/screenshot.sh                                          # 4페이지 × 3폭 스크린샷 → docs/screenshots/
```

## 2단계

리뷰 목록, 이벤트, 고객센터, 로그인·회원가입, 장바구니·주문, 마이페이지, 약관 페이지를 같은 디자인 시스템으로 확장한다. 별도 계획 문서로 진행.
````

- [x] **Step 4: 커밋**

```bash
git add -A && git commit -m "chore: 프로젝트 골격과 README

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 2: build.py 파서와 속성 추출 (TDD)

**Files:**
- Create: `data/build.py` (파서·속성 추출 부분)
- Create: `tests/test_build.py`

파서는 실제 사이트 마크업(2026-09-10 확인)에 맞춘다. 핵심 셀렉터:
- 목록 아이템: `<div class="item_cont">` … `</li>`. 안에 `data-goods-no`, `data-image-main`(400px), `<strong class="item_name">`, `<div class="dcPrice" custom="정가" price="판매가">`, `REVIEW : N`, `<div class='color'>` 스와치(`background-color:#HEX` + `title='이름[English]'`), `free_delivery.gif` 아이콘.
- 상세: `<div class="item_detail_tit"><h3>이름</h3>`, `name="set_goods_price" value="398000"`, `name="set_goods_fixedPrice" value="500000.00"`, `<dl class="item_delivery"><dd><strong>40,000원</strong>`, 갤러리 `detailKeyID[n] = "<img src=\"URL\"`, 옵션 `<select name="optionNo_0">` 의 `<option>`(`=`로 시작하는 안내 항목 제외), 상세 이미지 = `id="detail"` 이후 hgodo 이미지 중 `/img/` `/info/` `/ourhome/` 경로 제외, 고시 표 `<table class="left_table_type">` th/td, 탭 `상품후기 <strong>(N)</strong>` `상품문의 <strong>(N)</strong>`.
- 홈 리뷰: `<ul class="reviewWrap">` 블록. `background:url('IMG')`, `<a class="reviewContent">본문</a>`, `rating_star … width:100%`, `board_name`, `board_day`, `goods_view.php?goodsNo=N` + 상품명.

- [x] **Step 1: 실패하는 테스트 작성**

`tests/test_build.py`:
```python
import sys, pathlib, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "data"))
import build  # noqa: E402

LIST_HTML = """
<li style="width:25%;"> <div class="item_cont"> <p class="mpl_best">BEST 1</p>
<div class="item_photo_box" data-image-add1 = "https://furnius.hgodo.com/img/thumbnail/1000000107_400.jpg" data-image-list = "https://furnius.hgodo.com/img/thumbnail/1000000107_200.jpg" data-image-main = "https://furnius.hgodo.com/img/thumbnail/1000000107_400.jpg" data-image-detail = "https://furnius.hgodo.com/img/thumbnail/1000000107_1000_1.jpg">
<a href="../goods/goods_view.php?goodsNo=1000000107&mtn="><img src="https://furnius.hgodo.com/img/thumbnail/1000000107_400.jpg" alt="클래시 1400 포세린 통 세라믹 4인 식탁 세트" class="middle" /></a>
<div class="item_link"><button type="button" class="btn_basket_get btn_add_wish_widget" data-goods-no="1000000107" data-goods-nm="클래시 1400 포세린 통 세라믹 4인 식탁 세트" data-goods-price="178000.00"><span>WISH</span></button></div></div>
<div class="item_info_cont"> <div class='color' style='width: 290px'><div style='background-color:#FFFFFF;' title='흰색[White]'></div><div style='background-color:#191919; border-color:#191919;' title='검정색[Black]'></div></div>
<div class="item_tit_box"><a href="../goods/goods_view.php?goodsNo=1000000107"><strong class="item_name">클래시 1400 포세린 통 세라믹 4인 식탁 세트</strong></a></div>
<div class="item_money_box"><strong class="item_price"><div class="dcPrice" custom="300000.00" price="178000.00"></div><span style="">178,000원 </span></strong></div>
<div class="item_review_cnt">REVIEW : 47</div>
<div class="item_icon_box"><img src="https://cdn/data/icon/goods_icon/free_delivery.gif" alt="엠플샵아이콘" /></div>
</div></div></li>
<li style="width:25%;"> <div class="item_cont">
<div class="item_photo_box" data-image-main = "https://furnius.hgodo.com/img/thumbnail/1000000111_400.jpg">
<button class="btn_add_wish_widget" data-goods-no="1000000111"></button></div>
<div class="item_tit_box"><strong class="item_name">에버 유광 600/800 원형 포세린 통 세라믹 침실 테라스 테이블</strong></div>
<div class="item_money_box"><strong class="item_price"><div class="dcPrice" custom="64000.00" price="64000.00"></div><span>64,000원</span></strong></div>
<div class="item_review_cnt">REVIEW : 0</div>
</div></li>
"""

DETAIL_HTML = """
<input type="hidden" name="set_goods_price" value="398000" />
<input type="hidden" id="set_goods_fixedPrice" name="set_goods_fixedPrice" value="500000.00" />
<div class="item_detail_tit"> <h3>허그 1400 포세린 통 세라믹 4인 식탁 세트</h3> </div>
<dl class="item_price"><dt>판매가</dt><dd><strong><strong>398,000</strong></strong>원</dd></dl>
<dl class="item_delivery"><dt>배송비</dt><dd><strong>40,000원</strong> / 상품수령시결제(착불)</dd></dl>
<script>detailKeyID[0] = "<img src=\\"https://furnius.hgodo.com/img/thumbnail/1000000491_1000_1.jpg\\" width=\\"600\\" />"; detailKeyID[1] = "<img src=\\"https://furnius.hgodo.com/img/thumbnail/1000000491_1000_2.jpg\\" />";</script>
<select name="optionNo_0" class="chosen-select"><option value=""> = 구성 선택 = </option><option value="1">식탁+의자2+벤치1</option><option value="2">식탁+의자4</option><option value="3">식탁 단품</option></select>
<select name="optionNo_1"><option value=""> = 구성을 먼저 선택해 주세요 = </option></select>
<img src="https://furnius.hgodo.com/img/banner/top_banner_01.jpg" />
<div id="detail"><div class="item_goods_tab"><ul><li><a href="#reviews">상품후기 <strong>(12)</strong></a></li><li><a href="#qna">상품문의 <strong>(3)</strong></a></li></ul></div>
<img src="https://furnius.hgodo.com/table/ceramic/hug_ce4_01.jpg" /><img src="https://furnius.hgodo.com/table/ceramic/hug_ce4_02.jpg" /><img src="https://furnius.hgodo.com/info/company.jpg" />
<div class="datail_table"><table class="left_table_type"><tbody>
<tr><th style="width:20%">품명</th><td colspan="3">상세페이지 참조</td></tr>
<tr><th style="width:20%">KC 인증정보</th><td colspan="3">KC인증대상아님</td></tr>
<tr><th>제조/수입자</th><td>라로퍼니처</td></tr>
<tr><th>AS 책임자와 전화번호</th><td>[라로퍼니처 고객센터] 031 ) 977 - 7352</td></tr>
<tr><th>크기</th><td>상품상세참조</td></tr>
</tbody></table></div></div>
"""

REVIEW_HTML = """
<ul class="reviewWrap"> <li class="reviewImage reviewBtnViewPop" style="background:url('https://phinf.pstatic.net/checkout.phinf/a.jpeg?type=w640') no-repeat;" data-sno="4259"></li>
<li class="reviewInfo"> <a class="reviewSubject reviewBtnViewPop">일단 의자가 넓어서 좋구요...</a> <a class="reviewContent" >일단 의자가 넓어서 좋구요 디자인도 좋고 튼튼힙니다</a>
<a class="rating_star"> <span style="width:100%;">별 다섯개중 다섯개</span> </a>
<div class="board_name_day"> <span class="board_name">네이버페이 구매자</span> <span class="board_day">2026.09.09</span> </div>
<div class="prdGoods"> <a href="../goods/goods_view.php?goodsNo=1000000254"> <span><img src="x.jpg"> 레스트 800 포세린 통 세라믹 2인 낮은 식탁 세트</span> </a> </div> </li> </ul>
<ul class="reviewWrap"> <li class="reviewImage" style="background:url('https://phinf.pstatic.net/b.jpg') no-repeat;"></li>
<li class="reviewInfo"> <a class="reviewContent" >약간 크네요</a> <a class="rating_star"> <span style="width:80%;">별</span> </a>
<div class="board_name_day"> <span class="board_name">네이버페이 구매자</span> <span class="board_day">2026.09.05</span> </div>
<div class="prdGoods"> <a href="../goods/goods_view.php?goodsNo=1000000004"> <span>발렌시 팔걸이 원목 식탁 의자</span> </a> </div> </li> </ul>
"""


class ParseListTest(unittest.TestCase):
    def test_parses_two_items(self):
        items = build.parse_list(LIST_HTML)
        self.assertEqual([i["no"] for i in items], ["1000000107", "1000000111"])

    def test_first_item_fields(self):
        p = build.parse_list(LIST_HTML)[0]
        self.assertEqual(p["name"], "클래시 1400 포세린 통 세라믹 4인 식탁 세트")
        self.assertEqual(p["image"], "https://furnius.hgodo.com/img/thumbnail/1000000107_400.jpg")
        self.assertEqual(p["price"], 178000)
        self.assertEqual(p["listPrice"], 300000)
        self.assertEqual(p["reviewCount"], 47)
        self.assertEqual(p["colors"], [{"name": "흰색", "hex": "#FFFFFF"}, {"name": "검정색", "hex": "#191919"}])
        self.assertEqual(p["tags"], ["무료배송"])

    def test_no_discount_gives_null_list_price(self):
        p = build.parse_list(LIST_HTML)[1]
        self.assertEqual(p["price"], 64000)
        self.assertIsNone(p["listPrice"])
        self.assertEqual(p["colors"], [])
        self.assertEqual(p["tags"], [])


class ParseDetailTest(unittest.TestCase):
    def test_fields(self):
        d = build.parse_detail(DETAIL_HTML)
        self.assertEqual(d["name"], "허그 1400 포세린 통 세라믹 4인 식탁 세트")
        self.assertEqual(d["price"], 398000)
        self.assertEqual(d["listPrice"], 500000)
        self.assertEqual(d["shipping"], "40,000원 / 상품수령시결제(착불)")
        self.assertEqual(d["gallery"], [
            "https://furnius.hgodo.com/img/thumbnail/1000000491_1000_1.jpg",
            "https://furnius.hgodo.com/img/thumbnail/1000000491_1000_2.jpg"])
        self.assertEqual([o["name"] for o in d["options"]], ["식탁+의자2+벤치1", "식탁+의자4", "식탁 단품"])
        self.assertEqual(d["detailImages"], [
            "https://furnius.hgodo.com/table/ceramic/hug_ce4_01.jpg",
            "https://furnius.hgodo.com/table/ceramic/hug_ce4_02.jpg"])
        self.assertEqual(d["spec"], {"KC 인증정보": "KC인증대상아님", "제조/수입자": "라로퍼니처",
                                     "AS 책임자와 전화번호": "[라로퍼니처 고객센터] 031 ) 977 - 7352"})
        self.assertEqual(d["reviewCount"], 12)
        self.assertEqual(d["qnaCount"], 3)


class ParseReviewsTest(unittest.TestCase):
    def test_reviews(self):
        r = build.parse_reviews(REVIEW_HTML)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0]["img"], "https://phinf.pstatic.net/checkout.phinf/a.jpeg?type=w640")
        self.assertEqual(r[0]["text"], "일단 의자가 넓어서 좋구요 디자인도 좋고 튼튼힙니다")
        self.assertEqual(r[0]["stars"], 5)
        self.assertEqual(r[0]["name"], "네이버페이 구매자")
        self.assertEqual(r[0]["date"], "2026.09.09")
        self.assertEqual(r[0]["goodsNo"], "1000000254")
        self.assertEqual(r[0]["goodsName"], "레스트 800 포세린 통 세라믹 2인 낮은 식탁 세트")
        self.assertEqual(r[1]["stars"], 4)


class DeriveTest(unittest.TestCase):
    def test_ceramic_set(self):
        a = build.derive("허그 1400 포세린 통 세라믹 4인 식탁 세트", "012")
        self.assertEqual(a, {"series": "허그", "size": 1400, "seats": 4, "shape": "사각",
                             "material": "무광 세라믹", "kind": "세트"})

    def test_round_gloss_single(self):
        a = build.derive("에버 유광 600/800 원형 포세린 통 세라믹 침실 테라스 테이블", "012")
        self.assertEqual(a["size"], 600)
        self.assertEqual(a["shape"], "원형")
        self.assertEqual(a["material"], "유광 세라믹")
        self.assertEqual(a["kind"], "단품")
        self.assertIsNone(a["seats"])

    def test_marble_and_bracket_prefix(self):
        a = build.derive("[무료배송] 1+1 비너스 가죽 화이트 스틸 식탁 의자 편한 카페 인테리어 체어", "006")
        self.assertEqual(a["series"], "비너스")
        self.assertEqual(a["material"], "가죽")
        self.assertIsNone(a["size"])
        b = build.derive("몬타 대리석 1400 4인 식탁 세트", "012")
        self.assertEqual(b["material"], "대리석")

    def test_sofa_and_bed(self):
        a = build.derive("모먼트 천연 면피 가죽 원터치 전동 리클라이너 4인 소파 4인용 쇼파", "003")
        self.assertEqual(a["seats"], 4)
        self.assertEqual(a["material"], "가죽")
        self.assertIsNone(a["shape"])
        self.assertIsNone(a["kind"])
        b = build.derive("데이지 타이보 갤럭시 원단 패브릭 2서랍 수납 침대 LK 매트리스 포함 세트", "004")
        self.assertEqual(b["material"], "패브릭")
        self.assertEqual(b["kind"], "세트")


class PriceBandTest(unittest.TestCase):
    def test_bands(self):
        self.assertEqual(build.price_band(178000), "30만원 이하")
        self.assertEqual(build.price_band(300000), "30만원 이하")
        self.assertEqual(build.price_band(398000), "30–50만원")
        self.assertEqual(build.price_band(689000), "50만원 이상")


if __name__ == "__main__":
    unittest.main()
```

- [x] **Step 2: 테스트가 실패하는지 확인**

Run: `PYTHONIOENCODING=utf-8 python -m unittest tests.test_build -v`
Expected: `ModuleNotFoundError: No module named 'build'` 로 전부 실패(ERROR).

- [x] **Step 3: build.py 파서 구현 (수집·조립은 Task 3에서)**

`data/build.py`:
```python
#!/usr/bin/env python3
"""라로퍼니처(rarofurniture.co.kr) 상품·카테고리 데이터를 수집해 data/site.json을 만든다.

사용법:
    PYTHONIOENCODING=utf-8 python data/build.py            # 캐시 없는 페이지만 요청 후 생성
    PYTHONIOENCODING=utf-8 python data/build.py --offline  # data/raw/ 캐시만 사용 (네트워크 없음)

요청은 브라우저 UA로 1초 간격, 총 35건 안팎. 결과 HTML은 data/raw/에 캐시한다.
"""
import html as html_lib
import json
import pathlib
import re
import sys
import time
import urllib.request
from datetime import date

BASE = "https://www.rarofurniture.co.kr"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
ROOT = pathlib.Path(__file__).resolve().parent
RAW = ROOT / "raw"
OUT = ROOT / "site.json"


# ---------------------------------------------------------------- 공통
def clean(s: str) -> str:
    """태그 제거 + 엔티티 해제 + 공백 정리."""
    s = re.sub(r"<[^>]+>", " ", s)
    s = html_lib.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def to_int(s):
    """'178,000원' / '178000.00' → 178000. 없으면 None."""
    if s is None:
        return None
    m = re.search(r"[\d,]+", s)
    if not m:
        return None
    return int(float(m.group(0).replace(",", "")))


# ---------------------------------------------------------------- 목록 파서
def parse_list(page: str) -> list:
    """goods_list.php 페이지에서 상품 목록을 뽑는다."""
    items = []
    for block in re.findall(r'<div class="item_cont">.*?</li>', page, re.S):
        no = re.search(r'data-goods-no="(\d+)"', block)
        name = re.search(r'<strong class="item_name">(.*?)</strong>', block, re.S)
        if not (no and name):
            continue
        img = re.search(r'data-image-main\s*=\s*"([^"]+)"', block)
        dc = re.search(r'<div class="dcPrice" custom="([\d.]+)" price="([\d.]+)"', block)
        price = to_int(dc.group(2)) if dc else to_int(
            (re.search(r'data-goods-price="([\d.]+)"', block) or [None, None])[1])
        custom = to_int(dc.group(1)) if dc else None
        list_price = custom if (custom and price and custom > price) else None
        rc = re.search(r"REVIEW\s*:\s*(\d+)", block)
        colors = []
        cbox = re.search(r"<div class='color'[^>]*>(.*?)</div>\s*</div>", block, re.S)
        if cbox:
            for hexv, title in re.findall(
                    r"background-color:(#[0-9A-Fa-f]{6});[^']*'\s*title='([^'\[]+)", cbox.group(1)):
                colors.append({"name": title.strip(), "hex": hexv.upper()})
        tags = ["무료배송"] if "free_delivery" in block else []
        items.append({
            "no": no.group(1),
            "name": clean(name.group(1)),
            "image": img.group(1) if img else "",
            "price": price,
            "listPrice": list_price,
            "reviewCount": int(rc.group(1)) if rc else 0,
            "colors": colors,
            "tags": tags,
        })
    return items


# ---------------------------------------------------------------- 상세 파서
_SKIP_SPEC = {"상세페이지 참조", "상품상세참조", "상세페이지참조", "상품 상세 참조", ""}


def parse_detail(page: str) -> dict:
    """goods_view.php 페이지에서 상세 정보를 뽑는다."""
    name = re.search(r'<div class="item_detail_tit">\s*<h3>(.*?)</h3>', page, re.S)
    price = re.search(r'name="set_goods_price" value="([\d.]+)"', page)
    fixed = re.search(r'name="set_goods_fixedPrice" value="([\d.]+)"', page)
    ship = re.search(r'<dl class="item_delivery">.*?<dd>(.*?)</dd>', page, re.S)
    gallery = re.findall(r'detailKeyID\[\d+\]\s*=\s*"<img src=\\"([^"\\]+)\\"', page)
    options = []
    sel = re.search(r'<select name="optionNo_0"[^>]*>(.*?)</select>', page, re.S)
    if sel:
        for label in re.findall(r"<option[^>]*>(.*?)</option>", sel.group(1), re.S):
            label = clean(label)
            if label and not label.startswith("="):
                options.append({"name": label, "delta": None})
    detail_images = []
    tail = page.split('id="detail"', 1)[1] if 'id="detail"' in page else ""
    for src in re.findall(r'<img[^>]+src="([^"]+)"', tail):
        if "hgodo.com" in src and not re.search(r"/(img|info|ourhome)/", src):
            detail_images.append(src)
    spec = {}
    table = re.search(r'<table class="left_table_type">(.*?)</table>', page, re.S)
    if table:
        for th, td in re.findall(r"<th[^>]*>(.*?)</th>\s*<td[^>]*>(.*?)</td>", table.group(1), re.S):
            k, v = clean(th), clean(td)
            if v not in _SKIP_SPEC:
                spec[k] = v
    rc = re.search(r"상품후기\s*<strong>\((\d+)\)</strong>", page)
    qc = re.search(r"상품문의\s*<strong>\((\d+)\)</strong>", page)
    price_v = to_int(price.group(1)) if price else None
    fixed_v = to_int(fixed.group(1)) if fixed else None
    return {
        "name": clean(name.group(1)) if name else "",
        "price": price_v,
        "listPrice": fixed_v if (fixed_v and price_v and fixed_v > price_v) else None,
        "shipping": clean(ship.group(1)) if ship else "",
        "gallery": gallery,
        "options": options,
        "detailImages": detail_images,
        "spec": spec,
        "reviewCount": int(rc.group(1)) if rc else 0,
        "qnaCount": int(qc.group(1)) if qc else 0,
    }


# ---------------------------------------------------------------- 홈 리뷰 파서
def parse_reviews(page: str) -> list:
    """메인 페이지의 <ul class="reviewWrap"> 블록에서 실제 후기를 뽑는다."""
    out = []
    for block in re.findall(r'<ul class="reviewWrap">(.*?)</ul>', page, re.S):
        img = re.search(r"background:url\('([^']+)'\)", block)
        text = re.search(r'<a class="reviewContent"[^>]*>(.*?)</a>', block, re.S)
        width = re.search(r'class="rating_star">\s*<span style="width:(\d+)%', block)
        name = re.search(r'<span class="board_name">(.*?)</span>', block, re.S)
        day = re.search(r'<span class="board_day">(.*?)</span>', block, re.S)
        goods = re.search(r'goods_view\.php\?goodsNo=(\d+)"[^>]*>\s*<span>(.*?)</span>', block, re.S)
        if not (text and goods):
            continue
        out.append({
            "img": img.group(1) if img else "",
            "text": clean(text.group(1)),
            "stars": round(int(width.group(1)) / 20) if width else 5,
            "name": clean(name.group(1)) if name else "구매자",
            "date": clean(day.group(1)) if day else "",
            "goodsNo": goods.group(1),
            "goodsName": clean(goods.group(2)),
        })
    return out


# ---------------------------------------------------------------- 속성 추출
DINING_TOPS = {"012", "013"}


def derive(name: str, top: str) -> dict:
    """상품명에서 시리즈·사이즈·인원·형태·소재·구성을 규칙으로 뽑는다."""
    tokens = [t for t in name.split() if not t.startswith("[") and not re.fullmatch(r"\d\+\d", t)]
    series = tokens[0] if tokens else ""
    sizes = [int(x) for x in re.findall(r"(?<![\d.])(\d{3,4})(?![\d.])", name) if 500 <= int(x) <= 2400]
    size = sizes[0] if sizes else None
    seats_m = re.search(r"(\d)인(?!용)", name)
    seats = int(seats_m.group(1)) if seats_m else None
    if "원형" in name:
        shape = "원형"
    elif "타원" in name:
        shape = "타원"
    elif top in DINING_TOPS:
        shape = "사각"
    else:
        shape = None
    if "대리석" in name:
        material = "대리석"
    elif "유광" in name and "세라믹" in name:
        material = "유광 세라믹"
    elif "세라믹" in name:
        material = "무광 세라믹"
    elif "가죽" in name:
        material = "가죽"
    elif "패브릭" in name or "원단" in name:
        material = "패브릭"
    elif "라탄" in name:
        material = "라탄"
    elif "스틸" in name:
        material = "스틸"
    elif "원목" in name:
        material = "원목"
    else:
        material = None
    if "세트" in name:
        kind = "세트"
    elif "단품" in name or (top in DINING_TOPS and "테이블" in name):
        kind = "단품"
    else:
        kind = None
    return {"series": series, "size": size, "seats": seats, "shape": shape,
            "material": material, "kind": kind}


def price_band(price: int) -> str:
    if price <= 300000:
        return "30만원 이하"
    if price <= 500000:
        return "30–50만원"
    return "50만원 이상"
```

- [x] **Step 4: 테스트 통과 확인**

Run: `PYTHONIOENCODING=utf-8 python -m unittest tests.test_build -v`
Expected: `Ran 10 tests … OK`

- [x] **Step 5: 커밋**

```bash
git add data/build.py tests/test_build.py && git commit -m "feat(data): 목록·상세·리뷰 파서와 상품 속성 추출

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 3: build.py 수집·조립 + site.json 생성

**Files:**
- Modify: `data/build.py` (Task 2 코드 아래에 추가)
- Create: `data/site.json` (실행 결과)
- Modify: `tests/test_build.py` (조립 테스트 1개 추가)

- [x] **Step 1: 조립 로직 테스트 추가**

`tests/test_build.py` 맨 아래 `if __name__` 위에 추가:
```python
class AssembleTest(unittest.TestCase):
    def test_assemble_product_merges_detail_and_attrs(self):
        item = {"no": "1000000491", "name": "허그 1400 포세린 통 세라믹 4인 식탁 세트",
                "image": "t.jpg", "price": 398000, "listPrice": None, "reviewCount": 84,
                "colors": [], "tags": []}
        p = build.assemble_product(item, cate="012002", top="012")
        self.assertEqual(p["cate"], "012002")
        self.assertEqual(p["top"], "012")
        self.assertEqual(p["series"], "허그")
        self.assertEqual(p["priceBand"], "30–50만원")
        self.assertNotIn("detail", p)
        detail = {"name": "x", "price": 398000, "listPrice": 500000, "shipping": "40,000원",
                  "gallery": ["g1.jpg", "g2.jpg"], "options": [], "detailImages": [], "spec": {},
                  "reviewCount": 12, "qnaCount": 3}
        build.attach_detail(p, detail)
        self.assertEqual(p["listPrice"], 500000)
        self.assertEqual(p["detail"]["gallery"], ["g1.jpg", "g2.jpg"])
        self.assertEqual(len(p["features"]), 3)
        self.assertEqual(p["reviewCount"], 84)

    def test_categories_have_required_text(self):
        for top in build.CATEGORIES:
            self.assertTrue(top["desc"])
            self.assertTrue(top["guide"]["title"] and top["guide"]["body"])
            self.assertTrue(top["children"])
            self.assertIn(top["code"], build.FEATURES)
```

- [x] **Step 2: 테스트 실패 확인**

Run: `PYTHONIOENCODING=utf-8 python -m unittest tests.test_build.AssembleTest -v`
Expected: `AttributeError: module 'build' has no attribute 'assemble_product'`

- [x] **Step 3: 상수와 조립·수집 코드 추가**

`data/build.py` 맨 아래에 추가:
```python
# ---------------------------------------------------------------- 사이트 상수 (2026-09-10 사이트 확인 기준)
CATEGORIES = [
    {"code": "012", "name": "세라믹 · 대리석 식탁", "short": "세라믹·대리석 식탁",
     "desc": "열과 흠집에 강한 포세린 통 세라믹, 무늬가 살아 있는 대리석 상판. 2인 원형부터 6인 1900까지.",
     "guide": {"title": "식탁 사이즈, 이렇게 고르세요.",
               "body": "4인 가족은 1200~1400, 손님이 잦으면 1600 이상이 편합니다. 의자를 빼내는 공간으로 식탁 둘레에 70cm를 더해 보세요. 좁은 공간이면 원형이 동선을 덜 막습니다."},
     "children": [{"code": "012002", "name": "세라믹 식탁 세트"}, {"code": "012003", "name": "세라믹 테이블"},
                  {"code": "012004", "name": "대리석 식탁 세트"}, {"code": "012005", "name": "대리석 테이블"}]},
    {"code": "013", "name": "원목 식탁", "short": "원목 식탁",
     "desc": "고무나무·참죽나무 원목의 결을 그대로 살린 식탁. 의자·벤치 세트와 테이블 단품.",
     "guide": {"title": "원목 식탁은 이렇게 관리하세요.",
               "body": "뜨거운 냄비는 받침을 쓰고, 물기는 바로 닦아 주세요. 직사광선을 오래 받으면 색이 변할 수 있습니다. 6개월에 한 번 오일을 발라 주면 결이 오래 유지됩니다."},
     "children": [{"code": "013002", "name": "원목 테이블"}, {"code": "013003", "name": "원목 식탁 세트"}]},
    {"code": "003", "name": "거실가구", "short": "거실가구",
     "desc": "전동 리클라이너와 패브릭 소파, TV 거실장과 거실 테이블. 거실 한 세트를 같은 톤으로.",
     "guide": {"title": "소파 사이즈, 거실 폭부터 재세요.",
               "body": "4인 소파는 보통 폭 2.4~2.8m, 코너형 6인은 3m 이상 필요합니다. 리클라이너는 등받이가 젖혀지는 뒤쪽 여유 30cm를 더해 주세요."},
     "children": [{"code": "003001", "name": "소파"}, {"code": "003002", "name": "TV거실장"},
                  {"code": "003004", "name": "거실테이블"}, {"code": "003005", "name": "소가구"}]},
    {"code": "006", "name": "의자", "short": "의자",
     "desc": "고무나무 원목 의자부터 가죽·라탄 인테리어 체어, 스툴과 벤치까지.",
     "guide": {"title": "의자 높이는 식탁에 맞추세요.",
               "body": "식탁 높이 750 기준 좌판 높이 430~450이 편합니다. 벤치는 같은 길이의 의자 2개보다 자리를 덜 차지합니다."},
     "children": [{"code": "006001", "name": "원목 의자"}, {"code": "006003", "name": "인테리어 의자"},
                  {"code": "006004", "name": "스툴"}, {"code": "006005", "name": "벤치"}]},
    {"code": "004", "name": "서재 · 침실가구", "short": "서재·침실",
     "desc": "수납 침대와 원목 책상, 옷장·드레스룸·서랍장. 방 하나를 한 번에.",
     "guide": {"title": "침대 사이즈 표기 읽는 법.",
               "body": "SS 1100 · Q 1500 · K 1600 · LK 1700~1800(폭 mm). 매트리스 포함 세트와 프레임 단품을 구분해 확인하세요."},
     "children": [{"code": "004001", "name": "침대"}, {"code": "004002", "name": "책상"},
                  {"code": "004003", "name": "보조 가구"}, {"code": "004004", "name": "책상의자"},
                  {"code": "004005", "name": "옷장 · 드레스룸 · 서랍장"}]},
]

# 상세까지 수집하는 대표 상품 12개 (홈·목록 대표 이미지와 상세 페이지 시연용)
DETAIL_GOODS = ["1000000491", "1000000107", "1000000260", "1000000300", "1000000104", "1000000808",
                "1000000765", "1000001395", "1000000005", "1000000490", "1000001388", "1000000121"]

# 메인 섹션 구성 (현재 사이트 메인의 Weekly HOT 10 / BEST / NEW 순서를 그대로 옮김)
HOME = {
    "weekly": ["1000000003", "1000000005", "1000000490", "1000000004", "1000000238",
               "1000000295", "1000000252", "1000000665", "1000000491", "1000000260"],
    "best": ["1000000487", "1000000300", "1000000255", "1000000107",
             "1000000320", "1000000210", "1000000113", "1000000104"],
    "new": ["1000001396", "1000001395", "1000001394", "1000001393",
            "1000001392", "1000001391", "1000001390", "1000001388"],
    "lookbook": ["1000000491", "1000000765", "1000000104"],
}

HERO = [
    {"img": "assets/banner-interior.jpg", "title": "매일의 식탁을, 오래 쓰는 가구로.",
     "sub": "포세린 세라믹과 고무나무 원목. 일산 쇼룸에서 직접 앉아 보고 고르세요.",
     "cta": "세라믹 식탁 보기", "href": "list.html?cate=012"},
    {"img": "", "goodsNo": "1000001395", "title": "거실의 중심이 바뀝니다.",
     "sub": "비건 가죽 스윙 헤드레스트, 코나 소파 출시.",
     "cta": "소파 보러 가기", "href": "list.html?cate=003001"},
]

# 상세 페이지 "핵심 특징" — 카테고리 기본 문구. 상품명·고시표에서 확인되는 사실만 쓴다.
FEATURES = {
    "012": [{"title": "포세린 통 세라믹 상판", "body": "열과 흠집, 얼룩에 강해 뜨거운 냄비를 바로 올려도 됩니다. 물기는 닦아내기만 하면 됩니다."},
            {"title": "세트 구성 선택", "body": "식탁 단품, 의자 4개, 의자 2개 + 벤치 구성 중 고를 수 있습니다. 구성별 가격은 옵션에서 확인하세요."},
            {"title": "기사 방문 설치", "body": "배송비는 상품 수령 시 결제합니다. 설치 전 현관과 통로 폭을 확인해 주세요."}],
    "013": [{"title": "원목 상판", "body": "고무나무·참죽나무 원목의 결과 색을 그대로 살렸습니다. 같은 이름의 의자·벤치와 톤이 맞습니다."},
            {"title": "세트와 단품", "body": "테이블 단품과 의자·벤치 세트 구성이 있습니다. 구성별 가격은 옵션에서 확인하세요."},
            {"title": "기사 방문 설치", "body": "배송비는 상품 수령 시 결제합니다. 설치 전 현관과 통로 폭을 확인해 주세요."}],
    "003": [{"title": "소재와 마감", "body": "천연 가죽, 비건 가죽, 패브릭 원단 중 상품명에 표기된 소재를 사용합니다."},
            {"title": "편의 기능", "body": "전동 리클라이너, 스윙 헤드레스트, 틸팅 등 상품명에 표기된 기능이 적용됩니다."},
            {"title": "기사 방문 설치", "body": "배송비는 상품 수령 시 결제합니다. 설치 전 현관과 통로 폭을 확인해 주세요."}],
    "006": [{"title": "프레임", "body": "고무나무·참죽나무 원목 또는 스틸 프레임. 상품명에 표기된 소재를 확인하세요."},
            {"title": "좌판", "body": "원목 좌판, 인조가죽·패브릭 방석, 라탄 등 상품명에 표기된 마감입니다."},
            {"title": "배송", "body": "의자는 완제품 또는 간단 조립 상태로 배송됩니다. 배송비는 옵션 선택 후 표시됩니다."}],
    "004": [{"title": "구성", "body": "매트리스 포함 세트와 프레임 단품, 서랍·수납 여부는 상품명에 표기되어 있습니다."},
            {"title": "사이즈", "body": "SS·Q·K·LK 등 표기 사이즈를 방 크기와 함께 확인하세요."},
            {"title": "기사 방문 설치", "body": "배송비는 상품 수령 시 결제합니다. 설치 전 현관과 통로 폭을 확인해 주세요."}],
}

COMPANY = {
    "brand": "라로퍼니처", "name": "㈜퍼니우스", "ceo": "전재국",
    "address": "경기도 파주시 고봉로 721-50 (상지석동)",
    "showroom": "경기도 고양시 일산동구 고봉로 757-11",
    "tel": "031-977-7352", "fax": "031-946-9459", "email": "furnius946@naver.com",
    "bizNo": "668-86-00834", "mailOrderNo": "제 2018-경기파주-0229호", "privacyOfficer": "김영순",
    "slogan": "현대적 감각으로 자연을 다듬다.",
    "meaning": "RARO MEANS : 색다른, 희소성 있는",
    "story": [
        "30여 년 동안 쌓아 온 가구 제조 기술력을 바탕으로 최고급 가구를 직접 디자인합니다.",
        "철저한 품질관리와 최소한의 유통경로로, 프리미엄 상품을 합리적인 가격에 제공합니다.",
        "중국 심천·동관·순관·천진, 베트남 동나이·빈정의 6개 전문 제조 공장에서 원목가구, 대리석, 화산석, 세라믹, 소파를 분야별 장인의 손길로 만듭니다.",
    ],
    "numbers": [{"value": "30", "unit": "년", "label": "가구 제조 기술력"},
                {"value": "6", "unit": "개", "label": "자체 관리 제조 공장 (중국 4 · 베트남 2)"},
                {"value": "5", "unit": "종", "label": "원목 · 대리석 · 화산석 · 세라믹 · 소파"}],
    "showroomHours": "확인 필요",
}


# ---------------------------------------------------------------- 조립
def assemble_product(item: dict, cate: str, top: str) -> dict:
    p = dict(item)
    p["cate"] = cate
    p["top"] = top
    p.update(derive(p["name"], top))
    p["priceBand"] = price_band(p["price"]) if p.get("price") else None
    return p


def attach_detail(p: dict, detail: dict) -> None:
    p["detail"] = detail
    if detail.get("price"):
        p["price"] = detail["price"]
        p["listPrice"] = detail["listPrice"]
        p["priceBand"] = price_band(p["price"])
    p["features"] = FEATURES[p["top"]]


# ---------------------------------------------------------------- 수집
def fetch(path: str, cache_name: str, offline: bool) -> str:
    cache = RAW / f"{cache_name}.html"
    if cache.exists():
        return cache.read_text(encoding="utf-8", errors="replace")
    if offline:
        raise SystemExit(f"캐시가 없습니다: {cache} (--offline 없이 실행하세요)")
    req = urllib.request.Request(BASE + path, headers={"User-Agent": UA, "Referer": BASE + "/"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        text = resp.read().decode("utf-8", errors="replace")
    cache.write_text(text, encoding="utf-8")
    print(f"  fetched {path}")
    time.sleep(1.0)
    return text


def build(offline: bool = False) -> dict:
    RAW.mkdir(exist_ok=True)
    products, order = {}, []
    print("[1/3] 카테고리 목록")
    for top in CATEGORIES:
        for child in top["children"]:
            page = fetch(f"/goods/goods_list.php?cateCd={child['code']}&pageNum=40",
                         f"list-{child['code']}", offline)
            for item in parse_list(page):
                if item["no"] in products:
                    continue
                products[item["no"]] = assemble_product(item, child["code"], top["code"])
                order.append(item["no"])
    print("[2/3] 대표 상품 상세")
    for no in DETAIL_GOODS:
        if no not in products:
            print(f"  경고: {no} 는 목록에 없어 상세를 건너뜁니다")
            continue
        attach_detail(products[no], parse_detail(fetch(f"/goods/goods_view.php?goodsNo={no}", f"view-{no}", offline)))
    print("[3/3] 메인 페이지 후기")
    reviews = [r for r in parse_reviews(fetch("/main/index.php", "home", offline)) if r["goodsNo"] in products][:6]

    def gallery(no, idx):
        g = products.get(no, {}).get("detail", {}).get("gallery", [])
        return g[idx] if len(g) > idx else (products.get(no, {}).get("image", ""))

    hero = []
    for h in HERO:
        h = dict(h)
        if not h["img"] and h.get("goodsNo"):
            h["img"] = gallery(h["goodsNo"], 0)
        hero.append(h)
    lookbook = [{"img": gallery(no, 1), "goodsNo": no, "caption": products[no]["name"]}
                for no in HOME["lookbook"] if no in products]
    known = lambda nos: [n for n in nos if n in products]  # noqa: E731
    data = {
        "generatedAt": date.today().isoformat(),
        "categories": CATEGORIES,
        "products": [products[n] for n in order],
        "home": {"hero": hero, "weekly": known(HOME["weekly"]), "best": known(HOME["best"]),
                 "new": known(HOME["new"]), "lookbook": lookbook, "reviews": reviews},
        "company": COMPANY,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    # 요약
    print(f"\n생성: {OUT}")
    print(f"상품 {len(order)}개, 상세 {sum(1 for p in products.values() if 'detail' in p)}개, 후기 {len(reviews)}개")
    for top in CATEGORIES:
        n = sum(1 for p in products.values() if p["top"] == top["code"])
        print(f"  {top['code']} {top['name']}: {n}개")
    missing = [p["no"] for p in products.values() if not p.get("price")]
    print(f"가격 누락: {len(missing)}개 {missing[:5]}")
    for key in ("weekly", "best", "new"):
        lost = [n for n in HOME[key] if n not in products]
        if lost:
            print(f"  경고: home.{key} 에서 목록에 없는 상품 제외 {lost}")
    return data


if __name__ == "__main__":
    build(offline="--offline" in sys.argv)
```

- [x] **Step 4: 테스트 통과 확인**

Run: `PYTHONIOENCODING=utf-8 python -m unittest tests.test_build -v`
Expected: `Ran 12 tests … OK`

- [x] **Step 5: 실제 수집 실행**

Run: `PYTHONIOENCODING=utf-8 python data/build.py`
Expected: `fetched` 줄이 19(목록) + 12(상세) + 1(홈) = 32개 출력된 뒤 요약. 상품 수는 300개 안팎(소분류당 40개 상한), 상세 12개, 후기 1개 이상, 가격 누락 0개. `home.*` 경고가 나오면 해당 goodsNo가 어느 목록 첫 페이지에도 없는 것이므로 `HOME` 상수에서 빼고 다시 실행한다(`--offline`으로 재실행하면 네트워크 없이 재조립됨).

- [x] **Step 6: 결과 확인**

Run:
```bash
PYTHONIOENCODING=utf-8 python -c "import json;d=json.load(open('data/site.json',encoding='utf-8'));p=[x for x in d['products'] if x['no']=='1000000491'][0];print(p['name'],p['price'],p['listPrice'],p['size'],p['seats'],p['material'],p['kind']);print(len(p['detail']['gallery']),'gallery',len(p['detail']['detailImages']),'detail imgs',p['detail']['options']);print(d['home']['hero'][1]['img']);print(d['home']['reviews'][0] if d['home']['reviews'] else 'NO REVIEWS')"
```
Expected: `허그 1400 포세린 통 세라믹 4인 식탁 세트 398000 500000 1400 4 무광 세라믹 세트`, 갤러리 4개 이상, 상세 이미지 1개 이상, 옵션 3개, 히어로 2번째 이미지가 `…1000001395_1000_1.jpg`, 후기 dict 출력.

- [x] **Step 7: 커밋**

```bash
git add data/build.py data/site.json tests/test_build.py && git commit -m "feat(data): 사이트 수집·조립 스크립트와 site.json 생성

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 4: 디자인 토큰과 공통 스타일 (style.css)

**Files:**
- Create: `assets/style.css`

한 파일에 섹션 주석으로 구분한다. 순서: 토큰 → 리셋 → 레이아웃 → 타이포 → 버튼·칩 → 헤더·드로어 → 카드·그리드 → 메인 섹션 → 목록 → 상세 → 브랜드 → 푸터 → 유틸 → 반응형. 페이지별 규칙은 Task 6–9에서 이 파일의 해당 섹션에 이미 포함되어 있으므로, 그 Task들에서는 CSS를 추가로 쓰지 않는다.

- [x] **Step 1: style.css 작성**

`assets/style.css`:
```css
/* ============================================================
   라로퍼니처 리디자인 — 디자인 토큰 & 공통 스타일
   방향: Article 60 : Floyd 40 ("화이트 쇼룸")
   ============================================================ */

/* ---------- 1. 토큰 ---------- */
:root {
  --bg: #FFFFFF;
  --tile: #F3F2EF;
  --cream: #F6F2EA;
  --ink: #2B2B2B;
  --ink-2: #555555;
  --ink-3: #999999;
  --line: #E8E6E1;
  --accent: #C4613A;
  --footer: #262321;
  --radius-pill: 999px;
  --radius-sm: 4px;
  --container: 1400px;
  --gutter: 24px;
  --section: 96px;
  --header-h: 112px;
  --font: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
          "Apple SD Gothic Neo", "Noto Sans KR", sans-serif;
  --mono: "JetBrains Mono", Consolas, "Courier New", monospace;
}

/* ---------- 2. 리셋 ---------- */
*, *::before, *::after { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }
body { margin: 0; background: var(--bg); color: var(--ink); font-family: var(--font); font-size: 15px; line-height: 1.6;
       -webkit-font-smoothing: antialiased; }
h1, h2, h3, h4, h5, p, ul, ol, figure { margin: 0; }
ul, ol { padding: 0; list-style: none; }
img { max-width: 100%; height: auto; display: block; }
a { color: inherit; text-decoration: none; }
button, input, select, textarea { font: inherit; color: inherit; }
button { cursor: pointer; }
del { text-decoration: line-through; }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
.skip { position: absolute; left: -999px; top: 8px; background: var(--ink); color: #fff; padding: 8px 12px; z-index: 100; }
.skip:focus { left: 8px; }

/* ---------- 3. 레이아웃 ---------- */
.container { max-width: var(--container); margin: 0 auto; padding: 0 var(--gutter); }
.sec { padding-top: var(--section); }
.sec--tight { padding-top: 56px; }
.sec__head { display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; margin-bottom: 28px; }
.sec__head .more { flex: none; }

/* ---------- 4. 타이포 ---------- */
.label { font-family: var(--mono); font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: var(--ink-3); }
.label--accent { color: var(--accent); }
.h1 { font-size: 44px; font-weight: 700; line-height: 1.2; letter-spacing: -.01em; }
.h2 { font-size: 28px; font-weight: 700; line-height: 1.25; letter-spacing: -.01em; }
.h3 { font-size: 20px; font-weight: 700; line-height: 1.3; }
.sub { color: var(--ink-2); font-size: 15px; margin-top: 6px; }
.more { font-size: 14px; text-decoration: underline; text-underline-offset: 3px; white-space: nowrap; }
.muted { color: var(--ink-3); }
.crumb { font-size: 13px; color: var(--ink-3); }
.crumb a:hover { color: var(--ink); }

/* ---------- 5. 버튼 · 칩 · 폼 ---------- */
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 6px; height: 44px; padding: 0 22px;
       border-radius: var(--radius-pill); border: 1px solid transparent; font-size: 14px; font-weight: 600;
       white-space: nowrap; transition: background .15s, color .15s, border-color .15s; }
.btn--primary { background: var(--ink); color: #fff; }
.btn--primary:hover { background: #000; }
.btn--secondary { background: #fff; color: var(--ink); border-color: var(--ink); }
.btn--secondary:hover { background: var(--tile); }
.btn--white { background: #fff; color: var(--ink); }
.btn--white:hover { background: var(--tile); }
.btn--accent { background: var(--accent); color: #fff; }
.btn--sm { height: 36px; padding: 0 16px; font-size: 13px; }
.btn--lg { height: 52px; padding: 0 28px; font-size: 15px; }
.btn--block { width: 100%; }
.btn--icon { width: 44px; padding: 0; }
.chips { display: flex; gap: 8px; flex-wrap: wrap; }
.chip { display: inline-flex; align-items: center; height: 34px; padding: 0 14px; border-radius: var(--radius-pill);
        border: 1px solid var(--line); background: #fff; font-size: 13px; color: var(--ink-2); }
.chip:hover { border-color: var(--ink); color: var(--ink); }
.chip.is-on { background: var(--ink); color: #fff; border-color: var(--ink); }
.chip--x::after { content: "✕"; margin-left: 8px; font-size: 11px; }
.select { border: 1px solid var(--line); border-radius: var(--radius-pill); padding: 8px 36px 8px 14px; background: #fff;
          appearance: none; -webkit-appearance: none; font-size: 14px;
          background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%232B2B2B' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
          background-repeat: no-repeat; background-position: right 14px center; }
.input { width: 100%; border: 1px solid var(--line); border-radius: var(--radius-pill); padding: 10px 16px; background: #fff; }

/* ---------- 6. 헤더 · 드로어 ---------- */
.hdr { position: sticky; top: 0; z-index: 50; background: var(--bg); border-bottom: 1px solid var(--line); }
.hdr__top { display: flex; align-items: center; gap: 24px; height: 72px; }
.hdr__burger { display: none; width: 40px; height: 40px; border: 0; background: none; padding: 0; align-items: center; justify-content: center; }
.hdr__logo img { height: 30px; width: auto; }
.hdr__search { flex: 1; display: flex; max-width: 560px; margin: 0 auto; border: 1px solid var(--line); border-radius: var(--radius-pill);
               overflow: hidden; background: #fff; }
.hdr__search:focus-within { border-color: var(--ink); }
.hdr__search input { flex: 1; border: 0; padding: 0 18px; height: 42px; outline: 0; background: transparent; }
.hdr__search button { border: 0; background: none; width: 44px; display: flex; align-items: center; justify-content: center; }
.hdr__util { display: flex; gap: 20px; margin-left: auto; }
.hdr__util a { display: flex; align-items: center; gap: 6px; font-size: 13px; color: var(--ink-2); position: relative; }
.hdr__util a:hover { color: var(--ink); }
.hdr__util svg { width: 20px; height: 20px; }
.hdr__count { position: absolute; top: -6px; left: 12px; min-width: 16px; height: 16px; border-radius: 8px; background: var(--accent);
              color: #fff; font-size: 10px; font-style: normal; font-weight: 700; display: flex; align-items: center; justify-content: center; padding: 0 4px; }
.hdr__nav { height: 40px; }
.hdr__menu { display: flex; align-items: center; gap: 26px; height: 100%; }
.hdr__menu > li { position: relative; height: 100%; display: flex; align-items: center; }
.hdr__menu > li > a { font-size: 14px; font-weight: 600; padding: 4px 0; border-bottom: 2px solid transparent; }
.hdr__menu > li > a:hover, .hdr__menu > li:focus-within > a { border-color: var(--ink); }
.hdr__menu .is-accent { color: var(--accent); }
.hdr__sep { width: 1px; height: 14px; background: var(--line); }
.hdr__sub { position: absolute; left: -16px; top: 100%; min-width: 200px; background: #fff; border: 1px solid var(--line);
            border-radius: 8px; padding: 10px 0; display: none; box-shadow: none; }
.hdr__sub li a { display: block; padding: 8px 18px; font-size: 14px; color: var(--ink-2); }
.hdr__sub li a:hover { background: var(--tile); color: var(--ink); }
.has-sub:hover .hdr__sub, .has-sub:focus-within .hdr__sub { display: block; }
.hdr.is-compact .hdr__top { height: 60px; }
.drawer { position: fixed; inset: 0; z-index: 60; display: none; }
.drawer.is-open { display: block; }
.drawer__backdrop { position: absolute; inset: 0; background: rgba(0,0,0,.4); }
.drawer__panel { position: absolute; left: 0; top: 0; bottom: 0; width: min(84vw, 360px); background: #fff; overflow: auto; padding: 20px 24px 40px; }
.drawer__head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.drawer__head button { border: 0; background: none; font-size: 20px; width: 36px; height: 36px; }
.drawer__menu > li { border-top: 1px solid var(--line); padding: 12px 0; }
.drawer__menu > li > a { display: block; font-weight: 700; font-size: 16px; margin-bottom: 4px; }
.drawer__menu ul a { display: block; font-size: 14px; color: var(--ink-2); padding: 5px 0; }
.drawer__links { display: flex; flex-wrap: wrap; gap: 8px 18px; padding: 16px 0; border-top: 1px solid var(--line); font-weight: 600; }
.drawer__util { display: flex; gap: 18px; padding-top: 14px; border-top: 1px solid var(--line); font-size: 14px; color: var(--ink-2); }
.chat-fab { display: none; position: fixed; right: 16px; bottom: 16px; z-index: 40; height: 48px; padding: 0 18px; border-radius: var(--radius-pill);
            background: var(--ink); color: #fff; align-items: center; gap: 8px; font-weight: 600; font-size: 14px; border: 0; }

/* ---------- 7. 카드 · 그리드 ---------- */
.grid { display: grid; gap: 28px 20px; }
.grid--2 { grid-template-columns: repeat(2, 1fr); }
.grid--3 { grid-template-columns: repeat(3, 1fr); }
.grid--4 { grid-template-columns: repeat(4, 1fr); }
.grid--5 { grid-template-columns: repeat(5, 1fr); }
.scroll-row { display: grid; grid-auto-flow: column; grid-auto-columns: calc((100% - 4 * 20px) / 5); gap: 20px; overflow-x: auto;
              scroll-snap-type: x mandatory; padding-bottom: 10px; scrollbar-width: thin; }
.scroll-row > * { scroll-snap-align: start; }
.card { position: relative; display: block; }
.card__tile { position: relative; aspect-ratio: 1 / 1; background: var(--tile); border-radius: var(--radius-sm); overflow: hidden; }
.card__tile img { width: 100%; height: 100%; object-fit: cover; transition: transform .4s ease; }
.card:hover .card__tile img { transform: scale(1.03); }
.card__tile.is-broken::after { content: "이미지 준비 중"; position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; color: var(--ink-3); font-size: 12px; }
.card__badge { position: absolute; left: 10px; top: 10px; z-index: 1; background: var(--accent); color: #fff; font-size: 11px; font-weight: 700;
               padding: 3px 9px; border-radius: var(--radius-pill); letter-spacing: .02em; }
.card__badge--new { background: var(--ink); }
.card__wish { position: absolute; right: 8px; top: 8px; z-index: 1; width: 32px; height: 32px; border-radius: 50%; border: 0;
              background: rgba(255,255,255,.9); display: flex; align-items: center; justify-content: center; font-size: 15px; color: var(--ink-2); }
.card__wish.is-on { color: var(--accent); }
.card__body { padding-top: 10px; }
.card__name { font-size: 14px; color: var(--ink-2); line-height: 1.45; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.card__price { margin-top: 5px; font-size: 15px; font-weight: 700; }
.card__price .rate { color: var(--accent); margin-right: 5px; }
.card__price del { color: var(--ink-3); font-weight: 400; font-size: 12px; margin-left: 5px; }
.card__meta { margin-top: 3px; font-size: 12px; color: var(--ink-3); }
.card__meta .tag { display: inline-block; border: 1px solid var(--line); border-radius: 3px; padding: 0 5px; margin-left: 5px; font-size: 11px; line-height: 17px; }
.room .card__tile { aspect-ratio: 4 / 3; }
.room__name { margin-top: 10px; font-weight: 600; font-size: 15px; }

/* ---------- 8. 메인 섹션 ---------- */
.hero { position: relative; height: clamp(440px, 62vh, 700px); overflow: hidden; background: var(--tile); }
.hero__slide { position: absolute; inset: 0; opacity: 0; transition: opacity .7s ease; }
.hero__slide.is-active { opacity: 1; }
.hero__slide img { width: 100%; height: 100%; object-fit: cover; }
.hero__shade { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,.5) 0%, rgba(0,0,0,.08) 55%, rgba(0,0,0,0) 100%); }
.hero__text { position: absolute; left: 0; right: 0; top: 17%; text-align: center; color: #fff; padding: 0 var(--gutter); }
.hero__text .h1 { color: #fff; text-shadow: 0 1px 12px rgba(0,0,0,.15); }
.hero__text p { font-size: 17px; opacity: .94; margin: 12px auto 24px; max-width: 560px; }
.hero__dots { position: absolute; bottom: 22px; left: 0; right: 0; display: flex; justify-content: center; gap: 8px; }
.hero__dots button { width: 8px; height: 8px; border-radius: 50%; border: 0; padding: 0; background: rgba(255,255,255,.5); }
.hero__dots button.is-active { background: #fff; }
.weekly__note { color: var(--accent); font-size: 14px; font-weight: 600; margin-left: 8px; }
.band { background: var(--cream); margin-top: var(--section); padding: 72px 0; }
.band__grid { display: grid; grid-template-columns: 1fr 1fr; gap: 48px; align-items: center; }
.band__img { aspect-ratio: 16 / 10; border-radius: var(--radius-sm); overflow: hidden; background: var(--tile); }
.band__img img { width: 100%; height: 100%; object-fit: cover; }
.band__actions { display: flex; gap: 10px; margin-top: 24px; flex-wrap: wrap; }
.band p.sub { margin-top: 12px; line-height: 1.7; }
.tabs { margin-bottom: 22px; }
.space { display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 20px; }
.space__big { position: relative; aspect-ratio: 4 / 3; background: var(--tile); border-radius: var(--radius-sm); overflow: hidden; }
.space__big img { width: 100%; height: 100%; object-fit: cover; }
.space__big figcaption { position: absolute; left: 16px; bottom: 16px; background: rgba(255,255,255,.92); border-radius: var(--radius-pill); padding: 6px 14px; font-size: 13px; }
.review__img { aspect-ratio: 1 / 1; background: var(--tile); border-radius: var(--radius-sm); overflow: hidden; }
.review__img img { width: 100%; height: 100%; object-fit: cover; }
.review__stars { color: var(--accent); font-size: 12px; letter-spacing: 1px; margin-top: 10px; }
.review__text { font-size: 14px; color: var(--ink-2); margin-top: 4px; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.review__meta { font-size: 12px; color: var(--ink-3); margin-top: 4px; }
.review__goods { font-size: 12px; margin-top: 4px; text-decoration: underline; text-underline-offset: 2px; }

/* ---------- 9. 상품 목록 ---------- */
.list__head { padding-top: 40px; }
.list__head .h2 { margin-top: 10px; }
.list__head .chips { margin-top: 18px; }
.list__body { display: grid; grid-template-columns: 200px 1fr; gap: 40px; margin-top: 36px; }
.filters { position: sticky; top: calc(var(--header-h) + 16px); align-self: start; }
.filters__backdrop { display: none; }   /* 데스크톱에서는 그리드 셀을 차지하지 않도록 숨김 */
.filters__head { display: none; }
.filters__group { margin-bottom: 22px; }
.filters__group h5 { font-family: var(--mono); font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: var(--ink-3); margin-bottom: 8px; }
.filters label { display: flex; align-items: center; gap: 8px; font-size: 14px; padding: 4px 0; cursor: pointer; color: var(--ink-2); }
.filters label:hover { color: var(--ink); }
.filters input { accent-color: var(--ink); width: 16px; height: 16px; }
.filters__reset { font-size: 13px; text-decoration: underline; background: none; border: 0; padding: 0; color: var(--ink-3); }
.filters__apply { display: none; }
.toolbar { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 18px; font-size: 14px; color: var(--ink-2); }
.toolbar__count b { color: var(--ink); }
.toolbar__filter-btn { display: none; }
.active-chips { margin-bottom: 14px; }
.active-chips:empty { display: none; }
.list__more { text-align: center; margin-top: 36px; }
.list__empty { padding: 80px 0; text-align: center; color: var(--ink-3); grid-column: 1 / -1; }
.guide { background: var(--cream); margin-top: var(--section); padding: 56px 0; }
.guide__grid { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; align-items: center; }
.guide__figure { aspect-ratio: 16 / 7; border-radius: var(--radius-sm); background: #EAE3D6; display: flex; align-items: center; justify-content: center; gap: 12px; padding: 20px; }
.guide__figure i { display: block; height: 36px; border: 2px solid var(--ink-2); border-radius: 4px; }

/* ---------- 10. 상품 상세 ---------- */
.pdp { display: grid; grid-template-columns: 7fr 5fr; gap: 48px; padding-top: 24px; }
.pdp .crumb { grid-column: 1 / -1; }
.gallery__main { position: relative; aspect-ratio: 1 / 1; background: var(--tile); border-radius: var(--radius-sm); overflow: hidden; }
.gallery__main img { width: 100%; height: 100%; object-fit: cover; }
.gallery__nav { position: absolute; top: 50%; transform: translateY(-50%); width: 40px; height: 40px; border-radius: 50%; border: 0;
                background: rgba(255,255,255,.9); font-size: 18px; display: flex; align-items: center; justify-content: center; }
.gallery__nav--prev { left: 12px; } .gallery__nav--next { right: 12px; }
.gallery__thumbs { display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; margin-top: 8px; }
.gallery__thumbs button { aspect-ratio: 1 / 1; border: 2px solid transparent; border-radius: var(--radius-sm); overflow: hidden; padding: 0; background: var(--tile); }
.gallery__thumbs button img { width: 100%; height: 100%; object-fit: cover; }
.gallery__thumbs button.is-active { border-color: var(--ink); }
.buy { position: sticky; top: calc(var(--header-h) + 16px); align-self: start; }
.buy__name { font-size: 24px; font-weight: 700; line-height: 1.3; margin-top: 6px; }
.buy__rating { font-size: 13px; color: var(--ink-3); margin-top: 6px; }
.buy__price { font-size: 26px; font-weight: 700; margin-top: 16px; line-height: 1.2; }
.buy__price .rate { color: var(--accent); margin-right: 6px; }
.buy__price del { font-size: 15px; color: var(--ink-3); font-weight: 400; margin-left: 6px; }
.buy__ship { font-size: 13px; color: var(--ink-2); margin-top: 6px; }
.buy .label { display: block; margin-top: 18px; }
.opt { display: flex; justify-content: space-between; align-items: center; border: 1px solid var(--line); border-radius: 8px; padding: 12px 14px; margin-top: 8px; cursor: pointer; font-size: 14px; }
.opt:hover { border-color: var(--ink-2); }
.opt.is-on { border: 2px solid var(--ink); padding: 11px 13px; }
.opt b { font-weight: 600; }
.opt span.muted { font-size: 12px; }
.swatches { display: flex; gap: 10px; margin-top: 8px; }
.swatch { width: 26px; height: 26px; border-radius: 50%; border: 1px solid var(--line); cursor: pointer; padding: 0; }
.swatch.is-on { outline: 2px solid var(--ink); outline-offset: 2px; }
.buy__qty { display: flex; justify-content: space-between; align-items: center; margin-top: 18px; padding-top: 14px; border-top: 1px solid var(--line); font-size: 14px; }
.qty { display: inline-flex; border: 1px solid var(--line); border-radius: var(--radius-pill); overflow: hidden; }
.qty button { width: 36px; height: 36px; border: 0; background: #fff; font-size: 16px; }
.qty span { width: 40px; text-align: center; line-height: 36px; font-weight: 600; }
.buy__total { display: flex; justify-content: space-between; align-items: baseline; margin-top: 14px; font-size: 14px; }
.buy__total b { font-size: 22px; }
.buy__actions { display: flex; gap: 8px; margin-top: 14px; }
.buy__actions .btn--primary { flex: 2; } .buy__actions .btn--secondary { flex: 1.2; }
.buy__notes { margin-top: 16px; font-size: 13px; color: var(--ink-2); line-height: 1.9; }
.buy__notes a { text-decoration: underline; text-underline-offset: 2px; }
.ptabs { position: sticky; top: var(--header-h); z-index: 30; background: #fff; border-bottom: 1px solid var(--line); margin-top: 56px; }
.ptabs ul { display: flex; gap: 28px; overflow-x: auto; }
.ptabs a { display: block; padding: 14px 0; font-size: 14px; font-weight: 600; color: var(--ink-2); border-bottom: 2px solid transparent; margin-bottom: -1px; white-space: nowrap; }
.ptabs a.is-active { color: var(--ink); border-color: var(--ink); }
.feats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.feat__img { aspect-ratio: 4 / 3; background: var(--tile); border-radius: var(--radius-sm); overflow: hidden; }
.feat__img img { width: 100%; height: 100%; object-fit: cover; }
.feat h4 { font-size: 16px; margin-top: 12px; }
.feat p { font-size: 14px; color: var(--ink-2); margin-top: 4px; line-height: 1.6; }
.spec { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; }
.spec__figure { aspect-ratio: 16 / 9; background: var(--tile); border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; color: var(--ink-3); font-size: 13px; }
.spec table { width: 100%; border-collapse: collapse; font-size: 14px; }
.spec th { text-align: left; padding: 10px 0; color: var(--ink-3); font-weight: 500; width: 36%; border-bottom: 1px solid var(--line); vertical-align: top; }
.spec td { padding: 10px 0; border-bottom: 1px solid var(--line); }
.detail-imgs { position: relative; max-height: 800px; overflow: hidden; }
.detail-imgs.is-open { max-height: none; }
.detail-imgs img { width: 100%; max-width: 860px; margin: 0 auto; }
.detail-imgs__fade { position: absolute; left: 0; right: 0; bottom: 0; height: 160px; background: linear-gradient(rgba(255,255,255,0), #fff); }
.detail-imgs.is-open .detail-imgs__fade { display: none; }
.detail-imgs__btn { text-align: center; margin-top: 16px; }
.rsum { display: grid; grid-template-columns: 200px 1fr; gap: 32px; align-items: start; }
.rsum__score { font-size: 44px; font-weight: 700; line-height: 1; }
.rsum__stars { color: var(--accent); margin-top: 6px; }
.rsum__bar { display: grid; grid-template-columns: 28px 1fr 32px; gap: 8px; align-items: center; font-size: 12px; color: var(--ink-3); margin-top: 6px; }
.rsum__bar i { height: 6px; background: var(--tile); border-radius: 3px; overflow: hidden; display: block; }
.rsum__bar i b { display: block; height: 100%; background: var(--ink); }
.rsum__photos { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.rsum__photos .ph { aspect-ratio: 1 / 1; background: var(--tile); border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; color: var(--ink-3); font-size: 12px; }
.shipinfo { font-size: 14px; color: var(--ink-2); line-height: 1.9; max-width: 720px; }
.shipinfo h4 { color: var(--ink); margin-top: 16px; }
.buybar { display: none; position: fixed; left: 0; right: 0; bottom: 0; z-index: 45; background: #fff; border-top: 1px solid var(--line);
          padding: 10px var(--gutter); align-items: center; justify-content: space-between; gap: 12px; }
.buybar b { font-size: 18px; }

/* ---------- 11. 브랜드 ---------- */
.bhero { position: relative; height: 440px; overflow: hidden; background: #2E2C2A; }
.bhero img { width: 100%; height: 100%; object-fit: cover; opacity: .7; }
.bhero__text { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; color: #fff; padding: 0 var(--gutter); }
.bhero__text .label { color: #D6D2CB; margin-bottom: 12px; }
.bhero__text .h1 { color: #fff; }
.statement { max-width: 760px; margin: 0 auto; text-align: center; font-size: 22px; line-height: 1.7; font-weight: 500; }
.numbers { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; text-align: center; }
.numbers b { font-size: 52px; font-weight: 700; line-height: 1; display: block; }
.numbers b small { font-size: 20px; margin-left: 2px; }
.numbers p { color: var(--ink-2); margin-top: 10px; font-size: 14px; }
.materials { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.showroom { background: var(--cream); margin-top: var(--section); padding: 72px 0; }
.showroom__grid { display: grid; grid-template-columns: 1fr 1fr; gap: 48px; align-items: center; }
.map { aspect-ratio: 16 / 10; background: #E6E1D6; border-radius: var(--radius-sm); display: flex; flex-direction: column; align-items: center; justify-content: center; color: var(--ink-2); font-size: 14px; gap: 8px; text-align: center; padding: 20px; }
.showroom__info { font-size: 15px; line-height: 1.9; margin-top: 10px; }

/* ---------- 12. 푸터 ---------- */
.ftr { background: var(--footer); color: #CFCAC3; margin-top: var(--section); padding: 64px 0 32px; font-size: 13px; }
.ftr__grid { display: grid; grid-template-columns: 1.6fr 1fr 1fr 1fr 1.6fr; gap: 32px; }
.ftr h4 { color: #fff; font-size: 13px; margin-bottom: 12px; }
.ftr li { margin-bottom: 8px; }
.ftr a:hover { color: #fff; }
.ftr__logo img { height: 28px; width: auto; filter: brightness(0) invert(1); opacity: .92; margin-bottom: 16px; }
.ftr__company { line-height: 1.8; }
.ftr__tel { color: #fff; font-size: 20px; font-weight: 700; }
.ftr__news { display: flex; gap: 8px; margin-top: 10px; }
.ftr__news input { flex: 1; min-width: 0; background: transparent; border: 1px solid #4A463F; color: #fff; padding: 10px 14px; border-radius: var(--radius-pill); }
.ftr__legal { border-top: 1px solid #3A3631; margin-top: 40px; padding-top: 20px; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px 16px; font-size: 12px; color: #8F8A82; }
.ftr__legal a { margin-right: 14px; }

/* ---------- 13. 유틸 ---------- */
.mt-8 { margin-top: 8px; } .mt-16 { margin-top: 16px; } .mt-24 { margin-top: 24px; } .mt-40 { margin-top: 40px; }
.center { text-align: center; }
.hide-m { } .show-m { display: none !important; }
.notice { padding: 40px; text-align: center; color: var(--ink-3); background: var(--tile); border-radius: var(--radius-sm); }

/* ---------- 14. 반응형 ---------- */
@media (max-width: 1024px) {
  :root { --header-h: 104px; }
  .grid--4, .grid--5 { grid-template-columns: repeat(3, 1fr); }
  .scroll-row { grid-auto-columns: calc((100% - 2 * 20px) / 3); }
  .hdr__util a span { display: none; }
  .hdr__menu { gap: 18px; }
  .ftr__grid { grid-template-columns: 1fr 1fr; }
  .list__body { grid-template-columns: 170px 1fr; gap: 24px; }
  .pdp { grid-template-columns: 1fr 1fr; gap: 28px; }
  .space { grid-template-columns: 1fr 1fr; }
  .space__big { grid-column: 1 / -1; }
}
@media (max-width: 768px) {
  :root { --gutter: 16px; --section: 56px; --header-h: 60px; }
  body { font-size: 14px; }
  .h1 { font-size: 30px; } .h2 { font-size: 22px; }
  .sec__head { margin-bottom: 18px; }
  .grid { gap: 20px 12px; }
  .grid--2, .grid--3, .grid--4, .grid--5 { grid-template-columns: repeat(2, 1fr); }
  .scroll-row { grid-auto-columns: 42vw; gap: 12px; }
  .hdr__top { height: 60px; gap: 10px; }
  .hdr__burger { display: flex; }
  .hdr__logo img { height: 24px; }
  .hdr__search { display: none; }
  .hdr__util { gap: 14px; }
  .hdr__nav { display: none; }
  .chat-fab { display: flex; }
  .hero { height: 62vw; min-height: 340px; }
  .hero__text { top: 14%; }
  .hero__text p { font-size: 14px; margin: 8px auto 16px; }
  .band { padding: 40px 0; }
  .band__grid, .guide__grid, .showroom__grid { grid-template-columns: 1fr; gap: 20px; }
  .band__img { order: -1; }
  .space { grid-template-columns: 1fr 1fr; gap: 12px; }
  .list__body { grid-template-columns: 1fr; gap: 0; margin-top: 20px; }
  .filters { position: fixed; left: 0; right: 0; bottom: 0; top: auto; max-height: 82vh; background: #fff; border-radius: 16px 16px 0 0;
             padding: 20px; transform: translateY(100%); transition: transform .3s; z-index: 61; overflow: auto; }
  .filters.is-open { transform: none; }
  .filters__head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; font-weight: 700; }
  .filters__head button { border: 0; background: none; font-size: 20px; }
  .filters__apply { display: block; margin-top: 12px; }
  .filters__backdrop { position: fixed; inset: 0; background: rgba(0,0,0,.4); z-index: 60; display: none; }
  .filters__backdrop.is-open { display: block; }
  .toolbar__filter-btn { display: inline-flex; }
  .pdp { grid-template-columns: 1fr; gap: 20px; padding-top: 12px; }
  .buy { position: static; }
  .ptabs { margin-top: 32px; }
  .ptabs ul { gap: 18px; }
  .feats, .materials, .numbers { grid-template-columns: 1fr; gap: 20px; }
  .numbers { grid-template-columns: repeat(3, 1fr); gap: 8px; }
  .numbers b { font-size: 32px; } .numbers b small { font-size: 14px; }
  .spec { grid-template-columns: 1fr; gap: 16px; }
  .rsum { grid-template-columns: 1fr; gap: 16px; }
  .rsum__photos { grid-template-columns: repeat(4, 1fr); gap: 6px; }
  .buybar { display: flex; }
  body.has-buybar { padding-bottom: 72px; }
  .bhero { height: 300px; }
  .statement { font-size: 17px; }
  .ftr { padding: 40px 0 24px; }
  .ftr__grid { grid-template-columns: 1fr; gap: 20px; }
  .hide-m { display: none !important; } .show-m { display: block !important; }
}
```

- [x] **Step 2: 문법 확인**

Run: `python -c "import re,io;s=open('assets/style.css',encoding='utf-8').read();print('braces', s.count('{'), s.count('}'))"`
Expected: 두 숫자가 같음(여는/닫는 중괄호 수 일치).

- [x] **Step 3: 커밋**

```bash
git add assets/style.css && git commit -m "feat(style): 디자인 토큰과 공통 컴포넌트 스타일

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 5: app.js 공통 코드와 순수 함수 테스트 (TDD)

**Files:**
- Create: `assets/app.js`
- Create: `tests/app.test.html`

`app.js`는 즉시실행함수 하나로 `window.RARO`를 만든다. 페이지별 초기화 함수는 `pages` 객체에 등록하며, Task 6–9에서 `/* ==== END PAGES ==== */` 주석 **바로 위**에 추가한다.

- [x] **Step 1: 실패하는 테스트 페이지 작성**

`tests/app.test.html`:
```html
<!doctype html>
<meta charset="utf-8">
<title>RARO app.js 테스트</title>
<style>body{font-family:monospace;padding:20px} .ok{color:green} .ng{color:#c00;font-weight:bold}</style>
<h1>RARO app.js 순수 함수 테스트</h1>
<pre id="result">실행 중…</pre>
<script src="../assets/app.js"></script>
<script>
(function () {
  const out = [];
  let pass = 0, fail = 0;
  function eq(name, actual, expected) {
    const a = JSON.stringify(actual), e = JSON.stringify(expected);
    if (a === e) { pass++; out.push('PASS ' + name); }
    else { fail++; out.push('FAIL ' + name + '\n   expected ' + e + '\n   actual   ' + a); }
  }
  const P = [
    { no: '1', name: 'A 1400 세라믹 4인 식탁 세트', price: 398000, listPrice: 500000, reviewCount: 84, size: 1400, seats: 4, shape: '사각', material: '무광 세라믹', kind: '세트', priceBand: '30–50만원', cate: '012002', top: '012' },
    { no: '2', name: 'B 800 원목 2인 식탁 세트', price: 178000, listPrice: null, reviewCount: 3, size: 800, seats: 2, shape: '사각', material: '원목', kind: '세트', priceBand: '30만원 이하', cate: '013003', top: '013' },
    { no: '3', name: 'C 1800 유광 세라믹 6인 원형 테이블', price: 689000, listPrice: 800000, reviewCount: 20, size: 1800, seats: 6, shape: '원형', material: '유광 세라믹', kind: '단품', priceBand: '50만원 이상', cate: '012003', top: '012' },
  ];

  eq('fmt', RARO.fmt(398000), '398,000원');
  eq('fmt null', RARO.fmt(null), '가격 문의');
  eq('discountRate 20%', RARO.discountRate(398000, 500000), 20);
  eq('discountRate none', RARO.discountRate(178000, null), 0);
  eq('discountRate not higher', RARO.discountRate(178000, 178000), 0);
  eq('optionTotal', RARO.optionTotal(398000, 40000, 2), 876000);
  eq('optionTotal null delta', RARO.optionTotal(398000, null, 1), 398000);
  eq('optionTotal qty min 1', RARO.optionTotal(100, 0, 0), 100);
  eq('sizeBand', [RARO.sizeBand(800), RARO.sizeBand(1400), RARO.sizeBand(1800), RARO.sizeBand(null)], ['1000 이하', '1200–1400', '1600 이상', null]);
  eq('sort priceAsc', RARO.sortProducts(P, 'priceAsc').map(p => p.no), ['2', '1', '3']);
  eq('sort priceDesc', RARO.sortProducts(P, 'priceDesc').map(p => p.no), ['3', '1', '2']);
  eq('sort popular', RARO.sortProducts(P, 'popular').map(p => p.no), ['1', '3', '2']);
  eq('sort new', RARO.sortProducts(P, 'new').map(p => p.no), ['3', '2', '1']);
  eq('sort reco keeps order', RARO.sortProducts(P, 'reco').map(p => p.no), ['1', '2', '3']);
  eq('sort does not mutate', P.map(p => p.no), ['1', '2', '3']);
  eq('filter none', RARO.applyFilters(P, {}).length, 3);
  eq('filter material', RARO.applyFilters(P, { material: ['무광 세라믹'] }).map(p => p.no), ['1']);
  eq('filter size band', RARO.applyFilters(P, { size: ['1200–1400', '1600 이상'] }).map(p => p.no), ['1', '3']);
  eq('filter two groups AND', RARO.applyFilters(P, { size: ['1600 이상'], kind: ['세트'] }).map(p => p.no), []);
  eq('filter seats', RARO.applyFilters(P, { seats: ['6인'] }).map(p => p.no), ['3']);
  eq('filter price', RARO.applyFilters(P, { price: ['30만원 이하'] }).map(p => p.no), ['2']);
  eq('filter sale', RARO.applyFilters(P, { sale: ['1'] }).map(p => p.no), ['1', '3']);
  eq('filterOptions material', RARO.filterOptions(P, 'material'), ['무광 세라믹', '원목', '유광 세라믹']);
  eq('filterOptions price fixed order', RARO.filterOptions(P, 'price'), ['30만원 이하', '30–50만원', '50만원 이상']);
  eq('filterOptions size ordered', RARO.filterOptions(P, 'size'), ['1000 이하', '1200–1400', '1600 이상']);
  eq('filterOptions seats', RARO.filterOptions(P, 'seats'), ['2인', '4인', '6인']);
  eq('searchProducts', RARO.searchProducts(P, '세라믹 4인').map(p => p.no), ['1']);
  eq('searchProducts empty query', RARO.searchProducts(P, '').length, 3);
  eq('childName', RARO.childName('012002'), '세라믹 식탁 세트');
  eq('topName', RARO.topName('006'), '의자');
  eq('topOfCate', RARO.topOfCate('004003'), '004');
  eq('stars', RARO.stars(4), '★★★★☆');
  eq('esc', RARO.esc('<a href="x">&\'</a>'), '&lt;a href=&quot;x&quot;&gt;&amp;&#39;&lt;/a&gt;');

  const summary = (fail ? 'FAIL ' : 'OK ') + pass + ' passed, ' + fail + ' failed';
  document.getElementById('result').innerHTML = out.map(l => '<div class="' + (l.startsWith('PASS') ? 'ok' : 'ng') + '">' + l.replace(/</g, '&lt;') + '</div>').join('') + '<hr><b id="summary">' + summary + '</b>';
  document.title = summary;
  console.log(summary);
})();
</script>
```

- [x] **Step 2: 실패 확인**

먼저 로컬 서버를 띄운다. Bash 도구의 `run_in_background: true`로 아래를 **한 번만** 실행한다(이미 떠 있으면 생략. 포트가 잡혀 있으면 `netstat -ano | grep 8080`으로 확인):
```bash
cd "c:/Users/전윤성/yunseong/raro-furniture" && python -m http.server 8080
```
그다음 Run:
```bash
"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless=new --disable-gpu --user-data-dir="$LOCALAPPDATA/Temp/edge-shot" --dump-dom "http://localhost:8080/tests/app.test.html" 2>/dev/null | grep -o 'id="summary">[^<]*'
```
Expected: `app.js`가 없으므로 `RARO is not defined` 오류로 결과가 비어 있거나 `summary`가 출력되지 않음(= 실패).

`--dump-dom`이 아무것도 출력하지 않으면 대신 `--screenshot=docs/screenshots/test.png --window-size=900,1400` 으로 찍어 Read 도구로 확인한다.

- [x] **Step 3: app.js 공통 코드 작성**

`assets/app.js`:
```js
/* ============================================================
   RARO — 라로퍼니처 리디자인 프로토타입 공통 스크립트
   - 데이터: data/site.json (fetch)
   - 페이지: <body data-page="home|list|view|brand">
   ============================================================ */
window.RARO = (function () {
  'use strict';

  /* ==== 정적 내비게이션 (site.json 없이도 헤더가 그려지도록 상수로 보관) ==== */
  const NAV = [
    { code: '012', name: '세라믹 · 대리석 식탁', short: '세라믹·대리석 식탁',
      children: [['012002', '세라믹 식탁 세트'], ['012003', '세라믹 테이블'], ['012004', '대리석 식탁 세트'], ['012005', '대리석 테이블']] },
    { code: '013', name: '원목 식탁', short: '원목 식탁',
      children: [['013002', '원목 테이블'], ['013003', '원목 식탁 세트']] },
    { code: '003', name: '거실가구', short: '거실가구',
      children: [['003001', '소파'], ['003002', 'TV거실장'], ['003004', '거실테이블'], ['003005', '소가구']] },
    { code: '006', name: '의자', short: '의자',
      children: [['006001', '원목 의자'], ['006003', '인테리어 의자'], ['006004', '스툴'], ['006005', '벤치']] },
    { code: '004', name: '서재 · 침실가구', short: '서재·침실',
      children: [['004001', '침대'], ['004002', '책상'], ['004003', '보조 가구'], ['004004', '책상의자'], ['004005', '옷장 · 드레스룸 · 서랍장']] },
  ];
  const COMPANY_FALLBACK = { brand: '라로퍼니처', name: '㈜퍼니우스', ceo: '전재국', address: '경기도 파주시 고봉로 721-50',
    showroom: '경기도 고양시 일산동구 고봉로 757-11', tel: '031-977-7352', email: 'furnius946@naver.com',
    bizNo: '668-86-00834', mailOrderNo: '제 2018-경기파주-0229호', privacyOfficer: '김영순' };
  const PRICE_BANDS = ['30만원 이하', '30–50만원', '50만원 이상'];
  const SIZE_BANDS = ['1000 이하', '1200–1400', '1600 이상'];
  const FILTER_DEFS = {
    '012': [['size', '사이즈'], ['shape', '형태'], ['material', '상판'], ['kind', '구성'], ['price', '가격']],
    '013': [['size', '사이즈'], ['shape', '형태'], ['kind', '구성'], ['price', '가격']],
    '003': [['cate', '종류'], ['seats', '인원'], ['material', '소재'], ['price', '가격']],
    '006': [['cate', '종류'], ['material', '소재'], ['price', '가격']],
    '004': [['cate', '종류'], ['size', '사이즈'], ['material', '소재'], ['kind', '구성'], ['price', '가격']],
    'all': [['top', '카테고리'], ['material', '소재'], ['price', '가격']],
  };
  const ICON = {
    menu: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
    search: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>',
    user: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7"/></svg>',
    heart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 21s-7-4.6-9.3-9A5.2 5.2 0 0 1 12 6.5 5.2 5.2 0 0 1 21.3 12C19 16.4 12 21 12 21z"/></svg>',
    cart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 4h2l2.4 11.2a1 1 0 0 0 1 .8h9.6a1 1 0 0 0 1-.8L21 8H6.5"/><circle cx="9" cy="20" r="1.3"/><circle cx="17" cy="20" r="1.3"/></svg>',
    chat: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 5h16v11H9l-5 4z"/></svg>',
  };

  /* ==== 순수 함수 ==== */
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const fmt = (n) => (n == null ? '가격 문의' : Number(n).toLocaleString('ko-KR') + '원');
  const stars = (n) => '★'.repeat(n) + '☆'.repeat(5 - n);
  function discountRate(price, listPrice) {
    if (!price || !listPrice || listPrice <= price) return 0;
    return Math.round((1 - price / listPrice) * 100);
  }
  function optionTotal(base, delta, qty) {
    return (Number(base) + (Number(delta) || 0)) * Math.max(1, Number(qty) | 0);
  }
  function sizeBand(size) {
    if (!size) return null;
    if (size <= 1000) return SIZE_BANDS[0];
    if (size <= 1400) return SIZE_BANDS[1];
    return SIZE_BANDS[2];
  }
  function sortProducts(list, key) {
    const a = list.slice();
    switch (key) {
      case 'popular': case 'review': return a.sort((x, y) => (y.reviewCount || 0) - (x.reviewCount || 0));
      case 'priceAsc': return a.sort((x, y) => (x.price || 0) - (y.price || 0));
      case 'priceDesc': return a.sort((x, y) => (y.price || 0) - (x.price || 0));
      case 'new': return a.sort((x, y) => Number(y.no) - Number(x.no));
      default: return a;
    }
  }
  function valueFor(p, key) {
    switch (key) {
      case 'size': return sizeBand(p.size);
      case 'seats': return p.seats ? p.seats + '인' : null;
      case 'price': return p.priceBand;
      case 'sale': return discountRate(p.price, p.listPrice) > 0 ? '1' : '0';
      default: return p[key] == null ? null : p[key];
    }
  }
  function applyFilters(list, active) {
    const groups = Object.entries(active || {}).map(([k, v]) => [k, Array.from(v || [])]).filter(([, v]) => v.length);
    if (!groups.length) return list.slice();
    return list.filter((p) => groups.every(([k, vals]) => vals.includes(valueFor(p, k))));
  }
  function filterOptions(list, key) {
    if (key === 'price') return PRICE_BANDS.filter((b) => list.some((p) => p.priceBand === b));
    if (key === 'size') return SIZE_BANDS.filter((b) => list.some((p) => sizeBand(p.size) === b));
    const vals = [];
    list.forEach((p) => { const v = valueFor(p, key); if (v != null && !vals.includes(v)) vals.push(v); });
    if (key === 'seats') vals.sort((a, b) => parseInt(a, 10) - parseInt(b, 10));
    return vals;
  }
  function searchProducts(list, q) {
    const terms = String(q || '').trim().split(/\s+/).filter(Boolean);
    if (!terms.length) return list.slice();
    return list.filter((p) => terms.every((t) => p.name.includes(t)));
  }
  const topOf = (code) => NAV.find((t) => t.code === code);
  const topName = (code) => (topOf(code) ? topOf(code).name : '');
  function childName(code) {
    for (const t of NAV) { const c = t.children.find((ch) => ch[0] === code); if (c) return c[1]; }
    return '';
  }
  function topOfCate(code) {
    for (const t of NAV) if (t.code === code || t.children.some((ch) => ch[0] === code)) return t.code;
    return null;
  }
  const labelFor = (key, v) => (key === 'cate' ? childName(v) : key === 'top' ? topName(v) : v);

  /* ==== 데이터 ==== */
  const state = { data: null, byNo: null };
  async function loadData() {
    if (state.data) return state.data;
    const res = await fetch('data/site.json', { cache: 'no-cache' });
    if (!res.ok) throw new Error('site.json ' + res.status);
    state.data = await res.json();
    state.byNo = new Map(state.data.products.map((p) => [p.no, p]));
    return state.data;
  }
  const product = (no) => (state.byNo ? state.byNo.get(String(no)) : undefined);
  const products = (nos) => (nos || []).map(product).filter(Boolean);
  const param = (k) => new URLSearchParams(location.search).get(k);

  /* ==== 템플릿 ==== */
  const IMG_ERR = 'onerror="this.onerror=null;this.parentNode.classList.add(\'is-broken\');this.remove()"';
  function cardHTML(p, opts) {
    opts = opts || {};
    const rate = discountRate(p.price, p.listPrice);
    const badge = opts.badge || (rate >= 20 ? '특가' : '');
    const meta = [];
    if (p.reviewCount) meta.push('★ 리뷰 ' + p.reviewCount);
    if (p.detail && p.detail.options && p.detail.options.length) meta.push('구성 ' + p.detail.options.length + '종');
    const tags = (p.tags || []).map((t) => '<span class="tag">' + esc(t) + '</span>').join('');
    return '<a class="card" href="view.html?no=' + esc(p.no) + '">'
      + '<div class="card__tile">'
      + (badge ? '<span class="card__badge' + (badge === 'NEW' ? ' card__badge--new' : '') + '">' + esc(badge) + '</span>' : '')
      + '<img src="' + esc(p.image) + '" alt="' + esc(p.name) + '" loading="lazy" ' + IMG_ERR + '>'
      + '<button class="card__wish" type="button" aria-label="찜하기" onclick="event.preventDefault();this.classList.toggle(\'is-on\')">♡</button>'
      + '</div><div class="card__body"><div class="card__name">' + esc(p.name) + '</div>'
      + '<div class="card__price">' + (rate ? '<span class="rate">' + rate + '%</span>' : '') + fmt(p.price)
      + (p.listPrice ? '<del>' + fmt(p.listPrice) + '</del>' : '') + '</div>'
      + '<div class="card__meta">' + meta.join(' · ') + tags + '</div></div></a>';
  }
  function renderCards(el, list, opts) {
    el.innerHTML = list.length ? list.map((p) => cardHTML(p, opts)).join('') : '<div class="list__empty">조건에 맞는 상품이 없습니다.</div>';
  }
  function img(src, alt, cls) {
    return '<img src="' + esc(src) + '" alt="' + esc(alt || '') + '"' + (cls ? ' class="' + cls + '"' : '') + ' loading="lazy" ' + IMG_ERR + '>';
  }

  /* ==== 헤더 · 푸터 ==== */
  function headerHTML() {
    const menu = NAV.map((t) => '<li class="has-sub"><a href="list.html?cate=' + t.code + '">' + esc(t.short) + '</a><ul class="hdr__sub">'
      + t.children.map((c) => '<li><a href="list.html?cate=' + c[0] + '">' + esc(c[1]) + '</a></li>').join('') + '</ul></li>').join('');
    const drawer = NAV.map((t) => '<li><a href="list.html?cate=' + t.code + '">' + esc(t.name) + '</a><ul>'
      + t.children.map((c) => '<li><a href="list.html?cate=' + c[0] + '">' + esc(c[1]) + '</a></li>').join('') + '</ul></li>').join('');
    return '<div class="hdr__top container">'
      + '<button class="hdr__burger" type="button" aria-label="전체 메뉴" data-open-drawer>' + ICON.menu + '</button>'
      + '<a class="hdr__logo" href="index.html"><img src="assets/logo-header.png" alt="라로퍼니처 RARO FURNITURE"></a>'
      + '<form class="hdr__search" action="list.html" role="search"><input type="search" name="q" placeholder="세라믹 식탁, 리클라이너 소파 검색" aria-label="검색어">'
      + '<input type="hidden" name="cate" value="all"><button type="submit" aria-label="검색">' + ICON.search + '</button></form>'
      + '<nav class="hdr__util" aria-label="회원 메뉴"><a href="#" title="로그인">' + ICON.user + '<span>로그인</span></a>'
      + '<a href="#" title="찜">' + ICON.heart + '<span>찜</span></a>'
      + '<a href="#" title="장바구니">' + ICON.cart + '<span>장바구니</span><em class="hdr__count">0</em></a></nav></div>'
      + '<nav class="hdr__nav container" aria-label="카테고리"><ul class="hdr__menu">' + menu
      + '<li class="hdr__sep" aria-hidden="true"></li>'
      + '<li><a href="list.html?cate=all&sort=popular">BEST</a></li><li><a href="list.html?cate=all&sort=new">NEW</a></li>'
      + '<li><a class="is-accent" href="list.html?cate=all&sale=1">SALE</a></li>'
      + '<li class="hdr__sep" aria-hidden="true"></li>'
      + '<li><a href="brand.html">브랜드</a></li><li><a href="brand.html#showroom">쇼룸</a></li><li><a href="index.html#space">리뷰</a></li></ul></nav>'
      + '<div class="drawer" data-drawer><div class="drawer__backdrop" data-close-drawer></div><div class="drawer__panel">'
      + '<div class="drawer__head"><img src="assets/logo-header.png" alt="라로퍼니처" height="26"><button type="button" aria-label="닫기" data-close-drawer>✕</button></div>'
      + '<ul class="drawer__menu">' + drawer + '</ul>'
      + '<div class="drawer__links"><a href="list.html?cate=all&sort=popular">BEST</a><a href="list.html?cate=all&sort=new">NEW</a>'
      + '<a class="is-accent" href="list.html?cate=all&sale=1">SALE</a><a href="brand.html">브랜드</a><a href="brand.html#showroom">쇼룸</a></div>'
      + '<div class="drawer__util"><a href="#">로그인</a><a href="#">회원가입</a><a href="#">주문조회</a></div></div></div>';
  }
  function footerHTML(c) {
    c = c || COMPANY_FALLBACK;
    return '<div class="container"><div class="ftr__grid">'
      + '<div><div class="ftr__logo"><img src="assets/logo-header.png" alt="라로퍼니처"></div>'
      + '<div class="ftr__company">' + esc(c.name) + ' · 대표 ' + esc(c.ceo) + '<br>' + esc(c.address) + '<br>사업자등록번호 ' + esc(c.bizNo)
      + '<br>통신판매업신고 ' + esc(c.mailOrderNo) + '<br>개인정보관리자 ' + esc(c.privacyOfficer) + '</div></div>'
      + '<div><h4>고객센터</h4><div class="ftr__tel">' + esc(c.tel) + '</div><ul class="mt-8"><li>평일 09:00–18:00 (확인 필요)</li><li>' + esc(c.email) + '</li>'
      + '<li><a href="#">카카오톡 상담</a></li><li><a href="#">네이버톡톡</a></li></ul></div>'
      + '<div><h4>쇼핑 안내</h4><ul><li><a href="#">이용안내</a></li><li><a href="#">배송 · 설치</a></li><li><a href="#">교환 · 반품</a></li><li><a href="#">이벤트</a></li><li><a href="index.html#space">리뷰</a></li></ul></div>'
      + '<div><h4>회사</h4><ul><li><a href="brand.html">브랜드 스토리</a></li><li><a href="brand.html#showroom">일산 쇼룸</a></li><li><a href="#">이용약관</a></li><li><a href="#">개인정보처리방침</a></li></ul></div>'
      + '<div><h4>새 소식 받기</h4><p>신제품과 이번 주 특가를 메일로 보내 드립니다.</p>'
      + '<form class="ftr__news" onsubmit="event.preventDefault();this.querySelector(\'input\').value=\'\';alert(\'구독 신청은 실제 사이트 연동 후 동작합니다.\')">'
      + '<input type="email" placeholder="이메일 주소" aria-label="이메일 주소" required><button class="btn btn--accent btn--sm" type="submit">구독</button></form></div>'
      + '</div><div class="ftr__legal"><div><a href="#">이용약관</a><a href="#">개인정보처리방침</a><a href="brand.html">회사소개</a></div>'
      + '<div>© ' + new Date().getFullYear() + ' ' + esc(c.name) + '. All rights reserved. · 호스팅 엔에이치엔커머스(주)</div></div></div>';
  }
  function bindHeader(hdr) {
    const drawer = hdr.querySelector('[data-drawer]');
    hdr.querySelectorAll('[data-open-drawer]').forEach((b) => b.addEventListener('click', () => drawer.classList.add('is-open')));
    hdr.querySelectorAll('[data-close-drawer]').forEach((b) => b.addEventListener('click', () => drawer.classList.remove('is-open')));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') drawer.classList.remove('is-open'); });
    let last = 0;
    window.addEventListener('scroll', () => {
      const y = window.scrollY;
      if ((y > 80) !== (last > 80)) hdr.classList.toggle('is-compact', y > 80);
      last = y;
    }, { passive: true });
  }

  /* ==== 페이지 초기화 ==== */
  const pages = {};

  /* ==== END PAGES ==== */

  async function init() {
    const hdr = document.getElementById('site-header');
    if (hdr) { hdr.innerHTML = headerHTML(); bindHeader(hdr); }
    let data = null;
    try { data = await loadData(); } catch (e) { console.error('[RARO] 데이터 로드 실패', e); }
    const ftr = document.getElementById('site-footer');
    if (ftr) ftr.innerHTML = footerHTML(data ? data.company : null);
    if (!document.querySelector('.chat-fab')) {
      const fab = document.createElement('a');
      fab.className = 'chat-fab'; fab.href = '#'; fab.innerHTML = ICON.chat + '상담';
      document.body.appendChild(fab);
    }
    const page = document.body.dataset.page;
    if (!data) {
      document.querySelectorAll('[data-needs-data]').forEach((el) => {
        el.innerHTML = '<div class="notice">상품 정보를 불러오지 못했습니다. <code>python -m http.server 8080</code> 으로 띄운 로컬 서버에서 열어 주세요.</div>';
      });
      return;
    }
    if (pages[page]) pages[page](data);
  }
  if (typeof document !== 'undefined') document.addEventListener('DOMContentLoaded', init);

  return { NAV, FILTER_DEFS, esc, fmt, stars, discountRate, optionTotal, sizeBand, sortProducts, applyFilters, filterOptions,
           searchProducts, valueFor, labelFor, topOf, topName, childName, topOfCate, loadData, product, products, param,
           cardHTML, renderCards, img, headerHTML, footerHTML, pages, state };
})();
```

- [x] **Step 4: 테스트 통과 확인**

Run:
```bash
"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless=new --disable-gpu --dump-dom "http://localhost:8080/tests/app.test.html" 2>/dev/null | grep -o 'id="summary">[^<]*'
```
Expected: `id="summary">OK 33 passed, 0 failed`

FAIL이 있으면 `--dump-dom` 전체 출력에서 `FAIL` 줄을 읽고 `app.js`를 고친다. `searchProducts`는 공백으로 나눈 모든 단어가 상품명에 포함되어야 한다(AND).

- [x] **Step 5: 커밋**

```bash
git add assets/app.js tests/app.test.html && git commit -m "feat(js): RARO 공통 코드(데이터·카드·헤더·푸터)와 순수 함수 테스트

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 6: 메인 페이지 (index.html + pages.home)

**Files:**
- Create: `index.html`
- Modify: `assets/app.js` (`/* ==== END PAGES ==== */` 바로 위에 `pages.home` 추가)

- [x] **Step 1: index.html 작성**

`index.html`:
```html
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>라로퍼니처 — 친환경 가구 브랜드</title>
<meta name="description" content="포세린 세라믹 식탁, 고무나무 원목 식탁, 전동 리클라이너 소파. 30년 제조 기술력의 원목 전문 브랜드 라로퍼니처.">
<link rel="icon" href="assets/logo-header.png">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="assets/style.css">
</head>
<body data-page="home">
<a class="skip" href="#main">본문 바로가기</a>
<header class="hdr" id="site-header"></header>
<main id="main">
  <section class="hero" id="hero" aria-label="추천 상품" data-needs-data></section>

  <section class="sec container" id="rooms">
    <div class="sec__head"><div><h2 class="h2">공간별로 둘러보기</h2><p class="sub">식탁부터 침실까지, 찾는 가구가 있는 곳으로 바로 갑니다.</p></div></div>
    <div class="grid grid--5" data-rooms></div>
  </section>

  <section class="sec container" id="weekly">
    <div class="sec__head">
      <div><h2 class="h2">이번 주 특가<span class="weekly__note">7일 단독 최저가</span></h2>
        <p class="sub">매주 월요일에 바뀝니다 · 이번 주 남은 기간 <b data-weekly-left></b></p></div>
      <a class="more" href="list.html?cate=all&sale=1">전체 보기</a>
    </div>
    <div class="scroll-row" data-weekly data-needs-data></div>
  </section>

  <section class="sec container" id="best">
    <div class="sec__head">
      <div><h2 class="h2">이번 달 베스트.</h2><p class="sub">고객들이 가장 많이 선택한 가구</p></div>
      <a class="more" href="list.html?cate=all&sort=popular">전체 보기</a>
    </div>
    <div class="grid grid--4" data-best data-needs-data></div>
  </section>

  <section class="band" id="brand-band">
    <div class="container band__grid">
      <div>
        <span class="label">Brand Story</span>
        <h2 class="h2 mt-8" data-slogan>현대적 감각으로 자연을 다듬다.</h2>
        <p class="sub" data-story></p>
        <div class="band__actions">
          <a class="btn btn--primary" href="brand.html">브랜드 스토리</a>
          <a class="btn btn--secondary" href="brand.html#showroom">일산 쇼룸 안내</a>
        </div>
      </div>
      <div class="band__img"><img src="assets/company-story.jpg" alt="원목을 다듬는 장인의 손"></div>
    </div>
  </section>

  <section class="sec container" id="new">
    <div class="sec__head">
      <div><h2 class="h2">새로 나온 가구</h2><p class="sub">이달의 신제품, 카테고리별로 골라 보세요.</p></div>
      <a class="more" href="list.html?cate=all&sort=new">전체 보기</a>
    </div>
    <div class="chips tabs" data-new-tabs></div>
    <div class="grid grid--4" data-new data-needs-data></div>
  </section>

  <section class="sec container" id="space">
    <div class="sec__head"><div><h2 class="h2">고객의 공간에서.</h2><p class="sub">실제 후기 사진과 라로퍼니처가 제안하는 스타일링</p></div></div>
    <div class="space" data-space data-needs-data></div>
  </section>
</main>
<footer class="ftr" id="site-footer"></footer>
<script src="assets/app.js"></script>
</body>
</html>
```

- [x] **Step 2: pages.home 추가**

`assets/app.js`의 `/* ==== END PAGES ==== */` 바로 위에 추가:
```js
  pages.home = function (data) {
    const H = data.home;
    /* 히어로 */
    const hero = document.getElementById('hero');
    hero.innerHTML = H.hero.map((s, i) => '<div class="hero__slide' + (i === 0 ? ' is-active' : '') + '">' + img(s.img, s.title)
      + '<div class="hero__shade"></div><div class="hero__text container"><h1 class="h1">' + esc(s.title) + '</h1><p>' + esc(s.sub) + '</p>'
      + '<a class="btn btn--white btn--lg" href="' + esc(s.href) + '">' + esc(s.cta) + '</a></div></div>').join('')
      + '<div class="hero__dots">' + H.hero.map((_, i) => '<button type="button" aria-label="' + (i + 1) + '번 슬라이드"' + (i === 0 ? ' class="is-active"' : '') + '></button>').join('') + '</div>';
    const slides = hero.querySelectorAll('.hero__slide'), dots = hero.querySelectorAll('.hero__dots button');
    let cur = 0, timer = null;
    const go = (n) => {
      slides[cur].classList.remove('is-active'); dots[cur].classList.remove('is-active');
      cur = (n + slides.length) % slides.length;
      slides[cur].classList.add('is-active'); dots[cur].classList.add('is-active');
    };
    const auto = () => { clearInterval(timer); if (slides.length > 1) timer = setInterval(() => go(cur + 1), 6000); };
    dots.forEach((d, i) => d.addEventListener('click', () => { go(i); auto(); }));
    auto();
    /* 공간별로 둘러보기: 대분류마다 상세가 있는 대표 상품의 두 번째 갤러리 사진 */
    const repImage = (code) => {
      const rep = data.products.find((p) => p.top === code && p.detail) || data.products.find((p) => p.top === code);
      return rep ? ((rep.detail && rep.detail.gallery[1]) || rep.image) : '';
    };
    document.querySelector('[data-rooms]').innerHTML = NAV.map((t) => '<a class="card room" href="list.html?cate=' + t.code + '"><div class="card__tile">'
      + img(repImage(t.code), t.name) + '</div><div class="room__name">' + esc(t.name) + '</div></a>').join('');
    /* 이번 주 특가 */
    renderCards(document.querySelector('[data-weekly]'), products(H.weekly), { badge: '특가' });
    const daysLeft = (8 - new Date().getDay()) % 7 || 7;
    document.querySelector('[data-weekly-left]').textContent = daysLeft + '일';
    /* 베스트 */
    renderCards(document.querySelector('[data-best]'), products(H.best));
    /* 브랜드 띠 */
    document.querySelector('[data-slogan]').textContent = data.company.slogan;
    document.querySelector('[data-story]').textContent = data.company.story[0] + ' ' + data.company.story[1];
    /* 새로 나온 가구: 전체 탭 = 사이트 NEW 목록, 카테고리 탭 = 해당 카테고리 최신 8개 */
    const newAll = products(H.new);
    const tabsEl = document.querySelector('[data-new-tabs]'), newEl = document.querySelector('[data-new]');
    const tabs = [['all', '전체']].concat(NAV.map((t) => [t.code, t.short]));
    tabsEl.innerHTML = tabs.map(([k, n], i) => '<button type="button" class="chip' + (i === 0 ? ' is-on' : '') + '" data-tab="' + k + '">' + esc(n) + '</button>').join('');
    const showTab = (k) => {
      const list = k === 'all' ? newAll : sortProducts(data.products.filter((p) => p.top === k), 'new').slice(0, 8);
      renderCards(newEl, list, { badge: 'NEW' });
      tabsEl.querySelectorAll('.chip').forEach((c) => c.classList.toggle('is-on', c.dataset.tab === k));
    };
    tabsEl.addEventListener('click', (e) => { const b = e.target.closest('[data-tab]'); if (b) showTab(b.dataset.tab); });
    showTab('all');
    /* 고객의 공간에서 */
    const lb = H.lookbook[0], reviews = H.reviews.slice(0, 2);
    document.querySelector('[data-space]').innerHTML =
      (lb ? '<figure class="space__big">' + img(lb.img, lb.caption) + '<figcaption><a href="view.html?no=' + esc(lb.goodsNo) + '">' + esc(lb.caption) + ' →</a></figcaption></figure>' : '')
      + reviews.map((r) => '<div class="review"><div class="review__img">' + (r.img ? img(r.img, '후기 사진') : '') + '</div>'
        + '<div class="review__stars">' + stars(r.stars) + '</div><p class="review__text">' + esc(r.text) + '</p>'
        + '<div class="review__meta">' + esc(r.name) + ' · ' + esc(r.date) + '</div>'
        + '<a class="review__goods" href="view.html?no=' + esc(r.goodsNo) + '">' + esc(r.goodsName) + '</a></div>').join('')
      + (reviews.length ? '' : '<div class="notice">후기를 불러오지 못했습니다.</div>');
  };
```

- [x] **Step 3: 브라우저 확인**

Run:
```bash
"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless=new --disable-gpu --hide-scrollbars --user-data-dir="$LOCALAPPDATA/Temp/edge-shot" --window-size=1440,3600 --virtual-time-budget=8000 --screenshot=docs/screenshots/home-desktop.png "http://localhost:8080/index.html" 2>/dev/null; echo done
```
그다음 Read 도구로 `docs/screenshots/home-desktop.png`를 열어 확인한다.
Expected: 원본 로고가 있는 헤더, 히어로(문장형 헤드라인 + 흰 알약 버튼), 공간별 5칸, 특가 가로 행, 베스트 8개, 크림 브랜드 띠, 탭 + 신제품 8개, 룩북 + 후기 2개, 다크 푸터. "불러오지 못했습니다" 문구가 없어야 한다.

- [x] **Step 4: 커밋**

```bash
git add index.html assets/app.js docs/screenshots/home-desktop.png && git commit -m "feat(home): 메인 페이지 9개 블록

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 7: 상품 목록 (list.html + pages.list)

**Files:**
- Create: `list.html`
- Modify: `assets/app.js` (`/* ==== END PAGES ==== */` 바로 위에 `pages.list` 추가)

- [x] **Step 1: list.html 작성**

`list.html`:
```html
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>상품 목록 — 라로퍼니처</title>
<link rel="icon" href="assets/logo-header.png">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="assets/style.css">
</head>
<body data-page="list">
<a class="skip" href="#main">본문 바로가기</a>
<header class="hdr" id="site-header"></header>
<main id="main">
  <div class="container">
    <div class="list__head">
      <div class="crumb" data-crumb></div>
      <h1 class="h2" data-title>상품</h1>
      <p class="sub" data-desc></p>
      <div class="chips" data-subcats></div>
    </div>
    <div class="list__body">
      <div class="filters__backdrop" data-filters-backdrop></div>
      <aside class="filters" data-filters aria-label="필터">
        <div class="filters__head">필터 <button type="button" data-filters-close aria-label="닫기">✕</button></div>
        <div data-filter-groups></div>
        <button class="filters__reset" type="button" data-filters-reset>필터 초기화</button>
        <button class="btn btn--primary btn--block filters__apply" type="button" data-filters-close>적용</button>
      </aside>
      <div>
        <div class="toolbar">
          <div class="toolbar__count"><b data-count>0</b>개 상품</div>
          <div style="display:flex;gap:8px;align-items:center">
            <button class="btn btn--secondary btn--sm toolbar__filter-btn" type="button" data-filters-open>필터</button>
            <select class="select" data-sort aria-label="정렬">
              <option value="reco">추천순</option><option value="popular">판매인기순</option>
              <option value="priceAsc">낮은가격순</option><option value="priceDesc">높은가격순</option>
              <option value="review">상품평순</option><option value="new">등록일순</option>
            </select>
          </div>
        </div>
        <div class="chips active-chips" data-active></div>
        <div class="grid grid--3" data-grid data-needs-data></div>
        <div class="list__more"><button class="btn btn--secondary" type="button" data-more>더 보기</button></div>
      </div>
    </div>
  </div>
  <section class="guide">
    <div class="container guide__grid">
      <div><span class="label">Buying Guide</span><h2 class="h2 mt-8" data-guide-title></h2><p class="sub" data-guide-body></p></div>
      <div class="guide__figure" aria-hidden="true"><i style="width:22%"></i><i style="width:34%"></i><i style="width:44%"></i></div>
    </div>
  </section>
</main>
<footer class="ftr" id="site-footer"></footer>
<script src="assets/app.js"></script>
</body>
</html>
```

- [x] **Step 2: pages.list 추가**

`assets/app.js`의 `/* ==== END PAGES ==== */` 바로 위에 추가:
```js
  pages.list = function (data) {
    const cate = param('cate') || 'all', q = param('q') || '', sale = param('sale') === '1';
    const top = cate === 'all' ? null : topOfCate(cate);
    const topDef = top ? data.categories.find((c) => c.code === top) : null;
    const isChild = !!top && cate !== top;
    const title = q ? '"' + q + '" 검색 결과' : !topDef ? (sale ? '이번 주 특가' : '전체 상품') : isChild ? childName(cate) : topDef.name;
    document.title = title + ' — 라로퍼니처';
    document.querySelector('[data-title]').textContent = title;
    document.querySelector('[data-desc]').textContent = topDef ? topDef.desc : (q ? '상품명에 검색어가 모두 포함된 상품입니다.' : '라로퍼니처의 모든 가구를 한 번에.');
    document.querySelector('[data-crumb]').innerHTML = '<a href="index.html">홈</a> › '
      + (topDef ? '<a href="list.html?cate=' + top + '">' + esc(topDef.name) + '</a>' : '전체 상품') + (isChild ? ' › ' + esc(childName(cate)) : '');
    /* 기본 목록 */
    let base = data.products.filter((p) => !top || p.top === top);
    if (q) base = searchProducts(base, q);
    if (sale) base = base.filter((p) => discountRate(p.price, p.listPrice) > 0);
    const subEl = document.querySelector('[data-subcats]');
    if (topDef) {
      subEl.innerHTML = '<a class="chip' + (!isChild ? ' is-on' : '') + '" href="list.html?cate=' + top + '">전체 ' + base.length + '</a>'
        + topDef.children.map((c) => '<a class="chip' + (cate === c.code ? ' is-on' : '') + '" href="list.html?cate=' + c.code + '">' + esc(c.name) + '</a>').join('');
    } else { subEl.remove(); }
    if (isChild) base = base.filter((p) => p.cate === cate);
    /* 필터 */
    const defs = (FILTER_DEFS[top || 'all'] || []).filter(([k]) => !(isChild && k === 'cate'));
    const active = {};
    const groupsEl = document.querySelector('[data-filter-groups]');
    groupsEl.innerHTML = defs.map(([k, label]) => {
      const opts = filterOptions(base, k);
      if (opts.length < 2) return '';
      return '<div class="filters__group"><h5>' + esc(label) + '</h5>' + opts.map((v) =>
        '<label><input type="checkbox" data-key="' + k + '" value="' + esc(v) + '"> ' + esc(labelFor(k, v)) + '</label>').join('') + '</div>';
    }).join('');
    const sortEl = document.querySelector('[data-sort]');
    sortEl.value = param('sort') || 'reco';
    let shown = 12;
    const grid = document.querySelector('[data-grid]'), countEl = document.querySelector('[data-count]');
    const moreBtn = document.querySelector('[data-more]'), activeEl = document.querySelector('[data-active]');
    function render() {
      const list = sortProducts(applyFilters(base, active), sortEl.value);
      countEl.textContent = list.length;
      renderCards(grid, list.slice(0, shown));
      moreBtn.parentNode.style.display = list.length > shown ? '' : 'none';
      moreBtn.textContent = Math.min(12, list.length - shown) + '개 더 보기';
      activeEl.innerHTML = Object.entries(active).flatMap(([k, set]) => Array.from(set).map((v) =>
        '<button type="button" class="chip is-on chip--x" data-key="' + k + '" data-value="' + esc(v) + '">' + esc(labelFor(k, v)) + '</button>')).join('');
    }
    groupsEl.addEventListener('change', (e) => {
      const i = e.target; if (!i.matches('input')) return;
      active[i.dataset.key] = active[i.dataset.key] || new Set();
      if (i.checked) active[i.dataset.key].add(i.value); else active[i.dataset.key].delete(i.value);
      shown = 12; render();
    });
    activeEl.addEventListener('click', (e) => {
      const b = e.target.closest('[data-key]'); if (!b) return;
      active[b.dataset.key].delete(b.dataset.value);
      groupsEl.querySelectorAll('input[data-key="' + b.dataset.key + '"]').forEach((cb) => { if (cb.value === b.dataset.value) cb.checked = false; });
      render();
    });
    document.querySelector('[data-filters-reset]').addEventListener('click', () => {
      Object.keys(active).forEach((k) => active[k].clear());
      groupsEl.querySelectorAll('input').forEach((i) => { i.checked = false; });
      render();
    });
    sortEl.addEventListener('change', () => { shown = 12; render(); });
    moreBtn.addEventListener('click', () => { shown += 12; render(); });
    /* 모바일 필터 시트 */
    const sheet = document.querySelector('[data-filters]'), backdrop = document.querySelector('[data-filters-backdrop]');
    const openSheet = (o) => { sheet.classList.toggle('is-open', o); backdrop.classList.toggle('is-open', o); };
    document.querySelectorAll('[data-filters-open]').forEach((b) => b.addEventListener('click', () => openSheet(true)));
    document.querySelectorAll('[data-filters-close]').forEach((b) => b.addEventListener('click', () => openSheet(false)));
    backdrop.addEventListener('click', () => openSheet(false));
    /* 구매 가이드 */
    const g = topDef ? topDef.guide : { title: '어떤 가구를 찾으세요?',
      body: '식탁은 인원과 공간 폭, 소파는 거실 폭, 침대는 매트리스 규격부터 확인하면 고르기 쉽습니다. 카테고리를 고르면 맞춤 가이드가 나옵니다.' };
    document.querySelector('[data-guide-title]').textContent = g.title;
    document.querySelector('[data-guide-body]').textContent = g.body;
    render();
  };
```

- [x] **Step 3: 브라우저 확인**

Run:
```bash
E="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"; C="--headless=new --disable-gpu --hide-scrollbars --user-data-dir=$LOCALAPPDATA/Temp/edge-shot --virtual-time-budget=8000"
"$E" $C --window-size=1440,3000 --screenshot=docs/screenshots/list-desktop.png "http://localhost:8080/list.html?cate=012" 2>/dev/null
"$E" $C --window-size=1440,2000 --screenshot=docs/screenshots/list-all-sale.png "http://localhost:8080/list.html?cate=all&sale=1" 2>/dev/null
"$E" $C --dump-dom "http://localhost:8080/list.html?cate=012" 2>/dev/null | grep -o 'data-count>[0-9]*' ; echo done
```
Read 도구로 두 스크린샷 확인. Expected: 제목 "세라믹 · 대리석 식탁" + 설명 + 소분류 칩 5개(전체 N 포함), 왼쪽 필터에 사이즈·형태·상판·구성·가격 그룹, 3열 카드 12개, "더 보기", 크림 가이드 띠. `data-count`가 0보다 큼.

- [x] **Step 4: 커밋**

```bash
git add list.html assets/app.js docs/screenshots/list-desktop.png docs/screenshots/list-all-sale.png && git commit -m "feat(list): 상품 목록 — 소분류 칩, 자동 필터, 정렬, 더 보기, 구매 가이드

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 8: 상품 상세 (view.html + pages.view)

**Files:**
- Create: `view.html`
- Modify: `assets/app.js` (`/* ==== END PAGES ==== */` 바로 위에 `pages.view` 추가)

- [ ] **Step 1: view.html 작성**

`view.html`:
```html
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>상품 상세 — 라로퍼니처</title>
<link rel="icon" href="assets/logo-header.png">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="assets/style.css">
</head>
<body data-page="view">
<a class="skip" href="#main">본문 바로가기</a>
<header class="hdr" id="site-header"></header>
<main id="main" class="container">
  <div class="pdp" data-pdp data-needs-data></div>

  <nav class="ptabs" data-ptabs aria-label="상품 정보 탭">
    <ul>
      <li><a href="#sec-detail" class="is-active">상세정보</a></li>
      <li><a href="#sec-spec">사양 · 치수</a></li>
      <li><a href="#sec-ship">배송 · 교환 · 반품</a></li>
      <li><a href="#sec-review">리뷰 <span data-rc></span></a></li>
      <li><a href="#sec-qna">Q&amp;A <span data-qc></span></a></li>
    </ul>
  </nav>

  <section class="sec sec--tight" id="sec-detail">
    <div class="feats" data-feats></div>
    <div class="detail-imgs mt-40" data-detail-imgs></div>
    <div class="detail-imgs__btn" data-detail-btn></div>
  </section>

  <section class="sec" id="sec-spec">
    <h2 class="h2">사양 · 치수</h2>
    <div class="spec mt-24" data-spec></div>
  </section>

  <section class="sec" id="sec-ship">
    <h2 class="h2">배송 · 교환 · 반품</h2>
    <div class="shipinfo mt-16">
      <h4>배송 · 설치</h4>
      <p data-ship-text></p>
      <p>기사 방문 설치 상품은 배송비를 수령 시 결제합니다. 설치 전 현관 · 엘리베이터 · 통로 폭을 확인해 주세요. 도서산간 지역은 추가 배송비가 있을 수 있습니다.</p>
      <h4>교환 · 반품</h4>
      <p>수령 후 7일 이내 교환 · 반품을 신청할 수 있으며, 설치가 끝난 가구와 주문 제작 옵션 상품은 제외됩니다. 세부 기준은 이용안내 정책을 그대로 옮깁니다. (확인 필요)</p>
      <h4>A/S</h4>
      <p data-as-text></p>
    </div>
  </section>

  <section class="sec" id="sec-review">
    <h2 class="h2">리뷰</h2>
    <div class="rsum mt-24" data-rsum></div>
  </section>

  <section class="sec" id="sec-qna">
    <h2 class="h2">Q&amp;A</h2>
    <p class="sub">상품 문의는 로그인 후 남길 수 있습니다. 급한 문의는 카카오톡 상담 또는 고객센터로 연락해 주세요.</p>
    <div class="mt-16"><a class="btn btn--secondary" href="#">문의 남기기</a></div>
  </section>

  <section class="sec" id="sec-related">
    <div class="sec__head"><div><h2 class="h2" data-series-title>함께 보기</h2></div></div>
    <div class="grid grid--4" data-series></div>
    <div class="sec__head mt-40"><div><h2 class="h2">비슷한 가격대의 다른 선택</h2></div></div>
    <div class="grid grid--4" data-similar></div>
  </section>
</main>
<div class="buybar" data-buybar></div>
<footer class="ftr" id="site-footer"></footer>
<script src="assets/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: pages.view 추가**

`assets/app.js`의 `/* ==== END PAGES ==== */` 바로 위에 추가:
```js
  pages.view = function (data) {
    const p = product(param('no')) || product(data.home.best[0]);
    if (!p) return;
    const d = p.detail || { gallery: [], options: [], detailImages: [], spec: {}, shipping: '', reviewCount: p.reviewCount, qnaCount: 0 };
    const gallery = d.gallery.length ? d.gallery : [p.image];
    const rate = discountRate(p.price, p.listPrice);
    const reviewCount = d.reviewCount || p.reviewCount || 0;
    document.title = p.name + ' — 라로퍼니처';
    const el = document.querySelector('[data-pdp]');
    const optionPrice = (o, i) => {
      if (o.delta != null) return (o.delta >= 0 ? '+' : '−') + fmt(Math.abs(o.delta));
      return i === 0 ? fmt(p.price) : '<span class="muted">옵션 선택 시 표시</span>';
    };
    el.innerHTML = '<div class="crumb"><a href="index.html">홈</a> › <a href="list.html?cate=' + p.top + '">' + esc(topName(p.top))
      + '</a> › <a href="list.html?cate=' + p.cate + '">' + esc(childName(p.cate)) + '</a></div>'
      + '<div class="gallery"><div class="gallery__main">' + img(gallery[0], p.name)
      + (gallery.length > 1 ? '<button class="gallery__nav gallery__nav--prev" type="button" aria-label="이전 사진">‹</button><button class="gallery__nav gallery__nav--next" type="button" aria-label="다음 사진">›</button>' : '')
      + '</div>' + (gallery.length > 1 ? '<div class="gallery__thumbs">' + gallery.slice(0, 6).map((g, i) =>
        '<button type="button"' + (i === 0 ? ' class="is-active"' : '') + ' data-i="' + i + '" aria-label="' + (i + 1) + '번 사진">' + img(g, p.name + ' ' + (i + 1)) + '</button>').join('') + '</div>' : '') + '</div>'
      + '<div class="buy"><span class="label">' + esc(childName(p.cate)) + (p.series ? ' · ' + esc(p.series) : '') + '</span>'
      + '<h1 class="buy__name">' + esc(p.name) + '</h1>'
      + '<div class="buy__rating">리뷰 ' + reviewCount + ' · Q&amp;A ' + (d.qnaCount || 0) + '</div>'
      + '<div class="buy__price">' + (rate ? '<span class="rate">' + rate + '%</span>' : '') + fmt(p.price) + (p.listPrice ? '<del>' + fmt(p.listPrice) + '</del>' : '') + '</div>'
      + '<div class="buy__ship">' + (d.shipping ? '배송비 ' + esc(d.shipping) : '배송비는 옵션 선택 후 표시됩니다') + ' · 기사 설치</div>'
      + (d.options.length ? '<span class="label">구성 선택</span><div data-options role="radiogroup">' + d.options.map((o, i) =>
        '<div class="opt' + (i === 0 ? ' is-on' : '') + '" data-i="' + i + '" role="radio" aria-checked="' + (i === 0) + '" tabindex="0"><span>' + esc(o.name) + '</span><b>' + optionPrice(o, i) + '</b></div>').join('') + '</div>' : '')
      + (p.colors && p.colors.length ? '<span class="label">색상</span><div class="swatches">' + p.colors.map((c, i) =>
        '<button type="button" class="swatch' + (i === 0 ? ' is-on' : '') + '" style="background:' + esc(c.hex) + '" title="' + esc(c.name) + '" aria-label="' + esc(c.name) + '"></button>').join('') + '</div>' : '')
      + '<div class="buy__qty"><span>수량</span><div class="qty"><button type="button" data-qty="-1" aria-label="수량 줄이기">−</button><span data-qty-val>1</span><button type="button" data-qty="1" aria-label="수량 늘리기">+</button></div></div>'
      + '<div class="buy__total"><span>총 상품 금액</span><b data-total>' + fmt(p.price) + '</b></div>'
      + '<div class="buy__actions"><a class="btn btn--secondary" href="#">장바구니</a><a class="btn btn--primary" href="#">바로 구매</a>'
      + '<button class="btn btn--secondary btn--icon" type="button" aria-label="찜하기" onclick="this.classList.toggle(\'is-on\');this.textContent=this.classList.contains(\'is-on\')?\'♥\':\'♡\'">♡</button></div>'
      + '<div class="buy__notes">✓ 일산 쇼룸에서 실물을 확인할 수 있습니다 <a href="brand.html#showroom">쇼룸 안내</a><br>✓ 카카오톡 상담 · ' + esc(data.company.tel)
      + '<br>✓ 수령 후 7일 이내 교환 · 반품 (설치 완료 상품 제외)</div></div>';
    /* 갤러리 */
    let gi = 0;
    const main = el.querySelector('.gallery__main img'), thumbs = el.querySelectorAll('.gallery__thumbs button');
    const show = (i) => { gi = (i + gallery.length) % gallery.length; if (main) main.src = gallery[gi]; thumbs.forEach((t) => t.classList.toggle('is-active', Number(t.dataset.i) === gi)); };
    thumbs.forEach((t) => t.addEventListener('click', () => show(Number(t.dataset.i))));
    const prev = el.querySelector('.gallery__nav--prev'), next = el.querySelector('.gallery__nav--next');
    if (prev) prev.addEventListener('click', () => show(gi - 1));
    if (next) next.addEventListener('click', () => show(gi + 1));
    /* 옵션 · 수량 · 총액 */
    let oi = 0, qty = 1;
    const buybar = document.querySelector('[data-buybar]');
    document.body.classList.add('has-buybar');
    buybar.innerHTML = '<div><div class="muted" style="font-size:12px">총 상품 금액</div><b>' + fmt(p.price) + '</b></div><a class="btn btn--primary" href="#">구매하기</a>';
    const total = () => {
      const delta = d.options[oi] ? d.options[oi].delta : 0;
      const t = fmt(optionTotal(p.price || 0, delta, qty));
      el.querySelector('[data-total]').textContent = t;
      buybar.querySelector('b').textContent = t;
    };
    const optsEl = el.querySelector('[data-options]');
    if (optsEl) optsEl.addEventListener('click', (e) => {
      const o = e.target.closest('.opt'); if (!o) return;
      oi = Number(o.dataset.i);
      optsEl.querySelectorAll('.opt').forEach((x) => { x.classList.toggle('is-on', x === o); x.setAttribute('aria-checked', String(x === o)); });
      total();
    });
    el.querySelectorAll('[data-qty]').forEach((b) => b.addEventListener('click', () => {
      qty = Math.max(1, qty + Number(b.dataset.qty)); el.querySelector('[data-qty-val]').textContent = qty; total();
    }));
    const sw = el.querySelector('.swatches');
    if (sw) sw.addEventListener('click', (e) => { const s = e.target.closest('.swatch'); if (!s) return; sw.querySelectorAll('.swatch').forEach((x) => x.classList.toggle('is-on', x === s)); });
    /* 탭 카운트 + 스크롤 스파이 */
    document.querySelector('[data-rc]').textContent = reviewCount;
    document.querySelector('[data-qc]').textContent = d.qnaCount || 0;
    const tabLinks = Array.from(document.querySelectorAll('[data-ptabs] a'));
    const secs = tabLinks.map((a) => document.querySelector(a.getAttribute('href')));
    window.addEventListener('scroll', () => {
      const y = window.scrollY + 180; let idx = 0;
      secs.forEach((s, i) => { if (s && s.offsetTop <= y) idx = i; });
      tabLinks.forEach((a, i) => a.classList.toggle('is-active', i === idx));
    }, { passive: true });
    /* 핵심 특징 (상세 없는 상품은 같은 대분류의 기본 문구 사용) */
    const feats = p.features || ((data.products.find((x) => x.top === p.top && x.features) || {}).features) || [];
    document.querySelector('[data-feats]').innerHTML = feats.map((f, i) => '<div class="feat"><div class="feat__img">'
      + img(gallery[Math.min(i + 1, gallery.length - 1)], f.title) + '</div><h4>' + esc(f.title) + '</h4><p>' + esc(f.body) + '</p></div>').join('');
    /* 상세 이미지 */
    const di = document.querySelector('[data-detail-imgs]'), dbtn = document.querySelector('[data-detail-btn]');
    if (d.detailImages.length) {
      di.innerHTML = d.detailImages.map((s) => img(s, p.name + ' 상세')).join('') + '<div class="detail-imgs__fade"></div>';
      dbtn.innerHTML = '<button class="btn btn--secondary" type="button">상세 이미지 펼쳐 보기</button>';
      dbtn.querySelector('button').addEventListener('click', function () { di.classList.toggle('is-open'); this.textContent = di.classList.contains('is-open') ? '접기' : '상세 이미지 펼쳐 보기'; });
    } else {
      di.innerHTML = '<div class="notice">이 상품의 상세 이미지는 실제 사이트 상품 페이지에서 확인할 수 있습니다. (프로토타입은 대표 상품 12개만 상세를 수집)</div>';
      di.classList.add('is-open');
    }
    /* 사양 · 치수: 값이 있는 항목만 */
    const rows = {};
    if (p.size) rows['사이즈'] = p.size + (p.seats ? ' · ' + p.seats + '인' : '');
    if (p.material) rows['소재'] = p.material;
    if (p.shape) rows['형태'] = p.shape;
    if (p.kind) rows['구성'] = p.kind;
    Object.assign(rows, d.spec);
    document.querySelector('[data-spec]').innerHTML = '<div class="spec__figure">치수 도면 (' + (p.size ? 'W' + p.size + ' — 확인 필요' : '상세 이미지 참조') + ')</div>'
      + '<table><tbody>' + Object.entries(rows).map(([k, v]) => '<tr><th>' + esc(k) + '</th><td>' + esc(v) + '</td></tr>').join('') + '</tbody></table>';
    document.querySelector('[data-ship-text]').textContent = d.shipping ? '배송비 ' + d.shipping : '배송비는 옵션 선택 후 표시됩니다.';
    document.querySelector('[data-as-text]').textContent = d.spec['AS 책임자와 전화번호'] || ('라로퍼니처 고객센터 ' + data.company.tel);
    /* 리뷰 요약: 별점 집계는 사이트에 없으므로 개수만 */
    const mine = data.home.reviews.filter((r) => r.goodsNo === p.no);
    document.querySelector('[data-rsum]').innerHTML = '<div><div class="rsum__score">' + reviewCount + '<small style="font-size:16px"> 개</small></div>'
      + '<div class="rsum__stars">' + (reviewCount ? stars(5) : '') + '</div><div class="muted" style="font-size:13px;margin-top:6px">별점 평균과 분포는 실제 사이트 리뷰 게시판 연동 시 표시됩니다. (확인 필요)</div></div>'
      + '<div class="rsum__photos">' + mine.map((r) => '<div class="review"><div class="review__img">' + img(r.img, '후기 사진') + '</div><p class="review__text">' + esc(r.text) + '</p></div>').join('')
      + Array.from({ length: Math.max(0, 4 - mine.length) }).map(() => '<div class="ph">사진 후기</div>').join('') + '</div>';
    /* 함께 보기 */
    const series = data.products.filter((x) => x.no !== p.no && x.series && x.series === p.series).slice(0, 4);
    document.querySelector('[data-series-title]').textContent = series.length ? p.series + ' 시리즈 함께 보기' : '같은 카테고리 인기 상품';
    renderCards(document.querySelector('[data-series]'), series.length ? series : sortProducts(data.products.filter((x) => x.cate === p.cate && x.no !== p.no), 'popular').slice(0, 4));
    const similar = data.products.filter((x) => x.no !== p.no && x.top === p.top && x.price && !series.includes(x))
      .sort((a, b) => Math.abs(a.price - p.price) - Math.abs(b.price - p.price)).slice(0, 4);
    renderCards(document.querySelector('[data-similar]'), similar);
  };
```

- [ ] **Step 3: 브라우저 확인**

Run:
```bash
E="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"; C="--headless=new --disable-gpu --hide-scrollbars --user-data-dir=$LOCALAPPDATA/Temp/edge-shot --virtual-time-budget=8000"
"$E" $C --window-size=1440,4200 --screenshot=docs/screenshots/view-desktop.png "http://localhost:8080/view.html?no=1000000491" 2>/dev/null
"$E" $C --window-size=1440,2400 --screenshot=docs/screenshots/view-nodetail.png "http://localhost:8080/view.html?no=1000000003" 2>/dev/null; echo done
```
Read 도구로 확인. Expected(491): 갤러리 + 썸네일, 라벨 "세라믹 식탁 세트 · 허그", 가격 `20% 398,000원 500,000원`, 구성 3개 카드(첫 번째 선택), 색상 스와치 2개, 수량, 총액, 버튼 3개, 탭 바, 특징 3개, 상세 이미지(접힘), 사양 표(값 있는 항목만), 리뷰 개수, 허그 시리즈 4개, 비슷한 가격대 4개. Expected(003, 상세 없음): 옵션 블록 없음, "상세 이미지는 실제 사이트…" 안내, 나머지 정상.

- [ ] **Step 4: 커밋**

```bash
git add view.html assets/app.js docs/screenshots/view-desktop.png docs/screenshots/view-nodetail.png && git commit -m "feat(view): 상품 상세 — 갤러리, 스티키 구매 패널, 구성 옵션, 탭, 사양, 함께 보기

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 9: 브랜드 페이지 (brand.html + pages.brand)

**Files:**
- Create: `brand.html`
- Modify: `assets/app.js` (`/* ==== END PAGES ==== */` 바로 위에 `pages.brand` 추가)

- [ ] **Step 1: brand.html 작성**

`brand.html`:
```html
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>브랜드 스토리 · 일산 쇼룸 — 라로퍼니처</title>
<link rel="icon" href="assets/logo-header.png">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="assets/style.css">
</head>
<body data-page="brand">
<a class="skip" href="#main">본문 바로가기</a>
<header class="hdr" id="site-header"></header>
<main id="main">
  <section class="bhero">
    <img src="assets/company-story.jpg" alt="원목을 다듬는 장인의 손">
    <div class="bhero__text">
      <span class="label" data-meaning>RARO MEANS : 색다른, 희소성 있는</span>
      <h1 class="h1" data-slogan>현대적 감각으로 자연을 다듬다.</h1>
    </div>
  </section>

  <section class="sec container"><p class="statement" data-statement></p></section>

  <section class="sec container"><div class="numbers" data-numbers></div></section>

  <section class="sec container">
    <div class="sec__head"><div><span class="label">Materials</span><h2 class="h2 mt-8">소재 이야기</h2><p class="sub">라로퍼니처가 가장 많이 만드는 세 가지 소재</p></div></div>
    <div class="materials" data-materials data-needs-data></div>
  </section>

  <section class="showroom" id="showroom">
    <div class="container showroom__grid">
      <div class="map" data-map></div>
      <div>
        <span class="label">Showroom</span>
        <h2 class="h2 mt-8">일산 쇼룸에서 직접 앉아 보세요.</h2>
        <div class="showroom__info" data-showroom></div>
        <div class="band__actions">
          <a class="btn btn--primary" data-map-link href="#" target="_blank" rel="noopener">길찾기</a>
          <a class="btn btn--secondary" href="#">카카오톡 방문 예약</a>
        </div>
      </div>
    </div>
  </section>
</main>
<footer class="ftr" id="site-footer"></footer>
<script src="assets/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: pages.brand 추가**

`assets/app.js`의 `/* ==== END PAGES ==== */` 바로 위에 추가:
```js
  pages.brand = function (data) {
    const c = data.company;
    document.querySelector('[data-meaning]').textContent = c.meaning;
    document.querySelector('[data-slogan]').textContent = c.slogan;
    document.querySelector('[data-statement]').textContent = c.story.join(' ');
    document.querySelector('[data-numbers]').innerHTML = c.numbers.map((n) =>
      '<div><b>' + esc(n.value) + '<small>' + esc(n.unit) + '</small></b><p>' + esc(n.label) + '</p></div>').join('');
    const mats = [
      ['012', '포세린 통 세라믹', '열과 흠집에 강한 상판. 뜨거운 냄비를 바로 올려도 됩니다.'],
      ['013', '고무나무 · 참죽나무 원목', '자연 그대로의 결과 색. 오일 관리로 오래 씁니다.'],
      ['003', '천연 가죽 · 비건 가죽 소파', '전동 리클라이너와 스윙 헤드레스트까지.'],
    ];
    document.querySelector('[data-materials]').innerHTML = mats.map(([code, t, b]) => {
      const rep = data.products.find((p) => p.top === code && p.detail) || data.products.find((p) => p.top === code);
      const src = rep ? ((rep.detail && rep.detail.gallery[1]) || rep.image) : '';
      return '<a class="feat" href="list.html?cate=' + code + '"><div class="feat__img">' + img(src, t) + '</div><h4>' + esc(t) + '</h4><p>' + esc(b) + ' <u>' + esc(topName(code)) + ' 보기 →</u></p></a>';
    }).join('');
    document.querySelector('[data-showroom]').innerHTML = esc(c.showroom) + '<br>운영시간 · 주차: ' + esc(c.showroomHours) + '<br>' + esc(c.tel);
    document.querySelector('[data-map]').innerHTML = '<strong>' + esc(c.showroom) + '</strong><span>지도는 카카오맵 연동 후 표시됩니다 (이식 시 지도 API 키 필요)</span>';
    document.querySelector('[data-map-link]').href = 'https://map.kakao.com/link/search/' + encodeURIComponent(c.showroom);
  };
```

- [ ] **Step 3: 브라우저 확인**

Run:
```bash
"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless=new --disable-gpu --hide-scrollbars --user-data-dir="$LOCALAPPDATA/Temp/edge-shot" --window-size=1440,2600 --virtual-time-budget=8000 --screenshot=docs/screenshots/brand-desktop.png "http://localhost:8080/brand.html" 2>/dev/null; echo done
```
Read 도구로 확인. Expected: 흑백 공방 사진 히어로 + 슬로건, 스테이트먼트 3문장, 숫자 3개(30년/6개/5종), 소재 카드 3개, 크림 쇼룸 섹션(주소·전화·"확인 필요"·길찾기 버튼).

- [ ] **Step 4: 커밋**

```bash
git add brand.html assets/app.js docs/screenshots/brand-desktop.png && git commit -m "feat(brand): 브랜드 스토리 + 일산 쇼룸 페이지

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 10: 3개 폭 스크린샷 검증과 반응형 수정

**Files:**
- Create: `tools/screenshot.sh`
- Modify: `assets/style.css`, `assets/app.js` (스크린샷에서 발견한 문제만)
- Create: `docs/screenshots/*.png` (12장)

- [ ] **Step 1: 스크린샷 스크립트 작성**

`tools/screenshot.sh`:
```bash
#!/usr/bin/env bash
# 4페이지 × 3폭 스크린샷 → docs/screenshots/
# 사전 조건: 프로젝트 루트에서 `python -m http.server 8080` 실행 중
set -u
EDGE="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
BASE="${BASE:-http://localhost:8080}"
OUT="docs/screenshots"
PROFILE="${LOCALAPPDATA:-/tmp}/Temp/edge-shot"
mkdir -p "$OUT"
PAGES=("index.html|home" "list.html?cate=012|list" "view.html?no=1000000491|view" "brand.html|brand")
WIDTHS=("1440|desktop|3600" "1024|tablet|3600" "390|mobile|4200")
for p in "${PAGES[@]}"; do
  url="${p%%|*}"; name="${p##*|}"
  for w in "${WIDTHS[@]}"; do
    IFS='|' read -r width label height <<< "$w"
    "$EDGE" --headless=new --disable-gpu --hide-scrollbars --user-data-dir="$PROFILE" \
      --window-size="${width},${height}" --virtual-time-budget=8000 \
      --screenshot="$OUT/${name}-${label}.png" "$BASE/$url" > /dev/null 2>&1
    echo "saved $OUT/${name}-${label}.png"
  done
done
```

- [ ] **Step 2: 실행**

Run: `bash tools/screenshot.sh`
Expected: `saved …` 12줄. `ls docs/screenshots/*.png | wc -l` → 12 이상.

- [ ] **Step 3: 데이터 로드 실패 문구가 없는지 확인**

Run:
```bash
E="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"; for u in "index.html" "list.html?cate=012" "view.html?no=1000000491" "brand.html"; do n=$("$E" --headless=new --disable-gpu --user-data-dir="$LOCALAPPDATA/Temp/edge-shot" --virtual-time-budget=8000 --dump-dom "http://localhost:8080/$u" 2>/dev/null | grep -c "불러오지 못했습니다"); echo "$u -> $n"; done
```
Expected: 네 줄 모두 `-> 0`.

- [ ] **Step 4: 12장을 Read 도구로 하나씩 열어 점검**

점검 항목(스펙 3장·4장 기준):
- 데스크톱(1440): 헤더 2행(로고·검색·유틸 / 카테고리 메뉴), 상품 4열, 상세 7:5 2단, 푸터 5열.
- 태블릿(1024): 상품 3열, 상세 1:1 2단, 푸터 2열, 유틸 아이콘만.
- 모바일(390): 햄버거 + 로고 + 아이콘, 검색창·카테고리 행 숨김, 상품 2열, 특가 가로 스크롤, 브랜드 띠 1열(사진 먼저), 상세 1단 + 하단 구매 바, 목록의 "필터" 버튼 보임, 푸터 1열, 우하단 "상담" 버튼.
- 공통: 원본 로고 선명, 푸터 로고 흰색, 텍스트 잘림·겹침 없음, 이미지 깨짐(회색 타일 + "이미지 준비 중") 없음, 액센트 색은 할인율·특가 뱃지·구독 버튼에만.

발견한 문제는 `assets/style.css`의 반응형 섹션(14) 또는 해당 컴포넌트 규칙을 고치고 `bash tools/screenshot.sh`를 다시 실행해 확인한다. 흔한 문제와 처방:
- 히어로 글자가 사진과 겹쳐 안 읽힘 → `.hero__shade` 첫 정지점 `rgba(0,0,0,.5)`를 `.6`으로.
- 모바일에서 `.scroll-row` 카드가 너무 좁음 → `grid-auto-columns: 42vw`를 `56vw`로.
- 상세 페이지 스티키 패널이 헤더에 가려짐 → `--header-h` 값을 실제 헤더 높이(개발자 도구 대신 스크린샷의 헤더 높이 픽셀)로 맞춤.
- 긴 상품명이 카드 높이를 흔듦 → `.card__name`에 `min-height: 2.9em` 추가.

- [ ] **Step 5: JS 테스트 재확인**

Run:
```bash
"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless=new --disable-gpu --user-data-dir="$LOCALAPPDATA/Temp/edge-shot" --dump-dom "http://localhost:8080/tests/app.test.html" 2>/dev/null | grep -o 'id="summary">[^<]*'; PYTHONIOENCODING=utf-8 python -m unittest tests.test_build 2>&1 | tail -1
```
Expected: `OK 33 passed, 0 failed` 와 `OK`.

- [ ] **Step 6: 커밋**

```bash
git add tools/screenshot.sh docs/screenshots assets/style.css assets/app.js && git commit -m "test: 4페이지 × 3폭 스크린샷과 반응형 보정

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 11: 고도몰 이식 가이드와 마무리

**Files:**
- Create: `docs/godomall-porting.md`
- Modify: `README.md` (스크린샷 링크 추가)

- [ ] **Step 1: 이식 가이드 작성**

`docs/godomall-porting.md`:
````markdown
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
| 푸터 | `layout/footer.html` | `RARO.footerHTML()` 마크업. 사업자 정보는 고도몰 기본 정보 변수(`{{gGlobal.info}}`)로 교체. |
| 메인 2 히어로 | `main/index.html` | 메인 배너 위젯(관리자 > 디자인 > 배너)으로 슬라이드 2장 등록. 마크업은 `.hero__slide` 유지. |
| 메인 3 공간별 | `main/index.html` | 정적 HTML. 카테고리 코드 링크 그대로. |
| 메인 4 특가 / 5 베스트 / 7 신제품 | `main/index.html` | 메인 상품 진열 위젯 3개(타임세일·베스트·신상품). 반복부 `<li>` 안을 `RARO.cardHTML()` 마크업으로 교체하고 이미지·이름·가격을 위젯 변수(`{{goods.goodsNm}}`, `{{goods.goodsPrice}}`, `{{goods.fixedPrice}}`)로. 할인율은 `raro.js`의 `discountRate`로 계산. |
| 메인 6 브랜드 띠 | `main/index.html` | 정적 HTML. |
| 메인 8 고객의 공간 | `main/index.html` | 리뷰 게시판 위젯(`_board_article.html`) 반복부를 `.review` 마크업으로 교체. 룩북은 룩북 게시판 최신 1건. |
| 목록 1 카테고리 헤더 | `goods/goods_list.html` | 카테고리명 `{{cateNm}}`. 설명·가이드 문구는 관리자 카테고리 설명란에 넣고 변수로 출력. |
| 목록 2 필터·정렬·그리드 | `goods/goods_list.html` | 정렬은 고도몰 `sort` 파라미터 링크로 교체(추천 `sort=g.sortNo desc`, 인기 `g.orderCnt desc`, 가격 `g.goodsPrice asc/desc`, 상품평 `g.reviewCnt desc`, 최신 `g.regDt desc`). 필터는 1차 이식에서는 소분류 칩만 서버 링크로 두고, 사이즈·소재 필터는 클라이언트 필터(`raro.js` `applyFilters`)로 현재 페이지 상품에만 적용. 완전한 서버 필터는 2단계. |
| 목록 3 가이드 띠 | `goods/goods_list.html` | 정적 HTML, 카테고리 코드별 분기. |
| 상세 1 갤러리·구매 패널 | `goods/goods_view.html` | 갤러리는 고도몰 `detailKeyID` 이미지 배열 유지, 썸네일 마크업만 `.gallery__thumbs`. 구매 패널은 **고도몰 옵션 스크립트(`goodsViewController`)와 hidden input을 그대로 두고** 마크업만 교체. 카드형 라디오는 `<select name="optionNo_0">`를 숨기고 클릭 시 `select.value`를 바꾼 뒤 `change` 이벤트를 발생시켜 고도몰 가격 계산을 그대로 쓴다. |
| 상세 2 탭 | `goods/goods_view.html` | 기존 `.item_goods_tab` 마크업을 `.ptabs`로. 앵커 `#detail` `#exchange` `#reviews` `#qna` 유지. |
| 상세 3 특징 / 4 사양 | `goods/goods_view.html` | 특징 3개는 상품 관리자 "상품 요약 설명" 또는 추가 필드에 입력. 사양 표는 상품정보고시 변수 출력에서 "상세페이지 참조" 값을 `raro.js`가 숨긴다. |
| 상세 5 상세 이미지 | `goods/goods_view.html` | 기존 상세 설명 영역(`{{goodsDescription}}`)을 `.detail-imgs`로 감싼다. |
| 상세 6 리뷰·함께 보기 | `goods/goods_view.html` | 리뷰 위젯 + 관련상품 위젯(`RELATED ITEMS`) 반복부를 카드 마크업으로. |
| 브랜드 | `service/company.html` | 정적 HTML. 쇼룸 지도는 카카오맵 JavaScript API 키 발급 후 `.map`에 삽입. `company2.html`(HISTORY)은 메뉴에서 제거, `company3.html`(오시는 길)은 `company.html#showroom`으로 리다이렉트. |

## 2. 제거할 기존 요소
`layout/header.html`의 공지 티커·즐겨찾기·회원가입 포인트, 좌측 퀵메뉴(`quickLogo`·`quickNotice`·배송조회·택배사 링크), `main/index.html`의 HIT PRODUCT·추천상품 배너·Youtube_Movie·INSTAGRAM 섹션, 인트로 팝업, 비밀번호 인증 레이어(주문조회 페이지로 이동).

## 3. 데이터 연결 규칙
- 프로토타입 `data/site.json`의 필드는 고도몰 변수와 이렇게 대응한다: `no`↔`goodsNo`, `name`↔`goodsNm`, `price`↔`goodsPrice`, `listPrice`↔`fixedPrice`, `image`↔`goods.image` 400px, `reviewCount`↔`reviewCnt`, `colors`↔상품 색상 옵션.
- `raro.js`는 `data/site.json`을 fetch하지 않도록 `loadData`를 서버 렌더 값으로 대체한다: 각 페이지에서 `window.RARO_DATA = {...}`를 템플릿이 출력하고 `loadData`는 이 객체를 반환하게 한 줄만 바꾼다.

## 4. 검증
스킨 미리보기 URL로 `tools/screenshot.sh`를 `BASE=<미리보기 URL>`로 실행해 같은 12장을 찍고 프로토타입 스크린샷과 비교한다.
````

- [ ] **Step 2: README에 스크린샷·문서 링크 추가**

`README.md`의 `## 2단계` 앞에 추가:
````markdown
## 결과 확인

- 스크린샷 12장: `docs/screenshots/` (`home|list|view|brand` × `desktop|tablet|mobile`)
- 고도몰 이식 가이드: `docs/godomall-porting.md`
- 설계 문서: `docs/superpowers/specs/2026-09-10-raro-furniture-redesign-design.md`
````

- [ ] **Step 3: 최종 확인**

Run:
```bash
PYTHONIOENCODING=utf-8 python -m unittest tests.test_build 2>&1 | tail -1; git status --short | wc -l; ls docs/screenshots/*.png | wc -l
```
Expected: `OK`, 커밋 안 된 변경 2개(README, porting.md)만, 스크린샷 12개 이상.

- [ ] **Step 4: 커밋과 태그**

```bash
git add README.md docs/godomall-porting.md && git commit -m "docs: 고도몰 이식 가이드와 README 마무리

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" && git tag phase1-core-pages
```

- [ ] **Step 5: 사용자 검토 요청**

사용자에게 다음을 전달한다: 서버 실행 명령(`python -m http.server 8080`), 4개 URL, 스크린샷 폴더, 확인 부탁 항목(로고·색·글꼴 느낌, 메인 섹션 순서, 목록 필터 동작, 상세 구성 옵션, 브랜드 문구). 승인 후 2단계(나머지 페이지) 계획을 새로 작성한다.
