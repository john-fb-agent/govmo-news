#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Daily News Summary HTML
Run daily at 8:00 AM to summarize yesterday's news
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

# Configuration
OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "summary-examples"
PROMPT_FILE = Path(__file__).parent / "summary_prompt.txt"
LOG_FILE = Path(__file__).parent.parent / "data" / "summary.log"

def log(message):
    """Log message to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"{timestamp} - {message}"
    print(log_msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + "\n")

def load_yesterday_news():
    """Load yesterday's news JSON"""
    yesterday = datetime.now() - timedelta(days=1)
    news_file = Path(__file__).parent.parent / "data" / "processed" / \
                yesterday.strftime("%Y") / yesterday.strftime("%m") / \
                f"{yesterday.strftime('%d')}.json"
    
    if not news_file.exists():
        log(f"❌ News file not found: {news_file}")
        return None, yesterday
    
    with open(news_file, 'r', encoding='utf-8') as f:
        news_data = json.load(f)
    
    log(f"📰 Loaded {len(news_data)} news items from {yesterday.strftime('%Y-%m-%d')}")
    return news_data, yesterday

def generate_summary(news_data, date):
    """Call OpenClaw AI to generate JSON summary, then convert to HTML"""
    # Load prompt template
    if not PROMPT_FILE.exists():
        log(f"❌ Prompt file not found: {PROMPT_FILE}")
        return None
    
    with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # Simplify news data (remove HTML tags to reduce size)
    import re
    simplified_news = []
    for news in news_data:
        # Remove HTML tags from summary
        summary = news.get("summary", "")
        summary = re.sub(r'<[^>]+>', '', summary)  # Remove HTML tags
        summary = summary[:150]  # Limit length
        
        simplified_news.append({
            "title": news.get("title", ""),
            "summary": summary,
            "link": news.get("link", "")
        })
    
    # Replace placeholder with simplified data
    prompt = prompt_template.replace("{news_json}", json.dumps(simplified_news, ensure_ascii=False))
    
    log("🤖 Calling OpenClaw AI...")
    
    # Use openclaw infer model run
    # Timeout: 10 minutes (600 seconds) for AI analysis
    result = subprocess.run([
        'openclaw', 'infer', 'model', 'run',
        '--prompt', prompt,
        '--model', 'qwen/qwen3.5-plus'
    ], capture_output=True, text=True, timeout=600)
    
    if result.returncode == 0:
        log("✅ AI analysis completed")
        # Parse JSON and generate HTML
        try:
            # Extract JSON from response
            ai_output = result.stdout.strip()
            if ai_output.startswith('```json'):
                ai_output = ai_output[7:]
            if ai_output.endswith('```'):
                ai_output = ai_output[:-3]
            
            summary_data = json.loads(ai_output.strip())
            html_content = build_html(summary_data, date)
            log("✅ HTML generated successfully")
            return html_content
        except Exception as e:
            log(f"❌ Failed to parse AI output: {e}")
            log(f"Output: {result.stdout[:500]}...")
            return None
    else:
        log(f"❌ OpenClaw call failed: {result.stderr}")
        return None

