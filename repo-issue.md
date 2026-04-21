# Task: 統一重點新聞區塊標題樣式

**Created:** 2026-04-21 09:30  
**Status:** In Progress  
**Model:** qwen/qwen3.5-plus  
**Related Issue:** #3

---

## 1. Work Brief

Implement Issue #3: Standardize the "Key News" (重點新聞) section header style across all pages.

**Current styles found:**
- `重點新聞（高重要性）` - no emoji (2026-04-14, 2026-04-17)
- `🔥 重點新聞（高重要性）` - fire emoji (2026-04-15, 2026-04-16, 2026-04-19, 2026-04-20)
- `⭐ 重點新聞（高重要性）` - star emoji (2026-04-18)

**Standard:** Use `🔥 重點新聞（高重要性）` (most recent pages use this)

---

## 2. TODO List

- [x] Analyze current header styles across all pages
- [x] Fix inconsistent headers (2026-04-14, 2026-04-17, 2026-04-18)
- [x] Update generate_summary.py template
- [ ] Commit and push changes
- [ ] Update documentation ⚠️ (requires user approval)

---

## 3. Information

**Files modified:**
- public/2026-04-14.html (was: 重點新聞 → now: 🔥 重點新聞)
- public/2026-04-17.html (was: 重點新聞 → now: 🔥 重點新聞)
- public/2026-04-18.html (was: ⭐ 重點新聞 → now: 🔥 重點新聞)
- src/generate_summary.py (was: 🔑 重點新聞 → now: 🔥 重點新聞（高重要性）)

**Standard format:** `🔥 重點新聞（高重要性）`

**Commands used:**
```bash
sed -i 's/<h2>重點新聞（高重要性）<\/h2>/<h2>🔥 重點新聞（高重要性）<\/h2>/g' public/2026-04-14.html public/2026-04-17.html
sed -i 's/<h2>⭐ 重點新聞（高重要性）<\/h2>/<h2>🔥 重點新聞（高重要性）<\/h2>/g' public/2026-04-18.html
```
