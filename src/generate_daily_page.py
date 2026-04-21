#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Daily News Webpage
Creates HTML page for today's news with department statistics

Run after fetch_news.py to generate public/YYYY-MM-DD.html
"""

import json
from pathlib import Path
from datetime import datetime

# Configuration
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
STAT_DIR = BASE_DIR / "stat" / "dept"
PUBLIC_DIR = BASE_DIR / "public"
LOG_FILE = BASE_DIR / "data" / "daily_page.log"

def log(message):
    """Log message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"{timestamp} - {message}"
    print(log_msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + "\n")

def get_today_data():
    """Load today's news data"""
    today = datetime.now()
    year = today.strftime("%Y")
    month = today.strftime("%m")
    day = today.strftime("%d")
    
    news_file = DATA_DIR / year / month / f"{day}.json"
    
    if not news_file.exists():
        log(f"❌ News file not found: {news_file}")
        return None, None
    
    with open(news_file, 'r', encoding='utf-8') as f:
        news_data = json.load(f)
    
    # Load department stats
    stat_file = STAT_DIR / year / month / f"{year}-{month}-{day}.json"
    dept_stats = {}
    if stat_file.exists():
        with open(stat_file, 'r', encoding='utf-8') as f:
            stats_data = json.load(f)
            dept_stats = stats_data.get('department_stats', {})
    
    log(f"📰 Loaded {len(news_data)} news items for {year}-{month}-{day}")
    log(f"🏛️ Department stats: {dept_stats}")
    
    return news_data, dept_stats

def generate_html(news_data, dept_stats, date_str):
    """Generate HTML for daily news page"""
    today = datetime.now()
    weekday_map = {
        0: '星期一', 1: '星期二', 2: '星期三', 3: '星期四',
        4: '星期五', 5: '星期六', 6: '星期日'
    }
    weekday = weekday_map[today.weekday()]
    timestamp = today.strftime("%Y-%m-%d %H:%M")
    
    # Build news items HTML
    news_html = ""
    for news in news_data:
        dept = news.get('department', '')
        dept_html = f'<span class="dept-tag">{dept}</span>' if dept else ''
        
        news_html += f"""
        <div class="news-item">
            <div class="news-title">
                {dept_html}
                <a href="{news['link']}" target="_blank">{news['title']}</a>
            </div>
            <div class="news-meta">
                <span class="news-time">{news['published'][:16].replace('T', ' ')}</span>
            </div>
        </div>
        """
    
    # Build department stats HTML
    dept_stats_html = ""
    if dept_stats:
        for dept, count in sorted(dept_stats.items(), key=lambda x: x[1], reverse=True):
            dept_stats_html += f"""
            <div class="dept-stat-item">
                <span class="dept-name">{dept}</span>
                <span class="dept-count">{count}</span>
            </div>
            """
    
    html = f"""<!DOCTYPE html>
<html lang="zh-HK">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>澳門政府新聞總結 - {date_str}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1a1a1a;
            border-bottom: 3px solid #00A86B;
            padding-bottom: 15px;
        }}
        h2 {{
            color: #00A86B;
            margin-top: 30px;
            border-left: 4px solid #00A86B;
            padding-left: 15px;
        }}
        .news-item {{
            background: #f9f9f9;
            border-radius: 6px;
            padding: 20px;
            margin: 15px 0;
            border-left: 4px solid #00A86B;
        }}
        .news-title {{
            font-weight: 600;
            font-size: 1.1em;
            margin-bottom: 10px;
        }}
        .news-title a {{
            color: #00A86B;
            text-decoration: none;
        }}
        .news-title a:hover {{
            text-decoration: underline;
        }}
        .news-meta {{
            color: #666;
            font-size: 0.9em;
        }}
        .dept-tag {{
            display: inline-block;
            background: #e3f2fd;
            color: #1976d2;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
            margin-right: 10px;
        }}
        .dept-stats {{
            margin-bottom: 30px;
        }}
        .dept-stats-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .dept-stat-item {{
            background: #e3f2fd;
            padding: 8px 15px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .dept-name {{
            color: #1976d2;
            font-weight: 600;
        }}
        .dept-count {{
            background: #1976d2;
            color: white;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📰 澳門政府新聞總結</h1>
        <p><strong>日期：</strong>{date_str}（{weekday}）</p>
        <p><strong>新聞總數：</strong>{len(news_data)} 則</p>

        <h2>🏛️ 部門統計</h2>
        <div class="dept-stats">
            <div class="dept-stats-list">
                {dept_stats_html if dept_stats_html else '<p>暫無部門統計數據</p>'}
            </div>
        </div>

        <h2>📋 全部新聞</h2>
        {news_html}

        <div class="footer">
            <strong>資料來源：</strong>澳門特別行政區政府新聞局 (GCS)<br>
            <strong>生成時間：</strong>{timestamp} (Asia/Macau)<br>
            <strong>Provider:</strong> Qwen | <strong>Model:</strong> qwen3.5-plus
        </div>
    </div>
</body>
</html>"""
    
    return html

def save_html(html_content, date_str):
    """Save HTML to public/YYYY-MM-DD.html"""
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    
    output_file = PUBLIC_DIR / f"{date_str}.html"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    log(f"✅ HTML saved to: {output_file}")
    
    return output_file

def main():
    """Main execution"""
    log("=" * 60)
    log("Generating daily news webpage...")
    log("=" * 60)
    
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get today's data
        news_data, dept_stats = get_today_data()
        
        if not news_data:
            log("❌ No news data to process")
            return 1
        
        # Generate HTML
        html_content = generate_html(news_data, dept_stats, today)
        
        # Save HTML
        output_file = save_html(html_content, today)
        
        log("=" * 60)
        log("Daily webpage generation completed!")
        log("=" * 60)
        
        return 0
        
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        log(f"❌ CRITICAL ERROR: {error_msg}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
