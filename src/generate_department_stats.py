#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Daily Department Statistics
Run after fetch_news.py to count news by department

Usage: python3 generate_department_stats.py [YYYY-MM-DD]
       If no date provided, uses yesterday's date

Schedule: After each fetch (09/11/13/15/18)
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

# Configuration
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
STAT_DIR = BASE_DIR / "stat"
LOG_FILE = BASE_DIR / "data" / "department_stats.log"

def log(message):
    """Log message to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"{timestamp} - {message}"
    print(log_msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + "\n")

def get_news_path(date_obj):
    """Get JSON file path for a given date"""
    year = date_obj.strftime("%Y")
    month = date_obj.strftime("%m")
    day = date_obj.strftime("%d")
    return DATA_DIR / year / month / f"{day}.json"

def generate_stats(news_data, date_str):
    """Generate department statistics from news data"""
    # Count by department (split by " / " for multi-department entries)
    dept_counter = Counter()
    no_dept_count = 0

    for news in news_data:
        dept = news.get('department')
        if dept:
            # Split by " / " for entries like "經濟及科技發展局 / 旅遊局 / 博彩監察協調局"
            departments = [d.strip() for d in dept.split(' / ') if d.strip()]
            for d in departments:
                dept_counter[d] += 1
        else:
            no_dept_count += 1

    # Build stats object
    stats = {
        "date": date_str,
        "news_count": len(news_data),
        "department_stats": dict(dept_counter),
        "no_department_count": no_dept_count,
        "generated_at": datetime.now().isoformat()
    }

    return stats

def save_stats(stats, date_obj):
    """Save statistics to stat/dept/YYYY/MM/DD.json"""
    year = date_obj.strftime("%Y")
    month = date_obj.strftime("%m")

    output_dir = STAT_DIR / "dept" / year / month
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{stats['date']}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    log(f"✅ Stats saved to: {output_file}")

    return output_file

def main(date_str=None):
    """Main execution"""
    log("=" * 60)
    log("Generating department statistics...")
    log("=" * 60)

    try:
        # Determine target date
        if date_str is None:
            target_date = datetime.now() - timedelta(days=1)
            date_str = target_date.strftime("%Y-%m-%d")
        else:
            target_date = datetime.strptime(date_str, "%Y-%m-%d")

        news_file = get_news_path(target_date)

        if not news_file.exists():
            log(f"❌ News file not found: {news_file}")
            return 1

        with open(news_file, 'r', encoding='utf-8') as f:
            news_data = json.load(f)

        log(f"📰 Loaded {len(news_data)} news items from {date_str}")

        # Generate stats
        stats = generate_stats(news_data, date_str)

        log(f"📊 Department breakdown:")
        for dept, count in sorted(stats['department_stats'].items(), key=lambda x: x[1], reverse=True):
            log(f"   {dept}: {count}")
        if stats['no_department_count'] > 0:
            log(f"   (No department): {stats['no_department_count']}")

        # Save stats
        save_stats(stats, target_date)

        log("=" * 60)
        log("Department statistics generation completed!")
        log("=" * 60)

        return 0

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        log(f"❌ CRITICAL ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    sys.exit(main(date_arg))
