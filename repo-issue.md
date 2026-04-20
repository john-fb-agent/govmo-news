# Task: 新增 12 項 GitHub Issues - 格式一致性改善清單

**Created:** 2026-04-20 14:55  
**Status:** Completed  
**Model:** qwen/qwen3.5-plus

---

## 1. Work Brief

關閉原有 Issue #1，改創建 12 項獨立 issues，每項包含標題、描述、驗收條件、估時、labels。

---

## 2. TODO List

- [x] 讀取 GITHUB-GUIDELINES.md
- [x] 讀取 repo-agent.md
- [x] 關閉原有 Issue #1
- [x] 創建所需 labels（format, quality, bug, ci, etc.）
- [x] 創建 12 項 issues（#2-#13）
- [x] 驗證 issues 創建成功

---

## 3. Information

**Issues 創建清單：**

| # | Title | Labels | Milestone |
|---|-------|--------|-----------|
| 2 | 統一重要性標示規格（高/中/低） | format, quality, breaking-risk | A |
| 3 | 統一重點新聞區塊標題樣式 | format, ui-consistency | A |
| 4 | 每日頁強制輸出返回索引頁連結 | navigation, template, ux | A |
| 5 | 修復查看原文連結輸出不穩定問題 | bug, data-integrity, parser | A |
| 6 | 建立生成後 Lint Gate | ci, quality-gate, automation | A |
| 7 | 統一章節命名 | content-schema, format | B |
| 8 | 統一頁面標題與日期格式 | format, i18n, ux | B |
| 9 | 標準化頁尾 metadata 區塊格式 | metadata, template, trust | B |
| 10 | 建立內容相似度去重規則 | nlp, quality, dedup | B |
| 11 | 建立抓取與解析失敗的回退策略 | reliability, pipeline, ops | B |
| 12 | 索引頁加入搜尋與篩選 | feature, index, ux | C |
| 13 | 新增昨日相比變化摘要 | feature, insight, analytics | C |

**命令：**
```bash
gh issue close 1
gh issue create --title "..." --body "..." --label "..."
gh issue list --limit 20
```

**結果：**
- Issue #1 已關閉
- Issues #2-#13 創建成功（共 12 項）
- 所有 labels 已創建
- Milestones 已存在（A/B/C）
