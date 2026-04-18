# 澳門政府新聞局 RSS 新聞抓取系統

> 自動抓取、轉換並存儲澳門政府新聞局（GCS）RSS 新聞，提供 AI 每日總結與 GitHub Pages 展示。

[![Version](https://img.shields.io/badge/version-1.4.0-blue)](docs/更新記錄.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-yellow)](https://python.org)

---

## 📖 專案簡介

本系統自動從澳門政府新聞局 RSS Feed 抓取新聞，轉換為結構化 JSON 格式，並提供：

- **自動抓取** — 每日 5 次定時抓取（09/11/13/15/18:00）
- **智能去重** — 基於 RSS guid 確保不重複
- **AI 每日總結** — 每天早上 8 點生成 HTML 新聞摘要
- **GitHub Pages** — 自動部署新聞總結網頁

**🌐 線上查看：** https://john-fb-agent.github.io/govmo-news/

---

## ⚡ 快速開始

### 前置條件

```bash
Python 3.8+
Git
pip
```

### 安裝與運行

```bash
# 1. 克隆倉庫
git clone https://github.com/john-fb-agent/govmo-news.git
cd govmo-news

# 2. 安裝依賴（Ubuntu/Debian）
sudo apt install python3-feedparser python3-requests

# 3. 首次運行抓取
python3 src/fetch_news.py
```

### 設置自動化

```bash
# 新聞抓取（每日 5 次）
./deployment/scripts/setup-cron.sh

# 自動推送（每日凌晨 1 點）
./deployment/scripts/setup-auto-push.sh

# AI 每日總結（每日早上 8 點）
./deployment/scripts/setup-summary-cron.sh
```

---

## 📅 定時任務一覽

| 時間 | 任務 | 說明 |
|------|------|------|
| 09:00, 11:00, 13:00, 15:00, 18:00 | 新聞抓取 | 從 RSS 抓取最新新聞 |
| 01:00 | 自動推送 | 先抓取再推送到 GitHub |
| 08:00 | AI 總結 | 生成前日新聞 HTML 摘要 |

---

## 🏗️ 專案結構

```
govmo-news/
├── src/
│   ├── fetch_news.py        # 主抓取腳本
│   ├── rss_parser.py        # RSS 解析器
│   ├── generate_summary.py  # AI 總結生成
│   └── summary_prompt.txt   # AI 提示詞模板
├── data/
│   └── processed/           # 新聞 JSON（年/月/日.json）
├── public/                  # GitHub Pages 輸出
│   ├── index.html           # 索引頁面
│   └── YYYY-MM-DD.html      # 每日總結
├── deployment/scripts/      # 部署腳本
├── docs/                    # 文檔
└── tests/                   # 測試
```

---

## 🤖 AI 新聞總結

每天早上 8 點自動執行，功能包括：

- ✅ **自動分類** — 政策、民生、經濟、旅遊、教育、文化、科技、其他
- ✅ **重要性評分** — ⭐⭐⭐ 高 / ⭐⭐ 中 / ⭐ 低
- ✅ **重點摘要** — 最多 5 則高重要性新聞
- ✅ **HTML 輸出** — 美觀的網頁格式
- ✅ **自動部署** — GitHub Actions 自動發布到 Pages

**查看範例：** https://john-fb-agent.github.io/govmo-news/2026-04-17.html

---

## 📄 文檔導航

| 文檔 | 說明 |
|------|------|
| [專案說明](docs/專案說明.md) | 專案目標與範圍 |
| [架構說明](docs/架構說明.md) | 技術架構與數據流 |
| [開發規則](docs/開發規則.md) | 開發規範與最佳實踐 |
| [部署說明](deployment/README.md) | 部署指南 |
| [更新記錄](docs/更新記錄.md) | 版本歷史 |
| [已知問題](docs/known-issues.md) | 已知問題與限制 |

---

## ⚖️ 版權聲明

**資料來源：** 澳門特別行政區政府新聞局  
**RSS Feed:** https://govinfohub.gcs.gov.mo/api/rss/n/zh-hant

本專案僅提供技術工具抓取並轉換 RSS Feed。所有新聞內容版權歸澳門特別行政區政府新聞局所有。

**使用限制：**
- 僅供非商業性使用
- 不得修改新聞內容
- 使用者需自行確保合規使用

詳細條款請參閱：https://govinfohub.gcs.gov.mo

---

## 📊 專案狀態

| 項目 | 狀態 |
|------|------|
| 新聞抓取 | ✅ 正常運行 |
| 自動去重 | ✅ 正常運行 |
| 自動推送 | ✅ 正常運行 |
| AI 總結 | ✅ 正常運行 |
| GitHub Pages | ✅ 正常運行 |

**最新版本：** 1.4.0（2026-04-16）  
**維護者：** john-fb-agent

---

## 📞 支援

如有問題，請提交 Issue：https://github.com/john-fb-agent/govmo-news/issues
