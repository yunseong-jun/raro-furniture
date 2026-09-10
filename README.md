# 라로퍼니처 UI 리디자인 프로토타입

rarofurniture.co.kr(고도몰)을 Article × Floyd 방향으로 다시 설계한 정적 프로토타입. 나중에 고도몰 스킨으로 옮기는 것을 전제로 페이지 구분을 고도몰과 1:1로 맞췄다.

## 실행

```bash
# 1) 데이터 생성 (사이트에서 약 42개 페이지를 1초 간격으로 가져온다. 캐시가 있으면 재요청하지 않음)
PYTHONIOENCODING=utf-8 python data/build.py
#    캐시(data/raw/)만으로 다시 조립하려면 --offline, 캐시를 무시하고 새로 받으려면 --refresh

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
powershell -ExecutionPolicy Bypass -File tools/screenshot.ps1   # 4페이지 × 3폭 스크린샷 → docs/screenshots/ (bash tools/screenshot.sh 도 동일)
```

## 결과 확인

- 스크린샷 12장: `docs/screenshots/` (`home|list|view|brand` × `desktop|tablet|mobile`). 헤드리스 Edge의 최소 뷰포트 제한으로 모바일은 500px 폭으로 찍는다.
- 고도몰 이식 가이드: `docs/godomall-porting.md`
- 설계 문서: `docs/superpowers/specs/2026-09-10-raro-furniture-redesign-design.md` · 구현 계획: `docs/superpowers/plans/2026-09-10-raro-furniture-phase1.md`
- JS 테스트: `http://localhost:8080/tests/app.test.html` (55개) · 파이썬 테스트: `python -m unittest tests.test_build` (41개)

## 2단계

리뷰 목록, 이벤트, 고객센터, 로그인·회원가입, 장바구니·주문, 마이페이지, 약관 페이지를 같은 디자인 시스템으로 확장한다. 별도 계획 문서로 진행.
