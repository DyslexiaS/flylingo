#!/usr/bin/env python3
"""Build the FlyLingo prototypes from flylingo.html.

flylingo.html already embeds the school / process / FAQ data and both logos,
so this script reuses them instead of re-reading the source spreadsheets.

  python3 _build_redesign.py
  -> flylingo-v1-soft.html   (borderless white cards, soft shadows, floating star)
  -> flylingo-v2-crisp.html  (hairline borders, sharper corners, scroll progress)
  -> flylingo-design-system.html  (color tokens, accent candidates, usage rules)
"""
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "flylingo.html"
FAVICON = ROOT / "icons" / "dark.favion.svg"


def favicon_link():
    # Inlined so a single emailed HTML file still shows the tab icon.
    # dark.favion.svg is the green tile: white mark, yellow star.
    svg = " ".join(FAVICON.read_text().split())
    return f'<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,{quote(svg, safe=" =:/,.-")}">'


# Link previews (LINE, Messages) do not run the page, and they do not show SVG.
# icons/og.png is the black-background FlyLingo Shooting Star Logo.
SITE = "https://dyslexias.github.io/flylingo"
OG_IMAGE = f"{SITE}/icons/og.png?v=2"
OG_TITLE = "FlyLingo 飛語｜從語言出發，飛向世界"
OG_DESC = "先了解你的目標、週數和預算，再幫你挑學校、辦報名，到結業都有人協助。"


def og_tags(path):
    url = SITE + "/" if path in ("", "index.html") else f"{SITE}/{path}"
    return f'''<meta name="description" content="{OG_DESC}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="FlyLingo 飛語">
<meta property="og:locale" content="zh_TW">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{OG_TITLE}">
<meta property="og:description" content="{OG_DESC}">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1024">
<meta property="og:image:height" content="1024">
<meta property="og:image:alt" content="FlyLingo 飛語">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{OG_TITLE}">
<meta name="twitter:description" content="{OG_DESC}">
<meta name="twitter:image" content="{OG_IMAGE}">'''


ICON_FILES = ["region-all", "region-cebu", "region-baguio", "region-clark", "region-tarlac", "region-manila",
              "school-room", "school-accommodation", "school-laundry"]


def icon_uris():
    # Same reason as the favicon: the illustrations travel inside the HTML file.
    return {name: "data:image/svg+xml," + quote(" ".join((ROOT / "icons" / f"{name}.svg").read_text().split()), safe=" =:/,.-")
            for name in ICON_FILES}

# Single source of truth for colors: used by the site CSS and the design-system page.
BRAND = [
    ("green", "主色 Primary・飛語綠", "主要按鈕、連結、選取狀態", [
        ("50", "#F4F9F2"), ("100", "#EAF2E7"), ("300", "#9CC392"),
        ("500", "#3A7C30"), ("700", "#2C6124"), ("900", "#1A3A15"),
    ]),
    ("mango", "輔色 Secondary・芒果黃", "精選標籤、標題螢光筆、星星", [
        ("50", "#FFFAEB"), ("100", "#FFF4D1"), ("300", "#FFDB6B"),
        ("500", "#FEC107"), ("700", "#C99400"), ("900", "#7A5A00"),
    ]),
]
NEUTRALS = [
    ("app", "#F4F5F2", "App 背景"),
    ("surface", "#FFFFFF", "白色區塊"),
    ("fill", "#F1F3EF", "輸入框、標籤底"),
    ("line", "#E5E8E2", "分隔線"),
    ("faint", "#8D958A", "最次要文字"),
    ("muted", "#5F6A5C", "說明文字"),
    ("ink", "#1B2119", "主要文字"),
]
ACCENTS = [
    {
        "key": "coral", "name": "珊瑚橘 Coral", "status": "推薦",
        "base": "#C84B2A", "soft": "#FDECE6", "ink": "#A8401F",
        "use": "強度、熱門、限時", "examples": ["斯巴達", "熱門", "限時優惠"],
        "why": "綠色的互補色，最搶眼。只留給「要注意」的資訊，例如斯巴達強度、限時活動。",
    },
    {
        "key": "ocean", "name": "海洋藍 Ocean", "status": "推薦",
        "base": "#2A73AB", "soft": "#E6F0F8", "ink": "#1D5A8A",
        "use": "考場、認證、資訊提示", "examples": ["官方考場", "TESDA 認證", "小提醒"],
        "why": "菲律賓海的冷色，平衡綠與黃兩個暖色。藍色給人可信任的感覺，適合認證與考場。",
    },
    {
        "key": "orchid", "name": "蘭花紫 Orchid", "status": "備選",
        "base": "#8459B3", "soft": "#F2ECF8", "ink": "#6A4394",
        "use": "親子、家庭、青少年", "examples": ["親子", "青少年營", "家長常問"],
        "why": "柔和、偏溫暖的紫，和芒果黃是對比色。只在親子相關內容出現，避免全站變花。",
    },
    {
        "key": "lagoon", "name": "潟湖青 Lagoon", "status": "不建議",
        "base": "#178278", "soft": "#E1F3F1", "ink": "#13675F",
        "use": "不使用", "examples": ["範例"],
        "why": "色相離飛語綠太近，放在一起像兩種綠在打架，使用者分不出哪個才是可以按的。",
    },
]


def accent_vars():
    return "\n".join(
        f"  --{a['key']}: {a['base']}; --{a['key']}-soft: {a['soft']}; --{a['key']}-ink: {a['ink']};"
        for a in ACCENTS if a["status"] != "不建議"
    )


def extract(src):
    data = re.search(r"const DATA = (.*?);\nconst LINE", src, re.S)
    word = re.search(r'<symbol id="mark-word"[^>]*>(.*?)</symbol>', src, re.S)
    star = re.search(r'<symbol id="mark-star"[^>]*>(.*?)</symbol>', src, re.S)
    if not (data and word and star):
        raise SystemExit("flylingo.html is missing DATA or logo symbols")
    return data.group(1), word.group(1), star.group(1)


