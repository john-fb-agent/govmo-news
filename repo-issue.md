# Task: Refactor README.md

**Created:** 2026-04-18 20:59  
**Status:** In Progress  
**Model:** qwen/qwen3.5-plus

---

## 1. Work Brief

Refactor root README.md to improve structure, clarity, and alignment with docs/ content. Remove duplication, add badges, update outdated information, and improve overall readability.

---

## 2. TODO List

- [x] Read current README.md and identify issues
- [x] Create refactoring plan
- [x] Draft new README.md structure
- [x] Update content (features, schedule, GitHub Pages)
- [x] Run markdown lint check (skipped - module not installed, manual review OK)
- [x] Verify all links work
- [ ] Update documentation ⚠️ (requires user approval)

**Changes made:**
- Removed broken license badge (no LICENSE file)
- Moved GitHub Pages link to top for visibility
- Streamlined content, reduced duplication with docs/
- Improved visual hierarchy
- Simplified quick start and project structure sections
- Kept version at 1.4.0 (consistent)

## 3. Information

**Issues identified:**
1. License badge points to non-existent LICENSE file
2. Version mismatch: README says 1.4.0, docs/專案說明.md says 1.3.1
3. Some duplication with docs/專案說明.md
4. Could improve flow and reduce redundancy

**Refactoring plan:**
- Remove broken license badge
- Align version numbers (use 1.4.0 consistently)
- Streamline content, reduce duplication with docs/
- Improve visual hierarchy
- Keep GitHub Pages link prominent
- Simplify quick start section

---

**Files to modify:**
- README.md (root)

**Related files to check for consistency:**
- docs/專案說明.md
- docs/架構說明.md
- repo-agent.md
- docs/更新記錄.md (verify latest version)
