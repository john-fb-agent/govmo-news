# Task: Add Department Daily Statistics (Issue #14)

**Created:** 2026-04-21 12:48  
**Status:** In Progress  
**Model:** qwen/qwen3.5-plus  
**Related Issue:** #14

---

## 1. Work Brief

Implement department statistics from RSS dc:creator field:
- Extract dc:creator from RSS XML
- Create stat/ folder for statistics
- Build script to count daily department news
- Display department stats on GitHub Pages daily webpages
- Start from today (2026-04-21), no backfill

---

## 2. TODO List

- [x] Update rss_parser.py to extract dc:creator (via RSS author field)
- [x] Create stat/ folder structure
- [x] Create department statistics script (generate_department_stats.py)
- [x] Update generate_summary.py to display department stats
- [x] Integrated dept stats generation into fetch_news.py
- [x] Test with today's data (2026-04-21)
  - All 5 news items have department field recorded
  - Stats: 治安警察局：1, 文化局：2, 澳門旅遊大學：1, 澳門金融管理局：1
- [x] Commit and push changes
- [ ] Update documentation ⚠️ (requires user approval)

---

## 3. Information

[Will add commands, logs, and findings as work progresses]
