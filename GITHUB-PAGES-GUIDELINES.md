# GitHub Pages Guidelines

**Created:** 2026-04-16  
**Last Updated:** 2026-04-16  
**Purpose:** Standard procedures for deploying and maintaining GitHub Pages for govmo-news

---

## ⚠️ MANDATORY PRE-TASK CHECK

**BEFORE any GitHub Pages task, ALWAYS:**

1. **Read this file FIRST** - `/home/js/.openclaw/workspace/github-repos/govmo-news/GITHUB-PAGES-GUIDELINES.md`
2. **Check deployment history** - `gh run list --workflow deploy-pages.yml --limit 5`
3. **Verify current status** - `gh api repos/john-fb-agent/govmo-news/pages`
4. **Confirm file structure** - `gh api repos/john-fb-agent/govmo-news/contents/public`

---

## 📁 File Structure

### Required Structure
```
govmo-news/
├── public/                    # ALL web pages go here
│   ├── index.html            # Main index page (REQUIRED)
│   ├── 2026-04-14.html       # Daily summaries
│   ├── 2026-04-15.html
│   └── .nojekyll             # Disable Jekyll rendering (REQUIRED)
├── .github/
│   └── workflows/
│       └── deploy-pages.yml  # GitHub Actions workflow
└── [other project files]
```

### Critical Files

| File | Purpose | Required |
|------|---------|----------|
| `public/index.html` | Main landing page | ✅ YES |
| `public/.nojekyll` | Disable Jekyll theme | ✅ YES |
| `.github/workflows/deploy-pages.yml` | Deployment workflow | ✅ YES |

---

## 🚀 Deployment Workflow

### Current Configuration

**Workflow File:** `.github/workflows/deploy-pages.yml`

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup Pages
        uses: actions/configure-pages@v5
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: './public'
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### Deployment Triggers

| Trigger | Action |
|---------|--------|
| Push to `main` branch | Auto-deploy `public/` folder |
| Manual workflow dispatch | `gh workflow run deploy-pages.yml` |

---

## 🔧 GitHub Pages Configuration

### Required Settings

**Use GitHub CLI to configure:**

```bash
# Delete existing Pages configuration (if any)
gh api repos/john-fb-agent/govmo-news/pages --method DELETE

# Create new configuration with workflow mode
gh api repos/john-fb-agent/govmo-news/pages \
  --method POST \
  -F source[branch]='main' \
  -F source[path]='/' \
  -F build_type='workflow'
```

### Expected Configuration

```json
{
  "build_type": "workflow",
  "source": {
    "branch": "main",
    "path": "/"
  },
  "status": "ready",
  "https_enforced": true
}
```

### Verify Configuration

```bash
gh api repos/john-fb-agent/govmo-news/pages
```

**Check for:**
- ✅ `build_type: "workflow"` (NOT "legacy")
- ✅ `source.path: "/"` (root path)
- ✅ `status: null` or `"ready"` (not "building" or error)

---

## ✅ POST-DEPLOYMENT VERIFICATION (MANDATORY)

**⚠️ CRITICAL: You MUST verify pages are accessible and content is correct BEFORE marking task complete**

### Step 1: Check Deployment Status

```bash
# Check latest workflow run
gh run list --workflow deploy-pages.yml --limit 1

# Check Pages configuration
gh api repos/john-fb-agent/govmo-news/pages
```

**Expected:**
- ✅ Latest run: `conclusion: "success"`
- ✅ Pages status: `"ready"` or `null`

---

### Step 2: Verify Index Page Accessibility

```bash
curl -sI https://john-fb-agent.github.io/govmo-news/
```

**Expected HTTP Response:**
```
HTTP/2 200
server: GitHub.com
content-type: text/html; charset=utf-8
```

**❌ If 404:**
- Wait 1-2 minutes (CDN propagation)
- Check workflow run status
- Verify `public/index.html` exists

---

### Step 3: Verify Content is Correct

```bash
curl -s https://john-fb-agent.github.io/govmo-news/ | head -30
```

**Check for:**
- ✅ `<title>澳門政府新聞總結 - 索引</title>` (correct page title)
- ✅ Contains expected links (e.g., `2026-04-14.html`, `2026-04-15.html`)
- ✅ NOT showing README.md content (Jekyll theme)
- ✅ NOT showing "Site not found" or "404"

**Example expected content:**
```html
<!DOCTYPE html>
<html lang="zh-HK">
<head>
    <title>澳門政府新聞總結 - 索引</title>
</head>
<body>
    <h1>📰 澳門政府新聞總結</h1>
    ...
    <li><a href="2026-04-15.html">📅 2026-04-15</a></li>
    <li><a href="2026-04-14.html">📅 2026-04-14</a></li>
</body>
</html>
```

---

### Step 4: Verify Daily Summary Pages

```bash
# Check latest daily summary
curl -sI https://john-fb-agent.github.io/govmo-news/2026-04-15.html

# Check content
curl -s https://john-fb-agent.github.io/govmo-news/2026-04-15.html | head -20
```

**Expected:**
- ✅ HTTP 200
- ✅ Contains news summary content
- ✅ Correct date in title

---

### Step 5: Check File List in public/

```bash
gh api repos/john-fb-agent/govmo-news/contents/public --paginate \
  -q '.[] | {name: .name, size: .size}'
```

