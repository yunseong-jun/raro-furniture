import sys, pathlib, tempfile, unittest
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
<div class="item_icon_box"><img src="https://cdn-saas-web-116-148.cdn-nhncommerce.com/furnius9462_godomall_com/data/icon/goods_icon/free_delivery.gif" alt="무료배송" /><img src="https://cdn-saas-web-116-148.cdn-nhncommerce.com/furnius9462_godomall_com/data/icon/goods_icon/ico_pastel_02.png" alt="엠플샵아이콘" /></div>
</div></div></li>
<li style="width:25%;"> <div class="item_cont">
<div class="item_photo_box" data-image-main = "https://furnius.hgodo.com/img/thumbnail/1000000111_400.jpg">
<button class="btn_add_wish_widget" data-goods-no="1000000111"></button></div>
<div class="item_tit_box"><strong class="item_name">에버 유광 600/800 원형 포세린 통 세라믹 침실 테라스 테이블</strong></div>
<div class="item_money_box"><strong class="item_price"><div class="dcPrice" custom="64000.00" price="64000.00"></div><span>64,000원</span></strong></div>
<div class="item_review_cnt">REVIEW : 0</div>
</div></li>
<li style="width:25%;"> <div class="item_cont" style="text-align:center;">
<div class="item_photo_box" data-image-main = "https://furnius.hgodo.com/img/thumbnail/1000000200_400.jpg">
<a href="../goods/goods_view.php?goodsNo=1000000200"><img src="https://furnius.hgodo.com/img/thumbnail/1000000200_400.jpg" /></a>
<div class="item_link"><button type="button" class="btn_basket_get" data-goods-no="1000000200" data-goods-nm="모카 방석 원목 식탁 의자" data-goods-price="99000.00"><span>WISH</span></button></div></div>
<div class="item_info_cont">
<div class="item_tit_box"><strong class="item_name">모카 방석 원목 식탁 의자</strong></div>
<div class="item_money_box"><strong class="item_price"><span>99,000원</span></strong></div>
<div class="item_review_cnt">REVIEW : 5</div>
</div></div></li>
"""

# 실제 마크업(data/raw/list-003004.html)에서 품절 상품은 위시 버튼(data-goods-no)이 아예 빠지고
# goods_view.php 링크와 icon_soldout.gif 아이콘만 남는다.
SOLDOUT_ITEM_HTML = """
<li class="item_soldout" style="width:25%;">
<div class="item_cont">
<div class="item_photo_box" data-image-main = "https://furnius.hgodo.com/img/thumbnail/1000000450_300.jpg">
<a href="../goods/goods_view.php?goodsNo=1000000450" >
<img  src="https://furnius.hgodo.com/img/thumbnail/1000000450_300.jpg" alt="몽크 600+700 사각 2단 포세린 통 세라믹 거실 테이블" class="middle"  />
<strong class="item_soldout_bg" style="background-image:url(/data/icon/goods_icon/custom/soldout_overlay);">SOLD OUT</strong>
</a>
</div>
<div class="item_info_cont">
<div class="item_tit_box">
<a href="../goods/goods_view.php?goodsNo=1000000450">
<strong class="item_name">몽크 600+700 사각 2단 포세린 통 세라믹 거실 테이블</strong>
</a>
</div>
<div class="item_money_box">
<strong class="item_price">
<div class="dcPrice" custom="240000.00" price="101000.00"></div>
<span  style="">101,000원 </span>
</strong>
</div>
<div class="item_review_cnt">REVIEW : 1</div>
<div class="item_icon_box">
<img src="https://cdn-saas-web-116-148.cdn-nhncommerce.com/furnius9462_godomall_com/data/icon/goods_icon/icon_soldout.gif" alt="품절" />
</div>
</div>
</div>
</li>
"""

# 실제 마크업(data/raw/list-012004.html)에서 data-image-detail 이 상품 이미지가 아니라
# "roman_mar4_logo_01.jpg" 같은 로고성 파일명을 가리키는 경우가 있다.
LOGO_IMAGE_ITEM_HTML = """
<li><div class="item_cont">
<div class="item_photo_box" data-image-main = "https://furnius.hgodo.com/img/thumbnail/1000000900_400.jpg" data-image-detail = "https://furnius.hgodo.com/img/thumbnail/roman/roman_mar4_logo_01.jpg">
<button class="btn_add_wish_widget" data-goods-no="1000000900"></button></div>
<div class="item_tit_box"><strong class="item_name">테스트 상품</strong></div>
<div class="item_money_box"><strong class="item_price"><span>10,000원</span></strong></div>
<div class="item_review_cnt">REVIEW : 0</div>
</div></li>
"""

DETAIL_HTML = """
<input type="hidden" name="set_goods_price" value="398000" />
<input type="hidden" id="set_goods_fixedPrice" name="set_goods_fixedPrice" value="500000.00" />
<input type="hidden" name="cateCd" value="012002" />
<div class="item_detail_tit"> <h3>허그 1400 포세린 통 세라믹 4인 식탁 세트</h3>
<div class='color'><div style='background-color:#FFFFFF;' title='흰색[White]'></div><div style='background-color:#8E562E; border-color:#8E562E;' title='갈색[Brown]'></div></div>
<div class="btn_layer btn_qa_share_box"></div>
</div>
<dl class="item_price"><dt>판매가</dt><dd><strong><strong>398,000</strong></strong>원</dd></dl>
<dl class="item_delivery"><dt>배송비</dt><dd><strong>40,000원</strong> / 상품수령시결제(착불) <span class="btn_layer"><a href="#lyDelivery">조건별배송</a></span><div id="lyDelivery">긴 표 내용 긴 표 내용 긴 표 내용</div></dd></dl>
<script>detailKeyID[0] = "<img  src=\\"https://furnius.hgodo.com/img/thumbnail/1000000491_1000_1.jpg\\" width=\\"600\\" />"; detailKeyID[1] = "<img  src=\\"https://furnius.hgodo.com/img/thumbnail/1000000491_1000_2.jpg\\" />";</script>
<dt>구성</dt>
<select name="optionNo_0" class="chosen-select"><option value=""> = 구성 선택 = </option><option value="1">식탁+의자2+벤치1</option><option value="2">식탁+의자4</option><option value="3">식탁 단품</option></select>
<select name="optionNo_1"><option value=""> = 구성을 먼저 선택해 주세요 = </option></select>
<img src="https://furnius.hgodo.com/img/banner/top_banner_01.jpg" />
<div id="detail"><div class="item_goods_tab"><ul><li><a href="#reviews">상품후기 <strong>(12)</strong></a></li><li><a href="#qna">상품문의 <strong>(3)</strong></a></li></ul></div>
<img src="https://furnius.hgodo.com/table/ceramic/hug_ce4_01.jpg" /><img src="https://furnius.hgodo.com/table/ceramic/hug_ce4_02.jpg" /><img src="https://furnius.hgodo.com/info/company.jpg" />
<img src="https://furnius.hgodo.com/banner/event_bnr.jpg" /><img src="https://furnius.hgodo.com/table/ceramic/ceramic_video_01.jpg" /><img src="https://furnius.hgodo.com/sofa/cona_sofa4_gift.jpg" /><img src="https://furnius.hgodo.com/table/wood/care_notice.jpg" /><img src="https://furnius.hgodo.com/delivery/chair_money_1box.jpg" />
<div class="datail_table"><table class="left_table_type"><tbody>
<tr><th style="width:20%">품명</th><td colspan="3">상세페이지 참조</td></tr>
<tr><th style="width:20%">KC 인증정보</th><td colspan="3">KC인증대상아님</td></tr>
<tr><th>제조/수입자</th><td>라로퍼니처</td></tr>
<tr><th>AS 책임자와 전화번호</th><td>[라로퍼니처 고객센터] 031 ) 977 - 7352</td></tr>
<tr><th>크기</th><td>상품상세참조</td></tr>
</tbody></table></div></div>
"""

# 실제 마크업(data/raw/view-1000000104.html)의 optionSnoInput 셀렉트를 그대로 옮긴 조각.
# value 형식: "옵션일련번호||추가금액||||...^|^옵션명" — 두 번째 필드가 delta(음수 가능).
OPTION_SNO_HTML = """
<div class="item_add_option_box">
<dl>
<dt>구성</dt>
<dd>
<select name="optionSnoInput" class="chosen-select" onchange="gd_option_image_apply();goodsViewController.option_price_display(this);">
<option value="">
    =
