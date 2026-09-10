#!/usr/bin/env python3
"""라로퍼니처(rarofurniture.co.kr) 상품·카테고리 데이터를 수집해 data/site.json을 만든다.

사용법:
    PYTHONIOENCODING=utf-8 python data/build.py            # 캐시 없는 페이지만 요청 후 생성
    PYTHONIOENCODING=utf-8 python data/build.py --offline  # data/raw/ 캐시만 사용 (네트워크 없음)

요청은 브라우저 UA로 1초 간격, 총 40건 안팎(목록 19 + 목록 밖 대표 상품 상세 ~10 + DETAIL_GOODS 상세 + 홈 1).
결과 HTML은 data/raw/에 캐시한다.
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


# ---------------------------------------------------------------- 색상 스와치 (목록·상세 공용)
def parse_colors(fragment: str) -> list:
    """<div class='color'>...스와치...</div> 조각에서 색상 목록을 뽑는다."""
    colors = []
    cbox = re.search(r"<div class='color'[^>]*>(.*?)</div>\s*</div>", fragment, re.S)
    if cbox:
        for hexv, title in re.findall(
                r"background-color:(#[0-9A-Fa-f]{6});[^']*'\s*title='([^'\[]+)", cbox.group(1)):
            colors.append({"name": title.strip(), "hex": hexv.upper()})
    return colors


# ---------------------------------------------------------------- 목록 파서
def parse_list(page: str, stats: dict = None) -> list:
    """goods_list.php 페이지에서 상품 목록을 뽑는다.

    stats 를 넘기면 {"skipped": N} 형태로 (번호나 이름이 없어) 건너뛴 블록 수를 누적한다.
    """
    items = []
    for block in re.findall(r'<div class="item_cont"[^>]*>(?:(?!<div class="item_cont"|</ul>).)*',
                             page, re.S):
        no = re.search(r'data-goods-no="(\d+)"', block)
        name = re.search(r'<strong class="item_name">(.*?)</strong>', block, re.S)
        if not (no and name):
            if stats is not None:
                stats["skipped"] += 1
            continue
        img = re.search(r'data-image-main\s*=\s*"([^"]+)"', block)
        img_large = re.search(r'data-image-detail\s*=\s*"([^"]+)"', block)
        dc = re.search(r'<div class="dcPrice" custom="([\d.]+)" price="([\d.]+)"', block)
        price = to_int(dc.group(2)) if dc else to_int(
            (re.search(r'data-goods-price="([\d.]+)"', block) or [None, None])[1])
        custom = to_int(dc.group(1)) if dc else None
        list_price = custom if (custom and price and custom > price) else None
        rc = re.search(r"REVIEW\s*:\s*(\d+)", block)
        colors = parse_colors(block)
        tags = ["무료배송"] if "free_delivery" in block else []
        items.append({
            "no": no.group(1),
            "name": clean(name.group(1)),
            "image": img.group(1) if img else "",
            "imageLarge": img_large.group(1) if img_large else "",
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
    cate_cd = re.search(r'name="cateCd" value="(\d+)"', page)
    tit_start = page.find("item_detail_tit")
    if tit_start == -1:
        tit_head = ""
    else:
        tit_end = page.find("btn_qa_share_box", tit_start)
        tit_head = page[tit_start:tit_end] if tit_end != -1 else page[tit_start:]
    colors = parse_colors(tit_head)
    price = re.search(r'name="set_goods_price" value="([\d.]+)"', page)
    fixed = re.search(r'name="set_goods_fixedPrice" value="([\d.]+)"', page)
    ship = re.search(r'<dl class="item_delivery">.*?<dd>(.*?)(?:<span class="btn_layer"|</dd>)', page, re.S)
    gallery = re.findall(r'detailKeyID\[\d+\]\s*=\s*"<img\s+src=\\"([^"\\]+)\\"', page)
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
        "cateCd": cate_cd.group(1) if cate_cd else "",
        "colors": colors,
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
    seats_m = re.search(r"(?<!\d)(\d)인(?!용)", name)
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
    return {"series": series, "size": size, "sizes": sizes, "seats": seats, "shape": shape,
            "material": material, "kind": kind}


def price_band(price):
    if price is None:
        return None
    if price <= 300000:
        return "30만원 이하"
    if price <= 500000:
        return "30–50만원"
    return "50만원 이상"


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


def top_of(cate: str):
    """cateCd(소분류)가 속한 대분류 코드. CATEGORIES 자식 목록에 없으면 앞 3자리로 대체,
    cate 자체가 없으면 None."""
    if not cate:
        return None
    for top in CATEGORIES:
        if any(child["code"] == cate for child in top["children"]):
            return top["code"]
    return cate[:3]


def product_from_detail(no: str, d: dict) -> dict:
    """목록 어디에도 없는 대표 상품을 상세 페이지 정보만으로 조립한다."""
    image = d["gallery"][0] if d.get("gallery") else ""
    item = {
        "no": no,
        "name": d["name"],
        "image": image,
        "imageLarge": image,
        "price": d["price"],
        "listPrice": d["listPrice"],
        "reviewCount": d["reviewCount"],
        "colors": d["colors"],
        "tags": [],
    }
    p = assemble_product(item, cate=d["cateCd"], top=top_of(d["cateCd"]))
    attach_detail(p, d)
    return p


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
    total_skipped = 0
    print("[1/3] 카테고리 목록")
    for top in CATEGORIES:
        for child in top["children"]:
            page = fetch(f"/goods/goods_list.php?cateCd={child['code']}&pageNum=40",
                         f"list-{child['code']}", offline)
            stats = {"skipped": 0}
            items = parse_list(page, stats)
            total_skipped += stats["skipped"]
            expected = len(set(re.findall(r'data-goods-no="(\d+)"', page)))
            if len(items) != expected:
                print(f"  경고: {child['code']} 목록 {len(items)}/{expected}개만 파싱됨")
            for item in items:
                if item["no"] in products:
                    continue
                products[item["no"]] = assemble_product(item, child["code"], top["code"])
                order.append(item["no"])
    extra, seen_extra = [], set()
    for no in DETAIL_GOODS + HOME["weekly"] + HOME["best"] + HOME["new"] + HOME["lookbook"]:
        if no not in products and no not in seen_extra:
            extra.append(no)
            seen_extra.add(no)
    print(f"[1b/3] 목록 밖 대표 상품 {len(extra)}개 상세로 등록")
    for no in extra:
        d = parse_detail(fetch(f"/goods/goods_view.php?goodsNo={no}", f"view-{no}", offline))
        if d.get("name") and d.get("price"):
            products[no] = product_from_detail(no, d)
            order.append(no)
        else:
            print(f"  경고: {no} 상세 페이지에서 상품을 읽지 못함")
    print("[2/3] 대표 상품 상세")
    for no in DETAIL_GOODS:
        if no not in products:
            print(f"  경고: {no} 는 목록에 없어 상세를 건너뜁니다")
            continue
        if "detail" in products[no]:
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
    print(f"목록에서 건너뛴 블록: {total_skipped}개")
    bad_detail = [p["no"] for p in products.values() if "detail" in p and
                  (len(p["detail"].get("shipping") or "") > 60 or not p["detail"].get("gallery"))]
    if bad_detail:
        print(f"  경고: 배송비 문구가 60자를 넘거나 갤러리가 빈 상세 {bad_detail}")
    for key in ("weekly", "best", "new"):
        lost = [n for n in HOME[key] if n not in products]
        if lost:
            print(f"  경고: home.{key} 에서 목록에 없는 상품 제외 {lost}")
    return data


if __name__ == "__main__":
    build(offline="--offline" in sys.argv)
