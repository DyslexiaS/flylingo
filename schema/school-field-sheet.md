# 學校欄位表單

一筆是一個校區。後台欄位以 [school-fields.json](school-fields.json) 為準，共 40 欄。

清單上真正做成篩選按鈕的只有三個：城市、課程、管理類型。搜尋框會比對校名、品牌、校區、城市、管理風格、課程說明。

## 後台要建的欄位

| 中文 | 英文 key | 型態 | 必填 | 篩選 | 選項 | 前台 |
| --- | --- | --- | --- | --- | --- | --- |
| 中文校名 | school_name_zh | 單行文字 | 是 | 搜尋 |  | 列表標題、詳情標題 |
| 英文品牌 | brand | 單行文字 | 是 | 搜尋 |  | 不單獨顯示 |
| 校區 | campus_zh | 單行文字 | 是 | 搜尋 |  | 列表、詳情副標 |
| 校區英文 | campus_en | 單行文字 |  |  |  | 這一版不顯示 |
| 正式英文名稱 | legal_name_en | 單行文字 |  |  |  | 這一版不顯示 |
| 城市 | city | 單選 | 是 | 清單 | 宿霧、碧瑤、克拉克、克拉克／打拉（畫面寫打拉）、馬尼拉 | 篩選、列表、詳情 |
| 管理類型 | management_level | 單選 | 是 | 清單 | 半斯巴達、斯巴達、親子、其他 | 篩選。選「其他」時卡片不顯示標籤 |
| 管理風格 | study_style | 單行文字 | 是 | 搜尋 | 自由填寫，不要做成選單 | 詳情簡介 |
| 成立年份 | established | 單行文字 |  |  |  | 詳情簡介，空的就藏起 |
| 學生人數 | capacity | 單行文字 |  |  |  | 詳情簡介。寫「未公開」就藏起 |
| 課程 | courses | 多選 | 是 | 清單 | ESL、雅思、多益、托福、商務、親子 | 篩選、列表底部、詳情打勾、詢問單 |
| 雅思保證班 | ielts_guarantee | 單選 | 是 |  | 有、沒有 | 先存，這一版不顯示 |
| 課程說明 | courses_text | 多行文字 | 是 | 搜尋 | 「；」分隔 | 詳情「課程」 |
| 適合誰 | suitable_for | 多行文字 |  |  | 「；」分隔 | 詳情，最多 6 點 |
| 特色 | strengths | 可新增多列 | 是 |  | 每列一點 | 列表最多 3 點（超過 14 字不上卡片）；詳情全部 |
| 設施 | facilities_text | 多行文字 |  |  | 「；」分隔 | 詳情設施格 |
| 住宿說明 | accommodation | 多行文字 |  |  |  | 詳情住宿 |
| 房型 | room_types | 可新增多列 |  |  | 每列一個房型名 | 可點選並帶入 LINE。空的就顯示「用 LINE 問這間」 |
| 洗衣清潔 | laundry | 多行文字 |  |  | 「；」分隔 | 詳情住宿 |
| 認證 | accreditation | 多行文字 |  |  |  | 詳情簡介 |
| 官方考場 | official_tests | 多選 |  |  | IELTS、TOEIC、TOEFL、Cambridge | 有勾才顯示藍標 |
| 其他條件 | amenity_flags | 多選 |  |  | 打工度假、外師課程、高爾夫、游泳池、健身房、洗衣服務、醫護／診所、咖啡廳、校內宿舍、度假／海邊型 | 先存，這一版不篩、不顯示 |
| 中文地址 | address_zh | 多行文字 | 是 |  |  | 詳情位置 |
| 英文地址 | address_en | 多行文字 | 是 |  |  | 詳情位置小字 |
| 地圖 | google_maps | 網址 | 是 |  |  | 「查看地圖」 |
| 電話 | phone | 單行文字 |  |  | 多支用 / | 官方聯絡，預設收合 |
| Email | email | 單行文字 |  |  |  | 官方聯絡 |
| 官方網站 | website | 網址 |  |  |  | 官方聯絡 |
| 學校聯絡表單 | contact_form | 網址 |  |  |  | 官方聯絡 |
| Facebook | facebook | 網址 |  |  |  | 官方聯絡 |
| Instagram | instagram | 網址 |  |  |  | 官方聯絡 |
| 其他社群 | other_social | 可新增多列 |  |  | 類型：YouTube、其他 | 官方聯絡。HTML 還沒畫 |
| 首圖 | hero_image | 圖片 |  |  |  | 列表、詳情大圖。沒圖用城市插畫 |
| 相簿 | gallery | 可新增多列 |  |  | 分類：首圖／校園外觀、校園全景、一對一教室、團體教室、宿舍房間、衛浴、餐廳／餐點、洗衣區、泳池／健身房、地圖／周邊、影片。每列另有說明、YouTube | 詳情相簿。現在是空的 |
| 最後查核 | last_checked | 日期 | 是 |  |  | 頁尾要顯示。HTML 還沒畫 |
| 資料可信度 | confidence | 單選 |  |  | 高、中高、中、低 | 只放後台 |
| 資料來源 | source_urls | 可新增多列 |  |  | 網址，最多兩則 | 只放後台 |
| 官方相簿網址 | photo_source_url | 網址 |  |  |  | 只放後台 |
| 簡章 | brochure_url | 網址 |  |  |  | 只放後台 |
| 編輯備註 | editor_note | 多行文字 |  |  |  | 只放後台 |

