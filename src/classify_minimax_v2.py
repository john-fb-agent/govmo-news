#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiniMax-M2.7 classification with better prompt engineering
"""
import json
import subprocess
import os
import re
from pathlib import Path
from datetime import datetime
import time

LOG_FILE = Path(__file__).parent.parent / "data" / "classification_minimax.log"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"{timestamp} - {message}"
    print(log_msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + "\n")

def classify_single_news(title, summary, link, item_num, total_items):
    """Classify using MiniMax with JSON-focused prompt"""
    # Clean summary
    summary = re.sub(r'<[^>]+>', '', summary)
    summary = summary[:150]
    
    # Simple prompt with example
    prompt = f"""新聞標題：{title}
新聞摘要：{summary}

請分類到以下類別之一：金融財政、經濟產業、科技創新、文化體育、交通運輸、教育發展、人才發展、國家安全、社會服務、政府管治

評分：高 (3)、中 (2)、低 (1)

只輸出 JSON，不要其他文字：
{{"category":"金融財政","importance":2}}"""
    
    log(f"🤖 Classifying item {item_num}/{total_items}: {title[:30]}...")
    
    env = os.environ.copy()
    env["MINIMAX_API_KEY"] = 'os.environ.get("MINIMAX_API_KEY") or json.loads((Path.home()/".openclaw"/"credentials"/"minimax-default.apikey.json").read_text())["apiKey"]'
    
    try:
        result = subprocess.run([
            '/home/js/.npm-global/bin/openclaw', 'infer', 'model', 'run',
            '--prompt', prompt,
            '--model', 'minimax/MiniMax-M2.7'
        ], capture_output=True, text=True, timeout=90, env=env)
        
        if result.returncode == 0:
            output = result.stdout.strip()
            
            # Extract content after </think> tag (MiniMax reasoning model)
            if '</think>' in output:
                output = output.split('</think>')[-1].strip()
            
            # Find JSON in output
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
                    log(f"⚠️ JSON error: {e}")
                    log(f"Raw: {output[:100]}")
            else:
                log(f"⚠️ No JSON: {output[:80]}")
        else:
            log(f"❌ Failed: {result.stderr[:100]}")
    except subprocess.TimeoutExpired:
        log(f"❌ TIMEOUT (90s)")
    except Exception as e:
        log(f"❌ Error: {e}")
    
    return None

def main():
    log("=" * 60)
    log("MiniMax-M2.7 Classification (v2 - JSON prompt)")
    log("=" * 60)
    
    news_file = Path(__file__).parent.parent / "data" / "processed" / "2026" / "04" / "21.json"
    if not news_file.exists():
        log(f"❌ Not found: {news_file}")
        return 1
    
    with open(news_file, 'r', encoding='utf-8') as f:
        news_data = json.load(f)
    
    log(f"📰 {len(news_data)} items")
    
    classified = []
    category_counts = {}
    
    for i, news in enumerate(news_data, 1):
        title = news.get("title", "")
        link = news.get("link", "")
        summary = news.get("summary", "")
        guid = news.get("guid", "")
        
        result = classify_single_news(title, summary, link, i, len(news_data))
        if result:
            result["guid"] = guid
            classified.append(result)
            cat = result["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        time.sleep(1)
    
    if not classified:
        log("❌ Nothing classified")
        return 1
    
    output_dir = Path(__file__).parent.parent / "data" / "classification"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "2026-04-21.json"
    data = {
        "date": "2026-04-21",
        "news": classified,
        "category_stats": category_counts,
        "generated_at": datetime.now().isoformat(),
        "method": "MiniMax-M2.7"
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    log(f"✅ Saved: {output_file}")
    log("📊 Breakdown:")
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        log(f"   {cat}: {count}")
    log("=" * 60)
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