옵션
 : 가격
: 재고                                        =
</option>
<option  data-img-src="https://cdn-saas-web-116-148.cdn-nhncommerce.com/furnius9462_godomall_com/data/commonimg/ico_noimg_100.gif" value="196||-114000||||0^|^원형 테이블 1000" alt="원형 테이블 1000">
원형 테이블 1000

 : -114,000원                                    </option>
<option  data-img-src="https://cdn-saas-web-116-148.cdn-nhncommerce.com/furnius9462_godomall_com/data/commonimg/ico_noimg_100.gif" value="197||0||||0^|^원형 테이블1+의자2" alt="원형 테이블1+의자2">
원형 테이블1+의자2
</option>
<option  data-img-src="https://cdn-saas-web-116-148.cdn-nhncommerce.com/furnius9462_godomall_com/data/commonimg/ico_noimg_100.gif" value="199||111000||||0^|^원형 테이블1+의자4" alt="원형 테이블1+의자4">
원형 테이블1+의자4

 : +111,000원                                    </option>
</select>
</dd>
</dl>
</div>
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
    def test_parses_three_items(self):
        items = build.parse_list(LIST_HTML)
        self.assertEqual([i["no"] for i in items], ["1000000107", "1000000111", "1000000200"])

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

    def test_third_item_variant_and_fallback_price(self):
        p = build.parse_list(LIST_HTML)[2]
        self.assertEqual(p["no"], "1000000200")
        self.assertEqual(p["price"], 99000)
        self.assertIsNone(p["listPrice"])

    def test_image_large_field(self):
        items = build.parse_list(LIST_HTML)
        self.assertEqual(items[0]["imageLarge"],
                          "https://furnius.hgodo.com/img/thumbnail/1000000107_1000_1.jpg")
        self.assertEqual(items[1]["imageLarge"], "")

    def test_empty_input_returns_empty_list(self):
        self.assertEqual(build.parse_list(""), [])

    def test_last_block_does_not_run_past_list_close(self):
        # 목록 </ul> 뒤에 다른 위젯(예: 후기 카운트)이 이어져도 마지막 상품 블록이
        # 거기까지 먹어치우면 안 된다.
        page = LIST_HTML + '</ul><div class="item_review_cnt">REVIEW : 99</div>'
        items = build.parse_list(page)
        self.assertEqual(len(items), 3)
        self.assertNotEqual(items[-1]["reviewCount"], 99)

    def test_skipped_blocks_are_counted_in_stats(self):
        stats = {"skipped": 0}
        page = LIST_HTML + '<li><div class="item_cont"><div class="item_photo_box"></div></div></li>'
        items = build.parse_list(page, stats)
        self.assertEqual(len(items), 3)
        self.assertEqual(stats["skipped"], 1)

    def test_soldout_item_falls_back_to_href_and_tags_soldout(self):
        items = build.parse_list(SOLDOUT_ITEM_HTML)
        self.assertEqual(len(items), 1)
        p = items[0]
        self.assertEqual(p["no"], "1000000450")
        self.assertEqual(p["name"], "몽크 600+700 사각 2단 포세린 통 세라믹 거실 테이블")
        self.assertIn("품절", p["tags"])

    def test_normal_item_is_not_tagged_soldout(self):
        p = build.parse_list(LIST_HTML)[0]
        self.assertNotIn("품절", p["tags"])

    def test_image_large_excludes_logo_and_banner(self):
        items = build.parse_list(LOGO_IMAGE_ITEM_HTML)
        self.assertEqual(items[0]["imageLarge"], "")