def build_html(summary_data, date):
    """Build HTML from AI summary JSON"""
    date_str = date.strftime("%Y年%m月%d日")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Build highlights HTML
    highlights_html = ""
    for news in summary_data.get("highlights", []):
        highlights_html += f"""
        <div class="highlight-item">
            <h3>⭐⭐⭐ {news['title']}</h3>
            <p><span class="category-tag">{news['category']}</span></p>
            <p class="summary">{news.get('summary', '')}</p>
            <p><a href="{news['link']}" target="_blank">查看原文 →</a></p>
        </div>
        """
    
    # Build category stats HTML
    stats_html = ""
    for category, count in summary_data.get("category_stats", {}).items():
        stats_html += f"""
        <div class="stat-card">
            <div class="stat-number">{count}</div>
            <div class="stat-label">{category}</div>
        </div>
        """
    
    # Build full list HTML (grouped by category)
    from collections import defaultdict
    by_category = defaultdict(list)
    for news in summary_data.get("all_news", []):
        by_category[news['category']].append(news)
    
    full_list_html = ""
    for category, news_list in sorted(by_category.items()):
        full_list_html += f"<h3>{category}</h3><ul class='news-list'>"
        for news in news_list:
            stars = "⭐" * news.get('importance', 1)
            full_list_html += f"<li><span class='category-tag'>{stars}</span><a href='{news['link']}' target='_blank'>{news['title']}</a></li>"
        full_list_html += "</ul>"
    
    html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>澳門政府新聞總結 - {date_str}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        header {{ text-align: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 3px solid #007bff; }}
        h1 {{ color: #007bff; margin-bottom: 10px; }}
        .date {{ color: #666; font-size: 1.2em; }}
        .stats {{ color: #999; margin-top: 5px; }}
        section {{ margin-bottom: 40px; }}
        h2 {{ color: #333; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #eee; }}
        h3 {{ color: #007bff; margin: 20px 0 10px 0; }}
        .highlight-item {{ background: #f8f9fa; padding: 20px; margin-bottom: 15px; border-radius: 8px; border-left: 4px solid #007bff; }}
        .summary {{ color: #555; margin: 10px 0; }}
        .news-list {{ list-style: none; }}
        .news-list li {{ padding: 10px 0; border-bottom: 1px solid #eee; }}
        .news-list a {{ color: #007bff; text-decoration: none; }}
        .news-list a:hover {{ text-decoration: underline; }}
        .category-tag {{ display: inline-block; padding: 3px 8px; background: #e9ecef; border-radius: 4px; font-size: 0.85em; margin-right: 10px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 15px; margin-bottom: 30px; }}
        .stat-card {{ background: #f8f9fa; padding: 15px; text-align: center; border-radius: 8px; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .stat-label {{ color: #666; font-size: 0.9em; }}
        footer {{ text-align: center; color: #999; margin-top: 40px; padding-top: 20px; border-top: 2px solid #eee; }}
        @media (max-width: 600px) {{ .container {{ padding: 20px; }} h1 {{ font-size: 1.5em; }} }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📰 澳門政府新聞總結</h1>
            <p class="date">{date_str}</p>
            <p class="stats">共 {summary_data.get('total_count', 0)} 則新聞</p>
        </header>

        <section class="highlights">
            <h2>🔑 重點新聞</h2>
            {highlights_html}
        </section>

        <section class="stats-by-category">
            <h2>📊 分類統計</h2>
            <div class="stats-grid">
                {stats_html}
            </div>
        </section>

        <section class="full-list">
            <h2>📋 完整新聞列表</h2>
            {full_list_html}
        </section>

        <footer>
            <p>自動生成於 {timestamp}</p>
            <p>資料來源：澳門特別行政區政府新聞局</p>
        </footer>
    </div>
</body>
</html>"""
    
    return html

def save_html(html_content, date):
    """Save HTML to docs/summary-examples/YYYY-MM-DD.html"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    date_str = date.strftime("%Y-%m-%d")
    output_file = OUTPUT_DIR / f"{date_str}.html"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    log(f"✅ HTML saved to: {output_file}")
    
    # Also update index.html (latest summary)
    index_file = OUTPUT_DIR / "index.html"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    log(f"✅ Index updated: {index_file}")
    
    return output_file

def commit_and_push(html_file, date):
    """Commit and push HTML to GitHub"""
    repo_dir = Path(__file__).parent.parent
    date_str = date.strftime("%Y-%m-%d")
    
    try:
        subprocess.run(['git', 'add', 'docs/summary-examples/'], cwd=repo_dir, check=True)
        result = subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=repo_dir)
        if result.returncode == 0:
            log("ℹ️ No changes to commit")
            return True
        
        commit_msg = f"feat: add daily news summary ({date_str})\n\n🤖 Model: qwen/qwen3.5-plus"
        subprocess.run(['git', 'commit', '-m', commit_msg], cwd=repo_dir, check=True)
        log("✅ Committed changes")
        
        subprocess.run(['git', 'push'], cwd=repo_dir, check=True)
        log("✅ Pushed to GitHub")
        
        return True
    except subprocess.CalledProcessError as e:
        log(f"❌ Git operation failed: {e}")
        return False
    except Exception as e:
        log(f"❌ Error during commit/push: {e}")
        return False

def main():
    """Main execution"""
    log("=" * 60)
    log("Generating daily news summary...")
    log("=" * 60)
    
    try:
        news_data, date = load_yesterday_news()
        if not news_data:
            log("❌ No news data to process")
            send_notification("generate_summary.py", "No news data to process")
            return 1
        
        html_content = generate_summary(news_data, date)
        if not html_content:
            log("❌ Failed to generate HTML")
            send_notification("generate_summary.py", "Failed to generate HTML summary")
            return 1
        
        html_file = save_html(html_content, date)
        if not html_file:
            log("❌ Failed to save HTML")
            send_notification("generate_summary.py", "Failed to save HTML file")
            return 1
        
        if not commit_and_push(html_file, date):
            log("⚠️ Failed to commit/push (continuing anyway)")
        
        log("=" * 60)
        log("Summary generation completed!")
        log("=" * 60)
        
        return 0
        
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        log(f"❌ CRITICAL ERROR: {error_msg}")
        send_notification("generate_summary.py", error_msg)
        return 1

def send_notification(script_name: str, error_message: str):
    """Send failure notification via notify_failure.py"""
    notify_script = Path(__file__).parent / "notify_failure.py"
    if notify_script.exists():
        try:
            subprocess.run(
                ['python3', str(notify_script), script_name, error_message],
                capture_output=True,
                timeout=30
            )
        except Exception as e:
            log(f"⚠️ Failed to send notification: {e}")

if __name__ == "__main__":
    import sys
    sys.exit(main())
