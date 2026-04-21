# Task: Issues #6, #7, #8 Batch Processing

**Created:** 2026-04-21 12:05  
**Status:** In Progress  
**Model:** qwen/qwen3.5-plus  
**Related Issues:** #6 (closed), #7, #8

---

## 1. Work Brief

Handle Issues #6, #7, #8 together:

- **Issue #6:** 建立生成後 Lint Gate - ✅ Closed (not necessary)
- **Issue #7:** 統一章節命名（全部新聞列表、分類統計）
- **Issue #8:** 統一頁面標題與日期格式（含星期）

---

## 2. TODO List

- [x] Close Issue #6 (not necessary)
- [x] Analyze current chapter names across all HTML files (Issue #7)
- [x] Analyze current title/date formats across all HTML files (Issue #8)
- [x] Standardize chapter names:
  - Fixed 2026-04-14.html (`全部新聞` → `全部新聞列表`, `新聞分類統計` → `分類統計`)
- [x] Standardize title formats:
  - Fixed 2026-04-14.html, 2026-04-16.html (unified to `澳門政府新聞總結 - YYYY-MM-DD`)
- [x] Standardize date formats:
  - Fixed 2026-04-16.html (added `<strong>日期：</strong>` prefix)
- [x] Update generate_summary.py template (`完整新聞列表` → `全部新聞列表`)
- [ ] Commit and push changes
- [ ] Update documentation ⚠️ (requires user approval)

---

## 3. Information

[Will add commands, logs, and findings as work progresses]
