# Task: 透過 OpenClaw CLI 執行新聞分類任務

**Created:** 2026-04-22 19:22  
**Status:** In Progress  
**Model:** qwen/qwen3.5-plus  
**Related Issue:** #15 (新聞分類系統)

---

## 1. Work Brief

約翰要求使用 OpenClaw CLI（而非 API 调用）來執行或檢查新聞分類任務。需要：
1. 確認最新的分類任務是哪一個
2. 通過 `openclaw tasks` CLI 命令檢查或觸發分類任務

---

## 2. TODO List

- [ ] 創建 repo-issue.md（本文件）
- [x] 創建 repo-issue.md（本文件）
- [x] 確認分類任務的 task ID
- [x] 使用 openclaw tasks CLI 命令檢查任務
- [x] 使用 openclaw cron run 觸發分類 cron job
- [ ] 發現問題：HTTP 401 token 過期 ⚠️
- [ ] 修復認證問題
- [ ] 重新運行分類
- [ ] 更新文檔 ⚠️（需約翰確認）

---

## 3. Information

**相關背景任務（從 openclaw tasks list）：**
- `5f695250-…` cron timed_out — Daily News Summary（可能是分類任務）
- `b69e5a4c-…` cli succeeded — 17:19 任務，分析澳門政府新聞 JSON 數據

**可用 CLI 命令：**
```bash
openclaw tasks list
openclaw tasks show <task-id>
openclaw agent --message "..."
openclaw cron list
```

**repo-agent.md 關鍵信息：**
- 分類系統：10 類（🏦 金融財政、💼 經濟產業、🔬 科技創新 等）
- 分類數據：`data/classification/YYYY-MM-DD.json`
- 統計數據：`stat/class/YYYY/MM/DD.json`
