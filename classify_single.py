#!/usr/bin/env python3
"""Classify a single news item"""
import json
import subprocess
import sys
import re

def classify_news(title, summary, link):
    # Remove HTML and truncate
    summary = re.sub(r'<[^>]+>', '', summary)
    summary = summary[:150]
    
    prompt = f"""請將以下澳門政府新聞分類到其中一個類別：
金融財政、經濟產業、科技創新、文化體育、交通運輸、教育發展、人才發展、國家安全、社會服務、政府管治

並評定重要性：高(3)、中(2)、低(1)

新聞標題：{title}
摘要：{summary}

只輸出 JSON 格式：
{{"category": "類別", "importance": 1}}
"""
    
    try:
        result = subprocess.run([
            '/home/js/.npm-global/bin/openclaw', 'infer', 'model', 'run',
            '--prompt', prompt,
            '--model', 'qwen/qwen3.5-plus'
        ], capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0:
            output = result.stdout.strip()
            # Extract JSON
            if '{' in output:
                json_str = output[output.find('{'):output.rfind('}')+1]
                parsed = json.loads(json_str)
                return {
                    "title": title,
                    "category": parsed.get("category", "其他"),
                    "importance": parsed.get("importance", 1),
                    "link": link
                }
        print(f"Failed: {result.stderr[:200]}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    # Test with first news item
    test_news = {
        "title": "金管局赴深圳舉辦澳門投資基金業務推介活動",
        "summary": "為持續加強推廣澳門《投資基金法》及相關配套措施，吸引更多具資質及規模的投資基金管理公司落戶展業，由澳門金融管理局主辦...",
        "link": "https://www.gcs.gov.mo/detail/zh-hant/N26DULPKI2"
    }
    
    print(f"Classifying: {test_news['title']}")
    result = classify_news(**test_news)
    print(f"Result: {json.dumps(result, ensure_ascii=False, indent=2)}")
