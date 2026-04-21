# Task: 每日頁強制輸出返回索引頁連結

**Created:** 2026-04-21 10:17  
**Status:** In Progress  
**Model:** qwen/qwen3.5-plus  
**Related Issue:** #4

---

## 1. Work Brief

Implement Issue #4: Ensure all daily pages have a "Back to Index" link at the bottom.

**Current status:**
- ✅ 2026-04-15.html - Has link (← 返回索引頁面)
- ✅ 2026-04-17.html - Has link (← 返回索引頁)
- ❌ 2026-04-14.html - Missing
- ❌ 2026-04-16.html - Missing
- ❌ 2026-04-18.html - Missing (has 1 match, need to verify)
- ❌ 2026-04-19.html - Missing (has 1 match, need to verify)
- ❌ 2026-04-20.html - Missing

**Standard format:** `<a href="index.html" class="back-link">← 返回索引頁</a>`

---

## 2. TODO List

- [x] Analyze which pages have back-to-index links
- [x] Add missing links to pages:
  - 2026-04-14.html (added link + CSS)
  - 2026-04-16.html (added link with inline style)
  - 2026-04-20.html (added link + CSS)
  - 2026-04-15, 17, 18, 19 already had links ✅
- [x] Update generate_summary.py template (added CSS + link)
- [ ] Commit and push changes
- [ ] Update documentation ⚠️ (requires user approval)

---

## 3. Information

[Will add commands, logs, and findings as work progresses]
