#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Classification Statistics
Reads classification data and generates category/department statistics

Schedule: After generate_summary.py runs
"""

import json
from pathlib import Path
from datetime import datetime
from collections import Counter

# Configuration
BASE_DIR = Path(__file__).parent.parent
CLASSIFICATION_DIR = BASE_DIR / "data" / "classification"
STAT_DIR = BASE_DIR / "stat" / "class"
LOG_FILE = BASE_DIR / "data" / "classification_stats.log"

def log(message):
    """Log message to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"{timestamp} - {message}"
    print(log_msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + "\n")

def get_today_classification():
    """Get today's classification data"""
    today = datetime.now().strftime("%Y-%m-%d")
    classification_file = CLASSIFICATION_DIR / f"{today}.json"
    
    if not classification_file.exists():
        log(f"❌ Classification file not found: {classification_file}")
        return None, today
    
    with open(classification_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    log(f"📊 Loaded classification data for {today}")
    
    return data, today

def generate_stats(classification_data, date_str):
    """Generate statistics from classification data"""
    news_items = classification_data.get('news', []) or classification_data.get('classifications', [])
    
    # Count by category
    category_counter = Counter()
    importance_counter = Counter()
    
    for news in news_items:
        category = news.get('category', '未分類')
        importance = news.get('importance', 1)
        
        category_counter[category] += 1
        importance_counter[importance] += 1
    
    # Build stats object
    stats = {
        "date": date_str,
        "total_count": len(news_items),
        "category_stats": dict(category_counter),
        "importance_stats": {
            "高": importance_counter.get(3, 0),
            "中": importance_counter.get(2, 0),
            "低": importance_counter.get(1, 0)
        },
        "generated_at": datetime.now().isoformat()
    }
    
    return stats

def save_stats(stats, date_str):
    """Save statistics to stat/class/YYYY/MM/DD.json"""
    today = datetime.now()
    year = today.strftime("%Y")
    month = today.strftime("%m")
    
    output_dir = STAT_DIR / year / month
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{date_str}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    log(f"✅ Stats saved to: {output_file}")
    
    return output_file

def main(target_date=None):
    """Main execution"""
    log("=" * 60)
    log("Generating classification statistics...")
    log("=" * 60)

    if target_date is None:
        target_date = datetime.now().strftime("%Y-%m-%d")

    classification_file = CLASSIFICATION_DIR / f"{target_date}.json"
    if not classification_file.exists():
        log(f"❌ Classification file not found: {classification_file}")
        return 1

    with open(classification_file, 'r', encoding='utf-8') as f:
        classification_data = json.load(f)

    log(f"📊 Loaded classification data for {target_date}")

    try:
        # Generate stats
        stats = generate_stats(classification_data, target_date)

        log(f"📊 Total news: {stats['total_count']}")
        log(f"📊 Category breakdown:")
        for category, count in sorted(stats['category_stats'].items(), key=lambda x: x[1], reverse=True):
            log(f"   {category}: {count}")
        log(f"📊 Importance breakdown:")
        log(f"   高：{stats['importance_stats']['高']}")
        log(f"   中：{stats['importance_stats']['中']}")
        log(f"   低：{stats['importance_stats']['低']}")

        # Save stats
        save_stats(stats, target_date)

        log("=" * 60)
        log("Classification statistics generation completed!")
        log("=" * 60)

        return 0

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        log(f"❌ CRITICAL ERROR: {error_msg}")
        return 1


if __name__ == "__main__":
    import sys
    # Support python3 script.py YYYY-MM-DD
    target = sys.argv[1] if len(sys.argv) > 1 else None
    sys.exit(main(target_date=target))
