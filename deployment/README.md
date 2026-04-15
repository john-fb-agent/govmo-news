# 部署說明

本文件說明如何部署 govmo-news 新聞抓取系統。

## 📋 前置條件

### 系統要求

- **作業系統：** Linux (Ubuntu 20.04+ 推薦) 或 macOS
- **Python:** 3.8 或更高版本
- **Git:** 用於克隆倉庫
- **cron:** 用於定時任務（Linux 系統通常預裝）

### 檢查前置條件

```bash
# 檢查 Python 版本
python3 --version

# 檢查 Git
git --version

# 檢查 cron 服務（Linux）
systemctl status cron
```

## 🚀 安裝步驟

### 步驟 1：克隆倉庫

```bash
cd /home/js/.openclaw/workspace/github-repos
git clone https://github.com/john-fb-agent/govmo-news.git
cd govmo-news
```

### 步驟 2：建立虛擬環境（推薦）

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安裝依賴
pip install -r requirements.txt
```

### 步驟 3：測試運行

```bash
# 使用測試腳本
./deployment/scripts/test-fetch.sh

# 或直接運行
python3 src/fetch_news.py
```

### 步驟 4：設置定時任務

```bash
# 安裝新聞抓取 cron（每日 5 次：9,11,13,15,17 點）
./deployment/scripts/setup-cron.sh

# 安裝自動推送 cron（每晚 10 點自動抓取並推送）
./deployment/scripts/setup-auto-push.sh

# 驗證安裝
crontab -l | grep govmo-news
```

## 📁 目錄結構

執行安裝後，將產生以下結構：

```
govmo-news/
├── data/
│   ├── processed/        # 處理後的 JSON 檔案（提交到 Git）
│   │   └── YYYY/MM/      # 按年/月組織
│   │       └── DD.json   # 每天一個 JSON 檔
│   ├── fetch.log         # 抓取日誌（本地，不提交）
│   ├── cron.log          # Cron 日誌（本地，不提交）
│   └── auto-push.log     # 自動推送日誌（本地，不提交）
├── venv/                 # Python 虛擬環境（可選）
└── ...
```

## 🔧 常見操作

### 查看日誌

```bash
# 查看最新日誌
tail -f data/fetch.log

# 查看 cron 日誌
tail -f data/cron.log

# 查看特定日期日誌
cat data/fetch.log | grep "2026-04-14"
```

### 手動執行抓取

```bash
cd /home/js/.openclaw/workspace/github-repos/govmo-news
python3 src/fetch_news.py
```

### 手動執行抓取並推送

```bash
# 使用自動推送腳本
cd /home/js/.openclaw/workspace/github-repos/govmo-news
./deployment/scripts/auto-push.sh
```

### 檢查已抓取的新聞

```bash
# 查看最新新聞
ls -lt data/processed/*/*/*.json | head -10

# 統計新聞數量
find data/processed -name "*.json" | wc -l

# 查看某日新聞內容
cat data/processed/2026/04/15.json | python -m json.tool
```

### 更新代碼

```bash
cd /home/js/.openclaw/workspace/github-repos/govmo-news
git pull
source venv/bin/activate
pip install -r requirements.txt  # 如有新依賴
```

### 移除定時任務

```bash
# 移除新聞抓取 cron
./deployment/scripts/remove-cron.sh

# 移除自動推送 cron
./deployment/scripts/remove-auto-push.sh
```

## ⚠️ 注意事項

### 權限問題

確保腳本有執行權限：

```bash
chmod +x deployment/scripts/*.sh
chmod +x src/backend/*.py
```

### 時區設定

定時任務使用系統時區。確保系統時區設置為澳門時間（GMT+8）：

```bash
# 檢查時區
timedatectl | grep "Time zone"

# 設置時區（如需要）
sudo timedatectl set-timezone Asia/Macau
```

### 日誌輪轉

日誌檔案可能隨時間變大，建議設置日誌輪轉：

```bash
# 編輯 logrotate 配置
sudo nano /etc/logrotate.d/govmo-news

# 添加以下內容：
/home/js/.openclaw/workspace/github-repos/govmo-news/data/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
}
```

### 備份建議

定期備份以下目錄：

- `data/processed/` - 所有新聞數據
- `data/processed/.processed_ids.json` - 去重數據庫

## 🐛 常見問題

### Q: Cron 任務沒有執行

**檢查清單：**

1. cron 服務是否運行：`systemctl status cron`
2. cron 日誌：`grep CRON /var/log/syslog | tail -20`
3. 腳本路徑是否正確：`crontab -l`
4. 腳本是否有執行權限：`ls -la deployment/scripts/`

### Q: 抓取失敗

**檢查清單：**

1. 網絡連接：`curl -I https://govinfohub.gcs.gov.mo/api/rss/n/zh-hant`
2. Python 依賴：`pip list | grep feedparser`
3. 查看錯誤日誌：`tail -50 data/fetch.log`

### Q: 重複新聞被保存

**可能原因：**

1. 去重數據庫損壞
2. RSS feed 的 URL 或標題格式改變

**解決方案：**

```bash
# 重建去重數據庫
rm data/processed/.processed_ids.json
python src/backend/fetch_news.py  # 重新抓取
```

## 📞 技術支持

如遇問題，請查看：

- [測試說明](../tests/README.md)
- [已知問題](../docs/known-issues.md)
- GitHub Issues: https://github.com/john-fb-agent/govmo-news/issues

---

**最後更新：** 2026-04-15  
**維護者：** john-fb-agent
