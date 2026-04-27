# AI Agent 指南

**創建：** 2026-04-16 20:04 | **Provider:** OpenClaw | **Model:** minimax/MiniMax-M2.7  
**最後更新：** 2026-04-22 | **Last Review：** 2026-04-22

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

| 時間 | 任務 |
|------|------|
| 09/11/13/15/18 時 | 新聞抓取 |
| 08:00 UTC (16:00 Macau) | AI 總結生成 |

**Cron ID:** `6d4bc06c-6dfe-4801-ba12-af71874a1a58`
**Session:** `isolated` + `session-key: agent:main:main`（使用 main session 的 AI 憑證）
**Timeout:** 1800s（30 分鐘）
**Delivery:** none

⚠️ 重要：不要使用 `--session main`（需要 systemEvent payload），使用 `session-key agent:main:main` 代替。

---

## 📁 關鍵文件

```
src/fetch_news.py                      # 新聞抓取
src/rss_parser.py                      # RSS 解析
src/generate_summary.py                 # AI 總結生成（使用 OpenClaw agent CLI）
src/generate_classification_stats.py    # 分類統計（支援 YYYY-MM-DD 參數）
src/summary_prompt.txt                  # AI 提示詞模板
data/processed/YYYY/MM/DD.json          # 原始新聞數據
data/classification/YYYY-MM-DD.json   # 分類結果
stat/class/YYYY/MM/DD.json             # 分類統計
public/                                # GitHub Pages
```

---

## 🔗 資源

- RSS: https://govinfohub.gcs.gov.mo/api/rss/n/zh-hant
- Pages: https://john-fb-agent.github.io/govmo-news/
- GitHub Issues: https://github.com/john-fb-agent/govmo-news/issues

---

## 📝 重要標準格式（2026-04-21 統一）

### 重要性標籤
- **格式：** `高`、`中`、`低`（不用數字或星星）
- **CSS class：** `.importance-badge` + `.badge-high`/`.badge-medium`/`.badge-low`
- **HTML 範例：** `<span class="importance-badge badge-high">高</span>`

### 重點新聞標題
- **統一格式：** `🔥 重點新聞（高重要性）`
- **位置：** `<h2>` 標籤內
- **所有頁面：** public/2026-04-14.html 至 public/2026-04-20.html 已統一

### AI 提示詞（summary_prompt.txt）
- **重要性描述：** 使用 高/中/低，不用 ⭐⭐⭐
- **importance 值：** 3=高，2=中，1=低

### 返回索引頁連結
- **格式：** `<a href="index.html" class="back-link">← 返回索引頁</a>`
- **位置：** Footer 之前
- **CSS：** `.back-link { display: inline-block; margin-bottom: 20px; color: #00A86B; text-decoration: none; }`
- **所有頁面：** public/2026-04-14.html 至 public/2026-04-20.html 已統一

### 章節命名（Issue #7）
- **統一格式：** `📋 全部新聞列表`、`📊 分類統計`
- **避免混用：** 不要用 `全部新聞` 或 `新聞分類統計`

### 頁面標題與日期格式（Issue #8）
- **Title 格式：** `澳門政府新聞總結 - YYYY-MM-DD`
- **日期格式：** `<p><strong>日期：</strong>YYYY 年 M 月 D 日（星期 X）</p>`
- **時區：** Asia/Macau

### 頁尾 Metadata 格式（Issue #9）
- **統一格式：**
  ```html
  <div class="footer">
      <strong>資料來源：</strong>澳門特別行政區政府新聞局 (GCS)<br>
      <strong>生成時間：</strong>YYYY-MM-DD HH:MM (Asia/Macau)<br>
      <strong>Provider:</strong> OpenClaw | <strong>Model:</strong> minimax/MiniMax-M2.7
  </div>
  ```

### 部門每日統計（Issue #14）
- **數據來源：** RSS dc:creator 欄位（feedparser 映射為 author）
- **存儲位置：** stat/dept/YYYY/MM/DD.json
- **生成時機：** 每次 fetch_news.py 執行後自動生成
- **網頁顯示：** generate_summary.py 整合部門統計到 HTML
- **開始日期：** 2026-04-21（不追溯）

### 新聞分類系統（Issue #15）
- **分類數量：** 10 類
- **分類列表：**
  - 🏦 金融財政、💼 經濟產業、🔬 科技創新
  - 🎭 文化體育、🚦 交通運輸、🎓 教育發展
  - 👥 人才發展、🛡️ 國家安全、🏠 社會服務
  - 🏛️ 政府管治
- **AI 提示詞：** src/summary_prompt.txt
- **分類數據存儲：** data/classification/YYYY-MM-DD.json（鍵名：`classifications`）
- **統計數據存儲：** stat/class/YYYY/MM/DD.json
- **生成腳本：**
  - `generate_summary.py` — 主腳本，生成 HTML + 分類 + 統計
  - `generate_classification_stats.py` — 獨立統計腳本，支援 `python3 script.py YYYY-MM-DD`
- **重要：** `generate_summary.py` 的 `save_html()` 不再覆蓋 `index.html`
- **HTML 章節順序：** 頁面標題 → 🔥 今日綜合摘要 → 📊 分類統計 → 🔥 重點新聞 → 📋 全部新聞列表
- **實施日期：** 2026-04-21 起

---

**最後更新：** 2026-04-27 | **Last Review：** 2026-04-27 | **維護者：** AI Agent

---

## 🖼️ HTML 模板標準（2026-04-27 更新）

**⚠️ 重要：任何時候都不應完全替換 `build_html()` 模板！**

`generate_summary.py` 中的 `build_html()` 使用固定的卡片式模板，已經是 04-14 至 04-23 的統一風格。修改時只能：
- ✅ 新增功能（如 AI 摘要）
- ✅ 調整變量（如 importance threshold）
- ❌ 不可完全重寫 `build_html()` 或替換整個 HTML/CSS 結構

**模板關鍵元素：**
- **外層結構：** `.card` 包圍每個內容區塊（白底、圓角、陰影）
- **標題：** `<h2>🔥 今日綜合摘要</h2>`、`<h2>📊 分類統計</h2>`、`<h2>🔥 重點新聞（高重要性）</h2>`、`<h2>📋 全部新聞列表</h2>`
- **摘要文字：** `.summary-text`（行高 1.9、段落 `<p>` 包裹）
- **統計卡片：** `.stats-grid` > `.stat-card` > `.stat-num` + `.stat-label`
- **重點新聞卡：** `.highlight-card`（橙左邊框 `#ff6b35`、`.cat` 綠標籤、`.imp` 橙標籤）
- **新聞列表：** `.cat-group` > `.news-row` > `.imp-dot`（dot-high/medium/low）+ `<a>`
- **Footer：** `.footer` + `.back-link`
- **主色：** `#00A86B`（綠色）
- **重要性 dots：** `.dot-high`=#dc3545、`.dot-medium`=#fd7e14、`.dot-low`=#aaa

**模板調用方式：**
```python
html = build_html(summary_data, date)  # 傳入 summary dict 和 datetime 對象
save_html(html, date)
```
