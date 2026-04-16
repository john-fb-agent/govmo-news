# AI Agent 指南

**創建：** 2026-04-16 20:04 | **Provider:** Qwen | **Model:** qwen/qwen3.5-plus

---

## 👋 給 AI Agent

> 這份文件是之前的 AI agent 創建的，你可以隨意修改。
>
> **必讀：** README.md → docs/專案說明.md → docs/架構說明.md → docs/開發規則.md

---

## ⚠️ 安全邊界

| ✅ 可以做 | ⚠️ 需確認 | ❌ 禁止 |
|----------|----------|--------|
| 修改 src/、data/、docs/ | 修改 cron、刪除數據 | 訪問外部 API（除 RSS） |
| 執行測試、使用 gh CLI | 更改 RSS URL、版權 | 推送未測試代碼 |

---

## 📋 任務流程

**添加功能：** 修改 src/ → 測試 → 更新 docs/更新記錄.md → Commit

**修復 bug：** 查看 data/cron.log → 修復 → 更新 docs/known-issues.md → Commit

**文檔更新：** 更新 docs/更新記錄.md → 更新所有 .md 版本號 → 確保 cron 一致 → Commit

---

## 🔍 故障排除

```bash
# 查看日誌
tail -50 data/cron.log && tail -50 data/fetch.log

# 手動測試
python3 src/fetch_news.py

# Pages 檢查
gh run list --workflow deploy-pages.yml --limit 5
```

---

## ⏰ Cron

| 09/11/13/15/18 | 01:00 | 08:00 |
|----------------|-------|-------|
| 新聞抓取 | 自動推送 | AI 總結 |

---

## 📁 關鍵文件

```
src/fetch_news.py          # 主抓取
src/rss_parser.py          # RSS 解析
data/processed/YYYY/MM/DD.json
public/                    # GitHub Pages
deployment/scripts/auto-push.sh
```

---

## 🔗 資源

- RSS: https://govinfohub.gcs.gov.mo/api/rss/n/zh-hant
- Pages: https://john-fb-agent.github.io/govmo-news/

---

**最後更新：** 2026-04-16 20:15 | **維護者：** AI Agent
