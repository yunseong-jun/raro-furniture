#!/usr/bin/env python3
"""라로퍼니처(rarofurniture.co.kr) 상품·카테고리 데이터를 수집해 data/site.json을 만든다.

사용법:
    PYTHONIOENCODING=utf-8 python data/build.py            # 캐시 없는 페이지만 요청 후 생성
    PYTHONIOENCODING=utf-8 python data/build.py --offline  # data/raw/ 캐시만 사용 (네트워크 없음)

요청은 브라우저 UA로 1초 간격, 총 32건 안팎. 결과 HTML은 data/raw/에 캐시한다.
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
    for block in re.findall(r'<div class="item_cont"[^>]*>(?:(?!<div class="item_cont").)*', page, re.S):
        no = re.search(r'data-goods-no="(\d+)"', block)
        name = re.search(r'<strong class="item_name">(.*?)</strong>', block, re.S)
        if not (no and name):
            continue
        img = re.search(r'data-image-main\s*=\s*"([^"]+)"', block)
        img_large = re.search(r'data-image-detail\s*=\s*"([^"]+)"', block)
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