class ListPageWarningsTest(unittest.TestCase):
    def test_no_warning_when_counts_match(self):
        items = build.parse_list(LIST_HTML)
        self.assertEqual(build.list_page_warnings("012002", LIST_HTML, items), [])

    def test_mismatch_gives_warning(self):
        page = LIST_HTML + '<div data-goods-no="9999999"></div>'
        items = build.parse_list(LIST_HTML)
        msgs = build.list_page_warnings("012002", page, items)
        self.assertEqual(len(msgs), 1)
        self.assertIn("경고", msgs[0])
        self.assertIn("012002", msgs[0])

    def test_duplicate_exposure_gives_note_instead_of_warning(self):
        items = build.parse_list(LIST_HTML)
        items = items + [dict(items[0])]  # 같은 상품이 페이지에 두 번 노출된 경우
        msgs = build.list_page_warnings("012002", LIST_HTML, items)
        self.assertEqual(len(msgs), 1)
        self.assertIn("참고", msgs[0])
        self.assertIn("중복 노출", msgs[0])


class ParseDetailTest(unittest.TestCase):
    def test_fields(self):
        d = build.parse_detail(DETAIL_HTML)
        self.assertEqual(d["name"], "허그 1400 포세린 통 세라믹 4인 식탁 세트")
        self.assertEqual(d["cateCd"], "012002")
        self.assertEqual(d["colors"], [{"name": "흰색", "hex": "#FFFFFF"}, {"name": "갈색", "hex": "#8E562E"}])
        self.assertEqual(d["price"], 398000)
        self.assertEqual(d["listPrice"], 500000)
        self.assertEqual(d["shipping"], "40,000원 / 상품수령시결제(착불)")
        self.assertEqual(d["gallery"], [
            "https://furnius.hgodo.com/img/thumbnail/1000000491_1000_1.jpg",
            "https://furnius.hgodo.com/img/thumbnail/1000000491_1000_2.jpg"])
        self.assertEqual([o["name"] for o in d["options"]], ["식탁+의자2+벤치1", "식탁+의자4", "식탁 단품"])
        self.assertEqual([o["delta"] for o in d["options"]], [None, None, None])
        self.assertEqual(d["optionLabel"], "구성")
        self.assertEqual(d["optionLevels"], 1)
        self.assertEqual(d["detailImages"], [
            "https://furnius.hgodo.com/table/ceramic/hug_ce4_01.jpg",
            "https://furnius.hgodo.com/table/ceramic/hug_ce4_02.jpg"])
        self.assertEqual(d["spec"], {"KC 인증정보": "KC인증대상아님", "제조/수입자": "라로퍼니처",
                                     "AS 책임자와 전화번호": "[라로퍼니처 고객센터] 031 ) 977 - 7352"})
        self.assertEqual(d["reviewCount"], 12)
        self.assertEqual(d["qnaCount"], 3)

    def test_empty_input_is_safe(self):
        d = build.parse_detail("")
        self.assertEqual(d["gallery"], [])
        self.assertEqual(d["options"], [])
        self.assertEqual(d["spec"], {})
        self.assertIsNone(d["price"])
        self.assertEqual(d["cateCd"], "")
        self.assertEqual(d["colors"], [])
        self.assertEqual(d["optionLabel"], "")
        self.assertEqual(d["optionLevels"], 0)


