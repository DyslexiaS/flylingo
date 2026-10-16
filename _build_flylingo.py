#!/usr/bin/env python3
"""Build the single-file FlyLingo prototype. Deleted after flylingo.html is written."""
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path("/Users/haikyo./WorkSpace/light-tool/flylingo")
SCHOOL_XLSX = Path("/Users/haikyo./Downloads/菲律賓遊學網站_學校清單.xlsx")
PROCESS_XLSX = Path("/Users/haikyo./Downloads/菲律賓遊學網站_八大服務流程_設計師完整資料_V1(1).xlsx")
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

FEATURED = [
    ("CIA", "麥克坦校區", "宿霧", "大型半斯巴達"),
    ("EV Academy", "主校區", "宿霧", "考試・高強度"),
    ("Cebu Blue Ocean Academy", "主校區", "宿霧", "度假海濱"),
    ("PINES", "主校區", "碧瑤", "涼爽・斯巴達"),
    ("CIP", "主校區", "克拉克", "外師"),
    ("CIJ Academy", "Liloan 校區", "宿霧", "親子"),
]

COURSE_COLS = [
    (4, "ESL"),
    (5, "雅思"),
    (7, "多益"),
    (8, "托福"),
    (9, "商務"),
    (10, "親子"),
]

CITY_EN = {
    "宿霧": "Cebu",
    "碧瑤": "Baguio",
    "克拉克": "Clark",
    "克拉克／打拉": "Tarlac",
    "馬尼拉": "Manila",
}


def colrow(ref):
    col = "".join(c for c in ref if c.isalpha())
    row = int("".join(c for c in ref if c.isdigit()))
    n = 0
    for ch in col:
        n = n * 26 + (ord(ch) - 64)
    return n, row


def load_sheet(path, sheet):
    with zipfile.ZipFile(path) as zf:
        root = ET.fromstring(zf.read(sheet))
    rows = {}
    for cell in root.findall(".//m:c", NS):
        ref = cell.attrib.get("r")
        if not ref:
            continue
        col, row = colrow(ref)
        node = cell.find("m:v", NS)
        inline = cell.find("m:is", NS)
        if node is not None and node.text:
            val = node.text
        elif inline is not None:
            val = "".join(t.text or "" for t in inline.findall(".//m:t", NS))
        else:
            val = ""
        rows.setdefault(row, {})[col] = val.replace("\r", "").strip()
    return rows


def split_bits(text):
    if not text:
        return []
    parts = re.split(r"[；;]", text)
    return [p.strip() for p in parts if p.strip() and p.strip() != "—"]


def slugify(*parts):
    raw = "-".join(parts).lower()
    raw = raw.replace("／", "-").replace("'", "")
    raw = re.sub(r"[^a-z0-9]+", "-", raw)
    return raw.strip("-")


def style_group(style):
    text = style or ""
    if "半斯巴達" in text:
        return "半斯巴達"
    if "斯巴達" in text:
        return "斯巴達"
    if "親子" in text:
        return "親子"
    return "其他"


def schools():
    master = load_sheet(SCHOOL_XLSX, "xl/worksheets/sheet2.xml")
    filt = load_sheet(SCHOOL_XLSX, "xl/worksheets/sheet3.xml")
    items = []
    seen = set()
    for row in range(5, 80):
        if row not in master or not master[row].get(2):
            continue
        m = master[row]
        f = filt.get(row, {})
        if (m.get(1), m.get(4)) != (f.get(1), f.get(3)):
            raise SystemExit(f"row {row} master/filter mismatch")
        sid = slugify(m.get(3, ""), m.get(5, "") or m.get(4, ""))
        if sid in seen:
            sid = slugify(sid, m.get(1, ""))
        seen.add(sid)
        tags = [label for col, label in COURSE_COLS if f.get(col) == "✓"]
        strengths = split_bits(m.get(22, ""))
        items.append({
            "id": sid,
            "city": m.get(1, ""),
            "cityEn": CITY_EN.get(m.get(1, ""), ""),
            "name": m.get(2, ""),
            "brand": m.get(3, ""),
            "campus": m.get(4, ""),
            "style": m.get(7, ""),
            "established": m.get(8, ""),
            "capacity": m.get(9, ""),
            "address": m.get(10, ""),
            "addressEn": m.get(11, ""),
            "phone": m.get(12, ""),
            "email": m.get(13, ""),
            "website": m.get(14, ""),
            "contactForm": m.get(15, ""),
            "facebook": m.get(16, ""),
            "instagram": m.get(17, ""),
            "maps": m.get(19, ""),
            "courses": m.get(20, ""),
            "suitable": m.get(21, ""),
            "strengths": strengths,
            "facilities": m.get(23, ""),
            "accommodation": m.get(24, ""),
            "laundry": m.get(25, ""),
            "accreditation": m.get(26, ""),
            "checked": m.get(32, "") or "2026-10-03",
            "tags": tags[:5],
            "filters": tags,
            "kind": style_group(m.get(7, "")),
        })
    if len(items) != 43:
        raise SystemExit(f"expected 43 schools, got {len(items)}")
    featured = []
    for brand, campus, city, note in FEATURED:
        match = next((s for s in items if s["brand"] == brand and s["campus"] == campus and s["city"] == city), None)
        if not match:
            raise SystemExit(f"missing featured {brand} {campus} {city}")
        featured.append({"id": match["id"], "note": note})
    return items, featured


def steps():
    front = load_sheet(PROCESS_XLSX, "xl/worksheets/sheet2.xml")
    detail = load_sheet(PROCESS_XLSX, "xl/worksheets/sheet3.xml")
    summary = {}
    for row in range(5, 20):
        if row not in front or not front[row].get(1):
            continue
        summary[front[row][1]] = {
            "id": front[row][1],
            "title": front[row].get(2, ""),
            "en": front[row].get(3, ""),
            "summary": front[row].get(4, ""),
        }
    grouped = {sid: [] for sid in summary}
    for row in range(5, 200):
        if row not in detail or not detail[row].get(1):
            continue
        sid = detail[row][1]
        if sid not in grouped:
            continue
        grouped[sid].append({
            "name": detail[row].get(3, ""),
            "we": detail[row].get(4, ""),
            "you": detail[row].get(5, ""),
            "out": detail[row].get(6, ""),
        })
    ordered = []
    for sid in sorted(summary):
        item = summary[sid]
        item["volatile"] = sid >= "05"
        item["items"] = grouped[sid]
        ordered.append(item)
    if len(ordered) != 8:
        raise SystemExit(f"expected 8 steps, got {len(ordered)}")
    return ordered


def svg_inner(path):
    text = Path(path).read_text()
    text = re.sub(r"^.*?<svg[^>]*>", "", text, count=1, flags=re.S)
    text = re.sub(r"</svg>\s*$", "", text)
    return text.strip()