**Expected files:**
- ✅ `index.html` (2-3 KB)
- ✅ `2026-04-14.html` (12-17 KB)
- ✅ `2026-04-15.html` (12-17 KB)
- ✅ `.nojekyll` (0 bytes)

---

## 🐛 Troubleshooting

### Problem: Pages show README.md instead of index.html

**Symptoms:**
- Visiting https://john-fb-agent.github.io/govmo-news/ shows project README
- Page has Jekyll theme styling
- Content is repository description, not news summaries

**Solution:**
```bash
# Ensure build_type is "workflow"
gh api repos/john-fb-agent/govmo-news/pages --method DELETE
sleep 5
gh api repos/john-fb-agent/govmo-news/pages \
  --method POST \
  -F source[branch]='main' \
  -F source[path]='/' \
  -F build_type='workflow'
```

**Wait 1-2 minutes**, then verify again.

---

### Problem: 404 Not Found

**Symptoms:**
- `curl -sI` returns HTTP 404
- "Site not found" page

**Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| `public/index.html` missing | Create index.html in public/ |
| `.nojekyll` missing | Create empty `.nojekyll` file |
| Pages not configured | Run POST configuration command above |
| CDN not propagated | Wait 1-2 minutes, retry |

**Verification:**
```bash
# Check if index.html exists
gh api repos/john-fb-agent/govmo-news/contents/public/index.html

# Check Pages config
gh api repos/john-fb-agent/govmo-news/pages
```

---

### Problem: GitHub Actions deployment fails

**Symptoms:**
- `gh run list` shows `conclusion: "failure"`
- Workflow run failed at "Setup Pages" step

**Common Causes:**

1. **Missing `public/` folder**
   ```bash
   # Create if missing
   mkdir -p public
   ```

2. **Missing `public/index.html`**
   ```bash
   # Create index.html
   echo "<!DOCTYPE html><html><head><title>Index</title></head><body><h1>News Summaries</h1></body></html>" > public/index.html
   ```

3. **Workflow permissions issue**
   - Go to https://github.com/john-fb-agent/govmo-news/settings/actions
   - Ensure "Read and write permissions" is enabled

**Check workflow logs:**
```bash
gh run view <run-id> --log
```

---

## 📋 Checklist for Every GitHub Pages Task

### Before Starting
- [ ] Read this GITHUB-PAGES-GUIDELINES.md
- [ ] Check current deployment status: `gh run list --workflow deploy-pages.yml --limit 5`
- [ ] Verify Pages configuration: `gh api repos/john-fb-agent/govmo-news/pages`

### During Work
- [ ] All HTML files saved to `public/` folder (NOT `docs/`)
- [ ] `public/index.html` exists and is valid HTML
- [ ] `.nojekyll` file exists in `public/`
- [ ] Git commit includes all changes to `public/`

### After Deployment (MANDATORY VERIFICATION)
- [ ] Workflow run completed: `gh run list --workflow deploy-pages.yml --limit 1` → `conclusion: "success"`
- [ ] Index page accessible: `curl -sI https://john-fb-agent.github.io/govmo-news/` → HTTP 200
- [ ] Index content correct: `curl -s https://john-fb-agent.github.io/govmo-news/` → Shows news summary list
- [ ] NOT showing README.md or Jekyll theme
- [ ] Daily summary pages accessible: `curl -sI https://john-fb-agent.github.io/govmo-news/YYYY-MM-DD.html` → HTTP 200
- [ ] File list verified: `gh api repos/john-fb-agent/govmo-news/contents/public` → All expected files present

### Task Completion
- [ ] All verification steps passed
- [ ] Document results in task log
- [ ] Update GITHUB-PAGES-GUIDELINES.md if procedures changed

---

## 🔧 Useful Commands Reference

### Check Pages Status
```bash
gh api repos/john-fb-agent/govmo-news/pages
```

### Check Deployment History
```bash
gh run list --workflow deploy-pages.yml --limit 10
```

### Trigger Manual Deployment
```bash
cd /home/js/.openclaw/workspace/github-repos/govmo-news
gh workflow run deploy-pages.yml
```

### Verify File Exists
```bash
gh api repos/john-fb-agent/govmo-news/contents/public/index.html
```

### Test Page Accessibility
```bash
curl -sI https://john-fb-agent.github.io/govmo-news/
curl -s https://john-fb-agent.github.io/govmo-news/ | head -30
```

### Check Workflow YAML
```bash
gh workflow view deploy-pages.yml --yaml
```

---

## 📞 Support & Documentation

- **GitHub Pages Docs:** https://docs.github.com/en/pages
- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **OpenClaw GitHub Skill:** `/home/js/.npm-global/lib/node_modules/openclaw/skills/github/SKILL.md`

---

## 🔄 Update History

| Date | Change | Status |
|------|--------|--------|
| 2026-04-16 | Initial creation | ✅ Complete |
| | - Documented file structure | |
| | - Deployment workflow configuration | |
| | - GitHub Pages API configuration | |
| | - Post-deployment verification steps | |
| | - Troubleshooting guide | |

---

## ⚠️ REMEMBER

**NEVER mark a GitHub Pages task as complete without:**

1. ✅ Verifying deployment succeeded (`gh run list`)
2. ✅ Checking pages are accessible (`curl -sI`)
3. ✅ Confirming content is correct (`curl -s | head`)
4. ✅ Ensuring NOT showing README.md or Jekyll theme

**If verification fails, troubleshoot and retry until ALL checks pass!**