class ParseDetailOptionSnoTest(unittest.TestCase):
    def test_option_sno_input_parsed_with_deltas(self):
        d = build.parse_detail(OPTION_SNO_HTML)
        self.assertEqual([o["name"] for o in d["options"]],
                          ["원형 테이블 1000", "원형 테이블1+의자2", "원형 테이블1+의자4"])
        self.assertEqual([o["delta"] for o in d["options"]], [-114000, 0, 111000])
        self.assertEqual(d["optionLabel"], "구성")
        self.assertEqual(d["optionLevels"], 1)

    def test_option_levels_from_option_cnt_input(self):
        html = '<input type="hidden" name="optionCntInput" value="2" />' + OPTION_SNO_HTML
        d = build.parse_detail(html)
        self.assertEqual(d["optionLevels"], 2)


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
        self.assertEqual(a, {"series": "허그", "size": 1400, "sizes": [1400], "seats": 4, "shape": "사각",
                             "material": "무광 세라믹", "kind": "세트"})

    def test_round_gloss_single(self):
        a = build.derive("에버 유광 600/800 원형 포세린 통 세라믹 침실 테라스 테이블", "012")
        self.assertEqual(a["size"], 600)
        self.assertEqual(a["sizes"], [600, 800])
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
        self.assertEqual(build.price_band(64000), "10만원 이하")
        self.assertEqual(build.price_band(100000), "10만원 이하")
        self.assertEqual(build.price_band(178000), "10–20만원")
        self.assertEqual(build.price_band(200000), "10–20만원")
        self.assertEqual(build.price_band(300000), "20–30만원")
        self.assertEqual(build.price_band(398000), "30–50만원")
        self.assertEqual(build.price_band(500000), "30–50만원")
        self.assertEqual(build.price_band(689000), "50만원 이상")
        self.assertIsNone(build.price_band(None))