## Excel 每一欄對到哪

工作表 `01_學校資料總表_中文`，43 個校區。

| Excel 欄 | 中文 | 後台 key | 現在 HTML |
| --- | --- | --- | --- |
| A | 城市 | city | 有。篩選、列表、詳情 |
| B | 網站建議中文顯示名稱 | school_name_zh | 有。標題 |
| C | 英文品牌 | brand | 只參與搜尋 |
| D | 校區（中文） | campus_zh | 有 |
| E | 校區（英文） | campus_en | 沒有 |
| F | 正式英文名稱 | legal_name_en | 沒有 |
| G | 管理／學習風格 | study_style，另外手選 management_level | 風格原文在詳情。類型標籤是程式算出來的 |
| H | 成立年份 | established | 有。簡介 |
| I | 學生容量 | capacity | 有。寫未公開就藏起 |
| J | 中文地址 | address_zh | 有。位置 |
| K | 英文原始地址 | address_en | 有。位置小字 |
| L | 電話 | phone | 有。官方聯絡 |
| M | Email／聯絡方式 | email | 有。官方聯絡 |
| N | 官方網站 | website | 有。官方聯絡 |
| O | 聯絡表單 | contact_form | 有。官方聯絡 |
| P | Facebook | facebook | 有。官方聯絡 |
| Q | Instagram | instagram | 有。官方聯絡 |
| R | 其他社群 | other_social | 沒有。YouTube 被丟掉 |
| S | Google Maps | google_maps | 有。「查看地圖」 |
| T | 核心課程（中文） | courses_text | 有。詳情課程條列 |
| U | 適合族群（中文） | suitable_for | 有。最多 6 點 |
| V | 學校重點特色（中文） | strengths | 有。卡片 3 點、詳情全部 |
| W | 校園設施（中文） | facilities_text | 有。對成設施格 |
| X | 住宿（中文） | accommodation，能拆的再填 room_types | 有。拆不出房型就改走 LINE |
| Y | 洗衣／清潔（中文） | laundry | 有 |
| Z | 認證／考場（中文） | accreditation | 有。簡介 |
| AA | 官方照片／相簿 | photo_source_url | 沒有。只該放後台 |
| AB | 簡章 | brochure_url | 沒有。只該放後台 |
| AC | 資料來源 1 | source_urls | 沒有。只該放後台 |
| AD | 資料來源 2 | source_urls | 沒有。只該放後台 |
| AE | 資料可信度 | confidence | 沒有。只該放後台 |
| AF | 最後查核 | last_checked | 資料有帶，頁面沒畫 |
| AG | 設計師備註 | editor_note | 沒有。只該放後台 |

工作表 `02_網站篩選標籤`。值只有打勾或空白。

| Excel 欄 | 中文 | 目前幾校打勾 | 後台 | 現在 HTML |
| --- | --- | --- | --- | --- |
| A–C | 城市、品牌、校區 | 用來對校區 | 跟總表同一筆 | 有 |
| D | ESL | 41 | courses | 有。篩選「ESL」 |
| E | IELTS | 37 | courses「雅思」 | 有 |
| F | IELTS 保證班 | 8 | ielts_guarantee | 沒有單獨項目，被併進雅思 |
| G | TOEIC | 28 | courses「多益」 | 有 |
| H | TOEFL | 12 | courses「托福」 | 有 |
| I | 商務英文 | 31 | courses「商務」 | 有 |
| J | 親子／青少年 | 28 | courses「親子」 | 篩選有。卡片標籤被切短，只剩 19 校看得到「親子」 |
| K | 打工度假 | 3 | amenity_flags | 沒有 |
| L | 外師課程 | 4 | amenity_flags | 沒有。首頁 CIP 的「外師」是對照卡說明，不是這欄 |
| M | 高爾夫 | 6 | amenity_flags | 設施文字有提到才出現圖示，不能篩 |
| N | 游泳池 | 17 | amenity_flags | 同上 |
| O | 健身房 | 14 | amenity_flags | 同上 |
| P | 洗衣服務 | 22 | amenity_flags | 洗衣看的是總表 Y，不是這個勾 |
| Q | 醫護／診所 | 7 | amenity_flags | 設施文字對得到才顯示 |
| R | 咖啡廳／便利設施 | 14 | amenity_flags | 同上 |
| S | 校內宿舍 | 27 | amenity_flags | 沒有單獨勾選，住宿看總表 X |
| T | 度假／海邊型 | 8 | amenity_flags | 沒有 |
| U | 官方考場 | 1（只有 EG Academy） | official_tests | 有藍標，但是去掃認證句子，跟這欄不一致 |

