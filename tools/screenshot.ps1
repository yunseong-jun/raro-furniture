# 4페이지 × 3폭 스크린샷 → docs/screenshots/  (사전 조건: python -m http.server 8080 실행 중)
# 사용: powershell -ExecutionPolicy Bypass -File tools/screenshot.ps1
$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$base = if ($env:BASE) { $env:BASE } else { "http://localhost:8080" }
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$out = Join-Path $root "docs\screenshots"
New-Item -ItemType Directory -Force $out | Out-Null
$profile = Join-Path $env:LOCALAPPDATA "Temp\edge-shot"
$pages = @(
  @{ url = "index.html";               name = "home";  h = @{ desktop = 6400; tablet = 8700; mobile = 9200 } },
  @{ url = "list.html?cate=012";       name = "list";  h = @{ desktop = 3400; tablet = 3800; mobile = 5200 } },
  @{ url = "view.html?no=1000000491";  name = "view";  h = @{ desktop = 6400; tablet = 7000; mobile = 8400 } },
  @{ url = "brand.html";               name = "brand"; h = @{ desktop = 2800; tablet = 3200; mobile = 4200 } }
)
# 헤드리스 Edge는 뷰포트 최소 폭이 약 483px이라 모바일은 500px로 캡처한다.
$widths = @(@{ label = "desktop"; w = 1440 }, @{ label = "tablet"; w = 1024 }, @{ label = "mobile"; w = 500 })
foreach ($p in $pages) {
  foreach ($s in $widths) {
    $file = Join-Path $out ("{0}-{1}.png" -f $p.name, $s.label)
    $args = @('--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-sandbox', "--user-data-dir=$profile",
              ("--window-size={0},{1}" -f $s.w, $p.h[$s.label]), '--virtual-time-budget=4000',
              "--screenshot=$file", ("{0}/{1}" -f $base, $p.url))
    Start-Process -FilePath $edge -ArgumentList $args -Wait
    Start-Sleep -Seconds 2
    Write-Host ("saved {0}" -f $file)
  }
}
Stop-Process -Name msedge -Force -ErrorAction SilentlyContinue
