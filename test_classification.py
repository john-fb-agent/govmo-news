#!/usr/bin/env python3
"""Test classification with minimal news items"""
import json
import subprocess
from pathlib import Path

# Load news data
news_file = Path("/home/js/.openclaw/workspace/github-repos/govmo-news/data/processed/2026/04/21.json")
with open(news_file, 'r', encoding='utf-8') as f:
    all_news = json.load(f)

# Test with just 2 items
test_news = all_news[:2]

# Simplify
simplified = []
for n in test_news:
    summary = n.get("summary", "")
    # Remove HTML tags
    import re
    summary = re.sub(r'<[^>]+>', '', summary)
    summary = summary[:100]  # 100 chars
    
    simplified.append({
        "title": n.get("title", ""),
        "summary": summary,
        "link": n.get("link", "")
    })

# Build prompt
prompt = f"""# 任務
分析澳門政府新聞，自動分類到以下 10 個類別：
金融財政、經濟產業、科技創新、文化體育、交通運輸、教育發展、人才發展、國家安全、社會服務、政府管治

# 重要性評分
高（3）：新政策、重大建設、影響廣泛民生、突發重要事件
中（2）：常規政策、部門活動、數據發布
低（1）：常規會議、小型活動、人事任命

# 輸入數據
{json.dumps(simplified, ensure_ascii=False)}

# 輸出格式 (只輸出 JSON)
{{
  "all_news": [
    {{"title": "...", "category": "...", "importance": 1, "link": "..."}}
  ]
}}

# 注意事項
- 使用繁體中文
- 只輸出 JSON，不要其他文字
- 分類必須是上述 10 個類別之一
"""

print(f"Testing with {len(simplified)} news items...")
print(f"Prompt size: {len(prompt)} chars\n")

# Run inference
result = subprocess.run([
    '/home/js/.npm-global/bin/openclaw', 'infer', 'model', 'run',
    '--prompt', prompt,
    '--model', 'qwen/qwen3.5-plus'
], capture_output=True, text=True, timeout=180)

print("STDOUT:")
print(result.stdout[:2000] if result.stdout else "(empty)")
print("\nSTDERR:")
print(result.stderr[:500] if result.stderr else "(empty)")
print(f"\nReturn code: {result.returncode}")