工作表 `03_照片素材來源`。43 校都寫「可取得」，意思是找得到來源頁，不是已經有授權圖。

| Excel 欄 | 中文 | 後台 | 現在 HTML |
| --- | --- | --- | --- |
| D | 官方相簿／照片頁 | photo_source_url | 沒有 |
| E | 官方網站 | website | 跟總表重複 |
| F | Facebook | facebook | 跟總表重複 |
| G | Instagram | instagram | 跟總表重複 |
| H | 簡章 | brochure_url | 沒有 |
| I | 照片可取得 | 不建欄位 | 沒有 |
| J | 建議網站照片類型 | gallery 的分類 | 頁面分類比較少：校園、教室、宿舍、餐廳、公共空間，或影片 |
| K | 授權提醒 | editor_note 可以附一句 | 沒有。規定是上傳到自己的媒體庫，不要外連 |

## HTML 頁面上有、但不另建欄位

這些是畫面，資料來自上面的欄位，或是全站固定的。

| 畫面上的東西 | 出現位置 | 從哪來 |
| --- | --- | --- |
| 關鍵字搜尋 | 學校清單 | 比對校名、品牌、校區、城市、管理風格、管理類型、課程說明、課程標籤 |
| 城市篩選，含校區數 | 學校清單 | city。按鈕文案：全部、宿霧、碧瑤、克拉克、打拉、馬尼拉 |
| 課程篩選 | 學校清單 | courses。全部、ESL、雅思、多益、托福、商務、親子 |
| 類型篩選 | 學校清單 | management_level。全部、半斯巴達、斯巴達、親子、其他。數量是 0 的選項會藏起來 |
| 共 N 個校區、清除條件、每頁 9 間 | 學校清單 | 畫面，不建欄位 |
| 沒有結果時的 LINE | 學校清單 | 全站 LINE，不建欄位 |
| 城市插畫或示意照 | 列表卡、詳情 | 沒有 hero_image 就用插畫。現在五張示意照要標「示意」 |
| 城市英文 | 列表卡照片上、詳情方塊、清單標題 | 跟 city 一起：Cebu、Baguio、Clark、Tarlac、Manila |
| 管理類型標籤 | 列表卡、詳情 | management_level。「其他」不顯示 |
| 特色標籤，最多 3 個 | 列表卡 | strengths，超過 14 字的跳過 |
| 課程標籤，用「・」接起來 | 列表卡底部 | courses。現在程式最多留 5 個，後台不要截斷 |
| 官方考場藍標 | 列表卡、詳情 | official_tests |
| 麵包屑「學校 › 城市 › 校名」 | 詳情 | 點城市回到清單並篩該城市 |
| 複製連結 | 詳情 | 不建欄位 |
| 相簿：大圖、分類、縮圖、全螢幕、YouTube | 詳情 | gallery。空的時候宿霧和碧瑤用城市示意照，其他城市用五張插畫並寫「照片整理中」 |
| 管理強度，五格 | 詳情「一眼看懂」 | 不建欄位。半斯巴達是第 3 格，斯巴達是第 4 格；風格句子裡有「每日 9」或「嚴格」的斯巴達是第 5 格；其餘看句子偏彈性就是第 1 格，不然第 2 格 |
| 課程選擇，有的打勾、沒有的劃掉 | 詳情 | courses 六項 |
| 適合誰 | 詳情 | suitable_for |
| 簡介四格：成立、學生人數、管理風格、認證 | 詳情 | established、capacity、study_style、accreditation |
| 特色條列 | 詳情簡介 | strengths |
| 課程條列 | 詳情 | courses_text |
| 房型按鈕 | 詳情住宿 | room_types |
| 住宿方式、「每間都有」 | 詳情住宿 | accommodation 裡拆不進房型的句子 |
| 洗衣清潔 | 詳情住宿 | laundry |
| 設施 11 格：有、依校區、資料未提到 | 詳情 | 從 facilities_text 對文字。固定格是餐廳、自習空間、健身房、游泳池、醫護室、運動場、洗衣區、咖啡廳、商店、休閒娛樂、考場。Wi-Fi、高爾夫、度假環境、兒童空間只有原文有才出現。對不上的放「其他」。灰色是資料沒寫 |
| 中文地址、英文地址、查看地圖 | 詳情位置 | address_zh、address_en、google_maps |
| 幫我問這間 | 詳情右側 | 課程用這間學校有開的 courses。週數是全站固定：2 週、4 週、8 週、12 週以上，不建欄位。房型用 room_types；這間沒寫房型時，詢問單改用單人房、雙人房、多人房 |
| 學校官方聯絡 | 詳情，預設收合 | 電話、Email、官網、學校表單、Facebook、Instagram |
| 首頁六張對照卡的短說明 | 只在首頁 | 不放進每一間學校。固定是：CIA 大型半斯巴達、EV 考試・高強度、Cebu Blue Ocean 度假海濱、PINES 涼爽・斯巴達、CIP 外師、CIJ 親子 |

## 這一版不要做成學校欄位

學費、當地雜費、優惠、諮詢表單、報名文件。學校頁用 LINE 問費用。
