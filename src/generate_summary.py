#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate Daily News Summary HTML using MiniMax direct API."""

import json, re, requests, subprocess, time, os
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict

API_KEY = os.environ.get("MINIMAX_API_KEY", "")
if not API_KEY:
    cred = Path.home() / ".openclaw" / "credentials" / "minimax-default.apikey.json"
    if cred.exists():
        API_KEY = json.loads(cred.read_text())["apiKey"]
if not API_KEY:
    raise ValueError("MINIMAX_API_KEY not set")
API_URL  = "https://api.minimaxi.com/v1/chat/completions"
MODEL    = "MiniMax-M2.7"
BATCH_SIZE      = 5
REQUEST_TIMEOUT = 120
API_DELAY       = 0.3
MAX_TOKENS      = 2500

PROMPT_FILE = Path(__file__).parent / "summary_prompt.txt"
OUTPUT_DIR  = Path(__file__).parent.parent / "public"
LOG_FILE    = Path(__file__).parent.parent / "data" / "summary.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} - {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def call_minimax(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": MAX_TOKENS,
        "temperature": 0.1,
    }
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"]
    # Strip <thinking> tags
    content = re.sub(r"<[^>]*>", "", raw).strip()
    return content

def load_news(date):
    """Load news JSON for a given date."""
    news_file = Path(__file__).parent.parent / "data" / "processed" / \
                date.strftime("%Y") / date.strftime("%m") / f"{date.strftime('%d')}.json"
    if not news_file.exists():
        log(f"  File not found: {news_file}")
        return None
    with open(news_file, "r", encoding="utf-8") as f:
        return json.load(f)

def build_classify_prompt(news_items, batch_num, total_batches):
    """Build the classification prompt from summary_prompt.txt template."""
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        template = f.read()
    # Simplify items
    simplified = []
    for n in news_items:
        s = re.sub(r"<[^>]+>", "", n.get("summary", ""))[:30]
        simplified.append({"title": n.get("title",""), "summary": s, "link": n.get("link","")})
    prompt = template.replace("{news_json}", json.dumps(simplified, ensure_ascii=False))
    prompt += f"\n\n# Note: This is batch {batch_num}/{total_batches}."
    return prompt

def classify_batch(news_batch, batch_num, total_batches):
    """Call MiniMax API for a batch of news. Retries once on JSON parse failure."""
    prompt = build_classify_prompt(news_batch, batch_num, total_batches)
    log(f"  Batch {batch_num}/{total_batches}: calling API ({len(news_batch)} items)...")

    def _try_parse(raw):
        if "{" not in raw:
            return None, f"no brace: {raw[:80]}"
        # Find JSON start — scan for outermost '{'
        start = raw.find("{")
        json_str = raw[start:]
        # Use raw_decode to auto-find valid JSON end
        try:
            obj, idx = json.JSONDecoder().raw_decode(json_str)
        except json.JSONDecodeError as e:
            return None, f"JSON error: {e}"
        items = obj.get("all_news", [])
        return items, None

    for attempt in range(2):
        try:
            raw = call_minimax(prompt)
            items, err = _try_parse(raw)
            if err:
                log(f"  Batch {batch_num} attempt {attempt+1} failed: {err}")
                if attempt == 0:
                    time.sleep(2)  # brief pause before retry
                    continue
                return None
            log(f"  Batch {batch_num} OK: {len(items)} classified")
            return items
        except Exception as e:
            log(f"  Batch {batch_num} error: {e}")
            return None
    return None

