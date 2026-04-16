# AI Agent 指南

**創建時間：** 2026-04-16 20:04 (GMT+8)  
**創建者：** AI Agent (OpenClaw)  
**Provider:** Qwen  
**Model:** qwen/qwen3.5-plus

---

## 📖 給閱讀此文件的 AI Agent

> **你好！** 這份文件是之前的 AI agent 為了協助你工作而創建的。
>
> **你可以：**
> - ✅ 根據自己的想法和需要修改這份文件
> - ✅ 添加你認為重要的內容
> - ✅ 刪除不再適用的部分
> - ✅ 完全重寫（如果你有更好的想法）
>
> **這份文件的目的：** 幫助你快速理解這個倉庫，避免重複犯錯。
>
> **現有文檔（必讀）：**
> 1. [README.md](README.md) - 快速開始、cron 時間表
> 2. [docs/專案說明.md](docs/專案說明.md) - 核心功能
> 3. [docs/架構說明.md](docs/架構說明.md) - 系統設計
> 4. [docs/開發規則.md](docs/開發規則.md) - 編碼規範

---

## ⚠️ 安全邊界

### ✅ 可以執行的操作
- 讀取/修改 `src/` 代碼
- 讀取/寫入 `data/` 新聞數據
- 更新 `docs/` 文檔
- 執行 `python3 src/*.py` 測試
- 使用 `gh` CLI 管理 GitHub
- 提交並推送代碼（測試後）

### ⚠️ 需要用戶確認的操作
- 修改 cron 配置（時間、命令）
- 刪除歷史新聞數據
- 更改 RSS 來源 URL
- 修改版權聲明內容
- 更改 GitHub Pages 配置

### ❌ 禁止的操作
- 訪問外部 API（除了 RSS feed）
- 修改其他倉庫
- 執行未測試的危險命令
- 推送未測試的代碼到 main 分支

---

## 📋 常見任務流程

### 添加新功能
```
1. 修改 src/ 相關文件
   ↓
2. 測試：python3 src/fetch_news.py
   ↓
3. 更新 docs/更新記錄.md（添加新版本條目）
   ↓
4. Commit message 包含 🤖 Model: qwen/qwen3.5-plus
   ↓
5. 推送前確認 cron 配置未受影響
```

### 修復 bug
```
1. 查看日誌：
   - data/cron.log - cron 執行日誌
   - data/fetch.log - 抓取詳細日誌
   ↓
2. 定位問題代碼
   ↓
3. 修復後測試
   ↓
4. 更新 docs/known-issues.md（記錄問題和解決方案）
   ↓
5. 更新版本號和日期
```

### 文檔更新
```
1. 檢查所有 .md 文件的版本號
   ↓
2. 更新「最後更新」日期
   ↓
3. 確保 cron 時間一致（README + 專案說明）
   ↓
4. Commit 時詳細說明變更
```

---

## 🔍 故障排除

### 問題：抓取任務失敗
**檢查：**
```bash
# 查看 cron 日誌
tail -50 data/cron.log

# 查看抓取日誌
tail -50 data/fetch.log

# 測試 RSS 可訪問性
curl -I https://govinfohub.gcs.gov.mo/api/rss/n/zh-hant
```

**解決方案：**
```bash
# 手動測試抓取
python3 src/fetch_news.py
```

---

### 問題：GitHub Pages 未更新
**檢查：**
```bash
# 檢查 Actions 運行狀態
gh run list --workflow deploy-pages.yml --limit 5

# 檢查 Pages 配置
gh api repos/john-fb-agent/govmo-news/pages

# 檢查 public/ 文件夾
ls -la public/
```

**解決方案：**
```bash
# 手動觸發部署
gh workflow run deploy-pages.yml
```

---

### 問題：JSON 文件覆蓋（歷史教訓）
**問題：** 2026-04-15 前，每次抓取會覆蓋當天 JSON 文件

**現在：** 使用合併模式（載入 → 合併 → 保存）

**驗證：**
```bash
# 檢查當天新聞是否累積
cat data/processed/2026/04/16.json | jq '. | length'
```

---

## ⏰ Cron 時間表（快速參考）

| 時間 | 任務 | 腳本 |
|------|------|------|
| 09:00, 11:00, 13:00, 15:00, 18:00 | 新聞抓取 | `src/fetch_news.py` |
| 01:00 | 自動抓取 + 推送 | `deployment/scripts/auto-push.sh` |
| 08:00 | AI 新聞總結 | OpenClaw Cron |

**注意：** 所有時間為澳門時間 (GMT+8)

---

## 📁 關鍵路徑

```
govmo-news/
├── src/
│   ├── fetch_news.py      # 主抓取腳本
│   └── rss_parser.py      # RSS 解析器
├── data/processed/YYYY/MM/DD.json  # 新聞數據
├── public/                # GitHub Pages 文件
├── deployment/scripts/
│   └── auto-push.sh       # 自動推送腳本
└── docs/                  # 文檔
```

---

## 🔄 文件更新記錄

| 日期 | 更新內容 | AI Agent |
|------|---------|----------|
| 2026-04-16 20:04 | 初始創建 | qwen/qwen3.5-plus |

---

## 📞 資源連結

### 內部文檔
- [README.md](README.md) - 主說明文件
- [docs/專案說明.md](docs/專案說明.md)
- [docs/架構說明.md](docs/架構說明.md)
- [docs/開發規則.md](docs/開發規則.md)
- [docs/更新記錄.md](docs/更新記錄.md)
- [docs/known-issues.md](docs/known-issues.md)

### 外部資源
- RSS Feed: https://govinfohub.gcs.gov.mo/api/rss/n/zh-hant
- GitHub Pages: https://john-fb-agent.github.io/govmo-news/
- OpenClaw: https://docs.openclaw.ai/

---

**最後更新：** 2026-04-16 20:04  
**維護者：** AI Agent (你可以修改這份文件！)