BASE_CSS = r'''
:root {
  --green: #3A7C30;
  --green-dark: #2C6124;
  --green-soft: #EAF2E7;
  --mango: #FEC107;
  --mango-soft: #FFF4D1;
  --mango-ink: #7A5A00;
__ACCENT_VARS__
  --ink: #1B2119;
  --muted: #5F6A5C;
  --faint: #8D958A;
  --app: #F4F5F2;
  --surface: #FFFFFF;
  --line-gray: #E5E8E2;
  --fill: #F1F3EF;
  --fill-hover: #E7EAE4;
  --r-lg: 20px;
  --r-md: 14px;
  --r-sm: 10px;
  --r-btn: 999px;
  --r-tag: 999px;
  --ring: 0 0 0 0 transparent;
  --shadow-1: 0 1px 2px rgba(27,33,25,.04), 0 4px 14px rgba(27,33,25,.05);
  --shadow-2: 0 2px 6px rgba(27,33,25,.05), 0 16px 36px rgba(27,33,25,.09);
  --head-h: 68px;
  --ease: cubic-bezier(.2,.7,.2,1);
  --sans: 'Noto Sans TC', "微軟正黑體", "Work Sans", sans-serif, serif;
  --serif: var(--sans);
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; -webkit-text-size-adjust: 100%; }
body {
  margin: 0; background: var(--app); color: var(--ink);
  font-family: var(--sans); font-size: 16px; line-height: 1.7;
  -webkit-font-smoothing: antialiased;
}
a { color: var(--green-dark); text-decoration: none; }
a:hover { color: var(--green); }
p { margin: 0; }
ul { margin: 0; }
button { font: inherit; color: inherit; }
:focus-visible { outline: 2px solid var(--green); outline-offset: 3px; border-radius: 6px; }
.skip { position: absolute; left: 12px; top: -48px; background: var(--ink); color: #fff; padding: 8px 12px; z-index: 70; border-radius: 8px; }
.skip:focus { top: 12px; color: #fff; }
.wrap { width: min(1120px, calc(100% - 40px)); margin: 0 auto; }
h1, h2, h3 { margin: 0; line-height: 1.3; font-weight: 600; letter-spacing: 0; }
h1 { font-size: clamp(32px, 4.4vw, 52px); line-height: 1.2; }
h2 { font-size: clamp(22px, 2.4vw, 28px); }
h3 { font-size: 17px; }
.lede { color: var(--muted); font-size: 17px; max-width: 36rem; }
.meta { color: var(--muted); font-size: 14px; }
.num { font-family: var(--serif); font-weight: 600; }
.eyebrow {
  display: inline-flex; align-items: center; gap: 8px; margin-bottom: 14px;
  color: var(--green); font-weight: 600; font-size: 14px; letter-spacing: .06em;
}
.eyebrow::before, .star-mark {
  content: ""; width: 10px; height: 10px; flex: none; background: var(--mango);
  clip-path: polygon(50% 0, 62% 36%, 100% 36%, 69% 57%, 80% 100%, 50% 74%, 20% 100%, 31% 57%, 0 36%, 38% 36%);
}
.hl { background: linear-gradient(var(--mango), var(--mango)) no-repeat 0 88% / 100% .3em; }

/* Surfaces: the only white blocks on the gray app background */
.surface { background: var(--surface); border-radius: var(--r-lg); box-shadow: var(--ring); }

/* Buttons */
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  height: 46px; padding: 0 20px; border: 0; border-radius: var(--r-btn);
  font-weight: 600; font-size: 15px; white-space: nowrap; cursor: pointer;
  transition: background .2s, color .2s, transform .25s var(--ease), box-shadow .25s;
}
.btn svg { flex: none; }
.btn-primary { background: var(--green); color: #fff; box-shadow: 0 6px 16px rgba(58,124,48,.22); }
.btn-primary:hover { background: var(--green-dark); color: #fff; transform: translateY(-1px); box-shadow: 0 10px 22px rgba(58,124,48,.28); }
.btn-quiet { background: var(--fill); color: var(--ink); }
.btn-quiet:hover { background: var(--fill-hover); color: var(--ink); }
.btn-light { background: #fff; color: var(--green-dark); box-shadow: 0 8px 20px rgba(0,0,0,.12); }
.btn-light:hover { color: var(--green-dark); transform: translateY(-1px); }
.btn-sm { height: 38px; padding: 0 14px; font-size: 14px; }
.btn-block { width: 100%; }
.arr { transition: transform .25s var(--ease); }
a:hover > .arr, button:hover > .arr { transform: translateX(3px); }
.link-arrow { display: inline-flex; align-items: center; gap: 6px; font-weight: 600; color: var(--green); }

/* Tags & badges */
.tags { display: flex; flex-wrap: wrap; gap: 6px; }
.tag, .badge {
  display: inline-flex; align-items: center; height: 24px; padding: 0 9px;
  border-radius: var(--r-tag); font-size: 12.5px; font-weight: 500; white-space: nowrap;
}
.tag { background: var(--fill); color: var(--muted); }
.tag.green { background: var(--green-soft); color: var(--green-dark); }
.badge { background: var(--mango); color: var(--ink); font-weight: 600; }
.badge.soft { background: var(--mango-soft); color: var(--mango-ink); }
.badge.gray { background: var(--fill); color: var(--muted); }

/* Header */
header.site {
  position: sticky; top: 0; z-index: 30;
  background: rgba(255,255,255,.88); backdrop-filter: saturate(1.4) blur(14px);
  -webkit-backdrop-filter: saturate(1.4) blur(14px);
  transition: box-shadow .3s;
}
header.site.scrolled { box-shadow: 0 1px 0 var(--line-gray), 0 8px 24px rgba(27,33,25,.05); }
.head { display: flex; align-items: center; gap: 28px; height: var(--head-h); }
.logo-word { width: 104px; height: 51px; display: block; overflow: visible; }
.nav { display: flex; gap: 4px; }
.nav a {
  padding: 6px 12px; border-radius: 999px; color: var(--ink); font-weight: 500; font-size: 15px;
  transition: background .2s, color .2s;
}
.nav a:hover { background: var(--fill); color: var(--ink); }
.nav a[aria-current="page"] { background: var(--green-soft); color: var(--green-dark); }
.head-socials + .head-cta { margin-left: -14px; }
.head-cta { margin-left: auto; }
.menu-btn {
  display: none; margin-left: auto; width: 40px; height: 40px; border: 0; border-radius: 12px;
  background: var(--fill); place-items: center; cursor: pointer;
}
.menu-btn span, .menu-btn span::before, .menu-btn span::after {
  display: block; width: 16px; height: 2px; background: var(--ink); border-radius: 2px;
  transition: transform .25s var(--ease), background .2s; position: relative;
}
.menu-btn span::before, .menu-btn span::after { content: ""; position: absolute; left: 0; }
.menu-btn span::before { top: -5px; }
.menu-btn span::after { top: 5px; }
header.site.open .menu-btn span { background: transparent; }
header.site.open .menu-btn span::before { transform: translateY(5px) rotate(45deg); }
header.site.open .menu-btn span::after { transform: translateY(-5px) rotate(-45deg); }

/* Home */
.section { padding: 28px 0; }
.sec-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; margin-bottom: 16px; }
.sec-head .meta { margin-top: 4px; font-size: 15px; }
.hero {
  position: relative; overflow: hidden; margin-top: 20px; padding: 56px;
  display: grid; grid-template-columns: 1.3fr 1fr; gap: 32px; align-items: center;
}
.hero .lede { margin: 18px 0 30px; }
.row-btns { display: flex; flex-wrap: wrap; gap: 10px; }
.hero-art { position: relative; justify-self: stretch; width: 100%; max-width: none; }
.hero-photo { width: 100%; height: min(52vh, 460px); min-height: 300px; object-fit: cover; border-radius: 16px; display: block; }
.land { fill: var(--green-soft); }
.route { display: block; width: 100%; height: auto; overflow: visible; }
.hero .route {
  position: absolute; right: 12px; bottom: 12px; width: 150px;
  background: rgba(255,255,255,.94); border-radius: 14px; padding: 4px 2px 0;
  box-shadow: var(--shadow-1);
}
.route-draw { fill: none; stroke: #fff; stroke-width: 8; stroke-dasharray: 1 1; stroke-dashoffset: 0; }
.route-line { fill: none; stroke: var(--green); stroke-width: 2.5; stroke-linecap: round; stroke-dasharray: 1 8; }
.port circle { fill: #fff; stroke: var(--green); stroke-width: 3; }
.port.to circle { fill: var(--green); }
.port text { font: 600 13px var(--sans); fill: var(--muted); text-anchor: middle; }
.port .ping { fill: none; stroke: var(--green); stroke-width: 2; opacity: 0; transform-box: fill-box; transform-origin: center; }
.flyer .star { fill: var(--mango); }
.route-chip {
  position: absolute; left: 12px; bottom: 14px; top: auto; display: inline-flex; align-items: center; height: 30px; padding: 0 12px;
  border-radius: 999px; background: var(--mango); color: var(--ink); font-size: 13px; font-weight: 600;
}
.motion .hero-art:not(.fly) .route-draw { stroke-dashoffset: 1; }
.motion .hero-art:not(.fly) .flyer, .motion .hero-art:not(.fly) .route-chip { opacity: 0; }
.motion .hero-art.fly .route-draw { animation: draw 2.2s cubic-bezier(.4,0,.2,1) backwards; }
.motion .hero-art.fly .route-chip { animation: rise .5s var(--ease) 2.1s backwards; }
.motion .hero-art.fly .ping { animation: ping 1.2s ease-out 2.2s 2; }
@keyframes draw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes ping { from { opacity: .8; transform: scale(1); } to { opacity: 0; transform: scale(3.2); } }
.spark { display: none; }
.flow { display: grid; grid-template-columns: repeat(3, 1fr); padding: 8px; }
.flow-item { position: relative; padding: 22px 24px; }
.flow-item .num { color: var(--green); font-size: 15px; display: block; margin-bottom: 6px; }
.flow-item h3 { margin-bottom: 6px; }
.flow-item + .flow-item::before {
  content: ""; position: absolute; left: -4px; top: 30px; width: 8px; height: 8px;
  border-top: 2px solid var(--line-gray); border-right: 2px solid var(--line-gray); transform: rotate(45deg);
}
.cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.school-card {
  display: flex; flex-direction: column; overflow: hidden; color: inherit;
  transition: transform .3s var(--ease), box-shadow .3s var(--ease);
}
.school-card:hover { color: inherit; }
[data-city] { --city: #E4EEF6; --city-ink: #2A73AB; --city-text: #1D5A8A; --city-sun: #FEC107; }
[data-city="碧瑤"] { --city: #E5EEE1; --city-ink: #3A7C30; --city-text: #2C6124; }
[data-city="克拉克"] { --city: #FBF1D4; --city-ink: #A87B00; --city-text: #7A5A00; }
[data-city="克拉克／打拉"] { --city: #F5EFDC; --city-ink: #8C7A3A; --city-text: #6E5E22; }
[data-city="馬尼拉"] { --city: #F8EAE4; --city-ink: #C84B2A; --city-text: #A8401F; --city-sun: #F2A07F; }
.ph {
  position: relative; height: 92px; padding: 14px 16px; overflow: hidden;
  display: flex; flex-direction: column; justify-content: space-between; align-items: flex-start;
  background: var(--city);
}
.ph .city-en { position: relative; font-family: var(--serif); font-size: 24px; font-weight: 600; line-height: 1; color: var(--city-text); }
.city-art {
  position: absolute; right: 0; bottom: 0; width: 240px; height: 100px; pointer-events: none;
  fill: none; stroke: var(--city-ink); stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; opacity: .55;
}
.city-art .sun { fill: var(--city-sun); stroke: none; opacity: .9; }
.city-art .trail { stroke-dasharray: 2 6; }
.city-art .m { transition: transform .8s var(--ease); }
.school-card:hover .city-art .m { transform: translate(-8px, -3px); }
.school-card .ph { height: 128px; justify-content: flex-end; }
.school-card .ph .city-en { font-size: 30px; }
.ph.has-photo { background: #1A3A15; }
.ph-photo { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.ph.has-photo .city-en { color: #fff; text-shadow: 0 1px 8px rgba(0,0,0,.55); }
.school-card .ph.has-photo { height: 168px; }
.badge.photo-note { background: rgba(27,33,25,.62); color: #fff; }
.ph-badges { position: absolute; top: 12px; left: 12px; right: 12px; display: flex; align-items: flex-start; gap: 8px; }
.badge.note { background: rgba(255,255,255,.92); color: var(--green-dark); }
.ph-badges .kind { margin-left: auto; }
.kind {
  display: inline-flex; align-items: center; height: 24px; padding: 0 10px;
  border-radius: var(--r-tag); font-size: 12.5px; font-weight: 600; white-space: nowrap;
  background: var(--green-soft); color: var(--green-dark);
}
.ph .kind { box-shadow: 0 2px 8px rgba(27,33,25,.12); }
.kind[data-kind="斯巴達"] { background: var(--coral); color: #fff; }
.kind[data-kind="半斯巴達"] { background: var(--mango); color: var(--ink); }
.kind[data-kind="親子"] { background: var(--orchid); color: #fff; }
.school-body { padding: 16px 18px 16px; display: flex; flex-direction: column; gap: 4px; flex: 1; }
.school-card h3 { font-size: 18px; margin-bottom: 4px; }
.loc { display: flex; align-items: center; gap: 4px; }
.loc svg { color: var(--faint); flex: none; }
.school-body .tags { padding-top: 4px; }
.hint {
  display: flex; align-items: center; gap: 6px; margin-top: 10px; padding: 7px 10px;
  border-radius: var(--r-sm); background: var(--ocean-soft); color: var(--ocean-ink);
  font-size: 13px; font-weight: 600;
}
.hint svg { flex: none; }
.hint.inline { margin: 0; height: 24px; padding: 0 9px; border-radius: var(--r-tag); font-size: 12.5px; }
.card-foot {
  margin-top: auto; padding-top: 14px; display: flex; justify-content: space-between; align-items: center; gap: 8px;
  color: var(--faint); font-size: 13px;
}
.go { display: grid; place-items: center; color: var(--faint); transition: color .2s, transform .25s var(--ease); }
.school-card:hover .go { color: var(--green); transform: translateX(3px); }
.cards > .empty { grid-column: 1 / -1; }
.list-head { scroll-margin-top: calc(var(--head-h) + 16px); }
.pager { display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 6px; margin-top: 28px; }
.pager button {
  min-width: 40px; height: 40px; padding: 0 12px; border: 0; border-radius: var(--r-btn);
  display: inline-grid; place-items: center; background: var(--surface); box-shadow: var(--ring);
  font-weight: 500; font-size: 15px; color: var(--ink); cursor: pointer;
  transition: background .2s, color .2s, box-shadow .25s, transform .15s;
}
.pager button:hover:not(:disabled):not([aria-current]) { background: var(--green-soft); color: var(--green-dark); }
.pager button:active:not(:disabled) { transform: scale(.94); }
.pager button[aria-current="page"] { background: var(--green); color: #fff; box-shadow: 0 6px 16px rgba(58,124,48,.22); cursor: default; }
.pager button:disabled { opacity: .4; cursor: default; }
.pager .pg-arrow { padding: 0; color: var(--muted); }
.pager .prev svg { transform: rotate(180deg); }
.pager .gap { color: var(--faint); padding: 0 4px; }
.motion .cards.paging > * { animation: rise .45s var(--ease) backwards; }
.motion .cards.paging > :nth-child(3n+2) { animation-delay: .05s; }
.motion .cards.paging > :nth-child(3n) { animation-delay: .1s; }
.essay {
  display: grid; grid-template-columns: 1.35fr .85fr; gap: 16px 28px; align-items: stretch;
}
.essay-main { grid-row: span 3; margin: 0; display: flex; flex-direction: column; }
.essay-side { margin: 0; }
.essay-main img, .essay-side img { width: 100%; display: block; object-fit: cover; border-radius: 4px; }
.essay-main img { flex: 1; height: 280px; min-height: 320px; }
.essay-side img { height: 168px; }
.essay figcaption {
  margin-top: 8px; font-family: "DM Mono", ui-monospace, monospace;
  font-size: 12px; letter-spacing: .04em; color: var(--muted); line-height: 1.5;
}
.essay-copy { padding-top: 4px; }
.essay-copy .kicker {
  font-family: "DM Mono", ui-monospace, monospace; font-size: 12px;
  letter-spacing: .14em; color: var(--green); margin-bottom: 10px;
}
.essay-copy h2 {
  font-family: "Noto Serif TC", "Noto Sans TC", serif; font-weight: 600;
  font-size: clamp(28px, 3vw, 40px); line-height: 1.35; letter-spacing: -.01em;
}
.essay-copy p + p { margin-top: 14px; color: var(--muted); max-width: 36rem; }
.quote-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.quote { margin: 0; padding: 24px; display: flex; flex-direction: column; gap: 18px; }
.quote blockquote { margin: 0; font-size: 15.5px; position: relative; padding-top: 22px; }
.quote blockquote::before {
  content: "\201C"; position: absolute; top: -14px; left: -2px;
  font-family: var(--serif); font-size: 52px; line-height: 1; color: var(--mango);
}
.quote figcaption { margin-top: auto; display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.steps { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; padding: 8px; }
.step {
  display: flex; gap: 12px; padding: 16px; border-radius: var(--r-md); color: inherit;
  transition: background .2s;
}
.step:hover { background: var(--fill); color: inherit; }
.dot {
  width: 32px; height: 32px; flex: none; display: grid; place-items: center; border-radius: 50%;
  background: var(--green-soft); color: var(--green-dark); font-size: 15px;
  transition: background .25s, color .25s, transform .25s var(--ease);
}
.step:hover .dot { background: var(--green); color: #fff; }
.step strong { display: block; font-size: 15px; line-height: 1.45; margin-bottom: 2px; }
.step .meta { font-size: 13px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.ask { padding: 28px; display: grid; grid-template-columns: 1fr 1fr; gap: 36px; align-items: start; }
.ask h2 { margin-bottom: 16px; }
.search {
  position: relative; display: flex; align-items: center; gap: 6px;
  background: var(--fill); border-radius: 999px; padding: 4px 4px 4px 44px;
  transition: background .2s, box-shadow .2s;
}
.search:focus-within { background: #fff; box-shadow: 0 0 0 2px var(--green); }
.search > svg { position: absolute; left: 16px; color: var(--faint); }
.search input {
  flex: 1; min-width: 0; height: 40px; border: 0; background: transparent; outline: none;
  font: inherit; font-size: 15px; color: var(--ink);
}
.search input::placeholder { color: var(--faint); }
.search .btn { height: 38px; }
.hot { display: flex; flex-direction: column; }
.hot a {
  display: flex; justify-content: space-between; align-items: center; gap: 12px;
  padding: 12px 0; color: var(--ink); font-weight: 500;
}
.hot a + a { border-top: 1px solid var(--line-gray); }
.hot a .arr { color: var(--faint); }
.hot a:hover { color: var(--green-dark); }
.hot a:hover .arr { color: var(--green); }
.ask-foot { margin-top: 14px; }
.cta {
  position: relative; overflow: hidden; padding: 36px 40px;
  display: flex; justify-content: space-between; align-items: center; gap: 24px;
  background: var(--green); color: #fff;
}
.cta h2 { color: #fff; margin-bottom: 6px; }
.cta p { color: rgba(255,255,255,.82); }
.cta > * { position: relative; }
footer.site { padding: 36px 0 44px; color: var(--muted); font-size: 14px; }
.foot { display: flex; justify-content: space-between; align-items: center; gap: 24px; flex-wrap: wrap; }
.foot-links { display: flex; flex-direction: column; align-items: flex-end; gap: 14px; }
.foot nav { display: flex; gap: 18px; flex-wrap: wrap; }
.foot nav a { color: var(--muted); }
.foot nav a:hover { color: var(--green); }
.socials { display: flex; gap: 8px; }
.socials a {
  width: 34px; height: 34px; display: grid; place-items: center; border-radius: 50%; color: #fff;
  transition: transform .25s var(--ease), box-shadow .25s var(--ease);
}
.socials a:hover { transform: translateY(-2px); box-shadow: 0 6px 14px rgba(27,33,25,.18); }
.socials .social-threads { background: #000; }
.socials .social-instagram { background: radial-gradient(circle at 30% 107%, #FDF497 0%, #FDF497 5%, #FD5949 45%, #D6249F 60%, #285AEB 90%); }
.socials .social-facebook { background: #1877F2; }
.socials .social-line { background: #06C755; }
.head-socials { margin-left: auto; gap: 6px; }
.head-socials a { width: 32px; height: 32px; }
.foot-socials { display: none; }

/* Footer brand: a star flies over the slogan and lands, then the second phrase gets underlined */
.foot-brand { display: flex; align-items: center; gap: 22px; }
.foot-brand .logo-word { width: 108px; height: 53px; flex: none; }
.foot-copy { position: relative; padding: 26px 0 2px 22px; border-left: 1.5px solid var(--line-gray); }
.slogan { margin: 0; font-size: 19px; font-weight: 700; color: var(--ink); white-space: nowrap; letter-spacing: .02em; }
.slogan em {
  font-style: normal; color: var(--green-dark);
  background: linear-gradient(var(--mango), var(--mango)) no-repeat 0 88% / 100% .32em;
}
.foot-sub { margin: 4px 0 0; font-size: 13px; }
.foot-trail {
  position: absolute; left: 22px; top: 0; width: 250px; height: 28px; overflow: visible;
  fill: none; stroke: var(--mango); stroke-width: 1.6; stroke-linecap: round; stroke-dasharray: 1 6;
}
.trail-star {
  position: absolute; left: 22px; top: 0; width: 18px; height: 18px; fill: var(--mango);
  offset-path: path("M0 24C60-2 176-6 246 14"); offset-distance: 100%; offset-rotate: 0deg;
}
@keyframes fly-in { from { offset-distance: 0%; transform: rotate(-120deg) scale(.6); } to { offset-distance: 100%; transform: none; } }
@keyframes trail-in { from { clip-path: inset(0 100% 0 0); } to { clip-path: inset(0 0 0 0); } }
@keyframes glint { 0%, 86%, 100% { transform: none; } 93% { transform: scale(1.35) rotate(36deg); } }
@keyframes underline { from { background-size: 0 .32em; } to { background-size: 100% .32em; } }
.motion .foot-brand:not(.fly) .trail-star { offset-distance: 0%; opacity: 0; }
.motion .foot-brand:not(.fly) .foot-trail { clip-path: inset(0 100% 0 0); }
.motion .foot-brand:not(.fly) .slogan em { background-size: 0 .32em; }
.motion .foot-brand.fly .trail-star { animation: fly-in 1.3s var(--ease) both, glint 4.5s ease-in-out 1.3s infinite; }
.motion .foot-brand.fly .foot-trail { animation: trail-in 1.3s var(--ease) both; }
.motion .foot-brand.fly .slogan em { animation: underline .7s var(--ease) 1.1s both; }

/* Inner pages */
.page { padding: 32px 0 24px; }
.page-head { margin-bottom: 20px; }
.page-head h1 { font-size: clamp(28px, 3.4vw, 38px); }
.page-head .lede { margin-top: 6px; font-size: 16px; }
.h-sm { font-size: 18px; margin-bottom: 12px; }
.filter-bar { padding: 16px 20px 10px; margin-bottom: 18px; }
.filter-row { display: grid; grid-template-columns: 44px 1fr; gap: 12px; align-items: start; padding: 8px 0; }
.filter-row:first-of-type { margin-top: 8px; }
.filter-label { font-size: 13px; font-weight: 600; color: var(--faint); padding-top: 6px; }
.filters { display: flex; flex-wrap: wrap; gap: 6px; }
.chip {
  height: 34px; padding: 0 14px; border: 0; border-radius: var(--r-tag);
  background: var(--fill); font-size: 14px; color: var(--ink); cursor: pointer;
  transition: background .2s, color .2s, transform .15s;
}
.chip:hover { background: var(--fill-hover); }
.chip:active { transform: scale(.96); }
.chip .n { margin-left: 5px; font-size: 12px; color: var(--faint); }
.chip[aria-pressed="true"] { background: var(--green); color: #fff; }
.chip[aria-pressed="true"] .n { color: rgba(255,255,255,.75); }
.chip.region-chip {
  height: auto; padding: 4px 14px 4px 4px; display: inline-flex; align-items: center; gap: 8px;
  background: #fff; color: #1F3A2E; font-weight: 700;
  box-shadow: inset 0 0 0 1.5px #DDE8D6;
}
.chip.region-chip:hover { background: #fff; }
.region-ico {
  width: 40px; height: 40px; flex: none; display: grid; overflow: hidden; border-radius: 11px;
  background: var(--tint, var(--green-soft));
}
.region-ico img { width: 40px; height: 40px; display: block; }
.chip.region-chip[aria-pressed="true"] { background: var(--region, var(--green)); color: #fff; box-shadow: none; }
.chip.region-chip[aria-pressed="true"] .region-ico { background: #fff; }
.chip.region-chip[aria-pressed="true"] .n { color: rgba(255,255,255,.82); }
.region-row { align-items: center; }
.region-row .filter-label { padding-top: 0; }
.list-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin: 0 4px 14px; }
.list-title { display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; }
.list-title h2 { font-size: 20px; }
.list-title .en { margin-left: 6px; font-family: var(--serif); font-weight: 600; color: var(--green); }
.list-head strong { color: var(--ink); }
.reset { border: 0; background: none; color: var(--green); font-weight: 600; font-size: 14px; cursor: pointer; padding: 4px 0; }
.empty { padding: 32px; text-align: center; display: grid; justify-items: center; gap: 12px; }
.back {
  display: inline-flex; align-items: center; gap: 6px; margin-bottom: 14px;
  color: var(--muted); font-size: 14px; font-weight: 500;
}
.back svg { transform: rotate(180deg); transition: transform .25s var(--ease); }
.back:hover svg { transform: rotate(180deg) translateX(3px); }

/* School detail */
.crumbs { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin-bottom: 14px; font-size: 14px; color: var(--faint); }
.crumbs a { color: var(--muted); }
.crumbs a:hover { color: var(--green); }
.crumbs span[aria-current] { color: var(--ink); font-weight: 500; }
.d-top { overflow: hidden; }
.d-head { padding: 22px 24px; display: flex; align-items: center; gap: 18px; }

/* Gallery */
.gallery { padding: 0 24px 22px; display: grid; gap: 10px; }
.g-stage { position: relative; border-radius: var(--r-md); overflow: hidden; background: var(--fill); }
.g-track {
  display: flex; overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none;
  aspect-ratio: 16 / 7; outline: none;
}
.g-track::-webkit-scrollbar { display: none; }
.g-track:focus-visible { box-shadow: inset 0 0 0 3px var(--green); }
.g-slide {
  flex: 0 0 100%; position: relative; scroll-snap-align: start; scroll-snap-stop: always;
  border: 0; padding: 0; background: none; cursor: zoom-in; overflow: hidden;
}
.g-slide img, .g-thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }
.g-video { cursor: default; }
.g-video iframe, .lb-video iframe { width: 100%; height: 100%; border: 0; display: block; }
.g-ph {
  position: absolute; inset: 0; display: grid; place-items: center; background: var(--city);
}
.g-ph .city-art { width: 62%; height: 80%; right: 4%; bottom: 0; opacity: .45; }
.g-ph-label { position: relative; display: grid; gap: 4px; text-align: center; font-weight: 700; font-size: 22px; color: var(--city-text); }
.g-ph-label small { font-size: 13px; font-weight: 500; opacity: .75; }
.g-play {
  position: absolute; left: 50%; top: 50%; width: 56px; height: 56px; margin: -28px 0 0 -28px; border-radius: 50%;
  display: grid; place-items: center; background: rgba(255,255,255,.92); color: var(--coral); box-shadow: var(--shadow-2);
}
.g-thumb .g-play { width: 30px; height: 30px; margin: -15px 0 0 -15px; }
.g-thumb .g-play svg { width: 14px; height: 14px; }
.g-nav {
  position: absolute; top: 50%; width: 40px; height: 40px; margin-top: -20px; border: 0; border-radius: 50%;
  display: grid; place-items: center; background: rgba(255,255,255,.92); color: var(--ink); cursor: pointer;
  box-shadow: var(--shadow-1); opacity: 0; transition: opacity .2s, transform .2s;
}
.g-nav.prev { left: 12px; } .g-nav.next { right: 12px; }
.g-nav.prev svg { transform: rotate(180deg); }
.g-stage:hover .g-nav, .g-nav:focus-visible { opacity: 1; }
.g-nav:active { transform: scale(.92); }
.g-cap, .g-count {
  position: absolute; bottom: 12px; height: 30px; padding: 0 12px; border-radius: 999px;
  display: inline-flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 600;
}
.g-cap { left: 12px; background: rgba(255,255,255,.92); color: var(--ink); pointer-events: none; }
.g-count { right: 12px; border: 0; background: rgba(20,26,19,.62); color: #fff; cursor: pointer; transition: background .2s; }
.g-count:hover { background: rgba(20,26,19,.8); }
.g-cats { display: flex; flex-wrap: wrap; gap: 6px; }
.g-cats .chip[aria-pressed="true"] { background: var(--green-soft); color: var(--green-dark); box-shadow: none; }
.g-thumbs { display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; }
.g-thumb {
  position: relative; aspect-ratio: 4 / 3; padding: 0; border: 0; border-radius: 10px; overflow: hidden;
  background: var(--fill); cursor: pointer; opacity: .72; transition: opacity .2s, box-shadow .2s;
}
.g-thumb:hover, .g-thumb.active { opacity: 1; }
.g-thumb.active { box-shadow: 0 0 0 2px #fff, 0 0 0 4px var(--green); }
.g-thumb .g-ph-label { font-size: 12px; }
.g-thumb .city-art { width: 90%; }
.g-more {
  position: absolute; inset: 0; display: grid; place-items: center;
  background: rgba(20,26,19,.55); color: #fff; font-size: 18px; font-weight: 700;
}

/* Lightbox */
.lb-open { overflow: hidden; }
.lightbox {
  width: 100vw; height: 100dvh; max-width: none; max-height: none; margin: 0; padding: 16px 24px 20px; border: 0;
  background: #121610; color: #fff; overflow: hidden;
  display: none; grid-template-columns: minmax(0, 1fr); grid-template-rows: auto minmax(0, 1fr) auto auto; gap: 12px;
}
.lightbox[open] { display: grid; }
.lightbox::backdrop { background: rgba(16,20,15,.6); }
.lb-top { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.lb-top p { display: flex; align-items: baseline; gap: 12px; font-size: 15px; }
.lb-count { font-size: 13px; color: rgba(255,255,255,.65); }
.lb-close {
  width: 40px; height: 40px; border: 0; border-radius: 50%; background: rgba(255,255,255,.12); color: #fff;
  font-size: 24px; line-height: 1; cursor: pointer; transition: background .2s;
}
.lb-close:hover { background: rgba(255,255,255,.22); }
.lb-stage { position: relative; min-height: 0; min-width: 0; }
.lb-track { height: 100%; display: flex; overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none; }
.lb-track::-webkit-scrollbar { display: none; }
.lb-slide { flex: 0 0 100%; height: 100%; margin: 0; position: relative; scroll-snap-align: start; scroll-snap-stop: always; display: grid; place-items: center; }
.lb-slide > img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: contain; }
.lb-slide .g-ph { inset: 0 8%; border-radius: var(--r-md); }
.lb-video { width: min(100%, 1100px); aspect-ratio: 16 / 9; }
.lightbox .g-nav { opacity: 1; }
.lb-cap { text-align: center; font-size: 14px; color: rgba(255,255,255,.8); }
.lb-thumbs { display: flex; gap: 8px; overflow-x: auto; justify-content: safe center; padding: 4px; scrollbar-width: none; }
.lb-thumbs .g-thumb { flex: 0 0 88px; }
.lb-thumbs .g-thumb.active { box-shadow: 0 0 0 2px var(--mango); }
.city-tile {
  position: relative; overflow: hidden; width: 112px; height: 80px; flex: none; padding: 10px 12px;
  border-radius: var(--r-md); background: var(--city);
  font-family: var(--serif); font-size: 15px; font-weight: 600; line-height: 1; color: var(--city-text);
}
.city-tile .city-art { width: 100%; height: 100%; opacity: .5; }
.d-id { flex: 1; min-width: 0; display: grid; gap: 4px; }
.d-id h1 { font-size: clamp(24px, 2.8vw, 32px); }
.d-id .tags { margin-top: 6px; }
.share {
  flex: none; align-self: flex-start; display: inline-flex; align-items: center; gap: 6px; height: 36px; padding: 0 12px;
  border: 0; border-radius: var(--r-btn); background: var(--fill); color: var(--muted); font-size: 13px; font-weight: 500; cursor: pointer;
  transition: background .2s, color .2s;
}
.share:hover { background: var(--fill-hover); color: var(--ink); }
.share.done { background: var(--green-soft); color: var(--green-dark); }
.glance { margin-top: 12px; display: grid; grid-template-columns: 1fr 1fr 1.2fr; }
.glance > div { padding: 20px 24px; display: grid; gap: 10px; align-content: start; }
.glance > div + div { box-shadow: inset 1px 0 0 var(--line-gray); }
.glance h2 { font-size: 13px; font-weight: 600; color: var(--faint); letter-spacing: .04em; }
.glance .val { font-size: 17px; font-weight: 600; }
.meter { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; }
.meter i { height: 8px; border-radius: 4px; background: var(--fill); transform-origin: left; }
.meter i.on { background: var(--lvl, var(--green)); }
.motion .glance.in .meter i.on { animation: grow .5s var(--ease) backwards; }
.motion .glance.in .meter i.on:nth-child(2) { animation-delay: .06s; }
.motion .glance.in .meter i.on:nth-child(3) { animation-delay: .12s; }
.motion .glance.in .meter i.on:nth-child(4) { animation-delay: .18s; }
.motion .glance.in .meter i.on:nth-child(5) { animation-delay: .24s; }
@keyframes grow { from { transform: scaleX(0); } to { transform: none; } }
.meter-ends { display: flex; justify-content: space-between; font-size: 12px; color: var(--faint); }
.cover { display: flex; flex-wrap: wrap; gap: 6px; }
.cover span {
  display: inline-flex; align-items: center; gap: 4px; height: 26px; padding: 0 10px; border-radius: var(--r-tag);
  font-size: 13px; font-weight: 500; background: var(--green-soft); color: var(--green-dark);
}
.cover span.off { background: transparent; color: var(--faint); box-shadow: inset 0 0 0 1px var(--line-gray); text-decoration: line-through; }
.fit { list-style: none; padding: 0; display: flex; flex-wrap: wrap; gap: 6px 14px; font-size: 14px; }
.fit li { display: inline-flex; align-items: center; gap: 5px; }
.fit li svg { color: var(--green); flex: none; }
.detail-layout { display: grid; grid-template-columns: 1fr 320px; gap: 20px; align-items: start; margin-top: 20px; }
.detail-main { padding: 0 28px 4px; }
.detail-nav {
  position: sticky; top: var(--head-h); z-index: 5; display: flex; gap: 4px;
  margin: 0 -28px; padding: 12px 24px; background: #fff;
  border-radius: var(--r-lg) var(--r-lg) 0 0; box-shadow: inset 0 -1px 0 var(--line-gray);
}
.detail-nav a {
  padding: 6px 12px; border-radius: 999px; color: var(--muted); font-weight: 500; font-size: 15px;
  transition: background .2s, color .2s;
}
.detail-nav a:hover { color: var(--ink); background: var(--fill); }
.detail-nav a.active { color: var(--green-dark); background: var(--green-soft); }
.detail-section { padding: 26px 0; scroll-margin-top: calc(var(--head-h) + 70px); }
.detail-section + .detail-section { border-top: 1px solid var(--line-gray); }
.detail-section h2 { font-size: 19px; margin-bottom: 14px; }
.detail-section h3 { font-size: 15px; margin: 18px 0 6px; color: var(--muted); }
.facts { display: grid; grid-template-columns: 1fr 1fr; gap: 14px 24px; margin-bottom: 18px; }
.facts span { display: block; font-size: 13px; color: var(--faint); }
.bullets { list-style: none; padding: 0; display: grid; gap: 6px; }
.bullets li { position: relative; padding-left: 18px; }
.bullets li::before { content: ""; position: absolute; left: 2px; top: .7em; width: 6px; height: 6px; border-radius: 50%; background: var(--mango); }
.checks { list-style: none; padding: 0; display: grid; grid-template-columns: 1fr 1fr; gap: 10px 20px; }
.checks li { display: flex; gap: 8px; align-items: flex-start; }
.checks li svg { color: var(--green); flex: none; margin-top: 4px; }
.kv { display: grid; grid-template-columns: 140px 1fr; gap: 12px; align-items: start; padding: 10px 0; }
.kv > span { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--faint); padding-top: 0; }
.kv > span img { width: 40px; height: 40px; flex: none; border-radius: 11px; }
.amen { display: grid; grid-template-columns: repeat(auto-fill, minmax(112px, 1fr)); gap: 8px; }
.amen li {
  list-style: none; display: flex; align-items: center; gap: 8px; padding: 10px 12px;
  border-radius: var(--r-sm); background: var(--fill); font-size: 14px;
}
.amen li svg { color: var(--green); flex: none; }
.amen { padding: 0; margin: 0; }
.amen li small { margin-left: auto; font-size: 11.5px; color: var(--mango-ink); white-space: nowrap; }
.amen li.part { background: var(--mango-soft); }
.amen li.part svg { color: var(--mango-ink); }
.amen li.no { background: transparent; box-shadow: inset 0 0 0 1px var(--line-gray); color: var(--faint); }
.amen li.no svg { color: var(--line-gray); }
.sec-head { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; flex-wrap: wrap; }
.legend { display: flex; gap: 14px; font-size: 12.5px; color: var(--faint); }
.legend i { display: inline-block; width: 10px; height: 10px; border-radius: 3px; margin-right: 5px; vertical-align: -1px; background: var(--fill); }
.legend i.part { background: var(--mango-soft); box-shadow: inset 0 0 0 1px var(--mango); }
.legend i.no { background: transparent; box-shadow: inset 0 0 0 1px var(--line-gray); }
.more-fac { margin-top: 12px; font-size: 14px; color: var(--muted); }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
.chip.sm { height: 30px; padding: 0 12px; font-size: 13.5px; }
.chip-row { display: flex; flex-wrap: wrap; gap: 6px; }
.room-note { margin-top: 10px; font-size: 13px; color: var(--muted); min-height: 1.5em; }
.room-note b { color: var(--green-dark); font-weight: 600; }
.detail-aside { position: sticky; top: calc(var(--head-h) + 16px); display: grid; gap: 12px; }
.aside-cta { padding: 22px; box-shadow: var(--ring), var(--shadow-2); display: grid; gap: 6px; }
.aside-cta .btn { margin-top: 14px; }
.quote { gap: 0; scroll-margin-top: calc(var(--head-h) + 16px); }
.quote.flash { animation: flash 1s var(--ease); }
@keyframes flash { 0%, 100% { box-shadow: var(--ring), var(--shadow-2); } 30% { box-shadow: 0 0 0 3px var(--green-soft), var(--shadow-2); } }
.q-group { margin-top: 14px; display: grid; gap: 6px; }
.q-group > span { font-size: 12.5px; font-weight: 600; color: var(--faint); }
.bubble {
  position: relative; margin-top: 16px; padding: 12px 14px; border-radius: 16px 16px 4px 16px;
  background: var(--green-soft); color: var(--green-dark); font-size: 13.5px; line-height: 1.6; white-space: pre-line;
}
.motion .bubble.pop { animation: pop .3s var(--ease); }
@keyframes pop { from { transform: scale(.97); } to { transform: none; } }
.q-done { margin-top: 8px; font-size: 13px; color: var(--green-dark); text-align: center; min-height: 1.4em; }
.contact { padding: 0 22px; }
.contact summary {
  list-style: none; display: flex; justify-content: space-between; align-items: center;
  padding: 16px 0; font-weight: 600; cursor: pointer;
}
.contact summary::-webkit-details-marker { display: none; }
.contact summary svg { color: var(--faint); transform: rotate(90deg); transition: transform .25s var(--ease); }
.contact[open] summary svg { transform: rotate(-90deg); }
.contact-body { padding-bottom: 18px; display: grid; gap: 6px; font-size: 14.5px; }
.contact-body .meta { margin-bottom: 4px; }
.checked { color: var(--faint); font-size: 13px; padding: 0 6px; }

/* Process */
.phase { padding: 8px 24px; margin-bottom: 14px; scroll-margin-top: calc(var(--head-h) + 16px); }
.phase-head { display: flex; align-items: baseline; gap: 10px; padding: 14px 0 6px; font-size: 18px; font-weight: 600; }
.phase-head .no { color: var(--green); font-weight: 600; font-size: 13px; }
.step-list { list-style: none; padding: 0; margin: 0; }
.step-row {
  display: grid; grid-template-columns: auto 1fr 180px; gap: 16px; align-items: start;
  padding: 16px 0; margin: 0 -12px; padding-left: 12px; padding-right: 12px; border-radius: var(--r-md);
  transition: background .6s; scroll-margin-top: calc(var(--head-h) + 16px);
}
.step-row + .step-row { box-shadow: inset 0 1px 0 var(--line-gray); }
.step-row.focus { background: var(--green-soft); }
.step-row .dot { width: 36px; height: 36px; font-size: 16px; background: var(--green); color: #fff; }
.step-row h3 { font-size: 17px; margin-bottom: 2px; display: flex; align-items: center; gap: 8px; }
.you-line { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin-top: 10px; }
.you-line b { font-size: 13px; font-weight: 600; color: var(--mango-ink); margin-right: 2px; }
.you-line .tag { background: var(--mango-soft); color: var(--mango-ink); }
.get { display: grid; gap: 2px; font-size: 14px; font-weight: 500; padding-top: 2px; }
.get span { font-size: 12.5px; font-weight: 400; color: var(--faint); }
.process-note { margin: -8px 4px 18px; }
.related { padding: 24px 28px; margin-top: 8px; }

/* FAQ */
.page > .search { max-width: 560px; margin-bottom: 24px; background: var(--surface); box-shadow: var(--ring), var(--shadow-1); }
.page > .search:focus-within { box-shadow: 0 0 0 2px var(--green); }
.faq-grid { display: grid; grid-template-columns: .9fr 1.1fr; gap: 20px; align-items: start; }
.hot-box { padding: 20px 24px 12px; }
.cats { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.cat {
  display: flex; justify-content: space-between; align-items: center; gap: 10px;
  padding: 16px 18px; color: var(--ink);
  transition: transform .3s var(--ease), box-shadow .3s var(--ease);
}
.cat:hover { color: var(--ink); }
.cat strong { display: block; font-size: 15px; }
.cat .meta { font-size: 13px; }
.cat-head { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 14px; }
.acc-list { padding: 4px 24px; }
.acc + .acc { border-top: 1px solid var(--line-gray); }
.acc > button {
  width: 100%; display: flex; justify-content: space-between; align-items: center; gap: 16px;
  padding: 18px 0; border: 0; background: none; text-align: left; font-weight: 600; cursor: pointer;
  transition: color .2s;
}
.acc > button:hover, .acc.open > button { color: var(--green-dark); }
.pm { position: relative; width: 24px; height: 24px; flex: none; border-radius: 50%; background: var(--fill); transition: transform .3s var(--ease), background .2s; }
.pm::before, .pm::after { content: ""; position: absolute; left: 7px; top: 11px; width: 10px; height: 2px; border-radius: 2px; background: currentColor; }
.pm::after { transform: rotate(90deg); }
.acc.open .pm { transform: rotate(45deg); background: var(--green-soft); }
.a { display: grid; grid-template-rows: 0fr; transition: grid-template-rows .35s var(--ease); }
.a > div { overflow: hidden; }
.a p { padding-bottom: 18px; color: var(--muted); }
.acc.open .a { grid-template-rows: 1fr; }
.after-acc { margin-top: 16px; }

/* Blog */
[data-tone="mango"] { --city: #FFF5D6; --city-ink: #A87B00; --city-sun: #FEC107; }
[data-tone="blue"] { --city: #E4EEF6; --city-ink: #2A73AB; --city-sun: #FEC107; }
[data-tone="coral"] { --city: #F8EAE4; --city-ink: #C84B2A; --city-sun: #F2A07F; }
.blog-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.post-card { display: flex; flex-direction: column; overflow: hidden; color: inherit; transition: transform .3s var(--ease), box-shadow .3s var(--ease); }
.post-card:hover { color: inherit; }
.post-card:hover .city-art .m { transform: translate(-8px, -3px); }
.cover { position: relative; height: 128px; padding: 14px 16px; overflow: hidden; background: var(--city); flex: none; }
.cover .kind { position: relative; background: #fff; color: var(--city-ink); box-shadow: 0 2px 8px rgba(27,33,25,.08); }
.cover .city-art { width: 300px; height: 125px; opacity: .7; }
.post-body { display: flex; flex-direction: column; gap: 8px; padding: 18px 20px 20px; flex: 1; }
.post-body h2 { font-size: 18px; line-height: 1.5; }
.post-meta { display: inline-flex; align-items: center; gap: 4px; margin-top: auto; padding-top: 4px; font-size: 13px; color: var(--faint); }
.post-card .post-meta svg { width: 16px; height: 16px; transition: transform .25s var(--ease); }
.post-card:hover .post-meta svg { transform: translateX(3px); }
.post-card.feature { grid-column: 1 / -1; flex-direction: row; }
.post-card.feature .cover { width: 46%; height: auto; min-height: 220px; }
.post-card.feature .cover .city-art { width: 380px; height: 158px; }
.post-card.feature .post-body { justify-content: center; padding: 28px 32px; }
.post-card.feature h2 { font-size: 22px; }

.art-head { display: grid; grid-template-columns: 1fr 280px; overflow: hidden; }
.art-head > div:first-child { padding: 32px 36px; }
.art-head h1 { font-size: clamp(24px, 2.8vw, 32px); line-height: 1.4; margin-bottom: 12px; }
.art-head .lede { font-size: 16px; margin-bottom: 14px; }
.art-head .cover { height: auto; }
.art-head .cover .kind { display: none; }
.art-head .cover .city-art { width: 340px; height: 142px; }
.art-layout { display: grid; grid-template-columns: 1fr 260px; gap: 20px; align-items: start; margin-top: 20px; }
.article { padding: 32px 40px 36px; min-width: 0; }
/* WordPress post content: plain tags only, so posts pasted from the editor look right */
.wp-content { font-size: 16px; line-height: 1.9; }
.wp-content > * + * { margin-top: 16px; }
.wp-content h2 {
  font-size: 21px; line-height: 1.5; margin-top: 30px; padding-top: 24px; border-top: 1px solid var(--line-gray);
  scroll-margin-top: calc(var(--head-h) + 16px);
}
.wp-content h2:first-child { border-top: 0; margin-top: 0; }
.wp-content h3 { font-size: 17px; margin-top: 24px; scroll-margin-top: calc(var(--head-h) + 16px); }
.wp-content h2 + *, .wp-content h3 + * { margin-top: 10px; }
.wp-content a { text-decoration: underline; text-underline-offset: 3px; }
.wp-content ul, .wp-content ol { padding-left: 0; list-style: none; display: grid; gap: 6px; }
.wp-content li { position: relative; padding-left: 26px; }
.wp-content ul > li::before {
  content: ""; position: absolute; left: 6px; top: .78em; width: 7px; height: 7px; border-radius: 50%; background: var(--green);
}
.wp-content ol { counter-reset: n; }
.wp-content ol > li { counter-increment: n; }
.wp-content ol > li::before {
  content: counter(n); position: absolute; left: 0; top: .35em; width: 20px; height: 20px; border-radius: 50%;
  display: grid; place-items: center; background: var(--green-soft); color: var(--green-dark); font-size: 12px; font-weight: 700; line-height: 1;
}
.wp-content blockquote {
  margin-left: 0; margin-right: 0; padding: 14px 18px 14px 44px; position: relative;
  border-radius: var(--r-md); background: var(--mango-soft); font-size: 15px;
}
.wp-content blockquote::before {
  content: "!"; position: absolute; left: 14px; top: 16px; width: 20px; height: 20px; border-radius: 50%;
  display: grid; place-items: center; background: var(--mango); color: var(--ink); font-size: 13px; font-weight: 700; line-height: 1;
}
.wp-content blockquote p + p { margin-top: 8px; }
.wp-content blockquote cite { display: block; margin-top: 6px; font-size: 13px; font-style: normal; color: var(--mango-ink); }
.table-scroll, .wp-content figure.wp-block-table { overflow-x: auto; border-radius: var(--r-md); box-shadow: var(--ring); margin-left: 0; margin-right: 0; }
.wp-content table { width: 100%; border-collapse: collapse; font-size: 15px; line-height: 1.7; }
.wp-content th, .wp-content td { padding: 11px 16px; text-align: left; vertical-align: top; }
.wp-content th { background: var(--fill); font-size: 13px; font-weight: 600; color: var(--muted); }
.wp-content td:first-child { font-weight: 600; white-space: nowrap; }
.wp-content td:not(:first-child) { color: var(--muted); }
.wp-content tr + tr td, .wp-content tbody tr:first-child td { border-top: 1px solid var(--line-gray); }
.wp-content figure { margin-left: 0; margin-right: 0; }
.wp-content img { max-width: 100%; height: auto; display: block; border-radius: var(--r-md); }
.wp-content figcaption { margin-top: 8px; font-size: 13px; color: var(--faint); text-align: center; }
.wp-content details { border-top: 1px solid var(--line-gray); }
.wp-content details + details { margin-top: 0; }
.wp-content details:last-of-type { border-bottom: 1px solid var(--line-gray); }
.wp-content summary {
  display: flex; justify-content: space-between; align-items: center; gap: 16px;
  padding: 16px 0; font-weight: 600; cursor: pointer; list-style: none; transition: color .2s;
}
.wp-content summary::-webkit-details-marker { display: none; }
.wp-content summary::after {
  content: "+"; flex: none; width: 24px; height: 24px; border-radius: 50%; display: grid; place-items: center;
  background: var(--fill); font-size: 18px; font-weight: 500; line-height: 1; transition: transform .3s var(--ease), background .2s;
}
.wp-content summary:hover, .wp-content details[open] summary { color: var(--green-dark); }
.wp-content details[open] summary::after { transform: rotate(45deg); background: var(--green-soft); }
.wp-content details > :not(summary) { padding-bottom: 16px; color: var(--muted); }
.cover.has-img { padding: 0; }
.cover.has-img img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.cover.has-img .kind { position: absolute; left: 14px; top: 14px; z-index: 1; }
.art-cta {
  display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap;
  margin-top: 28px; padding: 20px 24px; border-radius: var(--r-md); background: var(--green-soft);
}
.art-cta .h-sm { margin-bottom: 2px; }
.art-aside { position: sticky; top: calc(var(--head-h) + 16px); }
.toc summary { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; font-weight: 600; cursor: pointer; list-style: none; }
.toc summary::-webkit-details-marker { display: none; }
.toc summary svg { color: var(--faint); transform: rotate(90deg); transition: transform .25s var(--ease); }
.toc[open] summary svg { transform: rotate(-90deg); }
.toc nav { display: grid; padding: 0 12px 14px; }
.toc nav a { padding: 7px 10px; border-radius: var(--r-sm); color: var(--muted); font-size: 14px; box-shadow: inset 2px 0 0 var(--line-gray); transition: color .2s, box-shadow .2s, background .2s; }
.toc nav a:hover { color: var(--ink); background: var(--fill); }
.toc nav a.active { color: var(--green-dark); font-weight: 600; box-shadow: inset 2px 0 0 var(--green); }
.more-posts { margin-top: 36px; }

/* Floating LINE (mobile only) */
.float-line {
  display: none; position: fixed; right: 16px; bottom: 16px; z-index: 40;
  height: 50px; padding: 0 18px 0 14px; border-radius: 999px; align-items: center; gap: 8px;
  background: var(--green); color: #fff; font-weight: 600;
  box-shadow: 0 10px 24px rgba(58,124,48,.35);
}
.float-line:hover { color: #fff; }

/* Reveal motion: only when JS + motion are allowed */
@keyframes rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
.motion .rv { opacity: 0; transform: translateY(14px); }
.motion .rv.in { opacity: 1; transform: none; transition: opacity .7s var(--ease), transform .7s var(--ease); }
.motion .rv-group:not(.in) > * { opacity: 0; }
.motion .rv-group.in > * { animation: rise .6s var(--ease) backwards; }
.motion .rv-group.in > :nth-child(2) { animation-delay: .06s; }
.motion .rv-group.in > :nth-child(3) { animation-delay: .12s; }
.motion .rv-group.in > :nth-child(4) { animation-delay: .18s; }
.motion .rv-group.in > :nth-child(5) { animation-delay: .24s; }
.motion .rv-group.in > :nth-child(6) { animation-delay: .30s; }
.motion .rv-group.in > :nth-child(7) { animation-delay: .36s; }
.motion .rv-group.in > :nth-child(8) { animation-delay: .42s; }
.motion .rv-group.in > :nth-child(n+9) { animation-delay: .48s; }

@media (max-width: 900px) {
  .hero { grid-template-columns: 1fr; padding: 40px 32px; }
  .hero-art { display: block; }
  .hero .route, .hero .route-chip { display: none; }
  .hero-photo { height: 240px; min-height: 0; }
  .essay { grid-template-columns: 1fr; }
  .essay-main { grid-row: auto; }
  .essay-main img { min-height: 240px; height: 280px; }
  .cards, .quote-grid { grid-template-columns: 1fr 1fr; }
  .steps { grid-template-columns: 1fr 1fr; }
  .ask, .faq-grid { grid-template-columns: 1fr; }
  .detail-layout { grid-template-columns: 1fr; }
  .detail-aside { position: static; }
  .glance { grid-template-columns: 1fr 1fr; }
  .glance > div:last-child { grid-column: 1 / -1; box-shadow: inset 0 1px 0 var(--line-gray); }
  .art-layout { grid-template-columns: 1fr; }
  .art-aside { position: static; order: -1; }
  .art-head { grid-template-columns: 1fr; }
  .art-head .cover { display: none; }
}
@media (max-width: 760px) {
  :root { --head-h: 60px; }
  .wrap { width: calc(100% - 28px); }
  .logo-word { width: 90px; height: 44px; }
  .nav {
    display: none; position: absolute; top: calc(var(--head-h) - 4px); left: 14px; right: 14px;
    flex-direction: column; gap: 2px; padding: 8px; background: #fff;
    border-radius: var(--r-md); box-shadow: var(--shadow-2);
  }
  .nav a { padding: 12px 14px; border-radius: var(--r-sm); }
  header.site.open .nav { display: flex; }
  .menu-btn { display: grid; }
  .head-cta { display: none; }
  .float-line { display: inline-flex; }
  .hero { padding: 32px 22px; margin-top: 14px; }
  .hero-art { display: block; }
  .hero .lede { font-size: 16px; }
  .flow, .cards, .quote-grid, .steps, .cats { grid-template-columns: 1fr; }
  .flow-item + .flow-item::before { display: none; }
  .ask, .cta, .related { padding: 24px 22px; }
  .cta { flex-direction: column; align-items: flex-start; }
  .sec-head { flex-direction: column; align-items: flex-start; gap: 6px; }
  .filter-row { grid-template-columns: 1fr; gap: 6px; }
  .filter-label { padding-top: 0; }
  .school-card .ph { height: 112px; }
  .school-card .ph.has-photo { height: 148px; }
  .detail-main { padding-left: 20px; padding-right: 20px; }
  .detail-nav { margin: 0 -20px; padding: 10px 16px; overflow-x: auto; }
  .facts { grid-template-columns: 1fr; }
  .d-head { padding: 18px; gap: 14px; flex-wrap: wrap; }
  .gallery { padding: 0 14px 16px; }
  .g-track { aspect-ratio: 4 / 3; }
  .g-nav { display: none; }
  .g-thumbs { grid-template-columns: none; grid-auto-flow: column; grid-auto-columns: 26%; overflow-x: auto; scrollbar-width: none; padding: 4px; margin: -4px; }
  .g-cats { flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none; }
  .g-cats .chip { flex: none; }
  .d-top .city-tile { display: none; }
  .g-ph-label { font-size: 18px; }
  .lightbox { padding: 12px 10px 16px; }
  .lightbox .g-nav { display: none; }
  .lb-slide .g-ph { inset: 10% 0; }
  .lb-thumbs .g-thumb { flex-basis: 64px; }
  .city-tile { width: 84px; height: 60px; font-size: 13px; padding: 8px 10px; }
  .share { width: 36px; padding: 0; justify-content: center; }
  .share span { display: none; }
  .glance { grid-template-columns: 1fr; }
  .glance > div + div { box-shadow: inset 0 1px 0 var(--line-gray); }
  .checks { grid-template-columns: 1fr; }
  .kv { grid-template-columns: 1fr; gap: 6px; }
  .phase { padding: 4px 18px; }
  .step-row { grid-template-columns: auto 1fr; }
  .step-row .get { grid-column: 2; display: flex; gap: 6px; padding: 0; }
  .acc-list { padding: 0 18px; }
  .blog-grid { grid-template-columns: 1fr; }
  .post-card.feature { flex-direction: column; }
  .post-card.feature .cover { width: auto; min-height: 0; height: 128px; }
  .post-card.feature .cover .city-art { width: 300px; height: 125px; }
  .post-card.feature .post-body { padding: 18px 20px 20px; }
  .post-card.feature h2 { font-size: 18px; }
  .art-head > div:first-child { padding: 24px 22px; }
  .article { padding: 22px 22px 24px; }
  .wp-content td:first-child { white-space: normal; }
  .foot-links { align-items: flex-start; }
  footer.site { padding-bottom: 96px; }
  .head-socials { display: none; }
  .foot-socials { display: flex; }
  .foot-brand { flex-direction: column; align-items: flex-start; gap: 6px; }
  .foot-copy { padding-left: 0; border-left: 0; }
  .foot-trail, .trail-star { left: 0; }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
'''

