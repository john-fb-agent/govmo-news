# 測試說明

本文件說明如何測試 govmo-news 新聞抓取系統。

## 📋 測試類型

### 1. 手動測試（目前主要方式）

由於系統處於開發初期，目前以手動測試為主。

### 2. 自動化測試（待開發）

未來將加入 pytest 自動化測試。

## 🚀 手動測試步驟

### 測試入口

**主要測試腳本：**

```bash
./deployment/scripts/test-fetch.sh
```

**或直接運行：**

```bash
python src/backend/fetch_news.py
```

### 前置條件

1. **Python 環境已設置**
   ```bash
   python3 --version  # 應為 3.8+
   pip list | grep feedparser  # 應顯示 feedparser
   ```

2. **網絡連接正常**
   ```bash
   curl -I https://govinfohub.gcs.gov.mo/api/rss/n/zh-hant
   ```
   應返回 HTTP 200

3. **目錄權限**
   ```bash
   ls -la data/
   # 應可寫入
   ```

### 測試流程

#### 測試 1：基本抓取功能

```bash
# 1. 運行抓取腳本
cd /home/js/.openclaw/workspace/github-repos/govmo-news
python src/backend/fetch_news.py

# 2. 檢查輸出
# 應看到類似以下日誌：
# "Fetched X news items"
# "New entries saved: Y"

# 3. 檢查生成的檔案
ls -la data/raw/  # 應有 XML 檔案
ls -la data/processed/  # 應有 JSON 檔案和.processed_ids.json
```

**預期結果：**
- ✅ 日誌顯示成功抓取
- ✅ `data/raw/` 目錄有 XML 檔案
- ✅ `data/processed/` 目錄有 JSON 檔案（按年/月/日組織）
- ✅ `.processed_ids.json` 已更新

#### 測試 2：去重功能

```bash
# 1. 首次運行
python src/backend/fetch_news.py

# 2. 記錄新聞數量
FIRST_COUNT=$(find data/processed -name "*.json" | wc -l)
echo "首次運行後新聞數量：$FIRST_COUNT"

# 3. 立即再次運行（不應有新新聞）
python src/backend/fetch_news.py

# 4. 檢查新聞數量
SECOND_COUNT=$(find data/processed -name "*.json" | wc -l)
echo "第二次運行後新聞數量：$SECOND_COUNT"

# 5. 驗證
if [ "$FIRST_COUNT" -eq "$SECOND_COUNT" ]; then
    echo "✅ 去重功能正常"
else
    echo "❌ 去重功能異常"
fi
```

**預期結果：**
- ✅ 第二次運行沒有新新聞保存
- ✅ 日誌顯示 "Duplicates skipped: X"

#### 測試 3：日期組織結構

```bash
# 檢查 JSON 檔案是否按年/月組織
find data/processed -type d -name "20*"  # 應看到年份目錄
find data/processed -type d -name "01" -o -name "02"  # 應看到月份目錄
find data/processed -name "*.json" | head -5  # 查看檔案結構
```

**預期結果：**
- ✅ 目錄結構為 `YYYY/MM/DD.json`（每天一個 JSON 檔）
- ✅ 每個 JSON 檔案包含該日所有新聞（array 格式）

#### 測試 4：定時任務（如已安裝）

```bash
# 1. 檢查 cron 任務
crontab -l | grep govmo-news

# 2. 應看到 6 個任務：
#    - 新聞抓取（5 次）：9, 11, 13, 15, 17 點
#    - 自動推送（1 次）：22 點
# 0 9 * * * ...
# 0 11 * * * ...
# 0 13 * * * ...
# 0 15 * * * ...
# 0 17 * * * ...
# 0 22 * * * ... (auto-push.sh)

# 3. 查看 cron 日誌
tail -20 data/cron.log

# 4. 查看自動推送日誌
tail -20 data/auto-push.log
```

## 📊 測試檢查清單

每次測試前請確認：

- [ ] Python 環境正常
- [ ] 網絡連接正常
- [ ] RSS URL 可訪問
- [ ] 目錄有寫入權限
- [ ] 依賴套件已安裝

測試後請確認：

- [ ] 日誌無 ERROR 級別錯誤
- [ ] JSON 檔案格式正確
- [ ] 去重功能正常
- [ ] 日期目錄結構正確

## 🐛 已知問題與測試限制

### 目前無法自動化測試的項目

1. **RSS Feed 可用性**
   - 依賴外部服務（澳門政府新聞局）
   - 無法保證 100% 在線
   - 測試可能因外部服務不可用而失敗

2. **定時任務測試**
   - 需要等待實際執行時間
   - 建議手動觸發測試

3. **長期運行穩定性**
   - 需要觀察數天/數週
   - 建議設置監控

### 測試數據清理

測試後如需清理數據：

```bash
# 清理所有抓取數據
rm -rf data/raw/*
rm -rf data/processed/*
rm data/fetch.log data/cron.log

# 重新開始
python src/backend/fetch_news.py
```

## 🔧 除錯技巧

### 啟用詳細日誌

編輯 `src/backend/fetch_news.py`，修改日誌級別：

```python
logging.basicConfig(
    level=logging.DEBUG,  # 改為 DEBUG
    ...
)
```

### 檢查 RSS 內容

```bash
# 直接查看 RSS feed
curl -s https://govinfohub.gcs.gov.mo/api/rss/n/zh-hant | head -50

# 或使用 Python 解析
python -c "
import feedparser
feed = feedparser.parse('https://govinfohub.gcs.gov.mo/api/rss/n/zh-hant')
print(f'Title: {feed.feed.title}')
print(f'Entries: {len(feed.entries)}')
for entry in feed.entries[:3]:
    print(f'  - {entry.title}')
"
```

### 檢查 JSON 格式

```bash
# 驗證 JSON 格式
python -m json.tool data/processed/2026/04/14/*.json > /dev/null && echo "JSON 格式正確"

# 或使用 jq（如已安裝）
jq '.' data/processed/2026/04/14/*.json | head -20
```

## 📝 測試報告模板

測試完成後，請記錄：

```markdown
## 測試報告

**日期：** YYYY-MM-DD
**測試者：** [姓名]
**版本：** [Git commit 或 tag]

### 測試結果

| 測試項目 | 結果 | 備註 |
|---------|------|------|
| 基本抓取 | ✅/❌ | |
| 去重功能 | ✅/❌ | |
| 日期組織 | ✅/❌ | |
| 定時任務 | ✅/❌ | |

### 發現問題

1. [問題描述]

### 建議改進

1. [改進建議]
```

## 📞 問題回報

如測試中發現問題，請：

1. 記錄錯誤訊息和日誌
2. 檢查是否為已知問題
3. 提交 GitHub Issue: https://github.com/john-fb-agent/govmo-news/issues

---

**最後更新：** 2026-04-15  
**維護者：** john-fb-agent  
**版本：** 1.1.0
