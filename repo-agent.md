# AI Agent 指南

**創建時間：** 2026-04-16 20:04 (GMT+8)  
**創建者：** AI Agent (OpenClaw)  
**Provider:** Qwen  
**Model:** qwen/qwen3.5-plus

---

## 👋 給閱讀此文件的 AI Agent

> 這份文件是之前的 AI agent 為了協助你工作而創建的。
>
> **你可以：** 根據自己的想法修改、添加、刪除或重寫這份文件。
>
> **必讀文檔：**
> 1. [README.md](README.md) - 快速開始、cron 時間
> 2. [docs/專案說明.md](docs/專案說明.md) - 核心功能
> 3. [docs/架構說明.md](docs/架構說明.md) - 系統設計
> 4. [docs/開發規則.md](docs/開發規則.md) - 編碼規範

---

## ⚠️ 安全邊界

| 類型 | 操作 |
|------|------|
| ✅ **可以做** | 修改 `src/`、更新 `data/`、更新 `docs/`、執行測試、使用 `gh` CLI |
| ⚠️ **需確認** | 修改 cron、刪除數據、更改 RSS URL、修改版權聲明 |
| ❌ **禁止** | 訪問外部 API（除 RSS）、推送未測試代碼 |

---

## 📋 常見任務

### 添加功能
```
1. 修改 src/ → 2. 測試 → 3. 更新 docs/更新記錄.md → 4. Commit
```

### 修復 bug
```
1. 查看 data/cron.log 或 data/fetch.log → 2. 修復 → 3. 更新 docs/known-issues.md → 4. Commit
```

### 文檔更新
```
1. 更新 docs/更新記錄.md（新版本條目）
2. 更新所有 .md 文件的版本號和「最後更新」日期
3. 確保 cron 時間一致（README + 專案說明）
4. Commit message 包含 🤖 Model: qwen/qwen3.5-plus
```

---

## 🔍 故障排除

```bash
# 抓取失敗 - 查看日誌
tail -50 data/cron.log
tail -50 data/fetch.log

# 手動測試抓取
python3 src/fetch_news.py

# Pages 未更新 - 檢查 Actions
gh run list --workflow deploy-pages.yml --limit 5

# 驗證 JSON 累積（歷史教訓：2026-04-15 前會覆蓋）
cat data/processed/YYYY/MM/DD.json | jq '. | length'
```

---

## ⏰ Cron 時間表

| 時間 | 任務 |
|------|------|
| 09/11/13/15/18 | 新聞抓取 |
| 01:00 | 自動抓取 + 推送 |
| 08:00 | AI 新聞總結 |

---

## 📁 關鍵路徑

```
src/fetch_news.py              # 主抓取腳本
src/rss_parser.py              # RSS 解析器
data/processed/YYYY/MM/DD.json # 新聞數據
public/                        # GitHub Pages
deployment/scripts/auto-push.sh # 自動推送
```

---

## 📞 資源

- **RSS:** https://govinfohub.gcs.gov.mo/api/rss/n/zh-hant
- **Pages:** https://john-fb-agent.github.io/govmo-news/
- **OpenClaw:** https://docs.openclaw.ai/

---

**最後更新：** 2026-04-16 20:12  
**維護者：** AI Agent（你可以修改！）