SOFT_CSS = r'''
/* V1 Soft: borderless white blocks, shadow only when lifted */
.school-card:hover, .cat:hover, .post-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-2); }
@keyframes twinkle { 0%, 100% { opacity: 0; transform: scale(.4) rotate(0); } 50% { opacity: 1; transform: scale(1) rotate(45deg); } }
.spark {
  display: block; position: absolute; left: var(--x); top: var(--y); width: var(--s, 12px); height: var(--s, 12px);
  background: var(--mango); opacity: 0;
  clip-path: polygon(50% 0, 60% 40%, 100% 50%, 60% 60%, 50% 100%, 40% 60%, 0 50%, 40% 40%);
  animation: twinkle 3.2s ease-in-out infinite; animation-delay: var(--d, 0s);
}
.cta .spark { background: rgba(254,193,7,.9); }
@keyframes ring { from { box-shadow: 0 10px 24px rgba(58,124,48,.35), 0 0 0 0 rgba(58,124,48,.45); } to { box-shadow: 0 10px 24px rgba(58,124,48,.35), 0 0 0 16px rgba(58,124,48,0); } }
.motion .float-line { animation: ring 1.6s ease-out 2s 2; }
'''

CRISP_CSS = r'''
/* V2 Crisp: hairline gray edges, tighter corners, green edge on hover */
:root {
  --app: #EEF0EB;
  --r-lg: 12px; --r-md: 8px; --r-sm: 6px; --r-btn: 8px; --r-tag: 6px;
  --ring: 0 0 0 1px var(--line-gray);
}
.school-card:hover, .cat:hover, .post-card:hover {
  box-shadow: 0 0 0 1px var(--green), var(--shadow-1);
}
.nav { gap: 22px; }
.nav a { position: relative; padding: 6px 0; border-radius: 0; background: none !important; }
.nav a::after {
  content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 2px; border-radius: 2px;
  background: var(--green); transform: scaleX(0); transform-origin: left; transition: transform .35s var(--ease);
}
.nav a:hover::after { transform: scaleX(.35); }
.nav a[aria-current="page"] { color: var(--green-dark); }
.nav a[aria-current="page"]::after { transform: scaleX(1); }
.detail-nav { gap: 22px; }
.detail-nav a { position: relative; padding: 6px 0; border-radius: 0; background: none !important; }
.detail-nav a::after {
  content: ""; position: absolute; left: 0; right: 0; bottom: -12px; height: 2px;
  background: var(--green); transform: scaleX(0); transform-origin: left; transition: transform .35s var(--ease);
}
.detail-nav a.active::after { transform: scaleX(1); }

.steps { gap: 0; }
.step { border-radius: var(--r-md); }
.pm { border-radius: 6px; }

.progress {
  position: fixed; left: 0; right: 0; top: 0; height: 2px; z-index: 60; pointer-events: none;
  background: linear-gradient(90deg, var(--green), var(--mango));
  transform: scaleX(0); transform-origin: left;
}
@keyframes sweep { from { background-size: 0 .3em; } to { background-size: 100% .3em; } }
.motion .hl { animation: sweep .9s var(--ease) .35s backwards; }
.cta::after {
  content: ""; position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(105deg, transparent 40%, rgba(255,255,255,.12) 50%, transparent 60%);
  transform: translateX(-100%); transition: transform 1s var(--ease);
}
.cta:hover::after { transform: translateX(100%); }
'''

VARIANTS = [
    {
        "file": "flylingo-v1-soft.html",
        "theme": "soft",
        "label": "V1 Soft",
        "css": SOFT_CSS,
        "extra": "",
    },
    {
        "file": "flylingo-v2-crisp.html",
        "theme": "crisp",
        "label": "V2 Crisp",
        "css": CRISP_CSS,
        "extra": '<div class="progress" aria-hidden="true"></div>',
    },
]

LINE_ICON = '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 4C7 4 3.5 7.1 3.5 11c0 3.5 3 6.4 7.1 6.9.3.1.6.2.7.5l.5 1.8c.1.3.4.3.6.1l2.2-1.4c.2-.1.4-.2.7-.2 3.6-.2 6.2-2.9 6.2-6.7C21.5 7.1 17 4 12 4z"/></svg>'
ARROW = '<svg class="arr" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
SEARCH_ICON = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="m20 20-4-4"/></svg>'

