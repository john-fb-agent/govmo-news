# 開發容器設置（待實施）

## 📋 現狀

目前尚未配置開發容器。本文檔說明未來的開發容器設置計劃。

## 🎯 目標

提供一致的開發環境，確保所有開發者使用相同的：

- Python 版本
- 依賴套件
- 開發工具
- 環境變數

## 📦 計劃配置

### devcontainer.json

```json
{
  "name": "govmo-news",
  "image": "python:3.10-slim",
  "forwardPorts": [],
  "postCreateCommand": "pip install -r requirements.txt",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/usr/local/bin/python",
        "python.linting.enabled": true,
        "python.formatting.provider": "black"
      }
    }
  }
}
```

### Dockerfile（如需要自定義）

```dockerfile
FROM python:3.10-slim

WORKDIR /workspace

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["bash"]
```

## 🚀 使用方式（未來）

### 使用 VS Code

1. 安裝 "Remote - Containers" 擴展
2. 打開項目文件夾
3. 點擊左下角藍色圖標
4. 選擇 "Reopen in Container"

### 使用其他工具

```bash
# 如使用 devcontainer CLI
devcontainer up --workspace-folder .
devcontainer exec --workspace-folder . python src/backend/fetch_news.py
```

## ⚠️ 目前替代方案

在開發容器實施前，請使用：

### 虛擬環境

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Docker（手動）

```bash
docker run -it --rm \
  -v $(pwd):/app \
  -w /app \
  python:3.10-slim \
  bash

# 在容器內
pip install -r requirements.txt
python src/backend/fetch_news.py
```

## 📝 實施清單

- [ ] 建立 `.devcontainer/devcontainer.json`
- [ ] 建立 `.devcontainer/Dockerfile`（如需要）
- [ ] 測試容器啟動
- [ ] 測試代碼運行
- [ ] 更新本文檔

## 📞 相關文檔

- [部署說明](../deployment/README.md)
- [測試說明](../tests/README.md)
- [開發規則](../docs/開發規則.md)

---

**最後更新：** 2026-04-14  
**維護者：** john-fb-agent  
**狀態：** 待實施