FAQ = [
    {
        "id": "fit",
        "title": "適不適合我",
        "volatile": False,
        "questions": [
            ("去幾週比較適合？", "範例回答。很多人會先看 4 到 12 週：想開口就用 4 週試水溫，想把程度拉起來再拉長。實際週數要看你能請假多久，這題請直接問飛語。"),
            ("上班族請得到假嗎？", "範例回答。飛語會先問你的出發日和最長週數，再排除對不上假期的學校，不會先丟一長串校名。"),
            ("英文很破也可以去嗎？", "範例回答。可以。多數語言學校會在到校後分班。沒有正式成績也能先用自評開始談，不必在網站上假裝已經測過級。"),
        ],
    },
    {
        "id": "cost",
        "title": "費用",
        "volatile": True,
        "questions": [
            ("菲律賓遊學大概要準備多少錢？", "範例回答。學費、住宿、當地雜費和機票要分開看，而且會隨週數、房型、淡旺季變動。這份原型沒有價格表，請用 LINE 問飛語要最新區間。"),
            ("當地還要另付哪些錢？", "範例回答。SSP、延簽、教材、水電、押金各校不同，不能把某一間的數字套到全部學校。正式報價會標有效期間。"),
            ("代辦費什麼時候談？", "範例回答。第一次諮詢會先把總預算範圍談清楚，包含學費以外的項目。契約與退改規定以正式文件為準，網站不放條款全文。"),
        ],
    },
    {
        "id": "city",
        "title": "城市與學校",
        "volatile": False,
        "questions": [
            ("宿霧、碧瑤、克拉克差在哪？", "範例回答。宿霧選擇多、生活機能高；碧瑤較涼、學校多半管得較緊；克拉克校園通常較大，也有外師課程。飛語會先聽你的強度和預算，再縮小城市。"),
            ("網站上的六間學校是推薦排名嗎？", "範例回答。不是。首頁那六間只是風格對照：大型、考試、度假、涼爽、外師、親子。全部 43 個校區都在學校清單裡。"),
            ("可以指定校區嗎？", "範例回答。可以。同一品牌常有好幾個校區，管理方式和房型不一樣。清單是以校區為一張卡，不是把整個品牌合成一間。"),
        ],
    },
    {
        "id": "course",
        "title": "課程與強度",
        "volatile": False,
        "questions": [
            ("斯巴達和半斯巴達差在哪？", "範例回答。斯巴達通常平日管制外出、晚上要自習；半斯巴達保留部分外出，課表仍然緊。選之前先想你下班後還能讀幾小時，而不是只看校名。"),
            ("一對一每天有幾堂？", "範例回答。常見是每天數堂一對一加上團體課，各校差很多。卡片上的課程標籤只代表有開這類課，堂數請向飛語確認。"),
            ("可以衝雅思或多益嗎？", "範例回答。清單可以用雅思、多益、托福篩選。有沒有保證班、是不是考場，要看個別學校頁，不要把有開課當成保證分數。"),
        ],
    },
    {
        "id": "stay",
        "title": "住宿與生活",
        "volatile": False,
        "questions": [
            ("都住在學校裡嗎？", "範例回答。很多語言學校是校內宿舍，也有校外或飯店式。房型從單人到多人都有，詳情頁會寫這間學校目前查到的住宿方式。"),
            ("洗衣怎麼處理？", "範例回答。這是台灣學生常問的事，所以學校頁有單獨的洗衣欄位。次數和是否另收費，以該校最新資料為準。"),
            ("伙食吃得慣嗎？", "範例回答。多數校內住宿含餐。若有飲食禁忌，要在諮詢時先講，飛語會把它列進不能妥協的條件。"),
        ],
    },
    {
        "id": "visa",
        "title": "簽證、SSP、eTravel",
        "volatile": True,
        "questions": [
            ("SSP 和 eTravel 是飛語核發的嗎？", "範例回答。不是。SSP 是就讀語言課程時，依菲律賓移民局規定由學校辦理的學習文件。eTravel 是官方入出境申報，請依官方最新時限登記，不要連到收費的假網站。"),
            ("台灣護照可以待幾天？", "範例回答。停留天數、免簽和延簽都跟國籍、護照和當時政策有關。飛語會依你的國籍和就讀週數確認最新做法，網站不用一條規則套全部人。"),
            ("需要自己先辦保險嗎？", "範例回答。出發前會依停留時間確認保險需求。保額和要保項目會變，請以行前說明拿到的清單為準。"),
        ],
    },
    {
        "id": "agency",
        "title": "代辦與準備",
        "volatile": False,
        "questions": [
            ("找代辦和自己報名差在哪？", "範例回答。飛語負責把目標、學校、文件、付款和接機串起來，並在出發後留支援窗口。學校官網仍然可以看，但網站上的綠色按鈕是找飛語，不是把你直接丟給學校招生。"),
            ("第一次諮詢要準備什麼？", "範例回答。目標、大概週數、預算區間、住宿偏好就夠了。沒有考試成績也可以開始。護照影本等文件會在確認方案後再收。"),
            ("諮詢要收費嗎？", "範例回答。用官方 LINE 做第一次諮詢，不先收費。正式報名與契約是後面的步驟。"),
        ],
    },
    {
        "id": "depart",
        "title": "出發與抵達",
        "volatile": True,
        "questions": [
            ("機票可以自己訂嗎？", "範例回答。可以，但要先對上該校的接機日和抵達時段。不是所有學校都週日接機，請勿依別校的規則訂票。"),
            ("誰來接機？", "範例回答。確認航班後，由學校或飛語依該校規則預約接機。出發前你會拿到接機確認，而不是只在群組裡口頭說。"),
            ("下飛機後要做什麼？", "範例回答。行前說明會走一次入境、找接機和入住。eTravel 等申報請依當時官方時限完成。"),
        ],
    },
    {
        "id": "support",
        "title": "在學支援",
        "volatile": False,
        "questions": [
            ("到了學校還可以找飛語嗎？", "範例回答。可以。抵達、入住、上課到結業都有支援窗口。課程、住宿或身體不舒服，不要只留在學校群組裡。"),
            ("想換老師或換房怎麼辦？", "範例回答。先跟飛語說你遇到的情況和希望改成什麼。能不能換，要看該校規定和當時名額。"),
            ("結業後還會聯絡嗎？", "範例回答。結業時會確認文件和返台安排，也會請你留回饋。若你要接著規劃下一趟，可以沿用同一條 LINE。"),
        ],
    },
    {
        "id": "parent",
        "title": "家長常問",
        "volatile": False,
        "questions": [
            ("未成年可以自己去嗎？", "範例回答。要先講年齡、是否有人陪同，以及學校收不收該年齡。這不是另一條產品線，仍走同一套學校和同一條代辦。"),
            ("家長怎麼知道人有被接到？", "範例回答。航班、接機和入住會串在同一段流程裡。出發前會留下緊急聯絡人和在學時的窗口。"),
            ("親子課程和一般 ESL 差在哪？", "範例回答。清單可以用「親子」篩選。首頁的 CIJ 卡是這類風格的例子，不是排名第一。適不適合仍要看孩子的年齡和作息。"),
        ],
    },
]

ARTICLES = [
    {
        "id": "cities",
        "title": "宿霧、碧瑤、克拉克，差在氣候和被管得多緊",
        "kicker": "選城市",
        "body": [
            "範例文章。這篇是給還在比城市的人，上線前可以換成飛語自己的觀察。",
            "宿霧的學校最多，海邊和生活機能都在，半斯巴達到度假型都有。人多、選擇多，缺點是如果你沒有先講清楚強度，很容易被照片帶著走。",
            "碧瑤比較涼，學校常把平日和晚上排滿。想少出門、把時間用在課上的人，會比一直看海的校區合適。",
            "克拉克的校園常常比較大，也比較容易遇到外師課。它不是縮小版宿霧，作息和進城的方式都不一樣。",
            "打拉、馬尼拉在清單裡各有校區，首頁沒有把它們放進六張對照卡。要看全部，進學校清單即可。",
            "飛語會先問你能接受的門禁、天氣和預算，再縮小城市。城市沒有標準答案。",
        ],
    },
    {
        "id": "sparta",
        "title": "斯巴達和半斯巴達，先問晚上你還讀不讀",
        "kicker": "選強度",
        "body": [
            "範例文章。用來說明兩種常見管理方式，不是替任何一間學校背書。",
            "斯巴達通常代表平日外出少、晚上有自習或門禁。課表密的人進步空間在於你真的會坐在位子上。",
            "半斯巴達仍是密集課，但留一點外出。適合還要處理工作訊息、或知道自己被關太緊會反抗的人。",
            "名稱各校不完全一樣。有的寫制度型，有的寫彈性，有的寫度假型。看學校頁上的管理風格，比只記口號準。",
            "首頁六張卡把高強度、度假、外師、親子分開，是為了讓你看見差別，不是名次。",
        ],
    },
    {
        "id": "dates",
        "title": "簽證、SSP、費用為什麼要寫最後更新",
        "kicker": "維護",
        "body": [
            "範例文章。給之後維護網站的人，也給正在比較代辦的客人。",
            "eTravel 的登記時限、SSP 怎麼辦、延簽天數、當地雜費，都可能改。寫成永久規定，過期了還掛在頁面上，客人會以為是飛語保證的。",
            "所以這份原型把費用、簽證、SSP、eTravel、以及代辦流程的後四步，都標了最後更新。學校頁則標資料查核日，目前這批學校資料的查核日是 2026-10-03。",
            "價格不在這版網站上。沒有有效期間的學費，寧可不放。",
            "規定改了，就改那一區的日期和句子，不必整站重寫。",
        ],
    },
]