# Brand glyphs (white on each brand's colour, see .social-* in CSS).
SOCIAL_LINKS = [
    ("threads", "Threads", "https://www.threads.com/@sailingo2026",
     '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.19 24h-.01c-3.58-.02-6.33-1.2-8.18-3.51C2.35 18.44 1.5 15.59 1.47 12v-.02c.03-3.58.88-6.43 2.53-8.48C5.85 1.2 8.6.02 12.18 0h.01c2.75.02 5.04.73 6.83 2.1 1.68 1.29 2.86 3.13 3.51 5.47l-2.04.57c-1.1-3.96-3.9-5.99-8.3-6.02-2.91.02-5.11.94-6.54 2.72C4.31 6.5 3.62 8.91 3.59 12c.03 3.09.72 5.5 2.06 7.16 1.43 1.78 3.63 2.7 6.54 2.72 2.62-.02 4.36-.63 5.8-2.05 1.65-1.61 1.62-3.59 1.09-4.8-.31-.71-.87-1.3-1.63-1.75-.19 1.35-.62 2.45-1.28 3.27-.89 1.1-2.14 1.7-3.73 1.79-1.2.07-2.36-.22-3.26-.8-1.06-.69-1.68-1.74-1.75-2.96-.07-1.19.41-2.29 1.33-3.08.88-.76 2.12-1.21 3.58-1.29a13.85 13.85 0 0 1 3.02.14c-.13-.74-.38-1.33-.75-1.76-.51-.59-1.31-.88-2.36-.89h-.03c-.84 0-1.99.23-2.72 1.32L7.73 7.85c.98-1.45 2.57-2.26 4.48-2.26h.04c3.2.02 5.1 1.98 5.29 5.39l.32.14c1.49.7 2.58 1.76 3.15 3.07.8 1.82.87 4.79-1.55 7.16-1.85 1.81-4.09 2.63-7.28 2.65Zm1-11.69c-.24 0-.49.01-.74.02-1.84.1-2.98.95-2.92 2.14.07 1.26 1.45 1.84 2.78 1.77 1.23-.07 2.82-.54 3.09-3.71a10.5 10.5 0 0 0-2.21-.22Z"/></svg>'),
    ("instagram", "Instagram", "https://www.instagram.com/sailingo2026",
     '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.4" cy="6.6" r="1.1" fill="currentColor" stroke="none"/></svg>'),
    ("facebook", "Facebook", "https://www.facebook.com/share/1E7bGA2M6w",
     '<svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M13.5 21v-7.6h2.6l.4-3h-3V8.5c0-.9.3-1.5 1.5-1.5h1.6V4.3c-.3 0-1.2-.1-2.3-.1-2.3 0-3.9 1.4-3.9 4V10.4H7.8v3h2.6V21z"/></svg>'),
    ("line", "官方 LINE", "https://lin.ee/oDiSotr", LINE_ICON),
]


def socials(skip=()):
    return "".join(
        f'<a class="social-{key}" href="{url}" target="_blank" rel="noopener" aria-label="{label}">{svg}</a>'
        for key, label, url, svg in SOCIAL_LINKS if key not in skip)

TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-Hant" data-theme="__THEME__">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FlyLingo 飛語｜從語言出發，飛向世界</title>
__OG__
__FAVICON__
<!--
  FlyLingo 飛語原型（__LABEL__ 設計版本）。雙擊用瀏覽器開啟即可。
  由 _build_redesign.py 從 flylingo.html 產生，要改內容請改原始資料後重新產生。

  以後要換的地方：
  - 常見問題：改 _build_redesign.py 的 FAQ。費用、簽證、出發這三類如果規定有更新，改這裡。
  - 部落格文章：改 _build_redesign.py 的 ARTICLES
-->
<script>if (!matchMedia("(prefers-reduced-motion: reduce)").matches && "IntersectionObserver" in window) document.documentElement.classList.add("motion");</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Noto+Sans+TC:wght@400;500;600;700&family=Noto+Serif+TC:wght@600&family=Work+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
__BASE_CSS__
__VARIANT_CSS__
</style>
</head>
<body>
__EXTRA__
<a class="skip" href="#main">跳到內容</a>
<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">
  <symbol id="mark-word" viewBox="160 116 1040 510">__WORD__</symbol>
  <symbol id="mark-star" viewBox="155 115 760 800">__STAR__</symbol>
</svg>
<header class="site">
  <div class="wrap head">
    <a href="#home" aria-label="FlyLingo 飛語首頁">
      <svg class="logo-word" viewBox="0 0 1040 510" role="img" aria-label="FlyLingo 飛語"><use href="#mark-word"/></svg>
    </a>
    <nav class="nav" id="nav" aria-label="主選單">
      <a href="#schools" data-nav="schools">學校</a>
      <a href="#process" data-nav="process">代辦流程</a>
      <a href="#faq" data-nav="faq">常見問題</a>
      <a href="#blog" data-nav="blog">部落格</a>
    </nav>
    <button class="menu-btn" id="menu-btn" type="button" aria-expanded="false" aria-controls="nav" aria-label="選單"><span></span></button>
    <div class="socials head-socials" aria-label="社群">__HEAD_SOCIALS__</div>
    <a class="btn btn-primary btn-sm head-cta" href="https://lin.ee/oDiSotr" target="_blank" rel="noopener">__LINE_ICON__LINE 諮詢</a>
  </div>
</header>
<main id="main">
  <section data-view="home">
    <div class="wrap">
      <div class="surface hero rv">
        <div>
          <p class="eyebrow">菲律賓語言學校代辦</p>
          <h1>從語言出發，<br><span class="hl">飛向世界</span></h1>
          <p class="lede">先了解你的目標、週數和預算，再幫你挑學校、辦報名。住宿、接機和到校後的聯絡窗口，出發前都會跟你確認好。</p>
          <div class="row-btns">
            <a class="btn btn-primary" href="https://lin.ee/oDiSotr" target="_blank" rel="noopener">__LINE_ICON__加 LINE 諮詢</a>
            <a class="btn btn-quiet" href="#schools">看 43 個校區__ARROW__</a>
          </div>
        </div>
        <div class="hero-art" id="hero-route">
          <img class="hero-photo" src="images/editorial/cebu-palms.jpg" alt="宿霧海岸，椰子樹和船">
          <svg class="route" viewBox="0 0 300 300" role="img" aria-label="從台北直飛菲律賓，約 2 到 3 小時">
            <defs>
              <mask id="route-mask" maskUnits="userSpaceOnUse" x="0" y="0" width="300" height="290">
                <path class="route-draw" d="__ROUTE__" pathLength="1"/>
              </mask>
              <linearGradient id="route-trail" x1="0" x2="1">
                <stop offset="0" stop-color="#FEC107" stop-opacity="0"/>
                <stop offset="1" stop-color="#FEC107"/>
              </linearGradient>
            </defs>
            <path class="land" d="M62 34C71 41 71 61 63 82C57 89 50 80 50 66C50 50 54 39 62 34Z"/>
            <path class="land" d="M200 194C214 190 226 203 223 219C229 231 233 246 225 257C216 251 208 238 202 227C195 215 192 202 200 194ZM234 266C241 263 248 268 245 275C240 279 233 276 234 266ZM206 268C212 264 218 268 216 275C212 279 205 276 206 268ZM222 280C229 277 236 282 233 289C228 292 221 289 222 280Z"/>
            <path class="route-line" d="__ROUTE__" mask="url(#route-mask)"/>
            <g class="port"><circle cx="56" cy="58" r="6"/><text x="56" y="22">台北 TPE</text></g>
            <g class="port to"><circle class="ping" cx="214" cy="236" r="6"/><circle cx="214" cy="236" r="6"/><text x="190" y="241" style="text-anchor:end">菲律賓</text></g>
            <g class="flyer" transform="translate(214 236) rotate(132)">
              <line x1="-42" y1="0" x2="-8" y2="0" stroke="url(#route-trail)" stroke-width="4" stroke-linecap="round"/>
              <path class="star" d="M0-11L3.2-3.5L11-3.4L4.9 1.6L7 9.2L0 4.8L-7 9.2L-4.9 1.6L-11-3.4L-3.2-3.5Z"/>
            </g>
          </svg>
          <p class="route-chip">直飛約 2–3 小時</p>
        </div>
      </div>
    </div>

    <div class="wrap section">
      <div class="sec-head rv"><h2>從選校到上課，飛語幫你做這三件事</h2></div>
      <div class="surface flow rv-group">
        <article class="flow-item"><span class="num">01</span><h3>選校</h3><p class="meta">城市、課程、管理強度和住宿一起比較，不會一次給你一長串學校。</p></article>
        <article class="flow-item"><span class="num">02</span><h3>代辦</h3><p class="meta">報名、文件、付款、機票和接機分成八個步驟，每一步誰負責都寫清楚。</p></article>
        <article class="flow-item"><span class="num">03</span><h3>在當地</h3><p class="meta">入住、上課到結業，遇到問題都有固定窗口可以找。</p></article>
      </div>
    </div>

    <div class="wrap section">
      <div class="sec-head rv">
        <div><h2>六種類型的學校</h2><p class="meta">這不是排名，是讓你快速看出各類學校的差別。</p></div>
        <a class="link-arrow" href="#schools">看全部 43 個校區__ARROW__</a>
      </div>
      <div class="cards rv-group" id="featured-cards"></div>
    </div>

    <div class="wrap section">
      <div class="essay rv">
        <figure class="essay-main">
          <img src="images/editorial/cebu-shore.jpg" alt="宿霧白沙岸和小屋">
          <figcaption>CEB · 宿霧海岸</figcaption>
        </figure>
        <div class="essay-copy">
          <p class="kicker">在當地的一天</p>
          <h2>語言發生在點餐、看路牌、跟室友說話的時候。</h2>
          <p>先選城市，再看管理有多嚴。宿霧靠海、學校選擇多；碧瑤比較涼，適合想專心讀書的人；克拉克校園大，外師課比較好找。這裡的照片是城市風景，用來感受環境，不是某一間學校的校園。</p>
        </div>
        <figure class="essay-side">
          <img src="images/editorial/baguio-path.jpg" alt="碧瑤林蔭路">
          <figcaption>BAG · 碧瑤林蔭</figcaption>
        </figure>
        <figure class="essay-side">
          <img src="images/editorial/cebu-city.jpg" alt="宿霧市夜景">
          <figcaption>CEB · 宿霧市</figcaption>
        </figure>
      </div>
    </div>

    <div class="wrap section">
      <div class="sec-head rv"><h2>諮詢時，我們會先問這三件事</h2></div>
      <div class="quote-grid rv-group">
        <article class="surface quote">
          <h3>上課節奏</h3>
          <p>一天上幾堂、週末能不能出去。這兩件事先講清楚，再決定週數和學校。我們會先給你三間以內，不會一次給你一長串。</p>
        </article>
        <article class="surface quote">
          <h3>管理方式</h3>
          <p>先看門禁和晚自習，再看環境照片。接機日期確認之後，再訂機票。</p>
        </article>
        <article class="surface quote">
          <h3>到了找誰</h3>
          <p>誰去接機、宿舍幾個人一間、有事找哪個窗口。這些出發前會跟你確認。</p>
        </article>
      </div>
    </div>

    <div class="wrap section">
      <div class="sec-head rv">
        <div><h2>出發前的八個步驟</h2><p class="meta">每一步要準備什麼、完成後拿到什麼，先看清楚。</p></div>
        <a class="link-arrow" href="#process">看完整流程__ARROW__</a>
      </div>
      <div class="surface steps rv-group" id="home-steps"></div>
    </div>

    <div class="wrap section">
      <div class="surface ask rv">
        <div>
          <h2>有問題嗎？先搜尋看看</h2>
          <form class="search" id="home-search" role="search">
            __SEARCH_ICON__
            <input id="home-q" name="q" placeholder="簽證、費用、住宿、斯巴達…" aria-label="搜尋問題">
            <button class="btn btn-primary btn-sm" type="submit">搜尋</button>
          </form>
          <p class="ask-foot"><a class="link-arrow" href="#faq">看全部 10 個分類__ARROW__</a></p>
        </div>
        <div>
          <p class="meta" style="margin-bottom:4px">大家最常問</p>
          <div class="hot" id="home-hot"></div>
        </div>
      </div>
    </div>

    <div class="wrap section">
      <div class="surface cta rv">
        <span class="spark" style="--x:58%;--y:22%;--d:.4s" aria-hidden="true"></span>
        <span class="spark" style="--x:66%;--y:70%;--s:8px;--d:1.8s" aria-hidden="true"></span>
        <div>
          <h2>還沒決定學校？先跟我們聊聊</h2>
          <p>告訴我們目標、週數和預算，就能開始幫你挑。</p>
        </div>
        <a class="btn btn-light" href="https://lin.ee/oDiSotr" target="_blank" rel="noopener">__LINE_ICON__加 LINE 諮詢</a>
      </div>
    </div>
  </section>

  <section data-view="schools" hidden>
    <div class="wrap page">
      <div class="page-head rv">
        <h1>43 個校區</h1>
        <p class="lede">可以直接搜尋校名或城市，再用條件篩選。學費會依週數和房型變動，最新報價請用 LINE 詢問。</p>
      </div>
      <div class="surface filter-bar rv">
        <form class="search" id="school-search" role="search">
          __SEARCH_ICON__
          <input id="school-q" name="q" placeholder="搜尋學校、城市或課程，例如 CIA、碧瑤、雅思" autocomplete="off" aria-label="搜尋學校、城市或課程">
        </form>
        <div class="filter-row region-row"><span class="filter-label">城市</span><div class="filters" id="city-filters" role="group" aria-label="城市"></div></div>
        <div class="filter-row"><span class="filter-label">課程</span><div class="filters" id="course-filters" role="group" aria-label="課程"></div></div>
        <div class="filter-row"><span class="filter-label">類型</span><div class="filters" id="style-filters" role="group" aria-label="學校類型"></div></div>
      </div>
      <div class="list-head">
        <div class="list-title"><h2 id="list-title">全部校區</h2><p class="meta" id="school-count" aria-live="polite"></p></div>
        <button class="reset" id="filter-reset" type="button" hidden>清除條件</button>
      </div>
      <div class="cards" id="school-cards"></div>
      <nav class="pager" id="school-pager" aria-label="學校清單分頁"></nav>
    </div>
  </section>

  <section data-view="school" hidden>
    <div class="wrap page" id="school-detail"></div>
  </section>

  <section data-view="process" hidden>
    <div class="wrap page">
      <div class="page-head rv">
        <h1>代辦流程：四個階段、八個步驟</h1>
        <p class="lede">你要做的是說出需求、做決定、照清單準備；聯絡學校、整理文件和安排接機，由飛語處理。</p>
      </div>
      <div id="process-steps"></div>
      <div class="surface related">
        <h2 class="h-sm">和流程有關的常見問題</h2>
        <div class="hot">
          <a href="#faq/agency"><span>找代辦和自己報名差在哪？</span>__ARROW__</a>
          <a href="#faq/cost"><span>費用要怎麼估？</span>__ARROW__</a>
          <a href="#faq/visa"><span>SSP 和 eTravel 是什麼？要自己辦嗎？</span>__ARROW__</a>
        </div>
      </div>
    </div>
  </section>

  <section data-view="faq" hidden>
    <div class="wrap page">
      <div class="page-head rv">
        <h1>常見問題</h1>
        <p class="lede">依主題整理大家最常問的問題。找不到答案，可以直接用 LINE 問我們。</p>
      </div>
      <form class="search" id="faq-search" role="search">
        __SEARCH_ICON__
        <input id="faq-q" name="q" placeholder="輸入關鍵字" aria-label="搜尋問題">
        <button class="btn btn-primary btn-sm" type="submit">搜尋</button>
      </form>
      <div id="faq-body"></div>
    </div>
  </section>

  <section data-view="blog" hidden>
    <div class="wrap page">
      <div class="page-head rv">
        <h1>出發前，先讀這幾篇</h1>
        <p class="lede">行李怎麼帶、城市怎麼選、管理強度怎麼挑，出發前常見的問題整理在這裡。</p>
      </div>
      <div class="blog-grid rv-group" id="blog-list"></div>
    </div>
  </section>

  <section data-view="article" hidden>
    <div class="wrap page" id="article-body"></div>
  </section>
</main>
<footer class="site">
  <div class="wrap foot">
    <div class="foot-brand" id="foot-brand">
      <svg class="logo-word" viewBox="0 0 1040 510" role="img" aria-label="FlyLingo 飛語"><use href="#mark-word"/></svg>
      <div class="foot-copy">
        <svg class="foot-trail" viewBox="0 0 250 28" aria-hidden="true"><path d="M0 24C60-2 176-6 246 14"/></svg>
        <svg class="trail-star" viewBox="-11 -11 22 22" aria-hidden="true"><path d="M0-11L3.2-3.5L11-3.4L4.9 1.6L7 9.2L0 4.8L-7 9.2L-4.9 1.6L-11-3.4L-3.2-3.5Z"/></svg>
        <p class="slogan">從語言出發，<em>飛向世界。</em></p>
        <p class="foot-sub">菲律賓語言學校代辦，從選校到結業都有人協助。</p>
      </div>
    </div>
    <div class="foot-links">
      <nav aria-label="頁尾">
        <a href="#schools">學校</a>
        <a href="#process">代辦流程</a>
        <a href="#faq">常見問題</a>
        <a href="#blog">部落格</a>
      </nav>
      <div class="socials foot-socials" aria-label="社群">__FOOT_SOCIALS__</div>
    </div>
  </div>
</footer>
<a class="float-line" href="https://lin.ee/oDiSotr" target="_blank" rel="noopener" aria-label="官方 LINE 諮詢">__LINE_ICON__LINE 諮詢</a>
<script>
const DATA = __DATA__;
const LINE = DATA.line;
// LINE 官方帳號 ID（例如 "@flylingo"）。填了之後詢問單會直接帶入訊息，不用複製貼上。
const LINE_OA_ID = "";
const LINE_ICON = `__LINE_ICON__`;
const ARROW = `__ARROW__`;
const CHEV = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 6 6 6-6 6"/></svg>`;
const BACK = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>`;
const CITY_LABEL = { "克拉克／打拉": "打拉" };
const state = { city: "全部", course: "全部", kind: "全部", q: "", page: 1 };
const PAGE_SIZE = 9;

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function isUrl(s) { return /^https?:\/\//i.test(s || ""); }
function schoolById(id) { return DATA.schools.find((s) => s.id === id); }
function faqById(id) { return DATA.faq.find((c) => c.id === id); }
function cityName(c) { return CITY_LABEL[c] || c; }
function lineBtn(label, cls = "btn btn-primary") {
  return `<a class="${cls}" href="${esc(LINE)}" target="_blank" rel="noopener">${LINE_ICON}${esc(label)}</a>`;
}

/* Reveal-on-scroll and scroll-spy helpers */
const io = document.documentElement.classList.contains("motion")
  ? new IntersectionObserver((entries) => entries.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
    }), { rootMargin: "0px 0px -6% 0px" })
  : null;
function observeReveal() {
  if (!io) return;
  document.querySelectorAll(".rv:not(.in), .rv-group:not(.in)").forEach((el) => io.observe(el));
}
(function footBrand() {
  const el = document.getElementById("foot-brand");
  if (!io || !el) return;
  const fly = () => { el.classList.remove("fly"); void el.offsetWidth; el.classList.add("fly"); };
  new IntersectionObserver((entries, obs) => {
    if (entries[0].isIntersecting) { fly(); obs.disconnect(); }
  }, { threshold: .6 }).observe(el);
  el.addEventListener("mouseenter", () => { if (el.classList.contains("fly")) fly(); });
})();
let spy = null;
let spyPinned = false;
function stopSpy() {
  if (spy) window.removeEventListener("scroll", spy);
  spy = null;
  spyPinned = false;
}
function pinSpy() {
  spyPinned = true;
}
["wheel", "touchmove", "keydown"].forEach((type) =>
  window.addEventListener(type, () => { if (spyPinned) { spyPinned = false; if (spy) spy(); } }, { passive: true }));
function scrollSpy(targets, onActive, offset) {
  stopSpy();
  if (!targets.length) return;
  let last = "";
  spy = () => {
    if (spyPinned) return;
    let cur = targets[0];
    targets.forEach((t) => { if (t.getBoundingClientRect().top <= offset) cur = t; });
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2) cur = targets[targets.length - 1];
    if (cur.id !== last) { last = cur.id; onActive(cur.id); }
  };
  window.addEventListener("scroll", spy, { passive: true });
  spy();
}

const PIN = `<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2.5a7 7 0 0 0-7 7c0 5 7 12 7 12s7-7 7-12a7 7 0 0 0-7-7zm0 9.5a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5z"/></svg>`;
const CAP = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m12 4 10 5-10 5L2 9z"/><path d="M6 11v5c3 2 9 2 12 0v-5"/></svg>`;
const KIND_SHOWN = ["斯巴達", "半斯巴達", "親子"];

function kindPill(s) {
  return KIND_SHOWN.includes(s.kind) ? `<span class="kind" data-kind="${esc(s.kind)}">${esc(s.kind)}</span>` : "";
}

function examCenters(s) {
  const a = s.accreditation || "";
  const out = [];
  if (/IDP IELTS|British Council IELTS|IELTS 考場/.test(a)) out.push("IELTS");
  if (/ETS TOEIC|TOEIC 官方考場|TOEIC 考場/.test(a)) out.push("TOEIC");
  return out;
}

const CITY_ART = __CITY_ART__;
function cityArt(city, viewBox = "0 0 240 100") {
  return `<svg class="city-art" viewBox="${viewBox}" preserveAspectRatio="xMaxYMax meet" aria-hidden="true">${CITY_ART[city] || CITY_ART["宿霧"]}</svg>`;
}

// City scenery used until a school sends its own photos. Not the campus.
// Credits stay in images/editorial/CREDITS.txt; the page does not name the source.
const CARD_PHOTO = {
  "cia-mactan-campus": "images/editorial/cebu-palms.jpg",
  "ev-academy-main-campus": "images/editorial/cebu-city.jpg",
  "cebu-blue-ocean-academy-main-campus": "images/editorial/cebu-shore.jpg",
  "pines-main-campus": "images/editorial/baguio-path.jpg",
  "cij-academy-liloan-campus": "images/editorial/cebu-shore.jpg"
};
function cardPhoto(s) {
  const own = (s.photos || []).find((p) => p.src);
  return own ? own.src : (CARD_PHOTO[s.id] || "");
}
function cardHTML(s, note) {
  const tags = s.strengths.filter((p) => p.length <= 14).slice(0, 3).map((t) => `<span class="tag">${esc(t)}</span>`).join("");
  const exams = examCenters(s);
  const own = (s.photos || []).some((p) => p.src);
  const photo = cardPhoto(s);
  return `<a class="surface school-card" href="#school/${esc(s.id)}">
    <div class="ph${photo ? " has-photo" : ""}" data-city="${esc(s.city)}">
      ${photo ? `<img class="ph-photo" src="${esc(photo)}" alt="">` : cityArt(s.city)}
      <span class="ph-badges">${photo && !own ? `<span class="badge photo-note">城市風景</span>` : ""}${note ? `<span class="badge note">${esc(note)}</span>` : ""}${kindPill(s)}</span>
      <span class="city-en">${esc(s.cityEn)}</span>
    </div>
    <div class="school-body">
      <p class="meta loc">${PIN}${esc(cityName(s.city))} · ${esc(s.campus)}</p>
      <h3>${esc(s.name)}</h3>
      <div class="tags">${tags}</div>
      ${exams.length ? `<p class="hint">${CAP}官方考場：${exams.join("・")}</p>` : ""}
      <div class="card-foot"><span>${esc(s.tags.join("・"))}</span><span class="go">${CHEV}</span></div>
    </div>
  </a>`;
}