class AssembleTest(unittest.TestCase):
    def test_assemble_product_merges_detail_and_attrs(self):
        item = {"no": "1000000491", "name": "허그 1400 포세린 통 세라믹 4인 식탁 세트",
                "image": "t.jpg", "price": 398000, "listPrice": None, "reviewCount": 84,
                "colors": [], "tags": []}
        p = build.assemble_product(item, cate="012002", top="012")
        self.assertEqual(p["cate"], "012002")
        self.assertEqual(p["cates"], ["012002"])
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
        self.assertNotIn("features", p)
        self.assertEqual(p["reviewCount"], 84)

    def test_categories_have_required_text(self):
        for top in build.CATEGORIES:
            self.assertTrue(top["desc"])
            self.assertTrue(top["guide"]["title"] and top["guide"]["body"])
            self.assertTrue(top["children"])
            self.assertIn(top["code"], build.FEATURES)

    def test_all_categories_have_three_features(self):
        self.assertTrue(all(len(c["features"]) == 3 for c in build.CATEGORIES))


class RegisterItemTest(unittest.TestCase):
    def _item(self, no="1"):
        return {"no": no, "name": "테스트 세라믹 식탁", "image": "", "imageLarge": "", "price": 100000,
                "listPrice": None, "reviewCount": 0, "colors": [], "tags": []}

    def test_first_registration_sets_cate_and_cates(self):
        products, order = {}, []
        build.register_item(products, order, self._item(), "012002", "012")
        self.assertEqual(products["1"]["cate"], "012002")
        self.assertEqual(products["1"]["cates"], ["012002"])
        self.assertEqual(order, ["1"])

    def test_second_list_page_appends_cate_keeps_first_as_primary(self):
        products, order = {}, []
        build.register_item(products, order, self._item(), "012002", "012")
        build.register_item(products, order, self._item(), "012003", "012")
        self.assertEqual(products["1"]["cate"], "012002")
        self.assertEqual(products["1"]["cates"], ["012002", "012003"])
        self.assertEqual(order, ["1"])

    def test_same_cate_seen_twice_is_not_duplicated(self):
        products, order = {}, []
        build.register_item(products, order, self._item(), "012002", "012")
        build.register_item(products, order, self._item(), "012003", "012")
        build.register_item(products, order, self._item(), "012002", "012")
        self.assertEqual(products["1"]["cates"], ["012002", "012003"])
        self.assertEqual(order, ["1"])


class TopOfTest(unittest.TestCase):
    def test_known_child_resolves_to_its_top(self):
        self.assertEqual(build.top_of("012002"), "012")
        self.assertEqual(build.top_of("013003"), "013")

    def test_unknown_child_falls_back_to_prefix(self):
        self.assertEqual(build.top_of("006999"), "006")

    def test_empty_is_none(self):
        self.assertIsNone(build.top_of(""))