HOT = ["cost", "fit", "course", "visa"]


def main():
    school_items, featured = schools()
    step_items = steps()
    data = {
        "updated": "2026-10-10",
        "schools": school_items,
        "featured": featured,
        "steps": step_items,
        "faq": FAQ,
        "hot": HOT,
        "articles": ARTICLES,
        "line": "https://lin.ee/oDiSotr",
        "threads": "https://www.threads.com/@sailingo2026",
        "instagram": "https://www.instagram.com/sailingo2026",
        "facebook": "https://www.facebook.com/share/1E7bGA2M6w",
    }
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    word = svg_inner(ROOT / "icons" / "Flylingo 橫式.svg")
    star = svg_inner(ROOT / "icons" / "FlyLingo Shooting Star Logo.svg")
    html = TEMPLATE.replace("__WORD__", word).replace("__STAR__", star).replace("__DATA__", payload)
    out = ROOT / "flylingo.html"
    out.write_text(html)
    print(f"wrote {out} ({out.stat().st_size} bytes), schools {len(school_items)}, steps {len(step_items)}")


TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FlyLingo 飛語｜從語言出發，飛向世界</title>
<!--
  FlyLingo 飛語原型。把這一個檔案傳給客戶，雙擊用瀏覽器開啟。

  以後要換的地方：
  - 範例回饋：搜尋「範例回饋」
  - 範例回答：搜尋「範例回答」
  - 範例文章：搜尋「範例文章」
  - 會變動的日期：搜尋「最後更新」與「資料查核」
  - 官方 LINE：https://lin.ee/oDiSotr
  - Threads：https://www.threads.com/@sailingo2026
  - Instagram：https://www.instagram.com/sailingo2026
  - Facebook：https://www.facebook.com/share/1E7bGA2M6w

  兩張 logo 已嵌在這個檔案裡。