function renderFeatured() {
  document.getElementById("featured-cards").innerHTML = DATA.featured.map((f) => cardHTML(schoolById(f.id), f.note)).join("");
}

function renderHomeSteps() {
  document.getElementById("home-steps").innerHTML = DATA.steps.map((s) =>
    `<a class="step" href="#process/${esc(s.id)}"><span class="dot num">${Number(s.id)}</span><span><strong>${esc(s.title)}</strong><span class="meta">${esc(s.summary)}</span></span></a>`
  ).join("");
  document.getElementById("home-hot").innerHTML = DATA.hot.map((id) =>
    `<a href="#faq/${esc(id)}"><span>${esc(faqById(id).questions[0][0])}</span>${ARROW}</a>`
  ).join("");
}

function matchSchool(s) {
  if (state.city !== "全部" && s.city !== state.city) return false;
  if (state.course !== "全部" && !s.filters.includes(state.course)) return false;
  if (state.kind !== "全部" && s.kind !== state.kind) return false;
  if (state.q) {
    const blob = [s.name, s.brand, s.campus, s.city, s.style, s.kind, s.courses, ...(s.tags || [])].join(" ").toLowerCase();
    if (!blob.includes(state.q.toLowerCase())) return false;
  }
  return true;
}

function chip(attr, value, label, pressed, n) {
  return `<button class="chip" type="button" data-${attr}="${esc(value)}" aria-pressed="${pressed}">${esc(label)}${n == null ? "" : `<span class="n">${n}</span>`}</button>`;
}

const ICONS = __ICONS__;
// [icon, pressed colour (white text must stay readable), icon tile tint]
const REGION_ICON = {
  "全部": ["region-all", "#4E8A3E", "#EEF6E6"],
  "宿霧": ["region-cebu", "#0E8FA3", "#E2F6F8"],
  "碧瑤": ["region-baguio", "#2F7A5B", "#E8F1EC"],
  "克拉克": ["region-clark", "#E2553A", "#FFEFE8"],
  "克拉克／打拉": ["region-tarlac", "#7A7A16", "#F6F3D8"],
  "馬尼拉": ["region-manila", "#5B4FD6", "#EFEDFF"]
};

function regionChip(city, pressed, n) {
  const spec = REGION_ICON[city];
  if (!spec) return chip("city", city, cityName(city), pressed, n);
  const [icon, color, tint] = spec;
  return `<button class="chip region-chip" type="button" data-city="${esc(city)}" aria-pressed="${pressed}" style="--region:${color}"><span class="region-ico" style="--tint:${tint}"><img src="${ICONS[icon]}" alt="" width="40" height="40"></span>${esc(cityName(city))}<span class="n">${n}</span></button>`;
}

function renderSchools() {
  const input = document.getElementById("school-q");
  if (input && document.activeElement !== input) input.value = state.q;
  const cities = ["全部", "宿霧", "碧瑤", "克拉克", "克拉克／打拉", "馬尼拉"];
  document.getElementById("city-filters").innerHTML = cities.map((c) => {
    const n = c === "全部" ? DATA.schools.length : DATA.schools.filter((s) => s.city === c).length;
    return regionChip(c, state.city === c, n);
  }).join("");
  const courses = ["全部", "ESL", "雅思", "多益", "托福", "商務", "親子"];
  document.getElementById("course-filters").innerHTML = courses.map((c) => chip("course", c, c, state.course === c)).join("");
  const kinds = ["全部", "半斯巴達", "斯巴達", "親子", "其他"];
  document.getElementById("style-filters").innerHTML = kinds.map((k) => {
    const n = k === "全部" ? DATA.schools.length : DATA.schools.filter((s) => s.kind === k).length;
    return k !== "全部" && n === 0 ? "" : chip("kind", k, k, state.kind === k, n);
  }).join("");
  const list = DATA.schools.filter(matchSchool);
  const filtered = state.city !== "全部" || state.course !== "全部" || state.kind !== "全部" || state.q;
  const cityEn = (DATA.schools.find((s) => s.city === state.city) || {}).cityEn || "";
  document.getElementById("list-title").innerHTML = state.city === "全部"
    ? "全部校區"
    : `${esc(cityName(state.city))}<span class="en">${esc(cityEn)}</span>`;
  document.getElementById("school-count").innerHTML = `共 <strong>${list.length}</strong> 個校區`;
  document.getElementById("filter-reset").hidden = !filtered;
  const pages = Math.max(1, Math.ceil(list.length / PAGE_SIZE));
  state.page = Math.min(Math.max(1, state.page), pages);
  const start = (state.page - 1) * PAGE_SIZE;
  const shown = list.slice(start, start + PAGE_SIZE);
  document.getElementById("school-cards").innerHTML = shown.length
    ? shown.map((s) => cardHTML(s)).join("")
    : `<div class="surface empty"><h2 class="h-sm">沒有符合條件的學校</h2><p class="meta">試著放寬條件，或直接用 LINE 問我們。</p>${lineBtn("用 LINE 問飛語")}</div>`;
  renderPager(pages);
}

function pageNumbers(cur, total) {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
  const keep = new Set([1, total, cur - 1, cur, cur + 1]);
  const out = [];
  for (let i = 1; i <= total; i++) {
    if (keep.has(i)) out.push(i);
    else if (out[out.length - 1] !== "…") out.push("…");
  }
  return out;
}

function renderPager(pages) {
  const pager = document.getElementById("school-pager");
  if (pages <= 1) { pager.innerHTML = ""; return; }
  const cur = state.page;
  const nums = pageNumbers(cur, pages).map((n) => n === "…"
    ? `<span class="gap" aria-hidden="true">…</span>`
    : `<button type="button" data-page="${n}"${n === cur ? ` aria-current="page"` : ""} aria-label="第 ${n} 頁">${n}</button>`
  ).join("");
  pager.innerHTML = `
    <button type="button" class="pg-arrow prev" data-page="${cur - 1}"${cur === 1 ? " disabled" : ""} aria-label="上一頁">${CHEV}</button>
    ${nums}
    <button type="button" class="pg-arrow" data-page="${cur + 1}"${cur === pages ? " disabled" : ""} aria-label="下一頁">${CHEV}</button>`;
}

function goToPage(n) {
  state.page = n;
  renderSchools();
  const grid = document.getElementById("school-cards");
  grid.classList.remove("paging");
  void grid.offsetWidth;
  grid.classList.add("paging");
  document.querySelector(".list-head").scrollIntoView({ behavior: "smooth", block: "start" });
}

const CHECK = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>`;
const LINK_ICON = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/></svg>`;
const COURSE_TYPES = ["ESL", "雅思", "多益", "托福", "商務", "親子"];
const LEVELS = ["自由彈性", "偏彈性", "半斯巴達", "斯巴達", "高強度斯巴達"];
const LEVEL_COLOR = ["var(--green)", "var(--green)", "var(--mango)", "var(--coral)", "var(--coral)"];
const ic = (d) => `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${d}</svg>`;
const FACILITY_ICONS = [
  [/Wi.?Fi/i, "Wi‑Fi", ic('<path d="M3 9a14 14 0 0 1 18 0M6 12.5a9 9 0 0 1 12 0M9 16a4 4 0 0 1 6 0"/><circle cx="12" cy="19" r=".8" fill="currentColor"/>')],
  [/泳池/, "游泳池", ic('<path d="M3 17c2 0 2-1.5 4.5-1.5S9.5 17 12 17s2.5-1.5 4.5-1.5S19 17 21 17M8 14V5a2 2 0 0 1 4 0M16 14V5a2 2 0 0 0-4 0M8 9h8"/>')],
  [/健身/, "健身房", ic('<path d="M6 7v10M18 7v10M3 10v4M21 10v4M6 12h12"/>')],
  [/圖書館|自習/, "自習空間", ic('<path d="M4 5h6a2 2 0 0 1 2 2v12a2 2 0 0 0-2-2H4zM20 5h-6a2 2 0 0 0-2 2v12a2 2 0 0 1 2-2h6z"/>')],
  [/餐廳|用餐/, "餐廳", ic('<path d="M7 3v8M5 3v5a2 2 0 0 0 4 0V3M7 11v10M17 3c-2 2-2 6 0 8v10"/>')],
  [/咖啡|Cafe|點心吧/i, "咖啡廳", ic('<path d="M4 9h13v5a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5zM17 10h1.5a2.5 2.5 0 0 1 0 5H17M8 3v3M12 3v3"/>')],
  [/醫護|護理/, "醫護室", ic('<rect x="4" y="4" width="16" height="16" rx="4"/><path d="M12 8v8M8 12h8"/>')],
  [/籃球|排球|羽球|運動|多功能場地/, "運動場", ic('<circle cx="12" cy="12" r="8"/><path d="M4 12h16M12 4c3 2.5 3 13.5 0 16M12 4c-3 2.5-3 13.5 0 16"/>')],
  [/高爾夫/, "高爾夫", ic('<path d="M10 20V4l7 3.5-7 3.5"/><ellipse cx="10" cy="20" rx="5" ry="1.5"/>')],
  [/KTV|休閒/, "休閒娛樂", ic('<path d="M9 18V6l10-2v12"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/>')],
  [/商店/, "商店", ic('<path d="M4 9h16l-1 11H5zM8 9V7a4 4 0 0 1 8 0v2"/>')],
  [/海灘|度假/, "度假環境", ic('<path d="M12 21V11M5 11a7 7 0 0 1 14 0zM3 21h18"/>')],
  [/兒童|幼兒/, "兒童空間", ic('<circle cx="12" cy="7" r="3"/><path d="M7 21v-5a5 5 0 0 1 10 0v5"/>')],
  [/洗衣/, "洗衣區", ic('<rect x="5" y="3" width="14" height="18" rx="2"/><circle cx="12" cy="13" r="4"/><path d="M8 6h.01M11 6h.01"/>')],
  [/考場|測驗/, "考場", ic('<path d="M9 4h6l1 2h3v14H5V6h3z"/><path d="m9 13 2 2 4-4"/>')],
];

function splitList(text) {
  return String(text || "").split(/[；;]/).map((x) => x.trim()).filter((x) => x && x !== "—");
}

function intensity(s) {
  const style = s.style || "";
  if (s.kind === "斯巴達") return /每日 ?9|嚴格/.test(style) ? 5 : 4;
  if (s.kind === "半斯巴達") return 3;
  return /彈性|度假|自律|共學/.test(style) ? 1 : 2;
}

const CORE_FACILITIES = ["餐廳", "自習空間", "健身房", "游泳池", "醫護室", "運動場", "洗衣區", "咖啡廳", "商店", "休閒娛樂", "考場"];
const CONDITIONAL = /依校區|依方案|部分校區/;
const GENERIC_FACILITY = /教室|宿舍|住宿|辦公室|相簿|公共空間|公共區|校園|設施（|facilities/;

function facilityGrid(s) {
  const tokens = splitList(s.facilities);
  if (splitList(s.laundry).length) tokens.push("洗衣");
  if (/Wi.?Fi/i.test(s.accommodation || "")) tokens.push("Wi‑Fi");
  const used = new Set();
  const status = new Map();
  FACILITY_ICONS.forEach(([re, label]) => {
    const hits = tokens.filter((t) => re.test(t));
    hits.forEach((t) => used.add(t));
    if (hits.length) status.set(label, hits.every((t) => CONDITIONAL.test(t)) ? "part" : "yes");
  });
  const cell = ([, label, icon]) => {
    const st = status.get(label) || "no";
    const note = st === "part" ? "<small>依校區</small>" : st === "no" ? '<span class="sr-only">（資料未提到）</span>' : "";
    return `<li class="${st === "yes" ? "" : st}">${icon}${esc(label)}${note}</li>`;
  };
  const core = FACILITY_ICONS.filter(([, label]) => CORE_FACILITIES.includes(label));
  const extra = FACILITY_ICONS.filter(([, label]) => !CORE_FACILITIES.includes(label) && status.has(label));
  const others = tokens.filter((t) => !used.has(t) && !GENERIC_FACILITY.test(t) && !CONDITIONAL.test(t));
  return {
    cells: [...extra, ...core]
      .sort((a, b) => ["yes", "part", undefined].indexOf(status.get(a[1])) - ["yes", "part", undefined].indexOf(status.get(b[1])))
      .map(cell).join(""),
    others,
    known: status.size
  };
}

const ROOM_WORD = /人|房|套房|Deluxe|Premium|Standard|公寓/;

function roomInfo(s) {
  const groups = [];
  const notes = [];
  splitList(s.accommodation).forEach((seg) => {
    const m = seg.match(/^(.*?)[：:](.*)$/);
    const label = m ? m[1].trim() : "";
    const body = (m ? m[2] : seg).replace(/^主校區有/, "");
    const items = body.split(/[／/]/).map((x) => x.trim()).filter(Boolean);
    if (items.length >= 2 && items.every((x) => ROOM_WORD.test(x) && x.length <= 12)) {
      groups.push({ label: /住宿|宿舍/.test(label) ? "" : label, rooms: items.map((x) => /人$/.test(x) ? x + "房" : x) });
    } else {
      notes.push(seg);
    }
  });
  return { groups, notes, rooms: groups.flatMap((g) => g.rooms), laundry: splitList(s.laundry) };
}

const STAY_ICONS = { room: "school-room", stay: "school-accommodation", laundry: "school-laundry" };

function stayHTML(s) {
  const info = roomInfo(s);
  const tagList = (items) => `<div class="tags">${items.map((t) => `<span class="tag">${esc(t)}</span>`).join("")}</div>`;
  const key = (icon, label) => `<span class="kv-label"><img src="${ICONS[STAY_ICONS[icon]]}" alt="" width="40" height="40">${label}</span>`;
  const rows = [];
  if (info.groups.length) {
    const pills = info.groups.map((g) =>
      `${g.label ? `<span class="meta">${esc(g.label)}</span>` : ""}${g.rooms.map((r) => `<button class="chip sm" type="button" data-room="${esc(r)}" aria-pressed="false">${esc(r)}</button>`).join("")}`
    ).join("");
    rows.push(`<div class="kv">${key("room", "房型")}<div><div class="chip-row" id="room-pills">${pills}</div><p class="room-note" id="room-note">點選房型，會一起帶入「幫我問這間」詢問單。</p></div></div>`);
  } else {
    rows.push(`<div class="kv">${key("room", "房型")}<p class="meta">這間的房型資料整理中，<a href="${esc(LINE)}" target="_blank" rel="noopener">用 LINE 問我們</a>。</p></div>`);
  }
  if (info.notes.length) rows.push(`<div class="kv">${info.groups.length ? "<span>所有房型都有</span>" : key("stay", "住宿方式")}${tagList(info.notes)}</div>`);
  if (info.laundry.length) rows.push(`<div class="kv">${key("laundry", "洗衣清潔")}${tagList(info.laundry)}</div>`);
  return rows.join("");
}

const WEEK_OPTIONS = ["2 週", "4 週", "8 週", "12 週以上"];
const GENERIC_ROOMS = ["單人房", "雙人房", "多人房"];

function quoteHTML(s) {
  const rooms = roomInfo(s).rooms;
  const group = (key, label, options) => `<div class="q-group"><span>${label}</span><div class="chip-row" data-qkey="${key}">${options.map((o) => `<button class="chip sm" type="button" data-q="${esc(o)}" aria-pressed="false">${esc(o)}</button>`).join("")}</div></div>`;
  return `
    <div class="surface aside-cta quote" id="quote">
      <h3>幫我問這間</h3>
      <p class="meta">選好條件傳給飛語，我們會回覆課表、房型和最新費用。</p>
      ${group("course", "想上的課", COURSE_TYPES.filter((c) => s.filters.includes(c)))}
      ${group("weeks", "預計週數", WEEK_OPTIONS)}
      ${group("room", "想住的房型", rooms.length ? rooms : GENERIC_ROOMS)}
      <p class="bubble" id="q-bubble" aria-live="polite"></p>
      <a class="btn btn-primary btn-block" id="q-send" href="${esc(LINE)}" target="_blank" rel="noopener">${LINE_ICON}複製訊息，開啟 LINE</a>
      <p class="q-done" id="q-done"></p>
    </div>`;
}

function bindQuote(root, s) {
  const pick = { course: "", weeks: "", room: "" };
  const bubble = root.querySelector("#q-bubble");
  const send = root.querySelector("#q-send");
  const message = () => [
    `你好，我想詢問 ${s.name}`,
    pick.course && `課程：${pick.course}`,
    pick.weeks && `週數：${pick.weeks}`,
    pick.room && `房型：${pick.room}`,
    "想知道課表、房型和最新費用，謝謝！"
  ].filter(Boolean).join("\n");
  const render = () => {
    bubble.textContent = message();
    bubble.classList.remove("pop");
    void bubble.offsetWidth;
    bubble.classList.add("pop");
    root.querySelectorAll("[data-qkey]").forEach((row) => row.querySelectorAll("[data-q]").forEach((b) =>
      b.setAttribute("aria-pressed", String(pick[row.dataset.qkey] === b.dataset.q))));
    root.querySelectorAll("[data-room]").forEach((b) => b.setAttribute("aria-pressed", String(pick.room === b.dataset.room)));
    if (LINE_OA_ID) send.href = `https://line.me/R/oaMessage/${encodeURIComponent(LINE_OA_ID)}/?${encodeURIComponent(message())}`;
  };
  const set = (key, value) => { pick[key] = pick[key] === value ? "" : value; render(); };
  root.querySelectorAll("[data-qkey]").forEach((row) => row.addEventListener("click", (e) => {
    const b = e.target.closest("[data-q]");
    if (b) set(row.dataset.qkey, b.dataset.q);
  }));
  const pills = root.querySelector("#room-pills");
  if (pills) pills.addEventListener("click", (e) => {
    const b = e.target.closest("[data-room]");
    if (!b) return;
    set("room", b.dataset.room);
    root.querySelector("#room-note").innerHTML = pick.room
      ? `已帶入詢問單：<b>${esc(pick.room)}</b>`
      : "點選房型，會一起帶入「幫我問這間」詢問單。";
    const quote = root.querySelector("#quote");
    quote.classList.remove("flash");
    void quote.offsetWidth;
    quote.classList.add("flash");
  });
  send.addEventListener("click", () => {
    if (LINE_OA_ID) return;
    const done = root.querySelector("#q-done");
    const ok = () => { done.textContent = "已複製，到 LINE 對話框貼上就能送出。"; };
    if (navigator.clipboard) navigator.clipboard.writeText(message()).then(ok, () => { done.textContent = "請手動複製上面的訊息"; });
    else done.textContent = "請手動複製上面的訊息";
  });
  render();
}

function copyLink(btn) {
  const done = () => {
    btn.classList.add("done");
    btn.lastChild.textContent = "已複製";
    setTimeout(() => { btn.classList.remove("done"); btn.lastChild.textContent = "複製連結"; }, 1800);
  };
  if (navigator.clipboard) navigator.clipboard.writeText(location.href).then(done, done);
  else done();
}

function renderDetail(id) {
  const s = schoolById(id);
  const root = document.getElementById("school-detail");
  if (!s) {
    root.innerHTML = `<a class="back" href="#schools">${BACK}回學校清單</a><div class="surface empty"><p>找不到這間學校。</p></div>`;
    return;
  }
  const facts = [
    ["成立", s.established],
    ["學生人數", /未公開/.test(s.capacity || "") ? "" : s.capacity],
    ["管理風格", s.style],
    ["認證", s.accreditation]
  ].filter(([, v]) => v).map(([k, v]) => `<p><span>${esc(k)}</span>${esc(v)}</p>`).join("");
  const strengths = s.strengths.length ? s.strengths : ["特色整理中"];
  const level = intensity(s);
  const exams = examCenters(s);
  const fit = splitList(s.suitable).slice(0, 6);
  const fac = facilityGrid(s);
  const courses = splitList(s.courses);
  const phones = (s.phone || "").split("/").map((x) => x.trim()).filter((x) => /\d/.test(x));
  const contact = [
    ...phones.map((p) => `<p>電話 <a href="tel:${esc(p.replace(/\s/g, ""))}">${esc(p)}</a></p>`),
    (s.email || "").includes("@") ? `<p>Email <a href="mailto:${esc(s.email)}">${esc(s.email)}</a></p>` : (s.email ? `<p>${esc(s.email)}</p>` : ""),
    linkOrText("官方網站", s.website),
    linkOrText("學校官方表單", s.contactForm),
    linkOrText("Facebook", s.facebook),
    linkOrText("Instagram", s.instagram)
  ].join("");
  const cover = COURSE_TYPES.map((c) => s.filters.includes(c)
    ? `<span>${CHECK}${esc(c)}</span>` : `<span class="off">${esc(c)}</span>`).join("");
  const meter = [1, 2, 3, 4, 5].map((n) => `<i class="${n <= level ? "on" : ""}"></i>`).join("");
  root.innerHTML = `
    <nav class="crumbs" aria-label="位置">
      <a href="#schools">學校</a>${CHEV}
      <a href="#schools" data-city-crumb="${esc(s.city)}">${esc(cityName(s.city))}</a>${CHEV}
      <span aria-current="page">${esc(s.name)}</span>
    </nav>
    <div class="surface d-top rv">
      <div class="d-head">
        <span class="city-tile" data-city="${esc(s.city)}">${cityArt(s.city, "90 14 150 86")}<span style="position:relative">${esc(s.cityEn)}</span></span>
        <div class="d-id">
          <p class="meta">${esc(cityName(s.city))} · ${esc(s.campus)}</p>
          <h1>${esc(s.name)}</h1>
          <div class="tags">${kindPill(s)}${exams.length ? `<span class="hint inline">${CAP}官方考場：${exams.join("・")}</span>` : ""}</div>
        </div>
        <button class="share" type="button" aria-label="複製這間學校的連結">${LINK_ICON}<span>複製連結</span></button>
      </div>
      ${galleryHTML(s)}
    </div>
    <div class="surface glance rv">
      <div>
        <h2>管理強度</h2>
        <p class="val">${LEVELS[level - 1]}</p>
        <div class="meter" style="--lvl:${LEVEL_COLOR[level - 1]}" role="img" aria-label="管理強度 ${level} / 5">${meter}</div>
        <div class="meter-ends"><span>自由</span><span>嚴格</span></div>
      </div>
      <div>
        <h2>課程選擇</h2>
        <div class="cover">${cover}</div>
      </div>
      <div>
        <h2>適合誰</h2>
        ${fit.length ? `<ul class="fit">${fit.map((f) => `<li>${CHECK}${esc(f)}</li>`).join("")}</ul>` : `<p class="meta">資料整理中</p>`}
      </div>
    </div>
    <div class="detail-layout">
      <div class="surface detail-main rv">
        <nav class="detail-nav" aria-label="這間學校">
          <a href="#d-intro" data-jump="d-intro" class="active">簡介</a>
          <a href="#d-course" data-jump="d-course">課程</a>
          <a href="#d-stay" data-jump="d-stay">住宿</a>
          <a href="#d-fac" data-jump="d-fac">設施</a>
          <a href="#d-place" data-jump="d-place">位置</a>
        </nav>
        <section class="detail-section" id="d-intro">
          <h2>學校簡介</h2>
          <div class="facts">${facts}</div>
          <ul class="bullets">${strengths.map((p) => `<li>${esc(p)}</li>`).join("")}</ul>
        </section>
        <section class="detail-section" id="d-course">
          <h2>課程</h2>
          ${courses.length ? `<ul class="checks">${courses.map((c) => `<li>${CHECK}<span>${esc(c)}</span></li>`).join("")}</ul>` : `<p class="meta">課程資料整理中</p>`}
        </section>
        <section class="detail-section" id="d-stay">
          <h2>住宿與生活</h2>
          ${stayHTML(s)}
        </section>
        <section class="detail-section" id="d-fac">
          <div class="sec-head">
            <h2>設施</h2>
            <p class="legend"><span><i></i>有</span><span><i class="part"></i>依校區</span><span><i class="no"></i>資料未提到</span></p>
          </div>
          <ul class="amen">${fac.cells}</ul>
          ${fac.others.length ? `<p class="more-fac">其他：${fac.others.map(esc).join("、")}</p>` : ""}
        </section>
        <section class="detail-section" id="d-place">
          <h2>位置</h2>
          <p>${esc(s.address)}</p>
          <p class="meta">${esc(s.addressEn)}</p>
          ${isUrl(s.maps) ? `<p style="margin-top:10px"><a class="link-arrow" href="${esc(s.maps)}" target="_blank" rel="noopener">查看地圖${ARROW}</a></p>` : ""}
        </section>
      </div>
      <aside class="detail-aside">
        ${quoteHTML(s)}
        ${contact ? `<details class="surface contact">
          <summary>學校官方聯絡方式${CHEV}</summary>
          <div class="contact-body"><p class="meta">想比較學校或報名，請先聯絡飛語。以下是學校官方的聯絡方式。</p>${contact}</div>
        </details>` : ""}
      </aside>
    </div>`;
  root.querySelector(".share").addEventListener("click", (e) => copyLink(e.currentTarget));
  bindQuote(root, s);
  bindGallery(root.querySelector(".gallery"), s);
  root.querySelector("[data-city-crumb]").addEventListener("click", () => {
    Object.assign(state, { city: s.city, course: "全部", kind: "全部", q: "", page: 1 });
  });
  const tabs = root.querySelectorAll("[data-jump]");
  tabs.forEach((a) => a.addEventListener("click", (e) => {
    e.preventDefault();
    const el = document.getElementById(a.dataset.jump);
    if (!el) return;
    pinSpy();
    tabs.forEach((t) => t.classList.toggle("active", t === a));
    el.scrollIntoView({ behavior: "smooth", block: "start" });
  }));
  scrollSpy([...root.querySelectorAll(".detail-section")], (id) => {
    tabs.forEach((a) => a.classList.toggle("active", a.dataset.jump === id));
  }, 180);
}