class ProductFromDetailTest(unittest.TestCase):
    def test_builds_list_shaped_item_from_detail(self):
        d = {"name": "허그 1400 포세린 통 세라믹 4인 식탁 세트", "cateCd": "012002",
             "price": 398000, "listPrice": 500000, "shipping": "40,000원",
             "gallery": ["g1.jpg", "g2.jpg"], "options": [], "detailImages": [], "spec": {},
             "colors": [{"name": "흰색", "hex": "#FFFFFF"}], "reviewCount": 12, "qnaCount": 3}
        p = build.product_from_detail("1000000491", d)
        self.assertEqual(p["cate"], "012002")
        self.assertEqual(p["cates"], ["012002"])
        self.assertEqual(p["top"], "012")
        self.assertEqual(p["image"], "g1.jpg")
        self.assertEqual(p["series"], "허그")
        self.assertNotIn("features", p)
        self.assertIs(p["detail"], d)

    def _detail(self, cate_cd):
        return {"name": "미분류 상품", "cateCd": cate_cd,
                "price": 50000, "listPrice": None, "shipping": "",
                "gallery": [], "options": [], "detailImages": [], "spec": {},
                "colors": [], "reviewCount": 0, "qnaCount": 0}

    def test_unknown_category_does_not_raise(self):
        p = build.product_from_detail("9999999", self._detail("005001"))
        self.assertEqual(p["top"], "005")
        self.assertEqual(p["cate"], "005001")

    def test_empty_category_does_not_raise(self):
        p = build.product_from_detail("9999999", self._detail(""))
        self.assertIsNone(p["top"])


class FakeHTTPResponse:
    """urllib.request.urlopen 을 대체할 오프라인 테스트용 가짜 응답."""

    def __init__(self, body: str):
        self._body = body.encode("utf-8")

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FetchTest(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._orig_raw = build.RAW
        self._orig_urlopen = build.urllib.request.urlopen
        self._orig_sleep = build.time.sleep
        build.RAW = pathlib.Path(self._tmpdir.name)
        build.time.sleep = lambda seconds: None  # 테스트에서 실제로 대기하지 않는다

    def tearDown(self):
        build.RAW = self._orig_raw
        build.urllib.request.urlopen = self._orig_urlopen
        build.time.sleep = self._orig_sleep
        self._tmpdir.cleanup()

    def test_cache_hit_returns_text_without_network(self):
        (build.RAW / "cached.html").write_text("cached body", encoding="utf-8")

        def boom(*a, **k):
            raise AssertionError("네트워크를 사용하면 안 됨")
        build.urllib.request.urlopen = boom

        text = build.fetch("/x", "cached", offline=False)
        self.assertEqual(text, "cached body")

    def test_missing_cache_offline_raises_system_exit(self):
        with self.assertRaises(SystemExit):
            build.fetch("/x", "missing", offline=True)

    def test_body_without_marker_raises_and_does_not_cache(self):
        build.urllib.request.urlopen = lambda req, timeout=30: FakeHTTPResponse("<html>엉뚱한 페이지</html>")
        with self.assertRaises(SystemExit):
            build.fetch("/goods/goods_list.php?cateCd=012002", "badmarker", offline=False, marker="item_cont")
        self.assertFalse((build.RAW / "badmarker.html").exists())

    def test_retries_once_then_succeeds(self):
        calls = {"n": 0}

        def flaky(req, timeout=30):
            calls["n"] += 1
            if calls["n"] == 1:
                raise build.urllib.error.URLError("일시적 오류")
            return FakeHTTPResponse("<div class='item_cont'>ok</div>")
        build.urllib.request.urlopen = flaky

        text = build.fetch("/x", "retry-ok", offline=False, marker="item_cont")
        self.assertIn("item_cont", text)
        self.assertEqual(calls["n"], 2)

    def test_second_failure_raises_system_exit(self):
        def always_fails(req, timeout=30):
            raise build.urllib.error.URLError("영구 오류")
        build.urllib.request.urlopen = always_fails

        with self.assertRaises(SystemExit):
            build.fetch("/x", "fail-twice", offline=False, marker="item_cont")


if __name__ == "__main__":
    unittest.main()
