# 澳門政府新聞局 RSS 新聞抓取系統

抓取並轉換澳門政府新聞局（GCS）RSS 新聞為 JSON 格式，按日期組織存儲。

## 📋 功能特點

- ✅ 從 RSS Feed 自動抓取新聞
- ✅ XML 轉換為 JSON 格式
- ✅ 按 年/月/日 組織存儲
- ✅ 自動去重（避免重複保存相同新聞）
- ✅ 定時任務（每日 9:00, 11:00, 13:00, 15:00, 17:00）

## 🚀 快速開始

### 前置條件

- Python 3.8+
- pip
- Git

### 安裝

```bash
# 克隆倉庫
git clone https://github.com/john-fb-agent/govmo-news.git
cd govmo-news

# 安裝依賴
pip install -r requirements.txt

# 首次運行
python src/backend/fetch_news.py
```

### 部署定時任務

```bash
# 使用提供的腳本設置 cron
./deployment/scripts/setup-cron.sh
```

## 📁 目錄結構

```
govmo-news/
├── src/
│   ├── backend/          # 後端邏輯
│   │   ├── fetch_news.py    # 新聞抓取主程式
│   │   └── rss_parser.py    # RSS 解析器
│   ├── frontend/         # 前端介面（待開發）
│   └── utils/            # 工具函數
│       └── dedup.py         # 去重工具
├── data/
│   ├── raw/              # 原始 RSS XML
│   └── processed/        # 處理後的 JSON（按年/月/日組織）
├── deployment/           # 部署相關
│   ├── scripts/          # 部署腳本
│   └── README.md         # 部署說明
├── tests/                # 測試
│   └── README.md         # 測試說明
├── docs/                 # 文檔
└── requirements.txt      # Python 依賴
```

## 📅 定時任務時間

每日執行時間（澳門時間 GMT+8）：
- 09:00
- 11:00
- 13:00
- 15:00
- 17:00

## 🔗 RSS 來源

- **來源：** 澳門政府新聞局
- **RSS URL:** `https://govinfohub.gcs.gov.mo/api/rss/n/zh-hant`
- **語言：** 繁體中文

## 📄 相關文檔

- [專案說明](docs/專案說明.md)
- [架構說明](docs/架構說明.md)
- [開發規則](docs/開發規則.md)
- [部署說明](deployment/README.md)
- [測試說明](tests/README.md)

## ⚠️ 待確認事項

- [ ] 新聞去重標準（標題？URL？發布時間？）
- [ ] JSON 格式詳細規格
- [ ] 前端需求（是否需要 Web 介面？）
- [ ] 數據保留政策（保存多久的新聞？）

## 📝 更新記錄

| 日期 | 更新內容 | 負責人 |
|------|---------|--------|
| 2026-04-14 | 初始版本建立 | Claw |

---

**最後更新：** 2026-04-14  
**維護者：** john-fb-agent
