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
  const PRICE_BANDS = ['10만원 이하', '10–20만원', '20–30만원', '30–50만원', '50만원 이상'];
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
  function sizeBands(p) {
    const list = (p.sizes && p.sizes.length) ? p.sizes : [p.size];
    const out = [];
    list.forEach((s) => { const b = sizeBand(s); if (b && !out.includes(b)) out.push(b); });
    return out;
  }
  const catesOf = (p) => (p.cates && p.cates.length ? p.cates : (p.cate ? [p.cate] : []));
  const inCate = (p, code) => catesOf(p).includes(code);
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
    return list.filter((p) => groups.every(([k, vals]) => {
      if (k === 'size') return sizeBands(p).some((b) => vals.includes(b));
      if (k === 'cate') return catesOf(p).some((c) => vals.includes(c));
      return vals.includes(valueFor(p, k));
    }));
  }
  function filterOptions(list, key) {
    if (key === 'price') return PRICE_BANDS.filter((b) => list.some((p) => p.priceBand === b));
    if (key === 'size') return SIZE_BANDS.filter((b) => list.some((p) => sizeBands(p).includes(b)));
    const vals = [];
    const push = (v) => { if (v != null && !vals.includes(v)) vals.push(v); };
    list.forEach((p) => { if (key === 'cate') catesOf(p).forEach(push); else push(valueFor(p, key)); });
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
    const srcset = p.imageLarge ? ' srcset="' + esc(p.image) + ' 400w, ' + esc(p.imageLarge) + ' 1000w" sizes="(max-width: 768px) 50vw, 25vw"' : '';
    return '<a class="card" href="view.html?no=' + esc(p.no) + '">'
      + '<div class="card__tile">'
      + (badge ? '<span class="card__badge' + (badge === 'NEW' ? ' card__badge--new' : '') + '">' + esc(badge) + '</span>' : '')
      + '<img src="' + esc(p.image) + '"' + srcset + ' alt="' + esc(p.name) + '" loading="lazy" ' + IMG_ERR + '>'
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

  return { NAV, FILTER_DEFS, PRICE_BANDS, SIZE_BANDS, esc, fmt, stars, discountRate, optionTotal, sizeBand, sizeBands, catesOf, inCate,
           sortProducts, applyFilters, filterOptions, searchProducts, valueFor, labelFor, topOf, topName, childName, topOfCate,
           loadData, product, products, param, cardHTML, renderCards, img, headerHTML, footerHTML, pages, state };
})();
