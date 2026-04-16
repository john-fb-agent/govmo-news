# 澳門政府新聞局 RSS 新聞抓取系統

抓取並轉換澳門政府新聞局（GCS）RSS 新聞為 JSON 格式，按日期組織存儲。

## 📋 功能特點

- ✅ 從 RSS Feed 自動抓取新聞
- ✅ XML 轉換為 JSON 格式
- ✅ 按 年/月 組織存儲（每天一個 JSON 檔）
- ✅ 自動去重（使用 RSS guid）
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

# 安裝依賴（Ubuntu/Debian）
sudo apt install python3-feedparser python3-requests

# 首次運行
python3 src/fetch_news.py
```

### 部署定時任務

```bash
# 設置新聞抓取 cron（每日 5 次：9,11,13,15,17 點）
./deployment/scripts/setup-cron.sh

# 設置自動推送 cron（每晚 10 點自動抓取並推送）
./deployment/scripts/setup-auto-push.sh
```

## 📅 定時任務時間

**新聞抓取（每日 5 次）：**
- 09:00
- 11:00
- 13:00
- 15:00
- 18:00

**自動抓取 + 推送（每日 1 次）：**
- 01:00（凌晨 1 點）
- 推送前先抓取，確保數據是最新的

## 🔗 RSS 來源

- **來源：** 澳門政府新聞局
- **RSS URL:** `https://govinfohub.gcs.gov.mo/api/rss/n/zh-hant`
- **語言：** 繁體中文

---

## ⚖️ 版權聲明

**資料來源：** 澳門特別行政區政府新聞局 (https://govinfohub.gcs.gov.mo)

本專案僅提供技術工具抓取並轉換新聞局 RSS Feed 為 JSON 格式。所有新聞內容版權歸澳門特別行政區政府新聞局所有。

**使用限制：**
- 僅供非商業性使用
- 不得修改新聞內容
- 使用者需自行確保合規使用

**免責聲明：** 本專案不保證新聞內容的準確性、完整性或時效性，所有資料以新聞局官方網站公佈的「現狀」為準。

詳細使用條款請參閱新聞局網站：https://govinfohub.gcs.gov.mo

---

## ✅ 已確認事項

- [x] 新聞去重標準 - 使用 RSS guid
- [x] JSON 格式 - 每天一個 JSON 檔，包含該日所有新聞
- [x] 前端需求 - 不需要前端
- [x] 數據保留政策 - 永久保存

---

## 📄 相關文檔

- [專案說明](docs/專案說明.md)
- [架構說明](docs/架構說明.md)
- [開發規則](docs/開發規則.md)
- [部署說明](deployment/README.md)
- [測試說明](tests/README.md)
- [已知問題](docs/known-issues.md)
- [更新記錄](docs/更新記錄.md)

## 🌐 GitHub Pages

**已啟用！** ✅

**索引頁面：** https://john-fb-agent.github.io/govmo-news/summaries/

**每日新聞總結：** https://john-fb-agent.github.io/govmo-news/summaries/YYYY-MM-DD.html

**文件結構：**
```
docs/summaries/
├── index.html          (自動索引頁面)
├── 2026-04-14.html
├── 2026-04-15.html
└── ...
```

**自動化：**
- ✅ 每天早上 8 點自動生成
- ✅ AI 自動分類和重要性評分
- ✅ 自動提交並推送到 GitHub
- ✅ 保留所有歷史總結

---

**最後更新：** 2026-04-16  
**維護者：** john-fb-agent  
**版本：** 1.3.1