def generate_summary(news_data, date):
    """Classify all news items and build summary data dict."""
    if not PROMPT_FILE.exists():
        log(f"Prompt file not found: {PROMPT_FILE}")
        return None
    total = len(news_data)
    total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
    all_classified = []
    for i in range(0, total, BATCH_SIZE):
        batch = news_data[i:i+BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        result = classify_batch(batch, batch_num, total_batches)
        if result:
            all_classified.extend(result)
        else:
            log(f"  Batch {batch_num} failed, skipping...")
        time.sleep(API_DELAY)
    if not all_classified:
        log("All batches failed")
        return None
    log(f"Classified {len(all_classified)} items total")
    category_stats = Counter(it.get("category","其他") for it in all_classified)
    highlights = [it for it in all_classified if it.get("importance",1) >= 3][:5]
    return {
        "date": date.strftime("YYYY年MM月DD日").replace("YYYY", str(date.year)).replace("MM", f"{date.month:02d}").replace("DD", f"{date.day:02d}"),
        "total_count": len(all_classified),
        "highlights": highlights,
        "category_stats": dict(category_stats),
        "all_news": all_classified,
    }

def build_html(summary_data, date):
    """Build HTML from summary_data dict."""
    date_str = date.strftime("YYYY年MM月DD日").replace("YYYY", str(date.year)).replace("MM", f"{date.month:02d}").replace("DD", f"{date.day:02d}")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    imp_label = {1:"低",2:"中",3:"高"}
    imp_class = {1:"badge-low",2:"badge-medium",3:"badge-high"}

    hi_html = ""
    for n in summary_data.get("highlights",[]):
        imp = n.get("importance",3)
        hi_html += f"""
        <div class="highlight-item">
            <h3>{n["title"]} <span class="importance-badge {imp_class.get(imp,"badge-high")}">{imp_label.get(imp,"高")}</span></h3>
            <p><span class="category-tag">{n.get("category","")}</span></p>
            <p class="summary">{n.get("summary","")}</p>
            <p><a href="{n["link"]}" target="_blank">查看原文 →</a></p>
        </div>"""

    stats_html = ""
    for cat, cnt in summary_data.get("category_stats",{}).items():
        stats_html += f'<div class="stat-card"><div class="stat-number">{cnt}</div><div class="stat-label">{cat}</div></div>'

    by_cat = defaultdict(list)
    for n in summary_data.get("all_news",[]):
        by_cat[n.get("category","其他")].append(n)
    list_html = ""
    for cat, items in sorted(by_cat.items()):
        list_html += f"<h3>{cat}</h3><ul class='news-list'>"
        for n in items:
            imp = n.get("importance",1)
            list_html += f"<li><span class='importance-badge {imp_class.get(imp,"badge-low")}'>{imp_label.get(imp,"低")}</span><a href='{n['link']}' target='_blank'>{n['title']}</a></li>"
        list_html += "</ul>"

    return f"""<!DOCTYPE html>
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
        .back-link {{ display: inline-block; margin-bottom: 20px; color: #007bff; text-decoration: none; }}
        .back-link:hover {{ text-decoration: underline; }}
        footer {{ text-align: center; color: #999; margin-top: 40px; padding-top: 20px; border-top: 2px solid #eee; }}
        @media (max-width: 600px) {{ .container {{ padding: 20px; }} h1 {{ font-size: 1.5em; }} }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📰 澳門政府新聞總結</h1>
            <p class="date">{date_str}</p>
            <p class="stats">共 {summary_data.get("total_count",0)} 則新聞</p>
        </header>
        <section class="highlights">
            <h2>🔥 重點新聞（高重要性）</h2>
            {hi_html}
        </section>
        <section class="stats-by-category">
            <h2>📊 分類統計</h2>
            <div class="stats-grid">{stats_html}</div>
        </section>
        <section class="full-list">
            <h2>📋 全部新聞列表</h2>
            {list_html}
        </section>
        <a href="index.html" class="back-link">← 返回索引頁</a>
        <div class="footer">
            <strong>資料來源：</strong>澳門特別行政區政府新聞局 (GCS)<br>
            <strong>生成時間：</strong>{ts} (Asia/Macau)<br>
            <strong>Provider:</strong> MiniMax | <strong>Model:</strong> {MODEL}
        </div>
    </div>
</body>
</html>"""

def save_html(html, date):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    date_str = date.strftime("%Y-%m-%d")
    out_file = OUTPUT_DIR / f"{date_str}.html"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)
    # update index
    with open(OUTPUT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(html)
    log(f"HTML saved: {out_file}")
    return out_file

def save_classification(summary_data, date, news_data):
    """Save classification JSON to data/classification/."""
    out_dir = Path(__file__).parent.parent / "data" / "classification"
    out_dir.mkdir(parents=True, exist_ok=True)
    date_str = date.strftime("%Y-%m-%d")
    guid_map = {n.get("title",""): n.get("guid","") for n in news_data}
    classified = []
    for n in summary_data.get("all_news",[]):
        classified.append({
            "guid": guid_map.get(n.get("title",""),""),
            "title": n.get("title",""),
            "category": n.get("category",""),
            "importance": n.get("importance",1),
            "link": n.get("link","")
        })
    data = {
        "date": date_str,
        "news": classified,
        "generated_at": datetime.now().isoformat(),
        "model": MODEL
    }
    out_file = out_dir / f"{date_str}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log(f"Classification saved: {out_file}")
    return out_file

def commit_and_push(date):
    repo = Path(__file__).parent.parent
    try:
        subg = subprocess.run(["git", "add", "public/", "data/classification/"], cwd=repo, check=True, capture_output=True, text=True)
        r = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo)
        if r.returncode == 0:
            log("No changes to commit")
            return True
        date_str = date.strftime("%Y-%m-%d")
        msg = f"feat: add daily news summary ({date_str})\n\n🤖 Model: {MODEL}"
        subprocess.run(["git", "commit", "-m", msg], cwd=repo, check=True)
        subprocess.run(["git", "push"], cwd=repo, check=True)
        log("Committed and pushed")
        return True
    except Exception as e:
        log(f"Git error: {e}")
        return False

def main():
    log("=" * 60)
    log("Generating daily news summary (direct API)...")
    log("=" * 60)
    yesterday = datetime.now() - timedelta(days=1)
    log(f"Target date: {yesterday.strftime('%Y-%m-%d')}")
    news_data = load_news(yesterday)
    if not news_data:
        log("No news data found")
        return 1
    log(f"Loaded {len(news_data)} news items")
    summary = generate_summary(news_data, yesterday)
    if not summary:
        log("Classification failed")
        return 1
    html = build_html(summary, yesterday)
    save_html(html, yesterday)
    save_classification(summary, yesterday, news_data)
    commit_and_push(yesterday)
    log("Done!")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
