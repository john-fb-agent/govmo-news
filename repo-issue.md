# Task: 統一重要性標示規格（高/中/低）

**Created:** 2026-04-21 09:12  
**Status:** In Progress  
**Model:** qwen/qwen3.5-plus  
**Related Issue:** #2

---

## 1. Work Brief

Implement Issue #2: Standardize importance labels across all generated pages to use only 高/中/低 (High/Medium/Low) format, removing numeric formats and mixed styles.

**Acceptance Criteria:**
- Daily pages only show 高/中/低 three importance levels
- No more numeric importance format (e.g., "重要性：3")
- Statistics section can correctly aggregate by importance

---

## 2. TODO List

- [x] Explore codebase to find importance label usage
- [x] Identify all templates/files that render importance
- [x] Standardize to 高/中/低 format only
  - Fixed public/2026-04-14.html (was ⭐⭐⭐)
  - Fixed public/2026-04-15.html (was 重要性：高)
  - Fixed public/2026-04-16.html (was 重要性：高)
  - Fixed public/2026-04-17.html (was 高重要性 ⭐)
  - Fixed public/2026-04-18.html (was 重要性：高)
  - Fixed public/2026-04-19.html (was 重要性：3)
  - public/2026-04-20.html already correct ✅
- [x] Updated generate_summary.py to use 高/中/低 instead of stars
- [ ] Test changes on sample data
- [ ] Update documentation ⚠️ (requires user approval)

---

## 3. Information

**Files analyzed:**
- public/2026-04-14.html through public/2026-04-20.html
- src/generate_summary.py

**Findings:**
- 2026-04-20.html: ✅ Already uses correct format (高/中/低)
- 2026-04-19.html: ❌ Uses "重要性：3" (numeric format)
- 2026-04-18.html: ❌ Uses "重要性：高" (verbose format)
- 2026-04-17.html: ❌ Uses "高重要性 ⭐" with emojis
- 2026-04-14.html: ❌ Uses "⭐⭐⭐" stars
- generate_summary.py: Uses stars (⭐ * importance)

**Standard format:** Just "高", "中", or "低" in the badge span

**Commands used:**
```bash
sed -i 's/重要性：3/高/g' public/2026-04-19.html
sed -i 's/重要性：高/高/g' public/2026-04-15.html public/2026-04-16.html public/2026-04-18.html
sed -i 's/高重要性 ⭐/高重要性/g' public/2026-04-17.html
sed -i 's/⭐⭐⭐ 重點新聞/重點新聞/g' public/2026-04-14.html
sed -i 's/<span class="importance-tag">⭐⭐⭐<\/span>/<span class="importance-badge badge-high">高<\/span>/g' public/2026-04-14.html
```

**Files changed:**
- public/2026-04-14.html through public/2026-04-19.html (6 HTML files)
- src/generate_summary.py (future generation)

**Next steps:**
1. Commit and push changes
2. Update documentation (README.md, docs/)
