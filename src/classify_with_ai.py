#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-based news classification (one item at a time)
Uses Qwen LLM with 5-minute timeout per item
"""
import json
import subprocess
import re
from pathlib import Path
from datetime import datetime

LOG_FILE = Path(__file__).parent.parent / "data" / "classification_ai.log"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"{timestamp} - {message}"
    print(log_msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + "\n")

def classify_single_news(title, summary, link, item_num, total_items):
    """Classify a single news item with AI"""
    # Clean summary
    summary = re.sub(r'<[^>]+>', '', summary)
    summary = summary[:200]
    
    prompt = f"""請將以下澳門政府新聞分類。

# 類別（選擇其一）
金融財政、經濟產業、科技創新、文化體育、交通運輸、教育發展、人才發展、國家安全、社會服務、政府管治

# 重要性評分
高 (3)：新政策、重大建設、影響廣泛民生、突發重要事件
中 (2)：常規政策、部門活動、數據發布
低 (1)：常規會議、小型活動、人事任命

# 輸入數據
標題：{title}
摘要：{summary}

# 輸出格式 (只輸出 JSON)
{{"category": "類別", "importance": 1}}

# 注意事項
- 使用繁體中文
- 分類必須是上述 10 個類別之一
- 只輸出 JSON，不要其他文字
"""
    
    log(f"🤖 Classifying item {item_num}/{total_items}: {title[:30]}...")
    
    import os
    env = os.environ.copy()
    env['PATH'] = '/home/js/.npm-global/bin:' + env.get('PATH', '')
    
    try:
        # 5 minute timeout per item
        result = subprocess.run([
            '/home/js/.npm-global/bin/openclaw', 'infer', 'model', 'run',
            '--prompt', prompt,
            '--model', 'qwen/qwen3.5-plus'
        ], capture_output=True, text=True, timeout=300, env=env)
        
        if result.returncode == 0:
            output = result.stdout.strip()
            # Extract JSON
            if '{' in output:
                json_str = output[output.find('{'):output.rfind('}')+1]
                try:
                    parsed = json.loads(json_str)
                    category = parsed.get("category", "其他")
                    importance = parsed.get("importance", 1)
                    log(f"✅ Item {item_num}/{total_items}: {category} (importance={importance})")
                    return {
                        "guid": "",
                        "title": title,
                        "category": category,
                        "importance": importance,
                        "link": link
                    }
                except json.JSONDecodeError as e:
                    log(f"⚠️ Failed to parse JSON: {e}")
                    log(f"Output: {output[:200]}")
            else:
                log(f"⚠️ No JSON in output: {output[:200]}")
        else:
            log(f"❌ Item {item_num} failed: {result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        log(f"❌ Item {item_num} TIMEOUT (5 min)")
    except Exception as e:
        log(f"❌ Item {item_num} error: {e}")
    
    # Fallback: return unclassified
    return {
        "guid": "",
        "title": title,
        "category": "其他",
        "importance": 1,
        "link": link
    }

def main():
    log("=" * 60)
    log("Starting AI classification (one item at a time)...")
    log("=" * 60)
    
    # Load news data
    news_file = Path(__file__).parent.parent / "data" / "processed" / "2026" / "04" / "21.json"
    if not news_file.exists():
        log(f"❌ News file not found: {news_file}")
        return 1
    
    with open(news_file, 'r', encoding='utf-8') as f:
        news_data = json.load(f)
    
    log(f"📰 Loaded {len(news_data)} news items")
    
    # Classify each item one at a time
    classified = []
    category_counts = {}
    
    for i, news in enumerate(news_data, 1):
        title = news.get("title", "")
        link = news.get("link", "")
        summary = news.get("summary", "")
        guid = news.get("guid", "")
        
        result = classify_single_news(title, summary, link, i, len(news_data))
        result["guid"] = guid
        classified.append(result)
        
        cat = result["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # Small delay between requests
        import time
        time.sleep(1)
    
    # Save classification
    output_dir = Path(__file__).parent.parent / "data" / "classification"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "2026-04-21.json"
    classification_data = {
        "date": "2026-04-21",
        "news": classified,
        "category_stats": category_counts,
        "generated_at": datetime.now().isoformat(),
        "method": "AI (qwen/qwen3.5-plus)"
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(classification_data, f, ensure_ascii=False, indent=2)
    
    log(f"✅ Classification saved to: {output_file}")
    log(f"📊 Category breakdown:")
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        log(f"   {cat}: {count}")
    log("=" * 60)
    log("AI classification completed!")
    log("=" * 60)
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