-->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,560;9..144,650&family=IBM+Plex+Sans+TC:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {
  --paper: #ffffff;
  --wash: #F2F6F0;
  --green: #3A7C30;
  --green-dark: #2C6124;
  --mango: #FEC107;
  --ink: #1A2418;
  --muted: #4E5A4C;
  --line: #06C755;
  --line-dark: #049447;
  --border: #E3EADF;
  --shadow: 0 12px 32px rgba(26, 36, 24, 0.06);
  --sans: "IBM Plex Sans TC", "PingFang TC", "Noto Sans TC", sans-serif;
  --serif: "Fraunces", "Iowan Old Style", Palatino, serif;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  color: var(--ink);
  background: var(--paper);
  font-family: var(--sans);
  font-size: 17px;
  line-height: 1.7;
}
img { max-width: 100%; }
a { color: var(--green-dark); }
a:hover { color: var(--green); }
:focus-visible { outline: 2px solid var(--green); outline-offset: 3px; }
.skip {
  position: absolute; left: 12px; top: -40px; background: var(--ink); color: #fff;
  padding: 8px 12px; z-index: 50;
}
.skip:focus { top: 12px; }
.wrap { width: min(1120px, calc(100% - 40px)); margin: 0 auto; }
.kicker {
  display: flex; align-items: center; gap: 8px;
  margin: 0 0 8px; color: var(--green); font-weight: 600; letter-spacing: 0.04em;
}
.mark {
  width: 11px; height: 11px; flex: none; background: var(--mango);
  clip-path: polygon(50% 0, 62% 36%, 100% 36%, 69% 57%, 80% 100%, 50% 74%, 20% 100%, 31% 57%, 0 36%, 38% 36%);
}
h1, h2, h3 { line-height: 1.25; font-weight: 600; letter-spacing: 0; }
h1 { font-size: clamp(36px, 5vw, 60px); margin: 0 0 16px; }
h2 { font-size: clamp(28px, 3vw, 36px); margin: 0 0 12px; }
h3 { font-size: 20px; margin: 0 0 8px; }
.lede { font-size: 18px; max-width: 38rem; margin: 0 0 24px; }
.num { font-family: var(--serif); font-weight: 560; font-variation-settings: "opsz" 72; }
.mango-line {
  background-image: linear-gradient(var(--mango), var(--mango));
  background-repeat: no-repeat;
  background-size: 100% 0.32em;
  background-position: 0 88%;
}
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  min-height: 48px; padding: 0 18px; border-radius: 999px;
  text-decoration: none; font-weight: 600; border: 2px solid transparent;
}
.btn-line { background: var(--line); color: #fff; }
.btn-line:hover { background: var(--line-dark); color: #fff; }
.btn-green { background: var(--green); color: #fff; }
.btn-green:hover { background: var(--green-dark); color: #fff; }
.btn-ghost { background: #fff; color: var(--green-dark); border-color: var(--green); }
.row-btns { display: flex; flex-wrap: wrap; gap: 12px; }
header.site {
  position: sticky; top: 0; z-index: 30; background: rgba(255,255,255,.94);
  backdrop-filter: blur(10px); border-bottom: 1px solid var(--border);
}
.head {
  display: flex; align-items: center; gap: 20px; min-height: 104px;
}
.logo-word, .hero-star { flex: none; }
.logo-word { width: 188px; height: 92px; display: block; overflow: visible; }
.nav { display: flex; gap: 18px; align-items: center; margin-left: 8px; }
.nav a { text-decoration: none; color: var(--ink); font-weight: 500; }
.nav a[aria-current="page"] { color: var(--green); box-shadow: inset 0 -2px 0 var(--mango); }
.socials { display: flex; gap: 8px; margin-left: auto; }
.socials a, .icon-btn {
  width: 40px; height: 40px; display: grid; place-items: center;
  border-radius: 50%; color: var(--ink); border: 1px solid var(--border); text-decoration: none;
}
.socials a:hover { border-color: var(--green); color: var(--green); }
.menu-btn { display: none; margin-left: auto; background: #fff; }
header .btn-line { margin-left: 8px; }
.hero { padding: 56px 0 36px; }
.hero-grid { display: grid; grid-template-columns: 1.3fr .7fr; gap: 32px; align-items: center; }
.hero-star { width: 260px; height: 274px; justify-self: end; overflow: visible; }
.band { background: transparent; padding: 12px 0 8px; }
section.block { padding: 48px 0; background: #fff; }
.brand-grid .plain {
  border: 0; border-top: 3px solid var(--mango); border-radius: 0;
  box-shadow: none; padding: 14px 8px 0 0; background: transparent;
}
.brand-grid, .quote-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 24px; }
.card, .quote, .plain {
  background: #fff; border: 1px solid var(--border); border-radius: 18px; padding: 18px;
}
.plain h3 { color: var(--green-dark); }
.cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.school-card { display: flex; flex-direction: column; text-decoration: none; color: inherit; overflow: hidden; padding: 0; }
.school-card:hover { border-color: var(--green); }
.ph {
  min-height: 132px; padding: 16px; display: flex; flex-direction: column; justify-content: flex-end;
  background: #E7F0E4;
}
.ph[data-city="碧瑤"] { background: #E3EEE9; }
.ph[data-city="克拉克"] { background: #F8F3DE; }
.ph[data-city="克拉克／打拉"] { background: #F7F1D8; }
.ph[data-city="馬尼拉"] { background: #EEF3EA; }
.ph .city-en { font-family: var(--serif); font-size: 28px; line-height: 1; color: var(--green-dark); }
.ph small { color: var(--muted); }
.school-body { padding: 16px 16px 18px; display: flex; flex-direction: column; gap: 8px; flex: 1; }
.meta { color: var(--muted); margin: 0; }
.tags { display: flex; flex-wrap: wrap; gap: 6px; }
.tag, .badge {
  display: inline-flex; align-items: center; border-radius: 999px;
  padding: 2px 10px; font-size: 14px; font-weight: 500;
}
.tag { background: var(--wash); color: var(--green-dark); }
.tag.style { background: #fff; border: 1px solid var(--green); }
.badge { background: var(--mango); color: var(--ink); }
.badge.quiet { background: transparent; border: 1px solid var(--mango); }
.points { margin: 0; padding-left: 18px; }
.points li { margin: 2px 0; }
.more { margin-top: 18px; font-weight: 600; }
.quote header { display: flex; justify-content: space-between; gap: 8px; align-items: center; }
.quote p { margin: 10px 0 0; }
.step-pills { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.step-pill {
  display: block; text-decoration: none; color: inherit; background: #fff;
  border: 1px solid var(--border); border-radius: 16px; padding: 14px;
}
.step-pill:hover { border-color: var(--green); }
.step-pill .num { color: var(--green); font-size: 22px; }
.search {
  display: flex; flex-wrap: wrap; gap: 8px; margin: 18px 0 8px; align-items: center;
}
.search label { flex: 1 0 100%; }
.search input { flex: 1; }
.hot { display: grid; gap: 8px; margin-top: 12px; }
.hot a, .text-link { font-weight: 600; }
.line-band {
  background: #fff; color: inherit; padding: 28px 0 8px;
  border-top: 1px solid var(--border);
}
.filter-bar {
  border: 1px solid var(--border); border-radius: 18px; padding: 14px 16px 6px; margin: 8px 0 18px;
}
.finder { display: grid; gap: 6px; margin-bottom: 4px; }
.finder input, .search input {
  width: 100%; min-height: 48px; border-radius: 999px; border: 1px solid var(--border);
  padding: 0 16px; font: inherit; background: #fff;
}
.filter-row {
  display: grid; grid-template-columns: 52px 1fr; gap: 8px; align-items: start;
  padding: 10px 0; border-top: 1px solid var(--border);
}
.filter-label { font-weight: 600; color: var(--green-dark); padding-top: 8px; font-size: 15px; }
.school-list { display: grid; gap: 12px; }
.list-card {
  display: grid; grid-template-columns: 200px 1fr; gap: 0;
  text-decoration: none; color: inherit; background: #fff;
  border: 1px solid var(--border); border-radius: 18px; overflow: hidden;
}
.list-card:hover { border-color: var(--green); }
.list-card .ph { min-height: 100%; border-radius: 0; }
.list-card .school-body { padding: 16px 18px 18px; }
.detail-layout { display: grid; grid-template-columns: 1.4fr .7fr; gap: 28px; align-items: start; }
.detail-nav {
  display: flex; flex-wrap: wrap; gap: 16px; position: sticky; top: 104px; z-index: 5;
  background: rgba(255,255,255,.94); padding: 10px 0; border-bottom: 1px solid var(--border);
}
.detail-nav a { text-decoration: none; font-weight: 600; color: var(--ink); }
.detail-nav a:hover { color: var(--green); box-shadow: inset 0 -2px 0 var(--mango); }
.detail-section { padding: 26px 0; border-top: 1px solid var(--border); scroll-margin-top: 168px; }
.detail-section h2 { font-size: 24px; }
.detail-aside { position: sticky; top: 120px; }
.facts { display: grid; grid-template-columns: 1fr 1fr; gap: 12px 18px; }
.facts p { margin: 0; }
.sky-note {
  position: fixed; right: 28px; top: 0; z-index: 20; width: 46px; height: 46px;
  pointer-events: none; will-change: transform;
}
.sky-note svg { width: 46px; height: 46px; display: block; filter: drop-shadow(0 6px 8px rgba(58,124,48,.18)); }
footer.site { padding: 36px 0 88px; border-top: 1px solid var(--border); color: var(--muted); }
.foot { display: flex; justify-content: space-between; gap: 24px; flex-wrap: wrap; align-items: start; }
.foot nav { display: flex; gap: 14px; flex-wrap: wrap; }
.float-line {
  position: fixed; right: 18px; bottom: 18px; z-index: 40;
  background: var(--line); color: #fff; text-decoration: none; font-weight: 600;
  border-radius: 999px; min-height: 52px; padding: 0 16px 0 12px;
  display: inline-flex; align-items: center; gap: 8px;
  box-shadow: 0 10px 24px rgba(6, 199, 85, .35);
}
.float-line:hover { background: var(--line-dark); color: #fff; }
.filters { display: flex; flex-wrap: wrap; gap: 8px; margin: 14px 0; }
.chip {
  min-height: 40px; padding: 0 14px; border-radius: 999px; border: 1px solid var(--border);
  background: #fff; font: inherit; cursor: pointer; color: var(--ink);
}
.chip[aria-pressed="true"] { background: var(--green); color: #fff; border-color: var(--green); }
.back { font-weight: 600; }
.detail-grid { display: grid; grid-template-columns: 1.2fr .8fr; gap: 20px; align-items: start; }
.stack { display: grid; gap: 14px; }
.quiet { background: var(--wash); }
.quiet a { font-weight: 500; }
.checked { color: var(--muted); font-size: 14px; }
.trio { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 12px; }
.trio ul { margin: 0; padding-left: 18px; }
.step-block { border-top: 1px solid var(--border); padding: 22px 0; scroll-margin-top: 96px; }
.step-toggle {
  width: 100%; text-align: left; background: transparent; border: 0; padding: 0;
  font: inherit; font-weight: 600; font-size: clamp(28px, 3vw, 36px); color: inherit; cursor: pointer;
}
.cats { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.cat {
  display: block; text-decoration: none; color: inherit; border: 1px solid var(--border);
  border-radius: 16px; padding: 16px; background: #fff;
}
.cat:hover { border-color: var(--green); }
.acc { border-bottom: 1px solid var(--border); }
.acc button {
  width: 100%; text-align: left; background: transparent; border: 0; padding: 14px 0;
  font: inherit; font-weight: 600; cursor: pointer; display: flex; justify-content: space-between; gap: 12px;
}
.acc button[aria-expanded="true"] { color: var(--green-dark); }
.acc .a { padding: 0 0 14px; margin: 0; }
.article { max-width: 42rem; }
.article p { margin: 0 0 14px; }
.empty {
  border: 1px dashed var(--green); border-radius: 16px; padding: 18px; background: var(--wash);
}
@media (max-width: 1200px) {
  .sky-note { display: none; }
}
@media (max-width: 900px) {
  .hero-grid, .brand-grid, .quote-grid, .cards, .detail-grid, .trio, .step-pills { grid-template-columns: 1fr 1fr; }
  .detail-layout, .list-card { grid-template-columns: 1fr; }
  .hero-star { justify-self: start; width: 180px; height: 190px; }
  .cats { grid-template-columns: 1fr; }
  .list-card .ph { min-height: 140px; }
}
@media (max-width: 760px) {
  .menu-btn { display: grid; }
  .logo-word { width: 132px; height: 65px; }
  .filter-row, .facts { grid-template-columns: 1fr; }
  .filter-label { padding-top: 0; }
  .detail-nav { top: 72px; }
  header .btn-line { padding: 8px 12px; font-size: 14px; }
  .nav, .socials { display: none; }
  header.site.open .head { flex-wrap: wrap; padding-bottom: 14px; }
  header.site.open .nav,
  header.site.open .socials {
    display: flex; position: static; flex-basis: 100%; margin: 0; padding: 6px 0; border: 0;
  }
  header.site.open .nav { flex-direction: column; align-items: flex-start; gap: 12px; order: 5; }
  header.site.open .socials { order: 6; }
  .hero-grid, .brand-grid, .quote-grid, .cards, .detail-grid, .trio, .step-pills { grid-template-columns: 1fr; }
  .step-pills.jump { display: none; }
  .step-body { display: none; }
  .step-block.open .step-body { display: block; }
}
@media (min-width: 761px) {
  .step-body { display: block; }
  .step-toggle { cursor: default; }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  .sky-note { display: none; }
  * { transition: none !important; }
}
</style>
</head>
<body>
<a class="skip" href="#main">跳到內容</a>
<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">
  <symbol id="mark-word" viewBox="160 116 1040 510">__WORD__</symbol>
  <symbol id="mark-star" viewBox="155 115 760 800">__STAR__</symbol>
</svg>
<header class="site">
  <div class="wrap head">
    <a href="#home" aria-label="FlyLingo 飛語首頁">
      <svg class="logo-word" viewBox="160 116 1040 510" role="img" aria-label="FlyLingo 飛語"><use href="#mark-word"/></svg>
    </a>
    <nav class="nav" id="nav" aria-label="主選單">
      <a href="#schools" data-nav="schools">學校</a>
      <a href="#process" data-nav="process">代辦流程</a>
      <a href="#faq" data-nav="faq">常見問題</a>
      <a href="#blog" data-nav="blog">部落格</a>
    </nav>
    <div class="socials" aria-label="社群">
      <a id="link-threads" href="https://www.threads.com/@sailingo2026" target="_blank" rel="noopener" aria-label="Threads">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M9 8.5c2.8-2 7.2-.6 7 3.2-.3 4.8-6.8 4.2-6.5-1.2.2-3.6 5.5-3.2 6.5-1M8 12.2c.4 4.6 6.6 6.4 8.8 3.3"/></svg>
      </a>
      <a id="link-ig" href="https://www.instagram.com/sailingo2026" target="_blank" rel="noopener" aria-label="Instagram">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="4" y="4" width="16" height="16" rx="5"/><circle cx="12" cy="12" r="3.5"/><circle cx="17.2" cy="6.8" r=".8" fill="currentColor" stroke="none"/></svg>
      </a>
      <a id="link-fb" href="https://www.facebook.com/share/1E7bGA2M6w" target="_blank" rel="noopener" aria-label="Facebook">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M14 9h3V6h-3c-2.2 0-4 1.8-4 4v2H8v3h2v7h3v-7h2.6l.4-3H13v-2c0-.6.4-1 1-1z"/></svg>
      </a>
    </div>
    <button class="icon-btn menu-btn" id="menu-btn" type="button" aria-expanded="false" aria-controls="nav">選單</button>
    <a class="btn btn-line" id="header-line" href="https://lin.ee/oDiSotr" target="_blank" rel="noopener">加 LINE 諮詢</a>
  </div>
</header>
<main id="main">
  <section data-view="home">
    <div class="wrap hero">
      <div class="hero-grid">
        <div>
          <p class="kicker"><span class="mark" aria-hidden="true"></span>菲律賓語言學校代辦</p>
          <h1>從語言出發，<br><span class="mango-line">飛向世界</span></h1>
          <p class="lede">飛語幫你選菲律賓語言學校。先聽目標、週數和預算，再安排報名到抵達。住宿、接機、在學時找誰，出發前會先講清楚。</p>
          <div class="row-btns">
            <a class="btn btn-line" href="https://lin.ee/oDiSotr" target="_blank" rel="noopener">加 LINE 諮詢</a>
            <a class="btn btn-green" href="#schools">看學校</a>
          </div>
        </div>
        <svg class="hero-star" viewBox="155 115 760 800" role="img" aria-label="飛語流星標誌"><use href="#mark-star"/></svg>
      </div>
    </div>
    <div class="band">
      <div class="wrap">
        <p class="kicker"><span class="mark" aria-hidden="true"></span>飛語做的事</p>
        <h2>同一條路，把學校和出發接起來</h2>
        <div class="brand-grid">
          <article class="plain">
            <h3>選校</h3>
            <p>從城市、課程、強度和住宿一起看。第一次不會先塞一長串學校。</p>
          </article>
          <article class="plain">
            <h3>代辦</h3>
            <p>報名、入學文件、付款、機票和接機串成八步，每一步都寫明誰做什麼。</p>
          </article>
          <article class="plain">
            <h3>人在當地</h3>
            <p>入住、上課到結業都有窗口。家長在意的住宿、接機、出事找誰，放在同一條流程裡。</p>
          </article>
        </div>
      </div>
    </div>
    <section class="block">
      <div class="wrap">
        <p class="kicker"><span class="mark" aria-hidden="true"></span>學校</p>
        <h2>六種風格對照，不是排名</h2>
        <p class="lede">這六間用來看出差別：大型、考試、度假、涼爽、外師、親子。全部 <span class="num">43</span> 個校區在清單裡。</p>
        <div class="cards" id="featured-cards"></div>
        <p class="more"><a href="#schools">看全部 43 個校區</a></p>
      </div>
    </section>
    <div class="band">
      <div class="wrap">
        <p class="kicker"><span class="mark" aria-hidden="true"></span>範例回饋</p>
        <h2>別人怎麼描述這趟行程</h2>
        <p class="lede">下面三則是版面範例，上線前換成真的回饋。現在不要把它當成學生證言。</p>
        <div class="quote-grid">
          <figure class="quote">
            <header><span class="badge">範例</span><span class="meta">上班族 · 4 週</span></header>
            <p>範例回饋。我只要知道每天上幾堂、週末能不能出門。顧問沒有一次丟十間學校。</p>
          </figure>
          <figure class="quote">
            <header><span class="badge">範例</span><span class="meta">大學生 · 8 週</span></header>
            <p>範例回饋。比的是門禁和自習，不是泳池照片。行前清單把接機日寫死，機票才敢訂。</p>
          </figure>
          <figure class="quote">
            <header><span class="badge">範例</span><span class="meta">家長</span></header>
            <p>範例回饋。在意的是誰接機、宿舍幾人一間、人到了找誰。這些寫在同一條流程裡。</p>
          </figure>
        </div>
      </div>
    </div>
    <section class="block">
      <div class="wrap">
        <p class="kicker"><span class="mark" aria-hidden="true"></span>代辦流程</p>
        <h2>八步走完，才算出發</h2>
        <p class="lede">首頁只放一句話。點進去看我們做什麼、你要準備什麼、做完你會拿到什麼。</p>
        <div class="step-pills" id="home-steps"></div>
      </div>
    </section>
    <div class="band">
      <div class="wrap">
        <p class="kicker"><span class="mark" aria-hidden="true"></span>常見問題</p>
        <h2>先搜尋，再看分類</h2>
        <form class="search" id="home-search">
          <label class="meta" for="home-q">搜尋問題</label>
          <input id="home-q" name="q" placeholder="例如簽證、費用、住宿、斯巴達">
          <button class="btn btn-green" type="submit">搜尋</button>
        </form>
        <div class="hot" id="home-hot"></div>
        <p class="more"><a href="#faq">看 10 個分類</a></p>
      </div>
    </div>
    <div class="line-band">
      <div class="wrap">
        <h2>還不確定學校，就先把條件丟過來</h2>
        <p>目標、週數、預算，三件事就夠開始。官方 LINE 是這版網站唯一的諮詢口。</p>
        <a class="btn btn-line" href="https://lin.ee/oDiSotr" target="_blank" rel="noopener">加 LINE 諮詢</a>
      </div>
    </div>
  </section>

  <section data-view="schools" hidden>
    <div class="wrap block">
      <p class="kicker"><span class="mark" aria-hidden="true"></span>學校清單</p>
      <h1>43 個校區</h1>
      <p class="lede">先搜學校或城市，再用下面三列縮小範圍。這版不放學費。</p>
      <div class="filter-bar">
        <form class="finder" id="school-search">
          <label class="meta" for="school-q">搜尋學校、城市或課程</label>
          <input id="school-q" name="q" placeholder="例如 CIA、碧瑤、雅思" autocomplete="off">
        </form>
        <div class="filter-row">
          <span class="filter-label">城市</span>
          <div class="filters" id="city-filters" role="group" aria-label="城市"></div>
        </div>
        <div class="filter-row">
          <span class="filter-label">課程</span>
          <div class="filters" id="course-filters" role="group" aria-label="課程"></div>
        </div>
        <div class="filter-row">
          <span class="filter-label">類型</span>
          <div class="filters" id="style-filters" role="group" aria-label="學校類型"></div>
        </div>
      </div>
      <p class="meta" id="school-count"></p>
      <div class="school-list" id="school-cards"></div>
    </div>
  </section>

  <section data-view="school" hidden>
    <div class="wrap block" id="school-detail"></div>
  </section>

  <section data-view="process" hidden>
    <div class="wrap block">
      <p class="kicker"><span class="mark" aria-hidden="true"></span>代辦流程</p>
      <h1>八步，從諮詢到結業</h1>
      <p class="lede">每一步都是同一版型。第 5 到第 8 步含費用、機票和入境文件，頁上會標最後更新。</p>
      <div class="step-pills jump" id="process-jump"></div>
      <div id="process-steps"></div>
      <div class="empty" style="margin-top:28px">
        <h2>這段流程常一起被問</h2>
        <p><a href="#faq/agency">找代辦和自己報名差在哪？</a></p>
        <p><a href="#faq/cost">費用大概怎麼看？</a></p>
        <p><a href="#faq/visa">SSP 和 eTravel 是誰核發的？</a></p>
      </div>
    </div>
  </section>

  <section data-view="faq" hidden>
    <div class="wrap block">
      <p class="kicker"><span class="mark" aria-hidden="true"></span>常見問題</p>
      <h1>先搜尋，再選分類</h1>
      <p class="lede">題庫還在整理，所以每一題都標成範例回答。費用、簽證、SSP、eTravel 會變，旁邊有最後更新。</p>
      <form class="search" id="faq-search">
        <label class="meta" for="faq-q">搜尋問題</label>
        <input id="faq-q" name="q" placeholder="輸入關鍵字">
        <button class="btn btn-green" type="submit">搜尋</button>
      </form>
      <div id="faq-body"></div>
    </div>
  </section>

  <section data-view="blog" hidden>
    <div class="wrap block">
      <p class="kicker"><span class="mark" aria-hidden="true"></span>部落格</p>
      <h1>出發前值得先看的三篇</h1>
      <p class="lede">範例文章，上線前換成飛語自己的稿。</p>
      <div class="stack" id="blog-list"></div>
    </div>
  </section>

  <section data-view="article" hidden>
    <div class="wrap block" id="article-body"></div>
  </section>
</main>
<footer class="site">
  <div class="wrap foot">
    <div>
      <svg class="logo-word" viewBox="160 116 1040 510" role="img" aria-label="FlyLingo 飛語"><use href="#mark-word"/></svg>
      <p>從語言出發，飛向世界。<br>費用、簽證、SSP、eTravel 會變動，請看各頁的最後更新。</p>
    </div>
    <nav aria-label="頁尾">
      <a href="#schools">學校</a>
      <a href="#process">代辦流程</a>
      <a href="#faq">常見問題</a>
      <a href="#blog">部落格</a>
      <a href="https://lin.ee/oDiSotr" target="_blank" rel="noopener">官方 LINE</a>
    </nav>
  </div>
</footer>
<div class="sky-note" aria-hidden="true">
  <svg viewBox="0 0 64 64">
    <path d="M8 36 L56 12 L30 56 L27 38 Z" fill="#3A7C30"/>
    <path d="M27 38 L56 12 L36 36 Z" fill="#FEC107"/>
    <path d="M27 38 L30 56 L36 36 Z" fill="#2C6124"/>
  </svg>
</div>
<a class="float-line" href="https://lin.ee/oDiSotr" target="_blank" rel="noopener" aria-label="官方 LINE 諮詢">
  <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 4C7 4 3.5 7.1 3.5 11c0 3.5 3 6.4 7.1 6.9.3.1.6.2.7.5l.5 1.8c.1.3.4.3.6.1l2.2-1.4c.2-.1.4-.2.7-.2 3.6-.2 6.2-2.9 6.2-6.7C21.5 7.1 17 4 12 4z"/></svg>
  LINE 諮詢
</a>
<script>
const DATA = __DATA__;
const LINE = DATA.line;
const state = { city: "全部", course: "全部", kind: "全部", q: "" };

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function isUrl(s) { return /^https?:\/\//i.test(s || ""); }
function schoolById(id) { return DATA.schools.find((s) => s.id === id); }
function faqById(id) { return DATA.faq.find((c) => c.id === id); }

function cardHTML(s, note) {
  const tags = s.tags.map((t) => `<span class="tag">${esc(t)}</span>`).join("");
  const points = (s.strengths.slice(0, 3).map((p) => `<li>${esc(p)}</li>`).join("")) || "<li>特色待學校資料補上</li>";
  const noteHtml = note ? `<span class="badge">${esc(note)}</span>` : "";
  return `<a class="card school-card" href="#school/${esc(s.id)}">
    <div class="ph" data-city="${esc(s.city)}"><span class="city-en">${esc(s.cityEn)}</span><small>照片將使用學校授權素材</small></div>
    <div class="school-body">
      <div class="tags">${noteHtml}<span class="tag style">${esc(s.style || "管理風格待補")}</span></div>
      <h3>${esc(s.name)}</h3>
      <p class="meta">${esc(s.city)}｜${esc(s.campus)}</p>
      <div class="tags">${tags}</div>
      <ul class="points">${points}</ul>
    </div>
  </a>`;
}

function linkOrText(label, value) {
  if (!value || value.includes("未公開") || value.includes("Not published")) return "";
  if (isUrl(value)) return `<p><a href="${esc(value)}" target="_blank" rel="noopener">${esc(label)}</a></p>`;
  return `<p>${esc(label)}：${esc(value)}</p>`;
}

function renderFeatured() {
  const box = document.getElementById("featured-cards");
  box.innerHTML = DATA.featured.map((f) => cardHTML(schoolById(f.id), f.note)).join("");
}

function renderHomeSteps() {
  document.getElementById("home-steps").innerHTML = DATA.steps.map((s) =>
    `<a class="step-pill" href="#process/${esc(s.id)}"><span class="num">${esc(s.id)}</span><strong>${esc(s.title)}</strong><p class="meta">${esc(s.summary)}</p></a>`
  ).join("");
  const hot = DATA.hot.map((id) => {
    const cat = faqById(id);
    const q = cat.questions[0][0];
    return `<a href="#faq/${esc(id)}">${esc(q)}</a>`;
  }).join("");
  document.getElementById("home-hot").innerHTML = hot;
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

function listCardHTML(s) {
  const tags = s.tags.map((t) => `<span class="tag">${esc(t)}</span>`).join("");
  const points = (s.strengths.slice(0, 3).map((p) => `<li>${esc(p)}</li>`).join("")) || "<li>特色待學校資料補上</li>";
  return `<a class="list-card" href="#school/${esc(s.id)}">
    <div class="ph" data-city="${esc(s.city)}"><span class="city-en">${esc(s.cityEn)}</span><small>照片將使用學校授權素材</small></div>
    <div class="school-body">
      <p class="meta">${esc(s.city)}｜${esc(s.style || "類型待補")}</p>
      <h3>${esc(s.name)}</h3>
      <p class="meta">${esc(s.campus)}</p>
      <div class="tags">${tags}</div>
      <ul class="points">${points}</ul>
    </div>
  </a>`;
}

function renderSchools() {
  const cities = ["全部", "宿霧", "碧瑤", "克拉克", "克拉克／打拉", "馬尼拉"];
  const cityLabel = { "全部": "全部", "宿霧": "宿霧", "碧瑤": "碧瑤", "克拉克": "克拉克", "克拉克／打拉": "打拉", "馬尼拉": "馬尼拉" };
  const input = document.getElementById("school-q");
  if (input && document.activeElement !== input) input.value = state.q;
  document.getElementById("city-filters").innerHTML = cities.map((c) => {
    const n = c === "全部" ? DATA.schools.length : DATA.schools.filter((s) => s.city === c).length;
    return `<button class="chip" type="button" data-city="${esc(c)}" aria-pressed="${state.city === c}">${esc(cityLabel[c])} ${n}</button>`;
  }).join("");
  const courses = ["全部", "ESL", "雅思", "多益", "托福", "商務", "親子"];
  document.getElementById("course-filters").innerHTML = courses.map((c) =>
    `<button class="chip" type="button" data-course="${esc(c)}" aria-pressed="${state.course === c}">${esc(c)}</button>`
  ).join("");
  const kinds = ["全部", "半斯巴達", "斯巴達", "親子", "其他"];
  document.getElementById("style-filters").innerHTML = kinds.map((k) => {
    const n = k === "全部" ? DATA.schools.length : DATA.schools.filter((s) => s.kind === k).length;
    if (k !== "全部" && n === 0) return "";
    return `<button class="chip" type="button" data-kind="${esc(k)}" aria-pressed="${state.kind === k}">${esc(k)} ${n}</button>`;
  }).join("");
  const list = DATA.schools.filter(matchSchool);
  document.getElementById("school-count").textContent = `共 ${list.length} 個校區`;
  const box = document.getElementById("school-cards");
  box.innerHTML = list.length ? list.map((s) => listCardHTML(s)).join("") : `<div class="empty"><p>這個條件目前沒有學校。</p><a class="btn btn-line" href="${esc(LINE)}" target="_blank" rel="noopener">用 LINE 問飛語</a></div>`;
}

function renderDetail(id) {
  const s = schoolById(id);
  const root = document.getElementById("school-detail");
  if (!s) {
    root.innerHTML = `<p>找不到這間學校。</p><p><a href="#schools">回學校清單</a></p>`;
    return;
  }
  const bits = [
    ["成立", s.established],
    ["學生容量", s.capacity],
    ["管理風格", s.style],
    ["適合", s.suitable],
    ["認證／考場", s.accreditation]
  ].filter(([, v]) => v).map(([k, v]) => `<p><strong>${esc(k)}</strong><br>${esc(v)}</p>`).join("");
  const phones = (s.phone || "").split("/").map((x) => x.trim()).filter((x) => /\d/.test(x));
  const phoneHtml = phones.map((p) => `<p>電話 <a href="tel:${esc(p.replace(/\s/g, ""))}">${esc(p)}</a></p>`).join("");
  const emailHtml = (s.email || "").includes("@") ? `<p>Email <a href="mailto:${esc(s.email)}">${esc(s.email)}</a></p>` : (s.email ? `<p>${esc(s.email)}</p>` : "");
  const highlights = (s.strengths.length ? s.strengths : ["特色待補"]).slice(0, 3).map((p) => `<span class="tag">${esc(p)}</span>`).join("");
  root.innerHTML = `
    <p><a class="back" href="#schools">回學校清單</a></p>
    <p class="meta">${esc(s.city)}｜${esc(s.campus)}</p>
    <h1>${esc(s.name)}</h1>
    <div class="tags"><span class="tag style">${esc(s.style || s.kind)}</span>${highlights}</div>
    <div class="detail-layout">
      <div>
        <div class="ph" data-city="${esc(s.city)}" style="min-height:240px;border-radius:18px">
          <span class="city-en">${esc(s.cityEn)}</span>
          <small>照片將使用學校授權素材，此處為佔位</small>
        </div>
        <nav class="detail-nav" aria-label="這間學校">
          <a href="#d-intro" data-jump="d-intro">簡介</a>
          <a href="#d-course" data-jump="d-course">課程</a>
          <a href="#d-stay" data-jump="d-stay">住宿</a>
          <a href="#d-place" data-jump="d-place">位置</a>
        </nav>
        <section class="detail-section" id="d-intro">
          <h2>學校簡介</h2>
          <div class="facts">${bits}</div>
          <ul class="points">${(s.strengths.length ? s.strengths : ["特色待補"]).map((p) => `<li>${esc(p)}</li>`).join("")}</ul>
        </section>
        <section class="detail-section" id="d-course">
          <h2>課程</h2>
          <p>${esc(s.courses || "課程資料待補")}</p>
          <div class="tags">${s.tags.map((t) => `<span class="tag">${esc(t)}</span>`).join("")}</div>
        </section>
        <section class="detail-section" id="d-stay">
          <h2>住宿與生活</h2>
          <p>${esc(s.accommodation || "住宿資料待補")}</p>
          <p>${esc(s.laundry || "")}</p>
          <h2 style="margin-top:22px">設施</h2>
          <p>${esc(s.facilities || "設施資料待補")}</p>
        </section>
        <section class="detail-section" id="d-place">
          <h2>位置</h2>
          <p>${esc(s.address)}</p>
          <p class="meta">${esc(s.addressEn)}</p>
          ${isUrl(s.maps) ? `<p><a href="${esc(s.maps)}" target="_blank" rel="noopener">查看地圖</a></p>` : ""}
        </section>
      </div>
      <aside class="detail-aside stack">
        <a class="btn btn-line" href="${esc(LINE)}" target="_blank" rel="noopener">請飛語用 LINE 問這間</a>
        <div class="plain quiet">
          <h2>學校官方聯絡</h2>
          <p class="meta">想比較或報名，請先找飛語。下面是學校自己的窗口。</p>
          ${phoneHtml}${emailHtml}
          ${linkOrText("官方網站", s.website)}
          ${linkOrText("學校官方表單", s.contactForm)}
          ${linkOrText("Facebook", s.facebook)}
          ${linkOrText("Instagram", s.instagram)}
        </div>
        <p class="checked">資料查核：${esc(s.checked)}</p>
      </aside>
    </div>`;
  root.querySelectorAll("[data-jump]").forEach((a) => {
    a.addEventListener("click", (e) => {
      e.preventDefault();
      const el = document.getElementById(a.dataset.jump);
      if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
}

function column(title, key, items) {
  return `<article class="plain"><h3>${esc(title)}</h3><ul>${items.map((it) => `<li><strong>${esc(it.name)}</strong> ${esc(it[key])}</li>`).join("")}</ul></article>`;
}

function renderProcess(openId) {
  document.getElementById("process-jump").innerHTML = DATA.steps.map((s) =>
    `<a class="step-pill" href="#process/${esc(s.id)}"><span class="num">${esc(s.id)}</span><br><strong>${esc(s.title)}</strong></a>`
  ).join("");
  document.getElementById("process-steps").innerHTML = DATA.steps.map((s) => `
    <article class="step-block${openId === s.id ? " open" : ""}" id="step-${esc(s.id)}">
      <h2><button class="step-toggle" type="button" aria-expanded="${openId === s.id ? "true" : "false"}"><span class="num">${esc(s.id)}</span> ${esc(s.title)}</button></h2>
      <p class="meta">${esc(s.en)}</p>
      <p>${esc(s.summary)}</p>
      <div class="step-body">
        ${s.volatile ? `<p><span class="badge quiet">此內容會變</span> <span class="checked">最後更新：${esc(DATA.updated)}</span></p>` : ""}
        <div class="trio">
          ${column("我們會做什麼", "we", s.items)}
          ${column("你要準備什麼", "you", s.items)}
          ${column("完成後你會得到什麼", "out", s.items)}
        </div>
        <p style="margin-top:14px"><a class="btn btn-line" href="${esc(LINE)}" target="_blank" rel="noopener">用 LINE 詢問這一步</a></p>
      </div>
    </article>`).join("");
  document.querySelectorAll(".step-toggle").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (window.matchMedia("(min-width: 761px)").matches) return;
      const block = btn.closest(".step-block");
      const open = !block.classList.contains("open");
      block.classList.toggle("open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });
  if (openId) {
    const jump = () => {
      const el = document.getElementById("step-" + openId);
      if (el) el.scrollIntoView({ block: "start" });
    };
    requestAnimationFrame(() => requestAnimationFrame(jump));
  }
}

function acc(q, a, open) {
  return `<div class="acc"><button type="button" aria-expanded="${open ? "true" : "false"}">${esc(q)}<span aria-hidden="true">${open ? "−" : "+"}</span></button><p class="a"${open ? "" : " hidden"}>${esc(a)}</p></div>`;
}

function bindAcc(root) {
  root.querySelectorAll(".acc button").forEach((btn) => {
    btn.addEventListener("click", () => {
      const open = btn.getAttribute("aria-expanded") !== "true";
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.querySelector("span").textContent = open ? "−" : "+";
      btn.nextElementSibling.hidden = !open;
    });
  });
}

function renderFaq(id, q) {
  const body = document.getElementById("faq-body");
  const input = document.getElementById("faq-q");
  if (input && document.activeElement !== input) input.value = q || "";
  if (id && faqById(id) && !q) {
    const cat = faqById(id);
    body.innerHTML = `<p><a class="back" href="#faq">回到全部分類</a></p>
      <h2>${esc(cat.title)}</h2>
      ${cat.volatile ? `<p><span class="badge quiet">此內容會變</span> <span class="checked">最後更新：${esc(DATA.updated)}</span></p>` : `<p class="meta">範例回答，上線前替換。</p>`}
      ${cat.questions.map(([qq, aa], i) => acc(qq, aa, i === 0)).join("")}
      <p style="margin-top:16px"><a class="btn btn-line" href="${esc(LINE)}" target="_blank" rel="noopener">還是問 LINE</a></p>`;
    bindAcc(body);
    return;
  }
  if (q) {
    const query = q.trim().toLowerCase();
    const hits = [];
    DATA.faq.forEach((cat) => {
      cat.questions.forEach(([qq, aa]) => {
        if ((qq + aa + cat.title).toLowerCase().includes(query)) hits.push([qq, aa, cat]);
      });
    });
    body.innerHTML = hits.length
      ? `<h2>搜尋「${esc(q)}」</h2>${hits.map(([qq, aa]) => acc(qq, aa, false)).join("")}`
      : `<div class="empty"><h2>沒有對到的問題</h2><p>換一個詞，或直接把問題丟給飛語。</p><a class="btn btn-line" href="${esc(LINE)}" target="_blank" rel="noopener">用 LINE 問這題</a></div>`;
    bindAcc(body);
    return;
  }
  const hot = DATA.hot.map((hid) => {
    const cat = faqById(hid);
    return `<a href="#faq/${esc(hid)}">${esc(cat.questions[0][0])}</a>`;
  }).join("");
  const cats = DATA.faq.map((cat) => `<a class="cat" href="#faq/${esc(cat.id)}"><strong>${esc(cat.title)}</strong><br><span class="meta">${cat.questions.length} 題範例${cat.volatile ? " · 會變" : ""}</span></a>`).join("");
  body.innerHTML = `<h2>熱門問題</h2><div class="hot">${hot}</div><h2 style="margin-top:28px">10 個分類</h2><div class="cats">${cats}</div>`;
}

function renderBlog() {
  document.getElementById("blog-list").innerHTML = DATA.articles.map((a) =>
    `<a class="card" href="#article/${esc(a.id)}" style="text-decoration:none;color:inherit"><span class="badge">範例文章</span><h2>${esc(a.title)}</h2><p class="meta">${esc(a.kicker)}</p></a>`
  ).join("");
}

function renderArticle(id) {
  const a = DATA.articles.find((x) => x.id === id);
  const root = document.getElementById("article-body");
  if (!a) {
    root.innerHTML = `<p>找不到這篇文章。</p><p><a href="#blog">回部落格</a></p>`;
    return;
  }
  root.innerHTML = `<article class="article">
    <p><a class="back" href="#blog">回部落格</a></p>
    <p class="kicker"><span class="mark" aria-hidden="true"></span>${esc(a.kicker)}</p>
    <h1>${esc(a.title)}</h1>
    <p><span class="badge">範例文章</span></p>
    ${a.body.map((p) => `<p>${esc(p)}</p>`).join("")}
    <a class="btn btn-line" href="${esc(LINE)}" target="_blank" rel="noopener">用 LINE 接著問</a>
  </article>`;
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
  return { view: parts[0] || "home", id: parts[1] || "", q };
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
  if (view === "schools") renderSchools();
  if (view === "school") renderDetail(route.id);
  if (view === "process") renderProcess(route.id);
  if (view === "faq") renderFaq(route.id, route.q);
  if (view === "blog") renderBlog();
  if (view === "article") renderArticle(route.id);
  const titles = {
    home: "FlyLingo 飛語｜從語言出發，飛向世界",
    schools: "學校清單｜FlyLingo 飛語",
    school: "學校｜FlyLingo 飛語",
    process: "代辦流程｜FlyLingo 飛語",
    faq: "常見問題｜FlyLingo 飛語",
    blog: "部落格｜FlyLingo 飛語",
    article: "文章｜FlyLingo 飛語"
  };
  document.title = titles[view];
  if (view !== "process" || !route.id) window.scrollTo(0, 0);
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
document.getElementById("city-filters").addEventListener("click", (e) => {
  const btn = e.target.closest("[data-city]");
  if (!btn) return;
  state.city = btn.dataset.city;
  renderSchools();
});
document.getElementById("course-filters").addEventListener("click", (e) => {
  const btn = e.target.closest("[data-course]");
  if (!btn) return;
  state.course = btn.dataset.course;
  renderSchools();
});
document.getElementById("style-filters").addEventListener("click", (e) => {
  const btn = e.target.closest("[data-kind]");
  if (!btn) return;
  state.kind = btn.dataset.kind;
  renderSchools();
});
document.getElementById("school-search").addEventListener("submit", (e) => e.preventDefault());
document.getElementById("school-q").addEventListener("input", (e) => {
  state.q = e.target.value.trim();
  renderSchools();
});

function placePlane() {
  const el = document.querySelector(".sky-note");
  if (!el || getComputedStyle(el).display === "none") return;
  const max = document.documentElement.scrollHeight - window.innerHeight;
  const p = max > 0 ? Math.min(1, window.scrollY / max) : 0;
  const travel = Math.max(120, window.innerHeight - 210);
  el.style.transform = `translateY(${88 + p * travel}px) rotate(${-18 + p * 10}deg)`;
}
window.addEventListener("scroll", placePlane, { passive: true });
window.addEventListener("resize", placePlane);
placePlane();

renderFeatured();
renderHomeSteps();
window.addEventListener("hashchange", render);
render();
</script>
</body>
</html>
'''

if __name__ == "__main__":
    main()