/* Photo gallery: real photos/videos from SCHOOL_PHOTOS, otherwise illustrated placeholders */
const CITY_SCENERY = {
  "宿霧": [
    { src: "images/editorial/cebu-palms.jpg", cat: "海岸", caption: "宿霧海岸。城市風景，不是這間學校的照片。" },
    { src: "images/editorial/cebu-shore.jpg", cat: "海岸", caption: "宿霧白沙岸。城市風景，不是這間學校的照片。" },
    { src: "images/editorial/cebu-city.jpg", cat: "城市", caption: "宿霧市夜景。城市風景，不是這間學校的照片。" }
  ],
  "碧瑤": [
    { src: "images/editorial/baguio-path.jpg", cat: "街道", caption: "碧瑤林蔭路。城市風景，不是這間學校的照片。" },
    { src: "images/editorial/baguio-mtn.jpg", cat: "山城", caption: "碧瑤山城。城市風景，不是這間學校的照片。" }
  ]
};
const PLACEHOLDER_SHOTS = ["校園外觀", "教室", "宿舍", "餐廳", "公共空間"];
const THUMBS_SHOWN = 6;
const PLAY = `<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.5v13l11-6.5z"/></svg>`;
const GRID_ICON = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="4" width="7" height="7" rx="1.5"/><rect x="13" y="4" width="7" height="7" rx="1.5"/><rect x="4" y="13" width="7" height="7" rx="1.5"/><rect x="13" y="13" width="7" height="7" rx="1.5"/></svg>`;

function youTubeId(url) {
  const m = String(url || "").match(/(?:v=|youtu\.be\/|embed\/|shorts\/)([\w-]{11})/);
  return m ? m[1] : "";
}

function schoolMedia(s) {
  if (s.photos && s.photos.length) {
    return s.photos.map((p) => {
      const vid = youTubeId(p.video);
      return { ...p, vid, thumb: p.src || (vid ? `https://img.youtube.com/vi/${vid}/hqdefault.jpg` : ""), cat: p.cat || (vid ? "影片" : "校園") };
    });
  }
  if (CITY_SCENERY[s.city]) return CITY_SCENERY[s.city].map((p) => ({ ...p, thumb: p.src }));
  return PLACEHOLDER_SHOTS.map((cat) => ({ cat, placeholder: true }));
}

function mediaFace(m, s, big) {
  if (m.placeholder) {
    return `<span class="g-ph" data-city="${esc(s.city)}">${cityArt(s.city)}<span class="g-ph-label">${esc(m.cat)}${big ? "<small>照片整理中</small>" : ""}</span></span>`;
  }
  return `<img src="${esc(m.thumb)}" alt="${esc(m.caption || m.cat)}" loading="lazy">${m.vid ? `<span class="g-play">${PLAY}</span>` : ""}`;
}

function galleryHTML(s) {
  const media = schoolMedia(s);
  const cats = [...new Set(media.map((m) => m.cat))];
  const extra = media.length - THUMBS_SHOWN;
  const thumbs = media.slice(0, THUMBS_SHOWN).map((m, i) => {
    const more = i === THUMBS_SHOWN - 1 && extra > 0;
    return `<button type="button" class="g-thumb${i === 0 ? " active" : ""}" data-go="${i}"${more ? ` data-all aria-label="看全部 ${media.length} 張"` : ` aria-label="第 ${i + 1} 張：${esc(m.cat)}"`}>${mediaFace(m, s, false)}${more ? `<span class="g-more">+${extra + 1}</span>` : ""}</button>`;
  }).join("");
  return `<div class="gallery" aria-roledescription="相簿" aria-label="${esc(s.name)} 照片">
    <div class="g-stage">
      <div class="g-track" tabindex="0">${media.map((m, i) => `<button type="button" class="g-slide" data-open="${i}" aria-label="放大第 ${i + 1} 張">${mediaFace(m, s, true)}</button>`).join("")}</div>
      <button type="button" class="g-nav prev" data-step="-1" aria-label="上一張">${CHEV}</button>
      <button type="button" class="g-nav next" data-step="1" aria-label="下一張">${CHEV}</button>
      <span class="g-cap">${esc(media[0].caption || media[0].cat)}</span>
      <button type="button" class="g-count" data-all>${GRID_ICON}<span>1 / ${media.length}</span></button>
    </div>
    ${cats.length > 1 ? `<div class="g-cats">${cats.map((c) => `<button type="button" class="chip sm" data-cat="${esc(c)}">${esc(c)}</button>`).join("")}</div>` : ""}
    <div class="g-thumbs">${thumbs}</div>
  </div>`;
}

function trackIndex(track) {
  return Math.round(track.scrollLeft / Math.max(1, track.clientWidth));
}

// Arrows and keys step from the slide we're heading to, so quick repeated clicks don't count mid-scroll positions.
function slider(track, count) {
  let target = 0;
  return {
    go(i, smooth = true) {
      target = (i + count) % count;
      track.scrollTo({ left: target * track.clientWidth, behavior: smooth ? "smooth" : "auto" });
    },
    step(d) { this.go(target + d); },
    settle() {
      const i = trackIndex(track);
      if (Math.abs(track.scrollLeft - i * track.clientWidth) < 2) target = i;
      return i;
    }
  };
}

function bindGallery(g, s) {
  if (!g) return;
  const media = schoolMedia(s);
  const track = g.querySelector(".g-track");
  const nav = slider(track, media.length);
  const go = (i) => nav.go(i);
  const sync = () => {
    const i = nav.settle();
    g.querySelector(".g-count span").textContent = `${i + 1} / ${media.length}`;
    g.querySelector(".g-cap").textContent = media[i].caption || media[i].cat;
    g.querySelectorAll(".g-thumb").forEach((t) => t.classList.toggle("active", Number(t.dataset.go) === i));
    g.querySelectorAll("[data-cat]").forEach((c) => c.setAttribute("aria-pressed", String(c.dataset.cat === media[i].cat)));
  };
  let raf = 0;
  track.addEventListener("scroll", () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(sync); }, { passive: true });
  track.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight" || e.key === "ArrowLeft") { e.preventDefault(); nav.step(e.key === "ArrowRight" ? 1 : -1); }
  });
  g.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    if (b.hasAttribute("data-all")) return openLightbox(s, trackIndex(track));
    if (b.dataset.step) return nav.step(Number(b.dataset.step));
    if (b.dataset.go) return go(Number(b.dataset.go));
    if (b.dataset.cat) return go(media.findIndex((m) => m.cat === b.dataset.cat));
    if (b.dataset.open) {
      const m = media[Number(b.dataset.open)];
      if (m.vid) b.outerHTML = videoFrame(m);
      else openLightbox(s, Number(b.dataset.open));
    }
  });
  sync();
}

function videoFrame(m) {
  return `<div class="g-slide g-video"><iframe src="https://www.youtube-nocookie.com/embed/${esc(m.vid)}?autoplay=1&rel=0" title="${esc(m.caption || "學校影片")}" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe></div>`;
}

function openLightbox(s, start) {
  const media = schoolMedia(s);
  let box = document.getElementById("lightbox");
  if (!box) {
    box = document.createElement("dialog");
    box.id = "lightbox";
    box.className = "lightbox";
    document.body.appendChild(box);
    box.addEventListener("close", () => { box.innerHTML = ""; document.documentElement.classList.remove("lb-open"); });
  }
  box.setAttribute("aria-label", `${s.name} 照片`);
  box.innerHTML = `
    <div class="lb-top"><p><strong>${esc(s.name)}</strong><span class="lb-count"></span></p><button type="button" class="lb-close" aria-label="關閉">×</button></div>
    <div class="lb-stage">
      <div class="lb-track">${media.map((m) => `<figure class="lb-slide">${m.vid ? `<div class="lb-video" data-vid="${esc(m.vid)}"></div>` : mediaFace(m, s, true)}</figure>`).join("")}</div>
      <button type="button" class="g-nav prev" data-step="-1" aria-label="上一張">${CHEV}</button>
      <button type="button" class="g-nav next" data-step="1" aria-label="下一張">${CHEV}</button>
    </div>
    <p class="lb-cap"></p>
    <div class="lb-thumbs">${media.map((m, i) => `<button type="button" class="g-thumb" data-go="${i}" aria-label="第 ${i + 1} 張">${mediaFace(m, s, false)}</button>`).join("")}</div>`;
  const track = box.querySelector(".lb-track");
  const nav = slider(track, media.length);
  let last = -1;
  const sync = () => {
    const i = nav.settle();
    if (i === last) return;
    last = i;
    box.querySelector(".lb-count").textContent = `${i + 1} / ${media.length}`;
    box.querySelector(".lb-cap").textContent = media[i].caption || media[i].cat;
    box.querySelectorAll(".lb-thumbs .g-thumb").forEach((t, j) => {
      t.classList.toggle("active", j === i);
      if (j === i) t.scrollIntoView({ block: "nearest", inline: "center" });
    });
    box.querySelectorAll(".lb-video").forEach((v) => {
      const slide = [...track.children].indexOf(v.parentElement);
      v.innerHTML = slide === i ? `<iframe src="https://www.youtube-nocookie.com/embed/${esc(v.dataset.vid)}?rel=0" title="學校影片" allow="encrypted-media; picture-in-picture" allowfullscreen></iframe>` : "";
    });
  };
  let raf = 0;
  track.addEventListener("scroll", () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(sync); }, { passive: true });
  box.onclick = (e) => {
    const b = e.target.closest("button");
    if (b && b.classList.contains("lb-close")) return box.close();
    if (b && b.dataset.step) return nav.step(Number(b.dataset.step));
    if (b && b.dataset.go) return nav.go(Number(b.dataset.go));
  };
  box.onkeydown = (e) => {
    if (e.key === "ArrowRight" || e.key === "ArrowLeft") { e.preventDefault(); nav.step(e.key === "ArrowRight" ? 1 : -1); }
  };
  document.documentElement.classList.add("lb-open");
  box.showModal();
  nav.go(start, false);
  sync();
  box.querySelector(".lb-close").focus();
}

function linkOrText(label, value) {
  if (!value || value.includes("未公開") || value.includes("Not published")) return "";
  if (isUrl(value)) return `<p><a href="${esc(value)}" target="_blank" rel="noopener">${esc(label)}</a></p>`;
  return `<p>${esc(label)}：${esc(value)}</p>`;
}

const PHASES = [
  { id: "pick", title: "選校", steps: ["01", "02"], sum: "說出目標，收到幾間適合的學校" },
  { id: "apply", title: "報名", steps: ["03", "04"], sum: "確認方案、送出報名、拿到入學文件" },
  { id: "prep", title: "出發準備", steps: ["05", "06", "07"], sum: "付款、機票、文件、行前說明" },
  { id: "stay", title: "抵達與在學", steps: ["08"], sum: "接機入住，到結業都有人可問" }
];

function stepRow(s) {
  return `
    <li class="step-row" id="step-${esc(s.id)}">
      <span class="dot num">${Number(s.id)}</span>
      <div class="step-text">
        <h3>${esc(s.title)}</h3>
        <p class="meta">${esc(s.summary)}</p>
        <p class="you-line"><b>你要做</b>${s.you.map((n) => `<span class="tag">${esc(n)}</span>`).join("")}</p>
      </div>
      <p class="get"><span>完成後</span>${esc(s.get)}</p>
    </li>`;
}

function renderProcess(openId) {
  const byId = Object.fromEntries(DATA.steps.map((s) => [s.id, s]));
  document.getElementById("process-steps").innerHTML = PHASES.map((p, i) => `
    <section class="surface phase rv" id="phase-${p.id}">
      <p class="phase-head"><span class="no">階段 ${i + 1}</span>${esc(p.title)}</p>
      <ol class="step-list">${p.steps.filter((id) => byId[id]).map((id) => stepRow(byId[id])).join("")}</ol>
    </section>`).join("");
  observeReveal();
  if (openId) {
    requestAnimationFrame(() => requestAnimationFrame(() => {
      const el = document.getElementById("step-" + openId);
      if (!el) return;
      el.scrollIntoView({ block: "center" });
      el.classList.add("focus");
      setTimeout(() => el.classList.remove("focus"), 1600);
    }));
  }
}

function acc(q, a, open) {
  return `<div class="acc${open ? " open" : ""}"><button type="button" aria-expanded="${open ? "true" : "false"}">${esc(q)}<span class="pm" aria-hidden="true"></span></button><div class="a"><div><p>${esc(a)}</p></div></div></div>`;
}

