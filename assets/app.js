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
  const stars = (n) => {
    const k = Math.max(0, Math.min(5, Number(n) || 0));
    return '★'.repeat(k) + '☆'.repeat(5 - k);
  };
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
      // applyFilters/filterOptions의 다중 사이즈 매칭(sizeBands)과 대표값을 맞추기 위해 첫 밴드를 사용
      case 'size': return sizeBands(p)[0] || null;
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
    if (key === 'cate') vals.sort((a, b) => cateRank(a) - cateRank(b));
    return vals;
  }
  function searchProducts(list, q) {
    const terms = String(q || '').trim().split(/\s+/).filter(Boolean);
    if (!terms.length) return list.slice();
    return list.filter((p) => terms.every((t) => (p.name || '').toLowerCase().includes(t.toLowerCase())));
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
  // NAV 상의 노출 순서(대분류 순서 → 그 안의 자식 인덱스)로 카테고리 코드를 정렬하기 위한 우선순위
  function cateRank(code) {
    for (let ti = 0; ti < NAV.length; ti++) {
      if (NAV[ti].code === code) return ti * 1000;
      const ci = NAV[ti].children.findIndex((ch) => ch[0] === code);
      if (ci !== -1) return ti * 1000 + ci + 1;
    }
    return Infinity;
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
  const cateDef = (data, code) => data.categories.find((c) => c.code === code);

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
    const loadAttr = opts.eager ? 'loading="eager" fetchpriority="high"' : 'loading="lazy"';
    return '<a class="card" href="view.html?no=' + esc(p.no) + '">'
      + '<div class="card__tile">'
      + (badge ? '<span class="card__badge' + (badge === 'NEW' ? ' card__badge--new' : '') + '">' + esc(badge) + '</span>' : '')
      + '<img src="' + esc(p.image) + '"' + srcset + ' alt="' + esc(p.name) + '" ' + loadAttr + ' ' + IMG_ERR + '>'
      + '<button class="card__wish" type="button" aria-label="찜하기" onclick="event.preventDefault();this.classList.toggle(\'is-on\')">♡</button>'
      + '</div><div class="card__body"><div class="card__name">' + esc(p.name) + '</div>'
      + '<div class="card__price">' + (rate ? '<span class="rate">' + rate + '%</span>' : '') + fmt(p.price)
      + (p.listPrice ? '<del>' + fmt(p.listPrice) + '</del>' : '') + '</div>'
      + '<div class="card__meta">' + meta.join(' · ') + tags + '</div></div></a>';
  }
  function renderCards(el, list, opts) {
    opts = opts || {};
    el.innerHTML = list.length
      ? list.map((p, i) => cardHTML(p, Object.assign({}, opts, { eager: opts.eager || (opts.eagerFirst && i < 4) }))).join('')
      : '<div class="list__empty">조건에 맞는 상품이 없습니다.</div>';
  }
  function img(src, alt, cls, eager) {
    const loadAttr = eager ? 'loading="eager" fetchpriority="high"' : 'loading="lazy"';
    return '<img src="' + esc(src) + '" alt="' + esc(alt || '') + '"' + (cls ? ' class="' + esc(cls) + '"' : '') + ' ' + loadAttr + ' ' + IMG_ERR + '>';
  }

  /* ==== 헤더 · 푸터 ==== */
  function headerHTML() {
    const menu = NAV.map((t) => '<li class="has-sub"><a href="list.html?cate=' + t.code + '">' + esc(t.short) + '</a><ul class="hdr__sub">'
      + t.children.map((c) => '<li><a href="list.html?cate=' + c[0] + '">' + esc(c[1]) + '</a></li>').join('') + '</ul></li>').join('');
    const drawer = NAV.map((t) => '<li><a href="list.html?cate=' + t.code + '">' + esc(t.name) + '</a><ul>'
      + t.children.map((c) => '<li><a href="list.html?cate=' + c[0] + '">' + esc(c[1]) + '</a></li>').join('') + '</ul></li>').join('');
    return '<div class="hdr__top container">'
      + '<button class="hdr__burger" type="button" aria-label="전체 메뉴" aria-expanded="false" aria-controls="site-drawer" data-open-drawer>' + ICON.menu + '</button>'
      + '<a class="hdr__logo" href="index.html"><img src="assets/logo-header.png" alt="라로퍼니처 RARO FURNITURE"></a>'
      + '<form class="hdr__search" action="list.html" role="search"><input type="search" name="q" placeholder="세라믹 식탁, 리클라이너 소파 검색" aria-label="검색어">'
      + '<input type="hidden" name="cate" value="all"><button type="submit" aria-label="검색">' + ICON.search + '</button></form>'
      + '<nav class="hdr__util" aria-label="회원 메뉴"><a href="#" title="로그인">' + ICON.user + '<span>로그인</span></a>'
      + '<a href="#" title="찜">' + ICON.heart + '<span>찜</span></a>'
      + '<a href="#" title="장바구니">' + ICON.cart + '<span>장바구니</span><span class="hdr__count" aria-label="담긴 상품 0개">0</span></a></nav></div>'
      + '<nav class="hdr__nav container" aria-label="카테고리"><ul class="hdr__menu">' + menu
      + '<li class="hdr__sep" aria-hidden="true"></li>'
      + '<li><a href="list.html?cate=all&amp;sort=popular">BEST</a></li><li><a href="list.html?cate=all&amp;sort=new">NEW</a></li>'
      + '<li><a class="is-accent" href="list.html?cate=all&amp;sale=1">SALE</a></li>'
      + '<li class="hdr__sep" aria-hidden="true"></li>'
      + '<li><a href="brand.html">브랜드</a></li><li><a href="brand.html#showroom">쇼룸</a></li><li><a href="index.html#space">리뷰</a></li></ul></nav>'
      + '<div class="drawer" data-drawer id="site-drawer" role="dialog" aria-modal="true" aria-label="전체 메뉴"><div class="drawer__backdrop" data-close-drawer></div><div class="drawer__panel">'
      + '<div class="drawer__head"><img src="assets/logo-header.png" alt="라로퍼니처" height="26"><button type="button" aria-label="닫기" data-close-drawer>✕</button></div>'
      + '<ul class="drawer__menu">' + drawer + '</ul>'
      + '<div class="drawer__links"><a href="list.html?cate=all&amp;sort=popular">BEST</a><a href="list.html?cate=all&amp;sort=new">NEW</a>'
      + '<a class="is-accent" href="list.html?cate=all&amp;sale=1">SALE</a><a href="brand.html">브랜드</a><a href="brand.html#showroom">쇼룸</a></div>'
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
    const burger = hdr.querySelector('[data-open-drawer]');
    const drawerClose = drawer.querySelector('button[data-close-drawer]');
    function openDrawer() {
      drawer.classList.add('is-open');
      if (burger) burger.setAttribute('aria-expanded', 'true');
      if (drawerClose) drawerClose.focus();
    }
    function closeDrawer() {
      drawer.classList.remove('is-open');
      if (burger) burger.setAttribute('aria-expanded', 'false');
      if (burger) burger.focus();
    }
    hdr.querySelectorAll('[data-open-drawer]').forEach((b) => b.addEventListener('click', openDrawer));
    hdr.querySelectorAll('[data-close-drawer]').forEach((b) => b.addEventListener('click', closeDrawer));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && drawer.classList.contains('is-open')) closeDrawer(); });
    let last = 0;
    window.addEventListener('scroll', () => {
      const y = window.scrollY;
      if ((y > 80) !== (last > 80)) hdr.classList.toggle('is-compact', y > 80);
      last = y;
    }, { passive: true });
  }

  /* ==== 페이지 초기화 ==== */
  const pages = {};

  pages.home = function (data) {
    const H = data.home;
    /* 히어로 (첫 슬라이드는 LCP이므로 eager) */
    const hero = document.getElementById('hero');
    hero.innerHTML = H.hero.map((s, i) => '<div class="hero__slide' + (i === 0 ? ' is-active' : '') + '">' + img(s.img, s.title, null, i === 0)
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

  pages.list = function (data) {
    const cate = param('cate') || 'all', q = param('q') || '', sale = param('sale') === '1';
    const top = cate === 'all' ? null : topOfCate(cate);
    const topDef = top ? cateDef(data, top) : null;
    const isChild = !!top && cate !== top;
    const title = q ? '"' + q + '" 검색 결과' : !topDef ? (sale ? '이번 주 특가' : '전체 상품') : isChild ? childName(cate) : topDef.name;
    document.title = title + ' — 라로퍼니처';
    document.querySelector('[data-title]').textContent = title;
    document.querySelector('[data-desc]').textContent = topDef ? topDef.desc : (q ? '상품명에 검색어가 모두 포함된 상품입니다.' : '라로퍼니처의 모든 가구를 한 번에.');
    document.querySelector('[data-crumb]').innerHTML = '<a href="index.html">홈</a> › '
      + (topDef ? '<a href="list.html?cate=' + top + '">' + esc(topDef.name) + '</a>' : '전체 상품') + (isChild ? ' › ' + esc(childName(cate)) : '');
    /* 기본 목록 (소분류는 cates 기준) */
    let base = data.products.filter((p) => !top || p.top === top);
    if (q) base = searchProducts(base, q);
    if (sale) base = base.filter((p) => discountRate(p.price, p.listPrice) > 0);
    const subEl = document.querySelector('[data-subcats]');
    if (topDef) {
      subEl.innerHTML = '<a class="chip' + (!isChild ? ' is-on' : '') + '" href="list.html?cate=' + top + '">전체 ' + base.length + '</a>'
        + topDef.children.map((c) => '<a class="chip' + (cate === c.code ? ' is-on' : '') + '" href="list.html?cate=' + c.code + '">' + esc(c.name)
          + ' <span class="muted">' + base.filter((p) => inCate(p, c.code)).length + '</span></a>').join('');
    } else { subEl.remove(); }
    if (isChild) base = base.filter((p) => inCate(p, cate));
    /* 필터 (소분류 안에서는 종류 필터 제외) */
    const defs = (FILTER_DEFS[top || 'all'] || []).filter(([k]) => !(isChild && k === 'cate'));
    const active = {};
    const groupsEl = document.querySelector('[data-filter-groups]');
    groupsEl.innerHTML = defs.map(([k, label]) => {
      const opts = filterOptions(base, k);
      if (opts.length < 2) return '';
      return '<fieldset class="filters__group"><legend><h5>' + esc(label) + '</h5></legend>' + opts.map((v) =>
        '<label><input type="checkbox" data-key="' + k + '" value="' + esc(v) + '"> ' + esc(labelFor(k, v)) + '</label>').join('') + '</fieldset>';
    }).join('');
    const sortEl = document.querySelector('[data-sort]');
    sortEl.value = ['reco', 'popular', 'priceAsc', 'priceDesc', 'review', 'new'].includes(param('sort')) ? param('sort') : 'reco';
    let shown = 12;
    const grid = document.querySelector('[data-grid]'), countEl = document.querySelector('[data-count]');
    const moreBtn = document.querySelector('[data-more]'), activeEl = document.querySelector('[data-active]');
    function render() {
      const list = sortProducts(applyFilters(base, active), sortEl.value);
      countEl.textContent = list.length;
      if (!base.length) {
        grid.innerHTML = '<div class="list__empty">' + (q ? '검색 결과가 없습니다. 다른 검색어로 찾아보세요.' : '준비 중인 카테고리입니다. 다른 카테고리를 둘러보세요.') + '</div>';
      } else {
        renderCards(grid, list.slice(0, shown), { eagerFirst: true });
      }
      moreBtn.parentNode.style.display = list.length > shown ? '' : 'none';
      moreBtn.textContent = Math.min(12, list.length - shown) + '개 더 보기';
      activeEl.innerHTML = Object.entries(active).flatMap(([k, set]) => Array.from(set).map((v) =>
        '<button type="button" class="chip is-on chip--x" data-key="' + k + '" data-value="' + esc(v) + '" aria-label="' + esc(labelFor(k, v)) + ' 필터 해제">' + esc(labelFor(k, v)) + '</button>')).join('');
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
      shown = 12; render();
    });
    document.querySelector('[data-filters-reset]').addEventListener('click', () => {
      Object.keys(active).forEach((k) => active[k].clear());
      groupsEl.querySelectorAll('input').forEach((i) => { i.checked = false; });
      shown = 12; render();
    });
    sortEl.addEventListener('change', () => { shown = 12; render(); });
    moreBtn.addEventListener('click', () => { shown += 12; render(); });
    /* 모바일 필터 시트 */
    const sheet = document.querySelector('[data-filters]'), backdrop = document.querySelector('[data-filters-backdrop]');
    const openBtn = document.querySelector('[data-filters-open]');
    const openSheet = (o) => {
      sheet.classList.toggle('is-open', o); backdrop.classList.toggle('is-open', o);
      openBtn.setAttribute('aria-expanded', String(o));
      if (o) { const first = sheet.querySelector('input, button'); if (first) first.focus(); } else { openBtn.focus(); }
    };
    openBtn.addEventListener('click', () => openSheet(true));
    document.querySelectorAll('[data-filters-close]').forEach((b) => b.addEventListener('click', () => openSheet(false)));
    backdrop.addEventListener('click', () => openSheet(false));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && sheet.classList.contains('is-open')) openSheet(false); });
    /* 구매 가이드 */
    const g = topDef ? topDef.guide : { title: '어떤 가구를 찾으세요?',
      body: '식탁은 인원과 공간 폭, 소파는 거실 폭, 침대는 매트리스 규격부터 확인하면 고르기 쉽습니다. 카테고리를 고르면 맞춤 가이드가 나옵니다.' };
    document.querySelector('[data-guide-title]').textContent = g.title;
    document.querySelector('[data-guide-body]').textContent = g.body;
    render();
  };

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
    if (pages[page]) {
      try {
        pages[page](data);
      } catch (e) {
        console.error('[RARO] 페이지 렌더 실패', e);
        document.querySelectorAll('[data-needs-data]').forEach((el) => {
          el.innerHTML = '<div class="notice">화면을 그리는 중 문제가 발생했습니다. 콘솔을 확인해 주세요.</div>';
        });
      }
    }
  }
  if (typeof document !== 'undefined') document.addEventListener('DOMContentLoaded', init);

  return { NAV, FILTER_DEFS, PRICE_BANDS, SIZE_BANDS, esc, fmt, stars, discountRate, optionTotal, sizeBand, sizeBands, catesOf, inCate,
           sortProducts, applyFilters, filterOptions, searchProducts, valueFor, labelFor, topOf, topName, childName, topOfCate,
           loadData, product, products, param, cateDef, cardHTML, renderCards, img, headerHTML, footerHTML, pages, state };
})();
