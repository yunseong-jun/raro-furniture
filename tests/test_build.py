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
        self.assertEqual(build.price_band(178000), "30만원 이하")
        self.assertEqual(build.price_band(300000), "30만원 이하")
        self.assertEqual(build.price_band(398000), "30–50만원")
        self.assertEqual(build.price_band(689000), "50만원 이상")
        self.assertIsNone(build.price_band(None))


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
        self.assertEqual(p["top"], "012")
        self.assertEqual(p["image"], "g1.jpg")
        self.assertEqual(p["series"], "허그")
        self.assertEqual(len(p["features"]), 3)
        self.assertIs(p["detail"], d)


if __name__ == "__main__":
    unittest.main()
