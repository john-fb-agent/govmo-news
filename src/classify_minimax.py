#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiniMax AI classification via direct API (bypasses OpenClaw context issues)
"""
import json
import requests
import re
from pathlib import Path
from datetime import datetime
import time, os

API_KEY = os.environ.get("MINIMAX_API_KEY", "")
if not API_KEY:
    cred = Path.home() / ".openclaw" / "credentials" / "minimax-default.apikey.json"
    if cred.exists():
        API_KEY = json.loads(cred.read_text())["apiKey"]
if not API_KEY:
    raise ValueError("MINIMAX_API_KEY not set and no credentials file found")
API_URL = "https://api.minimaxi.com/v1/chat/completions"

LOG_FILE = Path(__file__).parent.parent / "data" / "classification_minimax.log"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"{timestamp} - {message}"
    print(log_msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + "\n")

def classify_single_news(title, summary, link, item_num, total_items):
    """Classify a single news item using MiniMax direct API"""
    # Clean summary
    summary = re.sub(r'<[^>]+>', '', summary)
    summary = summary[:200]
    
    # Simpler prompt for non-reasoning output
    prompt = f"""新聞：{title}
{summary}

分類：金融財政、經濟產業、科技創新、文化體育、交通運輸、教育發展、人才發展、國家安全、社會服務、政府管治
重要性：高 (3)/中 (2)/低 (1)

JSON：{{"category":"","importance":1}}"""
    
    log(f"🤖 Classifying item {item_num}/{total_items}: {title[:30]}...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "model": "MiniMax-M2.7",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 60
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Remove <think> reasoning tags
        if '<think>' in content:
            parts = content.split('</think>')
            content = parts[-1] if len(parts) > 1 else content
        
        # Extract JSON from response
        if '{' in content:
            json_str = content[content.find('{'):content.rfind('}')+1]
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
                log(f"⚠️ JSON parse error: {e}")
                log(f"Content: {content[:150]}")
        
        log(f"⚠️ No JSON in response: {content[:100]}")
        return None
    except Exception as e:
        log(f"❌ Item {item_num} error: {e}")
        return None

def main():
    log("=" * 60)
    log("Starting MiniMax AI classification (direct API)...")
    log("=" * 60)
    
    # Load news data
    news_file = Path(__file__).parent.parent / "data" / "processed" / "2026" / "04" / "21.json"
    if not news_file.exists():
        log(f"❌ News file not found: {news_file}")
        return 1
    
    with open(news_file, 'r', encoding='utf-8') as f:
        news_data = json.load(f)
    
    log(f"📰 Loaded {len(news_data)} news items")
    
    # Classify each item
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
        
        # Small delay between requests
        time.sleep(0.5)
    
    if not classified:
        log("❌ No items classified")
        return 1
    
    # Save classification
    output_dir = Path(__file__).parent.parent / "data" / "classification"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "2026-04-21.json"
    classification_data = {
        "date": "2026-04-21",
        "news": classified,
        "category_stats": category_counts,
        "generated_at": datetime.now().isoformat(),
        "method": "MiniMax-M2.5 (direct API)"
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(classification_data, f, ensure_ascii=False, indent=2)
    
    log(f"✅ Classification saved to: {output_file}")
    log(f"📊 Category breakdown:")
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        log(f"   {cat}: {count}")
    log("=" * 60)
    log("MiniMax classification completed!")
    log("=" * 60)
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
