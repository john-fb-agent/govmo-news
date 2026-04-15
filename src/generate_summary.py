#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Daily News Summary HTML
Run daily at 8:00 AM to summarize yesterday's news
"""

import json
import os
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import requests

# Configuration
OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "summary-examples"
PROMPT_FILE = Path(__file__).parent / "summary_prompt.txt"
LOG_FILE = Path(__file__).parent.parent / "data" / "summary.log"

def log(message):
    """Log message to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"{timestamp} - {message}"
    print(log_msg)
    
    # Append to log file
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
    """Call OpenClaw AI to generate HTML summary"""
    # Load prompt template
    if not PROMPT_FILE.exists():
        log(f"❌ Prompt file not found: {PROMPT_FILE}")
        return None
    
    with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # Replace placeholders
    date_str = date.strftime("%Y年%m月%d日")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    prompt = prompt_template
    prompt = prompt.replace("{news_json}", json.dumps(news_data, ensure_ascii=False))
    prompt = prompt.replace("{日期}", date_str)
    prompt = prompt.replace("{時間戳}", timestamp)
    
    log("🤖 Calling OpenClaw AI...")
    
    # Call OpenClaw API using the message tool pattern
    # This uses the openclaw CLI to call the AI
    try:
        # Use openclaw agent to generate the summary
        result = subprocess.run([
            'openclaw', 'agent',
            '--message', prompt,
            '--no-deliver'  # Don't deliver to chat, just get result
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            html_content = result.stdout
            log("✅ HTML generated successfully")
            return html_content
        else:
            log(f"❌ OpenClaw call failed: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        log("❌ OpenClaw call timed out")
        return None
    except Exception as e:
        log(f"❌ Error calling OpenClaw: {e}")
        return None

def save_html(html_content, date):
    """Save HTML to docs/summary-examples/YYYY-MM-DD.html"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save as dated HTML file
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
        # Add files
        subprocess.run(['git', 'add', 'docs/summary-examples/'], cwd=repo_dir, check=True)
        
        # Check if there are changes to commit
        result = subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=repo_dir)
        if result.returncode == 0:
            log("ℹ️ No changes to commit")
            return True
        
        # Commit
        commit_msg = f"feat: add daily news summary ({date_str})\n\n🤖 Model: qwen/qwen3.5-plus"
        subprocess.run(['git', 'commit', '-m', commit_msg], cwd=repo_dir, check=True)
        log("✅ Committed changes")
        
        # Push
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
    
    # Load news
    news_data, date = load_yesterday_news()
    if not news_data:
        log("❌ No news data to process")
        return 1
    
    # Generate summary
    html_content = generate_summary(news_data, date)
    if not html_content:
        log("❌ Failed to generate HTML")
        return 1
    
    # Save HTML
    html_file = save_html(html_content, date)
    if not html_file:
        log("❌ Failed to save HTML")
        return 1
    
    # Commit and push
    if not commit_and_push(html_file, date):
        log("⚠️ Failed to commit/push (continuing anyway)")
    
    log("=" * 60)
    log("Summary generation completed!")
    log("=" * 60)
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