function bindAcc(root) {
  root.querySelectorAll(".acc > button").forEach((btn) => {
    btn.addEventListener("click", () => {
      const item = btn.parentElement;
      const open = !item.classList.contains("open");
      item.classList.toggle("open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });
}

function renderFaq(id, q) {
  const body = document.getElementById("faq-body");
  const input = document.getElementById("faq-q");
  if (input && document.activeElement !== input) input.value = q || "";
  if (id && faqById(id) && !q) {
    const cat = faqById(id);
    body.innerHTML = `<a class="back" href="#faq">${BACK}回到全部分類</a>
      <div class="cat-head"><h2>${esc(cat.title)}</h2><span class="meta">${cat.questions.length} 題</span></div>
      <div class="surface acc-list rv">${cat.questions.map(([qq, aa], i) => acc(qq, aa, i === 0)).join("")}</div>
      <p class="after-acc"><a class="link-arrow" href="${esc(LINE)}" target="_blank" rel="noopener">沒找到答案？用 LINE 問飛語${ARROW}</a></p>`;
    bindAcc(body);
    return;
  }
  if (q) {
    const query = q.trim().toLowerCase();
    const hits = [];
    DATA.faq.forEach((cat) => cat.questions.forEach(([qq, aa]) => {
      if ((qq + aa + cat.title).toLowerCase().includes(query)) hits.push([qq, aa]);
    }));
    body.innerHTML = hits.length
      ? `<div class="cat-head"><h2 class="h-sm" style="margin:0">搜尋「${esc(q)}」</h2><span class="meta">${hits.length} 題</span></div>
         <div class="surface acc-list rv">${hits.map(([qq, aa]) => acc(qq, aa, false)).join("")}</div>`
      : `<div class="surface empty rv"><h2 class="h-sm">找不到相關問題</h2><p class="meta">換個關鍵字試試，或直接用 LINE 問我們。</p>${lineBtn("用 LINE 問這題")}</div>`;
    bindAcc(body);
    return;
  }
  const hot = DATA.hot.map((hid) => `<a href="#faq/${esc(hid)}"><span>${esc(faqById(hid).questions[0][0])}</span>${ARROW}</a>`).join("");
  const cats = DATA.faq.map((cat) =>
    `<a class="surface cat" href="#faq/${esc(cat.id)}"><span><strong>${esc(cat.title)}</strong><span class="meta">${cat.questions.length} 題</span></span></a>`
  ).join("");
  body.innerHTML = `<div class="faq-grid">
    <div class="surface hot-box rv"><h2 class="h-sm">熱門問題</h2><div class="hot">${hot}</div></div>
    <div><h2 class="h-sm">10 個分類</h2><div class="cats rv-group">${cats}</div></div>
  </div>`;
}

// Cover drawings share the 240x100 box and styling of the city art.
const BLOG_ART = {
  packing: '<circle class="sun m" cx="216" cy="22" r="9"/><rect x="140" y="42" width="70" height="48" rx="8"/><path d="M162 42v-9h26v9M140 60h70M158 90v6M192 90v6"/><path class="trail" d="M96 84q20-34 40-38"/>',
  cities: '<path class="trail" d="M100 86q36-44 72-30t56-28"/><circle cx="100" cy="86" r="4"/><circle cx="172" cy="56" r="4"/><g class="m"><path d="M222 12a10 10 0 0 1 10 10c0 8-10 18-10 18s-10-10-10-18a10 10 0 0 1 10-10z"/><circle cx="222" cy="22" r="3"/></g>',
  sparta: '<circle cx="198" cy="50" r="30"/><path d="M198 32v18l12 8"/><path class="m" d="M112 92h48V70h-48zM136 70v22"/><circle class="sun" cx="198" cy="50" r="2"/>',
};

function blogCover(a) {
  const art = a.cover
    ? `<img src="${esc(a.cover)}" alt="" loading="lazy">`
    : `<svg class="city-art" viewBox="0 0 240 100" preserveAspectRatio="xMaxYMax meet" aria-hidden="true">${BLOG_ART[a.id] || BLOG_ART.packing}</svg>`;
  return `<div class="cover${a.cover ? " has-img" : ""}" data-tone="${esc(a.tone || "blue")}"><span class="kind">${esc(a.kicker)}</span>${art}</div>`;
}

function readMinutes(a) {
  const text = a.html.replace(/<[^>]+>/g, "").replace(/\s+/g, "");
  return Math.max(2, Math.round(text.length / 300));
}

function postCard(a, cls = "") {
  return `<a class="surface post-card ${cls}" href="#article/${esc(a.id)}">
    ${blogCover(a)}
    <div class="post-body">
      <h2>${esc(a.title)}</h2>
      <p class="meta">${esc(a.excerpt)}</p>
      <span class="post-meta">閱讀約 ${readMinutes(a)} 分鐘${CHEV}</span>
    </div>
  </a>`;
}

function renderBlog() {
  document.getElementById("blog-list").innerHTML = DATA.articles.map((a, i) => postCard(a, i === 0 ? "feature" : "")).join("");
}

function renderArticle(id, section) {
  const a = DATA.articles.find((x) => x.id === id);
  const root = document.getElementById("article-body");
  if (!a) {
    root.innerHTML = `<a class="back" href="#blog">${BACK}回部落格</a><div class="surface empty"><p>找不到這篇文章。</p></div>`;
    document.title = "文章｜FlyLingo 飛語";
    return;
  }
  document.title = a.title + "｜FlyLingo 飛語";
  const others = DATA.articles.filter((x) => x.id !== a.id);
  const wide = window.matchMedia("(min-width: 901px)").matches;
  root.innerHTML = `<a class="back" href="#blog">${BACK}回部落格</a>
  <header class="surface art-head rv">
    <div>
      <p class="eyebrow">${esc(a.kicker)}</p>
      <h1>${esc(a.title)}</h1>
      <p class="lede">${esc(a.excerpt)}</p>
      <p class="post-meta">閱讀約 ${readMinutes(a)} 分鐘</p>
    </div>
    ${blogCover(a)}
  </header>
  <div class="art-layout">
    <article class="surface article rv">
      <div class="wp-content">${a.html}</div>
      <div class="art-cta">
        <div><h2 class="h-sm">還有其他問題？</h2><p class="meta">把你的狀況告訴飛語，我們會直接回覆你。</p></div>
        ${lineBtn("用 LINE 問飛語")}
      </div>
    </article>
    <aside class="art-aside">
      <details class="surface toc"${wide ? " open" : ""}>
        <summary>本篇目錄${CHEV}</summary>
        <nav></nav>
      </details>
    </aside>
  </div>
  ${others.length ? `<section class="more-posts"><h2 class="h-sm">接著看</h2><div class="blog-grid">${others.map((x) => postCard(x)).join("")}</div></section>` : ""}`;

  const content = root.querySelector(".wp-content");
  // WordPress headings keep their own anchor (Heading block → HTML anchor); others get sec-1, sec-2…
  const heads = [...content.querySelectorAll("h2")];
  heads.forEach((h, i) => { if (!h.id) h.id = "sec-" + (i + 1); });
  content.querySelectorAll("table").forEach((t) => {
    if (!t.parentElement.matches("figure, .table-scroll")) t.outerHTML = `<div class="table-scroll">${t.outerHTML}</div>`;
  });
  const toc = root.querySelector(".toc");
  if (!heads.length) toc.hidden = true;
  toc.querySelector("nav").innerHTML = heads.map((h) => `<a href="#article/${esc(a.id)}/${esc(h.id)}" data-jump="${esc(h.id)}">${esc(h.textContent)}</a>`).join("");
  const links = toc.querySelectorAll("[data-jump]");
  const jump = (sid, smooth) => {
    const el = document.getElementById(sid);
    if (!el) return;
    pinSpy();
    links.forEach((x) => x.classList.toggle("active", x.dataset.jump === sid));
    history.replaceState(null, "", `#article/${a.id}/${sid}`);
    el.scrollIntoView({ behavior: smooth ? "smooth" : "auto", block: "start" });
  };
  root.onclick = (e) => {
    const l = e.target.closest("a[href]");
    if (!l) return;
    const href = l.getAttribute("href");
    const sid = l.dataset.jump || (href.startsWith("#") && content.querySelector(`[id="${CSS.escape(href.slice(1))}"]`) ? href.slice(1) : "");
    if (!sid) return;
    e.preventDefault();
    jump(sid, true);
  };
  scrollSpy(heads, (sid) => {
    links.forEach((x) => x.classList.toggle("active", x.dataset.jump === sid));
  }, 140);
  if (section) requestAnimationFrame(() => jump(section, false));
}

function parseRoute() {
  let h = (location.hash || "#home").replace(/^#/, "");
  let q = "";
  const qi = h.indexOf("?");
  if (qi >= 0) {
    q = new URLSearchParams(h.slice(qi + 1)).get("q") || "";
    h = h.slice(0, qi);
  }
  const parts = h.split("/").filter(Boolean);
  return { view: parts[0] || "home", id: parts[1] || "", sub: parts[2] || "", q };
}

function render() {
  const route = parseRoute();
  const known = ["home", "schools", "school", "process", "faq", "blog", "article"];
  const view = known.includes(route.view) ? route.view : "home";
  document.querySelectorAll("[data-view]").forEach((el) => { el.hidden = el.dataset.view !== view; });
  const navKey = { school: "schools", article: "blog" }[view] || view;
  document.querySelectorAll("#nav a").forEach((a) => {
    if (a.dataset.nav === navKey) a.setAttribute("aria-current", "page");
    else a.removeAttribute("aria-current");
  });
  document.querySelector("header.site").classList.remove("open");
  document.getElementById("menu-btn").setAttribute("aria-expanded", "false");
  stopSpy();
  if (view === "schools") renderSchools();
  if (view === "school") renderDetail(route.id);
  if (view === "process") renderProcess(route.id);
  if (view === "faq") renderFaq(route.id, route.q);
  if (view === "blog") renderBlog();
  if (view === "article") renderArticle(route.id, route.sub);
  const titles = {
    home: "FlyLingo 飛語｜從語言出發，飛向世界",
    schools: "學校清單｜FlyLingo 飛語",
    school: "學校｜FlyLingo 飛語",
    process: "代辦流程｜FlyLingo 飛語",
    faq: "常見問題｜FlyLingo 飛語",
    blog: "部落格｜FlyLingo 飛語",
    article: "文章｜FlyLingo 飛語"
  };
  if (view !== "article") document.title = titles[view];
  if ((view !== "process" || !route.id) && !route.sub) window.scrollTo(0, 0);
  observeReveal();
}

document.getElementById("menu-btn").addEventListener("click", () => {
  const header = document.querySelector("header.site");
  const open = !header.classList.contains("open");
  header.classList.toggle("open", open);
  document.getElementById("menu-btn").setAttribute("aria-expanded", open ? "true" : "false");
});
document.getElementById("home-search").addEventListener("submit", (e) => {
  e.preventDefault();
  const q = document.getElementById("home-q").value.trim();
  location.hash = q ? "#faq?q=" + encodeURIComponent(q) : "#faq";
});
document.getElementById("faq-search").addEventListener("submit", (e) => {
  e.preventDefault();
  const q = document.getElementById("faq-q").value.trim();
  location.hash = q ? "#faq?q=" + encodeURIComponent(q) : "#faq";
});
[["city-filters", "city"], ["course-filters", "course"], ["style-filters", "kind"]].forEach(([box, key]) => {
  document.getElementById(box).addEventListener("click", (e) => {
    const btn = e.target.closest(`[data-${key}]`);
    if (!btn) return;
    state[key] = btn.dataset[key];
    state.page = 1;
    renderSchools();
  });
});
document.getElementById("filter-reset").addEventListener("click", () => {
  Object.assign(state, { city: "全部", course: "全部", kind: "全部", q: "", page: 1 });
  document.getElementById("school-q").value = "";
  renderSchools();
});
document.getElementById("school-search").addEventListener("submit", (e) => e.preventDefault());
document.getElementById("school-q").addEventListener("input", (e) => {
  state.q = e.target.value.trim();
  state.page = 1;
  renderSchools();
});
document.getElementById("school-pager").addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-page]");
  if (!btn || btn.disabled || btn.getAttribute("aria-current")) return;
  goToPage(Number(btn.dataset.page));
});

const header = document.querySelector("header.site");
const progress = document.querySelector(".progress");
function onScroll() {
  const y = window.scrollY;
  header.classList.toggle("scrolled", y > 4);
  if (progress) {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.transform = `scaleX(${max > 0 ? Math.min(1, y / max) : 0})`;
  }
}
window.addEventListener("scroll", onScroll, { passive: true });
onScroll();

function startFlight() {
  const art = document.getElementById("hero-route");
  if (!art || !document.documentElement.classList.contains("motion")) return;
  const flyer = art.querySelector(".flyer");
  const route = art.querySelector(".route-line").getAttribute("d");
  const run = () => {
    flyer.removeAttribute("transform");
    const motion = document.createElementNS("http://www.w3.org/2000/svg", "animateMotion");
    Object.entries({ path: route, dur: "2.2s", fill: "freeze", rotate: "auto", begin: "indefinite",
      calcMode: "spline", keyTimes: "0;1", keySplines: ".4 0 .2 1" }).forEach(([k, v]) => motion.setAttribute(k, v));
    flyer.appendChild(motion);
    art.classList.add("fly");
    motion.beginElement();
  };
  const io = new IntersectionObserver((entries) => {
    if (!entries.some((e) => e.isIntersecting)) return;
    io.disconnect();
    setTimeout(run, 300);
  }, { threshold: 0.4 });
  io.observe(art);
}

renderFeatured();
renderHomeSteps();
window.addEventListener("hashchange", render);
render();
startFlight();
</script>
</body>
</html>
'''


def base_css():
    return BASE_CSS.strip().replace("__ACCENT_VARS__", accent_vars())


def contrast(a, b):
    def lum(h):
        r, g, b_ = (int(h.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
        f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b_)
    hi, lo = sorted([lum(a), lum(b)], reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def ratio_chip(fg, bg, label):
    r = contrast(fg, bg)
    ok = "pass" if r >= 4.5 else ("large" if r >= 3 else "fail")
    mark = {"pass": "AA", "large": "僅大字", "fail": "不及格"}[ok]
    return f'<li><span class="pair" style="background:{bg};color:{fg}">Aa</span>{label}<b class="{ok}">{r:.1f}　{mark}</b></li>'


# Line drawings in a 240x100 box, art kept on the right so the city name on the left stays clear.
# Elements with class "m" drift a little when the card is hovered.
CITY_ART = {
    "宿霧": '<circle class="sun m" cx="212" cy="26" r="10"/>'
            '<path d="M168 96C166 80 164 66 170 52"/>'
            '<path d="M170 52C160 44 150 44 142 50M170 52C178 42 190 42 198 48M170 52C166 40 158 34 150 34M170 52C176 40 186 36 192 38"/>'
            '<path class="m" d="M100 84q10-6 20 0t20 0t20 0t20 0t20 0t20 0t20 0"/>'
            '<path d="M120 94q10-6 20 0t20 0t20 0t20 0t20 0t20 0"/>',
    "碧瑤": '<path class="m" d="M150 28h30a6 6 0 0 0-8-8a9 9 0 0 0-16 2a6 6 0 0 0-6 6"/>'
            '<path d="M96 96L132 52L152 72L180 38L236 96"/>'
            '<path d="M118 96v-6M108 90l10-14l10 14zM111 80l7-11l7 11z"/>'
            '<path d="M204 96v-6M194 90l10-14l10 14zM197 80l7-11l7 11z"/>'
            '<path d="M222 96v-5M215 91l7-10l7 10z"/>',
    "克拉克": '<path d="M118 96L160 66M236 96L194 66M177 96v-6M177 83v-5M177 73v-3"/>'
             '<path d="M150 66h70"/>'
             '<path class="trail" d="M96 54q40-12 82-22"/>'
             '<g class="m"><path d="M182 30l28-8M200 25l-6-10M200 25l2 11M184 29l-4-6"/></g>',
    "克拉克／打拉": '<path class="m" d="M118 66Q158 34 196 56Q216 44 238 52"/>'
                 '<path d="M96 96Q160 70 240 74M116 96Q170 80 240 85M146 96Q192 89 240 94"/>'
                 '<path d="M200 74v-7M200 70l-4-4M200 70l4-4M222 76v-6M222 72l-3-3M222 72l3-3"/>',
    "馬尼拉": '<path class="sun m" d="M206 44a12 12 0 0 1 24 0"/>'
             '<path d="M108 96V62h14v34M126 96V46h12v50M142 96V68h16v28M162 96V38h10v58M167 38v-8M176 96V58h14v38M194 96V72h20v24"/>'
             '<path d="M96 96h144"/>',
}


# Hero flight path from Taipei (56,58) to the Philippines (214,236); the flyer's resting angle matches its end tangent.
ROUTE = "M56 58C190 30 300 140 214 236"


def city_art_svg(city):
    inner = CITY_ART.get(city, CITY_ART["宿霧"])
    return f'<svg class="city-art" viewBox="0 0 240 100" aria-hidden="true">{inner}</svg>'


DS_PIN = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2.5a7 7 0 0 0-7 7c0 5 7 12 7 12s7-7 7-12a7 7 0 0 0-7-7zm0 9.5a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5z"/></svg>'
DS_CAP = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m12 4 10 5-10 5L2 9z"/><path d="M6 11v5c3 2 9 2 12 0v-5"/></svg>'
DS_CHEV = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 6 6 6-6 6"/></svg>'


def sample_card(s, exams):
    """Static preview of the site's school card (mirrors cardHTML in the template)."""
    import html as h
    kind = f'<span class="kind" data-kind="{s["kind"]}">{s["kind"]}</span>' if s["kind"] in ("斯巴達", "半斯巴達", "親子") else ""
    tags = "".join(f'<span class="tag">{h.escape(t)}</span>' for t in [p for p in s["strengths"] if len(p) <= 14][:3])
    hint = f'<p class="hint">{DS_CAP}官方考場：{"・".join(exams)}</p>' if exams else ""
    return f'''<div class="surface school-card">
      <div class="ph" data-city="{s["city"]}">{city_art_svg(s["city"])}<span class="ph-badges">{kind}</span><span class="city-en">{s["cityEn"]}</span></div>
      <div class="school-body">
        <p class="meta loc">{DS_PIN}{s["city"]} · {h.escape(s["campus"])}</p>
        <h3>{h.escape(s["name"])}</h3>
        <div class="tags">{tags}</div>
        {hint}
        <div class="card-foot"><span>{"・".join(s["tags"])}</span><span class="go">{DS_CHEV}</span></div>
      </div>
    </div>'''


DS_CSS = r'''
.ds { padding: 40px 0 72px; }
.ds-head { margin-bottom: 36px; }
.ds-head h1 { font-size: clamp(30px, 4vw, 44px); margin-bottom: 10px; }
.ds-sec { margin-top: 48px; }
.ds-sec > h2 { margin-bottom: 6px; }
.ds-sec > .meta { margin-bottom: 18px; font-size: 15px; max-width: 46rem; }
.scale { padding: 20px; margin-bottom: 14px; }
.scale-head { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; margin-bottom: 14px; flex-wrap: wrap; }
.tiles { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; }
.tiles.n7 { grid-template-columns: repeat(7, 1fr); }
.tile { display: grid; gap: 6px; font-size: 13px; }
.tile i { display: block; height: 64px; border-radius: var(--r-sm); box-shadow: inset 0 0 0 1px rgba(27,33,25,.06); }
.tile b { font-weight: 600; }
.tile span { color: var(--faint); font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; }
.tile.key i { box-shadow: 0 0 0 2px #fff, 0 0 0 4px var(--ink); }
.accents { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.accent { padding: 0; overflow: hidden; display: flex; flex-direction: column; }
.accent.off { opacity: .72; }
.strip { display: grid; grid-template-columns: 2fr 1fr 1fr; height: 84px; }
.strip i { display: flex; align-items: flex-end; padding: 10px 12px; font-style: normal; font-size: 12px; font-weight: 600; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
.accent-body { padding: 18px 20px 20px; display: grid; gap: 10px; }
.accent-title { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
.status { font-size: 12.5px; font-weight: 600; padding: 2px 10px; border-radius: 999px; }
.status.rec { background: var(--green-soft); color: var(--green-dark); }
.status.alt { background: var(--fill); color: var(--muted); }
.status.no { background: var(--fill); color: var(--faint); text-decoration: line-through; }
.ratios { list-style: none; padding: 0; display: grid; gap: 6px; font-size: 13px; color: var(--muted); }
.ratios li { display: flex; align-items: center; gap: 10px; }
.ratios .pair { width: 34px; height: 24px; border-radius: 6px; display: grid; place-items: center; font-weight: 600; font-size: 12px; box-shadow: inset 0 0 0 1px rgba(27,33,25,.06); }
.ratios b { margin-left: auto; font-weight: 600; font-size: 12px; }
.ratios b.pass { color: var(--green-dark); }
.ratios b.large { color: var(--mango-ink); }
.ratios b.fail { color: #A8401F; }
.mix { padding: 20px; }
.mix-bar { display: flex; height: 44px; border-radius: var(--r-sm); overflow: hidden; margin: 12px 0 10px; box-shadow: inset 0 0 0 1px var(--line-gray); }
.mix-bar span { display: flex; align-items: center; padding: 0 12px; font-size: 12.5px; font-weight: 600; }
.mix-legend { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; font-size: 14px; }
.mix-legend b { display: block; }
.roles { padding: 6px 20px; }
.role { display: grid; grid-template-columns: 200px 1fr auto; gap: 16px; align-items: center; padding: 14px 0; }
.role + .role { border-top: 1px solid var(--line-gray); }
.role b { font-weight: 600; }
.preview { display: grid; gap: 16px; }
.preview-row { padding: 20px; display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
.preview-row h3 { width: 100%; font-size: 14px; color: var(--muted); margin-bottom: 2px; }
.dos { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.dos .surface { padding: 20px 22px; }
.dos h3 { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.dos h3 i { width: 10px; height: 10px; border-radius: 50%; }
.dos ul { padding-left: 18px; display: grid; gap: 6px; color: var(--muted); font-size: 15px; }
@media (max-width: 900px) {
  .accents, .dos { grid-template-columns: 1fr; }
  .tiles, .tiles.n7 { grid-template-columns: repeat(3, 1fr); }
  .role { grid-template-columns: 1fr; gap: 6px; }
  .mix-legend { grid-template-columns: 1fr; }
}
'''


def design_system(data_json):
    import json
    data = json.loads(data_json)
    by = lambda name, campus: next(s for s in data["schools"] if s["name"].startswith(name) and s["campus"] == campus)
    samples = [
        (by("PINES", "主校區"), ["IELTS", "TOEIC"]),
        (by("CIA", "麥克坦校區"), ["IELTS"]),
        (by("CIJ", "Liloan 校區"), []),
    ]

    scales = ""
    for key, title, use, steps in BRAND:
        tiles = "".join(
            f'<div class="tile{" key" if step == "500" else ""}"><i style="background:{hexv}"></i><b>{key}-{step}</b><span>{hexv}</span></div>'
            for step, hexv in steps
        )
        scales += f'<div class="surface scale"><div class="scale-head"><h3>{title}</h3><span class="meta">{use}</span></div><div class="tiles">{tiles}</div></div>'
    neutrals = "".join(
        f'<div class="tile"><i style="background:{hexv}"></i><b>{label}</b><span>{hexv}</span></div>'
        for _, hexv, label in NEUTRALS
    )

    accent_cards = ""
    for a in ACCENTS:
        cls = {"推薦": "rec", "備選": "alt", "不建議": "no"}[a["status"]]
        ex = "".join(
            f'<span class="badge" style="background:{a["soft"]};color:{a["ink"]}">{e}</span>' for e in a["examples"]
        ) + f'<span class="badge" style="background:{a["base"]};color:#fff">{a["examples"][0]}</span>'
        ratios = "".join([
            ratio_chip("#FFFFFF", a["base"], "白字放在主色上"),
            ratio_chip(a["ink"], a["soft"], "深色字放在淡色底"),
            ratio_chip(a["ink"], "#FFFFFF", "深色字放在白底"),
        ])
        accent_cards += f'''<article class="surface accent{" off" if cls == "no" else ""}">
          <div class="strip"><i style="background:{a["base"]};color:#fff">{a["base"]}</i><i style="background:{a["soft"]};color:{a["ink"]}">{a["soft"]}</i><i style="background:{a["ink"]};color:#fff">{a["ink"]}</i></div>
          <div class="accent-body">
            <div class="accent-title"><h3>{a["name"]}</h3><span class="status {cls}">{a["status"]}</span></div>
            <p><b>用在：</b>{a["use"]}</p>
            <p class="meta">{a["why"]}</p>
            <div class="tags">{ex}</div>
            <ul class="ratios">{ratios}</ul>
          </div>
        </article>'''

    roles = [
        ("主要動作", "加 LINE 諮詢、搜尋、送出、選取中的篩選", '<span class="btn btn-primary btn-sm">加 LINE 諮詢</span>'),
        ("精選與重點", "首頁精選標籤、標題螢光筆、半斯巴達", '<span class="badge">精選</span> <span class="kind" data-kind="半斯巴達">半斯巴達</span>'),
        ("強度與注意", "斯巴達、熱門、限時活動", '<span class="kind" data-kind="斯巴達">斯巴達</span> <span class="badge" style="background:var(--coral-soft);color:var(--coral-ink)">限時優惠</span>'),
        ("可信任的資訊", "官方考場、認證、小提醒", f'<span class="hint inline">{DS_CAP}官方考場：IELTS</span>'),
        ("家庭與親子", "親子學校、青少年營、家長常問", '<span class="kind" data-kind="親子">親子</span>'),
        ("一般資訊", "課程、城市、說明文字", '<span class="tag">ESL</span> <span class="tag">雅思</span>'),
    ]
    roles_html = "".join(f'<div class="role"><b>{r}</b><span class="meta">{d}</span><span>{x}</span></div>' for r, d, x in roles)
    cards = "".join(sample_card(s, ex) for s, ex in samples)

    body = f'''<main class="wrap ds">
  <header class="ds-head">
    <p class="eyebrow">FlyLingo 設計系統</p>
    <h1>色彩：一個主色、一個輔色、<br><span class="hl">三個強調色</span></h1>
    <p class="lede">飛語綠負責「可以按」，芒果黃負責「被選出來」。強調色只拿來分類資訊，不拿來做按鈕。每個顏色都有三階：主色、淡色底、深色字。</p>
  </header>

  <section class="ds-sec">
    <h2>1. 品牌色</h2>
    <p class="meta">外框粗的是主色（500）。淡色（50–100）當背景，深色（700–900）當文字。</p>
    {scales}
  </section>

  <section class="ds-sec">
    <h2>2. 中性色</h2>
    <p class="meta">淺灰是 App 背景，白色是區塊。文字只用三種灰階，不要再多。</p>
    <div class="surface scale"><div class="tiles n7">{neutrals}</div></div>
  </section>

  <section class="ds-sec">
    <h2>3. 強調色候選</h2>
    <p class="meta">挑選原則：色相避開綠色（避免和主色打架）、亮度和飛語綠相近（放在一起重量一致）、白字和深色字都通過 WCAG AA 對比 4.5。</p>
    <div class="accents">{accent_cards}</div>
  </section>

  <section class="ds-sec">
    <h2>4. 用量比例 60 · 30 · 10</h2>
    <div class="surface mix">
      <div class="mix-bar">
        <span style="flex:60;background:var(--app);color:var(--muted)">中性 60%</span>
        <span style="flex:30;background:var(--green);color:#fff">飛語綠 30%</span>
        <span style="flex:6;background:var(--mango)"></span>
        <span style="flex:2;background:var(--coral)"></span>
        <span style="flex:1.5;background:var(--ocean)"></span>
        <span style="flex:.5;background:var(--orchid)"></span>
      </div>
      <div class="mix-legend">
        <p><b>60% 中性</b><span class="meta">灰底、白色區塊、文字</span></p>
        <p><b>30% 飛語綠</b><span class="meta">按鈕、連結、選取、CTA 區塊</span></p>
        <p><b>10% 黃 + 強調色</b><span class="meta">一張卡片最多兩個強調色，而且意思不同</span></p>
      </div>
    </div>
  </section>

  <section class="ds-sec">
    <h2>5. 什麼資訊用什麼顏色</h2>
    <p class="meta">顏色代表意思。同一種意思全站用同一個顏色，使用者看久了就不用讀字。</p>
    <div class="surface roles">{roles_html}</div>
  </section>

  <section class="ds-sec">
    <h2>6. 套用在學校卡片</h2>
    <p class="meta">右上角是學校類型（珊瑚＝斯巴達、黃＝半斯巴達、紫＝親子），藍色條是有官方考場的學校。資料來自學校清單，不是編的。</p>
    <div class="cards">{cards}</div>
  </section>

  <section class="ds-sec">
    <h2>7. 規則</h2>
    <div class="dos">
      <div class="surface"><h3><i style="background:var(--green)"></i>要這樣做</h3><ul>
        <li>按鈕永遠是飛語綠，強調色不做按鈕</li>
        <li>淡色底一定配同色系的深色字</li>
        <li>一張卡片最多兩個強調色（例如「類型」＋「考場」），而且意思不同</li>
        <li>顏色要配文字，不能只靠顏色傳達意思</li>
      </ul></div>
      <div class="surface"><h3><i style="background:var(--coral)"></i>不要這樣做</h3><ul>
        <li>不要把強調色用在大面積背景</li>
        <li>不要在主色綠旁邊放另一種綠或青色</li>
        <li>不要把白字放在芒果黃上（對比只有 1.6）</li>
        <li>不要讓同一個顏色有兩種意思，例如珊瑚色只表示「強度／熱門」，不另外拿來表示錯誤</li>
      </ul></div>
    </div>
  </section>
</main>'''

    return f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FlyLingo 色彩設計系統</title>
{og_tags("flylingo-design-system.html")}
{favicon_link()}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;600;700&family=Work+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
{base_css()}
{SOFT_CSS.strip()}
{DS_CSS.strip()}
</style>
</head>
<body>
{body}
</body>
</html>
'''


def build(variant, data, word, star):
    html = TEMPLATE
    for key, value in {
        "__BASE_CSS__": base_css(),
        "__VARIANT_CSS__": variant["css"].strip(),
        "__OG__": og_tags(variant["file"]),
        "__FAVICON__": favicon_link(),
        "__THEME__": variant["theme"],
        "__LABEL__": variant["label"],
        "__EXTRA__": variant["extra"],
        "__HEAD_SOCIALS__": socials(skip=("line",)),
        "__FOOT_SOCIALS__": socials(),
        "__LINE_ICON__": LINE_ICON,
        "__ARROW__": ARROW,
        "__SEARCH_ICON__": SEARCH_ICON,
        "__WORD__": word,
        "__STAR__": star,
        "__CITY_ART__": json.dumps(CITY_ART, ensure_ascii=False),
        "__ROUTE__": ROUTE,
        "__ICONS__": json.dumps(icon_uris()),
    }.items():
        html = html.replace(key, value)
    return html.replace("__DATA__", data)


PROCESS_STEPS = [
    {"id": "01", "title": "需求諮詢", "summary": "告訴我們目標、時間和預算。",
     "you": ["學習目標", "出發時間與週數", "預算範圍", "住宿偏好"], "get": "整理好的條件"},
    {"id": "02", "title": "選校規劃", "summary": "比較城市、管理強度、住宿和總費用，縮小到 2–4 間。",
     "you": ["排出你的優先順序"], "get": "2–4 間候選學校"},
    {"id": "03", "title": "確認方案・報名", "summary": "選定學校後填寫報名表、簽約、付訂金。",
     "you": ["護照資料頁", "報名表", "緊急聯絡人", "訂金"], "get": "報價單與契約"},
    {"id": "04", "title": "取得入學文件", "summary": "我們向學校送件，你只要核對文件內容。",
     "you": ["核對英文姓名與日期"], "get": "入學許可、正式帳單"},
    {"id": "05", "title": "付款・機票・接機", "summary": "學校確認名額後再買機票，我們會幫你對好接機時段。",
     "you": ["付尾款", "買機票", "回傳電子機票"], "get": "接機確認、當地費用清單", "volatile": True},
    {"id": "06", "title": "入境文件・保險", "summary": "依國籍和停留天數，確認你需要準備哪些文件。",
     "you": ["確認護照效期", "填 eTravel（出發前 72 小時內）", "旅遊平安險／海外醫療險"], "get": "入境文件清單", "volatile": True},
    {"id": "07", "title": "行前說明", "summary": "出發前 1–2 週說明一次，出發前 48 小時再確認一次。",
     "you": ["參加行前說明", "照清單打包"], "get": "出發檢查清單"},
    {"id": "08", "title": "抵達・在學・結業", "summary": "接機入住後，第一週和課程中段我們會主動聯絡你。",
     "you": ["抵達後回報平安"], "get": "結業前都有固定窗口"},
]


# FAQ shown on the site. Replaces the sample answers inside flylingo.html
# (_build_flylingo.py needs spreadsheets that are not on this computer).
# Keep the ids: DATA.hot, the process page and #faq/<id> links point at them.
# "volatile" marks answers that depend on prices or government rules; re-check those before launch.
FAQ = [
    {"id": "fit", "title": "適不適合我", "volatile": False, "questions": [
        ["去幾週比較適合？", "常見是 4 到 12 週。想先習慣開口說英文，4 週可以當起點；想把程度拉上來，建議 8 週以上。實際週數要看你能請多久的假，諮詢時跟我們一起定。"],
        ["上班族假期不長，也能去嗎？", "可以。先告訴我們你能出發的日期，以及最多能去幾週。我們會找開課日對得上的學校，短期也排得了。"],
        ["英文程度不好也可以去嗎？", "可以。多數學校到校後會先做分級測驗，再依程度分班。沒有考過檢定也沒關係，諮詢時說一下你現在的程度就好。"],
    ]},
    {"id": "cost", "title": "費用", "volatile": True, "questions": [
        ["菲律賓遊學大概要準備多少錢？", "費用分成三塊：學費和住宿、當地雜費、機票。金額會隨週數、房型和淡旺季變動，所以網站不放固定價目。用 LINE 告訴我們學校和週數，我們回你最新報價。"],
        ["當地還要另付哪些錢？", "常見有學生許可 SSP、延簽、教材、水電和宿舍押金。各校項目和金額不同，正式報價會列出明細和有效期限。"],
        ["代辦費什麼時候談？", "第一次諮詢就會說明費用怎麼算，學費以外的支出也會一起列出來。退費和改期規定，以你簽的契約為準。"],
    ]},
    {"id": "city", "title": "城市與學校", "volatile": False, "questions": [
        ["宿霧、碧瑤、克拉克差在哪？", "宿霧學校多，生活機能也方便。碧瑤天氣涼，管理比較嚴的學校多。克拉克校園通常比較大，外師課也比較好安排。我們會先聽你要的管理強度和預算，再幫你縮小城市。"],
        ["學校那麼多，要怎麼選？", "先定三件事：城市、能接受的管理強度、預算。首頁六間是六種類型的例子，不是排名。全部校區都在學校清單，也可以把條件傳給我們，我們幫你縮小到 2 到 4 間。"],
        ["可以指定校區嗎？", "可以。同一個品牌常有好幾個校區，管理方式和房型都不一樣。學校清單是一間校區一張卡，報名也是指定到校區。"],
    ]},
    {"id": "course", "title": "課程與管理強度", "volatile": False, "questions": [
        ["斯巴達和半斯巴達差在哪？", "兩邊的課都很密集。差別在課以外：斯巴達平日通常不能外出，晚上有強制自習；半斯巴達平日下課後可以外出，門禁比較晚。選之前先想一件事：下課後你還想讀幾個小時。"],
        ["一對一每天有幾堂？", "多數學校一天會排好幾堂一對一，再加小班或團體課，堂數各校差很多。有開這門課，不代表每天都上。學校確定之後，我們會把課表跟你確認。"],
        ["想準備雅思或多益，可以嗎？", "可以。學校清單可以用雅思、多益、托福篩選，學校頁也會註明是不是官方考場。有開準備課程，不代表保證分數。報名前把上課方式和目標分數跟我們確認。"],
    ]},
    {"id": "stay", "title": "住宿與生活", "volatile": False, "questions": [
        ["都住在學校裡嗎？", "多數學校提供校內宿舍，也有校外宿舍或飯店式住宿。房型從單人房到多人房都有，每一間的住宿方式寫在學校頁。"],
        ["洗衣怎麼處理？", "多數學校有洗衣和房間清潔，每週次數和要不要另外收費，各校不同。學校頁的「洗衣清潔」有目前查到的做法，報名前我們會再跟你確認一次。"],
        ["伙食吃得慣嗎？", "校內住宿多半含餐，菜色以當地料理為主。有吃素、過敏或其他飲食限制，諮詢時先告訴我們，我們會把它放進選校條件。"],
    ]},
    {"id": "visa", "title": "簽證、SSP、eTravel", "volatile": True, "questions": [
        ["SSP 和 eTravel 是什麼？要自己辦嗎？", "SSP 是在菲律賓上語言課程用的學生許可，由學校向移民局申請，不用自己跑。eTravel 是菲律賓官方的線上入境申報，要自己填。目前是出發前 72 小時內，到移民局官網登記；如果時限有改，以官網為準。請認明官方網站，不要用收費的代填網站。"],
        ["台灣護照可以待幾天？", "停留天數要看你的護照，以及你是短期入境還是留下來上課。免簽和延簽規定會調整。我們會依你的護照和就讀週數，告訴你要辦哪些手續。"],
        ["需要自己先辦保險嗎？", "建議出發前自己投保旅遊平安險或海外醫療險。需要哪些保障，行前說明時會跟你確認。"],
    ]},
    {"id": "agency", "title": "代辦與準備", "volatile": False, "questions": [
        ["找代辦和自己報名差在哪？", "自己報名，選校、文件、付款和接機都要自己跟學校確認。找飛語，這些我們一起處理，出發後也有固定的 LINE 窗口。學校官網還是可以看，報名請走飛語，我們才跟得上你的進度。"],
        ["第一次諮詢要準備什麼？", "準備學習目標、大概週數、預算範圍和住宿偏好就夠了。沒有檢定成績也可以開始。護照影本等文件，等方案確定後再提供。"],
        ["諮詢要收費嗎？", "用官方 LINE 做第一次諮詢，不收費。確定要報名之後，才會進入報名和簽約。"],
    ]},
    {"id": "depart", "title": "出發與抵達", "volatile": True, "questions": [
        ["機票可以自己訂嗎？", "可以，但要先對上這間學校的接機日和抵達時段。不是每一間都每天接機。請等學校確認名額、接機時間也對好之後，再訂票。"],
        ["誰來接機？", "航班確認後，由學校或飛語依該校規定安排接機。出發前你會收到接機確認，裡面有時間、地點和聯絡方式。"],
        ["下飛機後要做什麼？", "行前說明會先走一次：入境、找到接機人員、到校入住。eTravel 這類入境申報，要在官方規定的時間內完成。"],
    ]},
    {"id": "support", "title": "在學支援", "volatile": False, "questions": [
        ["到了學校還可以找飛語嗎？", "可以。入住、上課到結業，課程、住宿或身體不舒服，都可以用原來的 LINE 找飛語。"],
        ["想換老師或換房怎麼辦？", "先告訴我們發生了什麼、你希望怎麼調整。我們會跟學校溝通。能不能換，要看學校規定和當時的名額。"],
        ["結業後還會聯絡嗎？", "結業時會確認結業文件和返台安排。之後想再排一趟，用同一個 LINE 聯絡即可。"],
    ]},
    {"id": "parent", "title": "家長常問", "volatile": False, "questions": [
        ["未成年可以自己去嗎？", "要先確認孩子的年齡、有沒有家長陪同，以及學校收不收這個年齡。確認可以之後，選校和報名跟一般學員同一套流程，由飛語協助。"],
        ["家長怎麼知道孩子平安抵達？", "出發前會登記緊急聯絡人。孩子抵達並入住後，會回報平安。在學期間的聯絡窗口，也會一併給家長。"],
        ["親子課程和一般 ESL 差在哪？", "親子課程會依孩子的年齡排課表和作息，節奏跟成人 ESL 不同。學校清單可以用「親子」篩選。適不適合，還是要看孩子的年齡和生活習慣。"],
    ]},
]


# Blog posts, shaped like a WordPress post so they can move there unchanged:
#   title / excerpt / category -> WordPress post fields
#   cover  -> featured image URL ("" falls back to the illustration in BLOG_ART, coloured by tone)
#   html   -> post content. Only plain editor output: h2, h3, p, ul, ol, table, figure/img,
#             blockquote (shown as a tip), details/summary (WordPress "Details" block, shown as FAQ).
#             No classes needed; the site styles these tags. Every h2 becomes a table-of-contents anchor.
ARTICLES = [
    {
        "id": "packing",
        "kicker": "行前準備",
        "tone": "mango",
        "cover": "",
        "title": "菲律賓遊學行李清單：哪些一定要帶，哪些到當地再買",
        "excerpt": "一次去一兩個月，行李最容易帶太多。這份清單分成必帶和當地買得到，出發前照著點一次。",
        "html": """
<p>短途旅行常常一個箱子就走。遊學要待一到兩個月，行李反而要想清楚：哪些東西在菲律賓不好買，哪些到了再買比較省空間。</p>
<blockquote><p>先記三件事：證件文件、慣用藥品、隱形眼鏡要從台灣帶足。其他生活用品，當地大型商場幾乎都買得到。</p></blockquote>

<h2>證件與文件</h2>
<p>這些文件飛語會在行前說明時一起核對。出發前一晚，照下面再點一次。</p>
<ul>
<li>護照正本（建議效期還有 6 個月以上）</li>
<li>護照影本，手機也存一份</li>
<li>回程或下一段機票</li>
<li>入學許可信、接機資訊</li>
<li>海外醫療保險單</li>
<li>大頭照 2–4 張</li>
<li>少量現金（美金或披索）</li>
</ul>
<blockquote><p>入境時可能會被要求出示回程或下一程機票。存在手機裡可以，但要打得開。</p></blockquote>

<h2>衣物</h2>
<p>除了碧瑤，菲律賓多數城市一年四季都像台灣的夏天。帶一週份就夠，學校通常有洗衣服務。</p>
<table>
<thead><tr><th>要帶什麼</th><th>為什麼</th></tr></thead>
<tbody>
<tr><td>夏季衣物一週份</td><td>學校多半每週洗衣 1–2 次，不用多帶</td></tr>
<tr><td>薄外套 1–2 件</td><td>教室和宿舍冷氣常開很強</td></tr>
<tr><td>保暖長袖、外套</td><td>去碧瑤必帶，山上早晚涼，也常下雨</td></tr>
<tr><td>好走的鞋、拖鞋</td><td>雨季午後常有雷陣雨，拖鞋很實用</td></tr>
<tr><td>泳衣</td><td>海邊城市和有泳池的學校都用得到</td></tr>
</tbody>
</table>
<blockquote><p>有些學校對上課服裝有規定，例如不能穿太短或細肩帶。報名後看一下學校的生活守則。</p></blockquote>

<h2>生活用品</h2>
<table>
<thead><tr><th>要帶什麼</th><th>為什麼</th></tr></thead>
<tbody>
<tr><td>盥洗旅行組</td><td>先帶小瓶，到當地再買大瓶</td></tr>
<tr><td>隱形眼鏡和藥水</td><td>當地要到眼鏡行才買得到，建議帶足</td></tr>
<tr><td>防曬、防蚊液</td><td>太陽很強，蚊子也多，兩樣都要</td></tr>
<tr><td>生理用品</td><td>帶自己習慣的牌子比較安心</td></tr>
</tbody>
</table>

<h2>3C 與電器</h2>
<p>菲律賓電壓是 220V，很多插座和台灣一樣是雙平腳。手機、筆電的充電器多半支援 100–240V，可以直接用。</p>
<ul>
<li>手機、筆電或平板和充電線</li>
<li>行動電源（只能放隨身行李）</li>
<li>支援 220V 的吹風機或離子夾</li>
</ul>
<blockquote><p>台灣買的吹風機大多只支援 110V，插下去容易燒壞。買旅行用的雙電壓款，或到當地再買。</p></blockquote>

<h2>常備藥品</h2>
<p>國外看醫生不便宜，小感冒先吃自己習慣的藥最安心。藥品盡量保留原包裝，過海關比較好說明。</p>
<ul>
<li>感冒藥、止痛退燒藥</li>
<li>腸胃藥、止瀉藥、過敏藥</li>
<li>外傷藥和 OK 繃</li>
<li>個人處方藥（附英文說明）</li>
</ul>

<h2>食物</h2>
<p>想帶台灣零食可以，帶乾的、包裝完整的，例如餅乾和沒有肉塊的泡麵。肉類、肉乾這類製品，海關可能不讓帶。不確定就不要帶。當地大型超市也買得到一些台灣泡麵。</p>

<h2>常見問題</h2>
<details><summary>要帶洗衣精嗎？</summary><p>不用。多數學校有洗衣服務，自助洗衣的話第一週通常會帶大家去商場採買，到時再買就好。</p></details>
<details><summary>去碧瑤要多帶什麼？</summary><p>多帶幾件長袖和一件保暖外套，再加一把傘。碧瑤在山上，比宿霧涼很多，也比較常起霧下雨。</p></details>
<details><summary>行李超重怎麼辦？</summary><p>盥洗用品和文具都可以到當地買。先把這兩類拿出來，通常就能省下好幾公斤。</p></details>
""",
    },
    {
        "id": "cities",
        "kicker": "選城市",
        "tone": "blue",
        "cover": "",
        "title": "宿霧、碧瑤、克拉克怎麼選？差在天氣、步調和管得多緊",
        "excerpt": "三個城市沒有誰比較好，只有適不適合你。先看一張表，再看你在意哪一點。",
        "html": """
<p>很多人第一次查菲律賓遊學，會先被宿霧的海景吸引。但選城市其實是在選一種生活步調：天氣、學校類型、假日能做什麼，都會跟著城市走。</p>

<h2>先看一張表</h2>
<table>
<thead><tr><th>城市</th><th>適合誰</th></tr></thead>
<tbody>
<tr><td>宿霧</td><td>學校最多、選擇最廣；海邊和生活機能都方便，適合想兼顧學習和生活的人</td></tr>
<tr><td>碧瑤</td><td>天氣涼、步調慢，斯巴達學校多，適合想專心讀書的人</td></tr>
<tr><td>克拉克</td><td>校園大、外師課比較容易找，適合想多練不同口音的人</td></tr>
</tbody>
</table>

<h2>宿霧：選擇最多</h2>
<p>宿霧的學校從半斯巴達到度假型都有，週末可以跳島、潛水。選擇多的另一面是容易被照片帶著走，報名前要先想清楚自己要多少管理。</p>

<h2>碧瑤：適合想專心的人</h2>
<p>碧瑤在山上，整年都比較涼。學校常把平日和晚上排滿，外面能玩的也比較少，比較容易把時間花在讀書上。</p>

<h2>克拉克：校園大、外師多</h2>
<p>克拉克的學校校地常比較大，也比較容易安排外師課。它不是小一號的宿霧，進城方式和作息都不同，適合想換個環境的人。</p>

<h2>打拉和馬尼拉</h2>
<p>清單裡也有打拉和馬尼拉的校區。打拉在克拉克附近，生活更單純；馬尼拉是首都，生活機能最完整，但通勤和人潮也最多。</p>

<h2>問自己四個問題</h2>
<ol>
<li>我能接受平日不能外出嗎？</li>
<li>我怕熱還是怕冷？</li>
<li>假日想玩，還是想多讀一點？</li>
<li>我想多上外師課嗎？</li>
</ol>
<blockquote><p>把四題的答案傳給飛語，我們會幫你從 43 個校區縮小到 2–4 間。</p></blockquote>

<h2>常見問題</h2>
<details><summary>第一次去，選哪個城市比較合適？</summary><p>很多人從宿霧開始，因為學校多、生活機能也比較方便。如果你知道自己容易分心，可以先看碧瑤。最後還是要看你的目標，以及你能接受多嚴格的管理。</p></details>
<details><summary>可以一趟去兩個城市嗎？</summary><p>可以，但兩間學校的開學日要接得上。想這樣排，先跟飛語講，我們再對日期。</p></details>
""",
    },
    {
        "id": "sparta",
        "kicker": "選強度",
        "tone": "coral",
        "cover": "",
        "title": "斯巴達、半斯巴達差在哪？先問自己晚上還讀不讀",
        "excerpt": "名稱聽起來差很多，實際差別在平日能不能外出、晚上有沒有自習。看完就知道你適合哪一種。",
        "html": """
<p>斯巴達和半斯巴達都是密集課，差別在課以外的時間。報名前先想清楚：下課後，你希望自己在做什麼？</p>

<h2>兩種一起比</h2>
<table>
<thead><tr><th>類型</th><th>差在哪</th></tr></thead>
<tbody>
<tr><td>斯巴達</td><td>平日不能外出或有門禁，晚上有強制自習，週末才能外出</td></tr>
<tr><td>半斯巴達</td><td>課一樣密，但平日下課後可以外出，門禁時間比較晚</td></tr>
<tr><td>彈性・度假型</td><td>上課以外自己安排，適合自律、或有工作要處理的人</td></tr>
</tbody>
</table>

<h2>斯巴達的一天大概長這樣</h2>
<p>以下是常見排法，各校時間不同，實際以學校課表為準。</p>
<table>
<thead><tr><th>時段</th><th>在做什麼</th></tr></thead>
<tbody>
<tr><td>早上</td><td>早餐、晨間單字測驗</td></tr>
<tr><td>上午到下午</td><td>一對一和小班課，中間午休</td></tr>
<tr><td>傍晚</td><td>晚餐、自由時間</td></tr>
<tr><td>晚上</td><td>強制自習，點名後就寢</td></tr>
</tbody>
</table>

<h2>哪一種適合你</h2>
<ul>
<li>一放鬆就會滑手機，需要被管：斯巴達</li>
<li>要回工作訊息，但想密集上課：半斯巴達</li>
<li>很自律，想自己安排時間：彈性型</li>
<li>第一次出國，想有人照顧：斯巴達或半斯巴達</li>
</ul>
<blockquote><p>各校的名稱不一定統一，有的寫「制度型」或「度假型」。看學校頁上的管理強度條，比只看名字準。</p></blockquote>

<h2>常見問題</h2>
<details><summary>斯巴達會不會太累？</summary><p>第一週通常最累。如果讀下來不適合，跟我們說，我們再問學校能不能調整課表。能不能轉成半斯巴達，要看該校規定和名額。</p></details>
<details><summary>半斯巴達進步會比較慢嗎？</summary><p>不一定。差別在下課後你會不會自己複習。知道自己會讀的人，半斯巴達通常比較能撐完整個週期。</p></details>
""",
    },
]


# School photo galleries, keyed by school id (the part after #school/ in the URL).
# Each item is a photo {"src", "cat", "caption"} or a YouTube video {"video", "cat", "caption"}.
# "cat" groups photos into the gallery's category buttons (校園、教室、宿舍、餐廳、設施、影片…).
# Schools not listed here show illustrated placeholders until licensed photos arrive.
# Example:
#   "cia-mactan-campus": [
#       {"src": "https://…/cia-front.jpg", "cat": "校園", "caption": "校園入口"},
#       {"src": "https://…/cia-room.jpg", "cat": "宿舍", "caption": "雙人房"},
#       {"video": "https://www.youtube.com/watch?v=XXXXXXXXXXX", "cat": "影片", "caption": "校園導覽"},
#   ],
SCHOOL_PHOTOS = {}


def tidy_address(text):
    # Source data sometimes puts 區 before the name: "區 麥克坦" -> "麥克坦區".
    def repl(match):
        name = match.group(2).strip()
        gap = " " if re.search(r"[A-Za-z]", name) else ""
        return f"{match.group(1)}{name}{gap}區"

    return re.sub(r"([，,]|^)\s*區\s+([^，,]+)", repl, text or "")


def with_process(data_json):
    import json
    data = json.loads(data_json)
    data["steps"] = PROCESS_STEPS
    data["faq"] = FAQ
    data["articles"] = ARTICLES
    for school in data["schools"]:
        school["photos"] = SCHOOL_PHOTOS.get(school["id"], [])
        if school.get("address"):
            school["address"] = tidy_address(school["address"])
    return json.dumps(data, ensure_ascii=False)


def main():
    data, word, star = extract(SOURCE.read_text())
    data = with_process(data)
    for variant in VARIANTS:
        out = ROOT / variant["file"]
        out.write_text(build(variant, data, word, star))
        print(f"wrote {out.name} ({out.stat().st_size} bytes)")
    ds = ROOT / "flylingo-design-system.html"
    ds.write_text(design_system(data))
    print(f"wrote {ds.name} ({ds.stat().st_size} bytes)")
    # flylingo-v3.html 是從 v1 複製後手改的，這個函式不會動它。
    # 這裡只重建先前的行程單實驗 flylingo-v3-itinerary.html。
    from _build_v3 import main as build_v3
    build_v3(data, word, star)


if __name__ == "__main__":
    main()
