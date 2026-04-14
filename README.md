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
# 使用提供的腳本設置 cron
./deployment/scripts/setup-cron.sh
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

## 📄 相關文檔

- [專案說明](docs/專案說明.md)
- [架構說明](docs/架構說明.md)
- [開發規則](docs/開發規則.md)
- [部署說明](deployment/README.md)
- [測試說明](tests/README.md)
- [已知問題](docs/known-issues.md)

## ✅ 已確認事項

- [x] 新聞去重標準 - 使用 RSS guid
- [x] JSON 格式 - 每天一個 JSON 檔，包含該日所有新聞
- [x] 前端需求 - 不需要前端
- [x] 數據保留政策 - 永久保存

## 📝 更新記錄

| 日期 | 更新內容 | 負責人 |
|------|---------|--------|
| 2026-04-14 | 初始版本建立 | Claw |
| 2026-04-14 | 改為每天一個 JSON 檔 | Claw |
| 2026-04-14 | 簡化架構（移除 frontend/backend） | Claw |

---

**最後更新：** 2026-04-14  
**維護者：** john-fb-agent  
**版本：** 1.0.0
