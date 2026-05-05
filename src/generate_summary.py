#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate Daily News Summary HTML using OpenClaw agent CLI."""

import json, re, subprocess, time, os
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict

MODEL    = "minimax/MiniMax-M2.7"
BATCH_SIZE      = 5
REQUEST_TIMEOUT = 300
API_DELAY       = 1
MAX_TOKENS      = 2500

PROMPT_FILE = Path(__file__).parent / "summary_prompt.txt"
OUTPUT_DIR  = Path(__file__).parent.parent / "public"
LOG_FILE    = Path(__file__).parent.parent / "data" / "summary.log"

# Importance colors for stats
IMP_COLORS = {
    3: "#dc3545",  # red - high
    2: "#fd7e14",  # orange - medium
    1: "#aaa",     # gray - low
}
IMP_LABELS = {3: "高", 2: "中", 1: "低"}

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} - {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def call_openclaw(prompt):
    """Call OpenClaw agent via CLI instead of direct API."""
    cmd = [
        "openclaw", "agent",
        "--session-id", "agent:main:main",
        "--message", prompt,
        "--timeout", str(REQUEST_TIMEOUT),
        "--json"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=REQUEST_TIMEOUT + 30)
    if result.returncode != 0:
        raise RuntimeError(f"openclaw agent failed: {result.stderr}")
    output = result.stdout.strip()
    # Parse JSON wrapper to extract actual response text
    try:
        response_obj = json.loads(output)
        if "result" in response_obj and "payloads" in response_obj["result"]:
            payloads = response_obj["result"]["payloads"]
            if payloads and "text" in payloads[0]:
                content = payloads[0]["text"]
                content = re.sub(r"<[^>]*>", "", content).strip()
                return content
    except (json.JSONDecodeError, KeyError, IndexError):
        pass
    content = re.sub(r"<[^>]*>", "", output).strip()
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

SUMMARY_AI_PROMPT = """你是一位澳門政府新聞分析師。請根據以下今日澳門政府新聞，生成一段 200-300 字的繁體中文綜合摘要，總結今日最重要的新聞主題和趨勢。

規則：
- 使用繁體中文
- 摘要應該是連貫的段落，不是列表
- 重點提及高重要性新聞
- 提及至少3個不同類別的新聞
- 不要提及具體的新聞數量

新聞資料：
{news_json}

只輸出摘要文字，不要其他內容。"""

def build_classify_prompt(news_items, batch_num, total_batches):
    """Build the classification prompt from summary_prompt.txt template."""
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        template = f.read()
    simplified = []
    for n in news_items:
        s = re.sub(r"<[^>]+>", "", n.get("summary", ""))[:30]
        simplified.append({"title": n.get("title",""), "summary": s, "link": n.get("link","")})
    prompt = template.replace("{news_json}", json.dumps(simplified, ensure_ascii=False))
    prompt += f"\n\n# Note: This is batch {batch_num}/{total_batches}."
    return prompt

def generate_ai_summary(news_items):
    """Generate AI summary text using OpenClaw agent."""
    simplified = []
    for n in news_items:
        s = re.sub(r"<[^>]+>", "", n.get("summary", ""))
        imp_lbl = IMP_LABELS.get(n.get("importance", 1), "低")
        simplified.append({
            "title": n.get("title", ""),
            "summary": s[:100] if s else "",
            "importance": imp_lbl,
            "category": n.get("category", "")
        })
    prompt = SUMMARY_AI_PROMPT.replace("{news_json}", json.dumps(simplified, ensure_ascii=False, indent=2))
    log("Generating AI summary...")
    try:
        summary_text = call_openclaw(prompt)
        log(f"AI summary generated ({len(summary_text)} chars)")
        return summary_text
    except Exception as e:
        log(f"AI summary generation failed: {e}")
        return None

def classify_batch(news_batch, batch_num, total_batches):
    """Call OpenClaw agent for a batch of news. Retries once on JSON parse failure."""
    prompt = build_classify_prompt(news_batch, batch_num, total_batches)
    log(f"  Batch {batch_num}/{total_batches}: calling OpenClaw agent ({len(news_batch)} items)...")

    def _try_parse(raw):
        if "{" not in raw:
            return None, f"no brace: {raw[:80]}"
        start = raw.find("{")
        json_str = raw[start:]
        try:
            obj, idx = json.JSONDecoder().raw_decode(json_str)
        except json.JSONDecodeError as e:
            return None, f"JSON error: {e}"
        items = obj.get("all_news", [])
        return items, None

    for attempt in range(2):
        try:
            raw = call_openclaw(prompt)
            items, err = _try_parse(raw)
            if err:
                log(f"  Batch {batch_num} attempt {attempt+1} failed: {err}")
                if attempt == 0:
                    time.sleep(2)
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

    # Generate AI summary text
    ai_summary = generate_ai_summary(all_classified)

    category_stats = Counter(it.get("category","其他") for it in all_classified)
    # Use importance >= 2 as "high" threshold (original template style)
    highlights = [it for it in all_classified if it.get("importance",1) >= 2][:6]

    # Importance breakdown
    imp_count = Counter(it.get("importance",1) for it in all_classified)
    imp_breakdown = f"高重要性（紅）{imp_count.get(3,0)}則 · 中重要性（橙）{imp_count.get(2,0)}則 · 低重要性（灰）{imp_count.get(1,0)}則"

    return {
        "date": date.strftime("%Y年%m月%d日"),
        "date_short": date.strftime("%Y年%m月%d日"),
        "total_count": len(all_classified),
        "ai_summary": ai_summary,
        "highlights": highlights,
        "category_stats": dict(category_stats),
        "imp_breakdown": imp_breakdown,
        "all_news": all_classified,
    }

def build_html(summary_data, date, back_link_path="index.html"):
    """Build HTML from summary_data dict - original card-based style.
    
    back_link_path: relative path from the output HTML file to index.html.
    For public/YYYY/MM/YYYY-MM-DD.html, this is "../../index.html".
    """
    date_str = date.strftime("%Y-%m-%d")
    total = summary_data.get("total_count", 0)

    # AI Summary card
    ai_card = ""
    ai_summary = summary_data.get("ai_summary")
    if ai_summary:
        # Format summary text: split on <br> or newlines into paragraphs
        paras = re.split(r'<br\s*/?>\s*', ai_summary)
        para_html = ""
        for p in paras:
            p = p.strip()
            if not p:
                continue
            # Bold keywords at start of sentence
            para_html += f"<p>{p}</p>\n"
        ai_card = f"""
        <div class="card">
            <h2>🔥 今日綜合摘要</h2>
            <p class="summary-text">
                {para_html.strip()}
            </p>
        </div>"""

    # Stats card
    stats_html = ""
    cat_colors = ["#28a745","#17a2b8","#fd7e14","#dc3545","#6610f2",
                  "#6f42c1","#ffc107","#e83e8c","#00a86b","#6c757d"]
    for i, (cat, cnt) in enumerate(summary_data.get("category_stats", {}).items()):
        color = cat_colors[i % len(cat_colors)]
        stats_html += f'<div class="stat-card"><div class="stat-num">{cnt}</div><div class="stat-label" style="color:{color};font-weight:600">{cat}</div></div>'

    stats_card = f"""
        <div class="card">
            <h2>📊 分類統計</h2>
            <div class="stats-grid">
                {stats_html}
            </div>
            <p class="imp-note">{summary_data.get("imp_breakdown", "")}</p>
        </div>"""

    # Highlights card
    hi_html = ""
    imp_dot_class = {3: "dot-high", 2: "dot-medium", 1: "dot-low"}
    for n in summary_data.get("highlights", []):
        imp = n.get("importance", 2)
        imp_lbl = IMP_LABELS.get(imp, "高")
        cat = n.get("category", "")
        summary_txt = n.get("summary", "")
        if summary_txt:
            hi_html += f"""
        <div class="highlight-card">
            <h3>
                <span class="cat">{cat}</span>
                {n["title"]}
                <span class="imp">{imp_lbl}</span>
            </h3>
            <p class="summary">{summary_txt}</p>
        </div>"""
        else:
            hi_html += f"""
        <div class="highlight-card">
            <h3>
                <span class="cat">{cat}</span>
                {n["title"]}
                <span class="imp">{imp_lbl}</span>
            </h3>
        </div>"""

    highlights_card = f"""
        <div class="card">
            <h2>🔥 重點新聞（高重要性）</h2>
            {hi_html}
        </div>"""

    # Full news list card
    by_cat = defaultdict(list)
    for n in summary_data.get("all_news", []):
        by_cat[n.get("category", "其他")].append(n)

    list_html = ""
    for cat, items in sorted(by_cat.items()):
        list_html += f'<div class="cat-group">\n<h3>{cat}</h3>\n'
        for n in items:
            imp = n.get("importance", 1)
            imp_lbl = IMP_LABELS.get(imp, "低")
            imp_cls = imp_dot_class.get(imp, "dot-low")
            title = n.get("title", "")
            link = n.get("link", "#")
            list_html += f'<div class="news-row"><span class="imp-dot {imp_cls}">{imp_lbl}</span><a href="{link}" target="_blank">{title}</a></div>\n'
        list_html += '</div>\n'

    newslist_card = f"""
        <div class="card">
            <h2>📋 全部新聞列表</h2>
            {list_html}
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>澳門政府新聞總結 - {date_str}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.7; color: #333; background: #f0f4f8; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 30px 20px; }}
        header {{ text-align: center; margin-bottom: 30px; }}
        header h1 {{ font-size: 1.8em; color: #00A86B; margin-bottom: 6px; }}
        header .subtitle {{ color: #888; font-size: 0.9em; }}
        .card {{ background: white; border-radius: 12px; padding: 28px 30px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .card h2 {{ font-size: 1.1em; color: #00A86B; margin-bottom: 14px; padding-bottom: 10px; border-bottom: 2px solid #e8f5f0; display: flex; align-items: center; gap: 8px; }}
        .summary-text {{ font-size: 0.95em; color: #444; line-height: 1.9; text-align: justify; }}
        .summary-text strong {{ color: #00A86B; }}
        .summary-text p {{ margin-bottom: 12px; }}
        .summary-text p:last-child {{ margin-bottom: 0; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 12px; }}
        .stat-card {{ background: #f8faf9; border: 1px solid #e0f0e8; border-radius: 8px; padding: 14px 10px; text-align: center; }}
        .stat-num {{ font-size: 1.8em; font-weight: 700; color: #00A86B; }}
        .stat-label {{ font-size: 0.78em; color: #666; margin-top: 3px; }}
        .imp-note {{ font-size: 0.8em; color: #888; margin-top: 12px; text-align: center; }}
        .highlight-card {{ background: #fff9f0; border-radius: 12px; padding: 20px 22px; margin-bottom: 14px; border-left: 5px solid #ff6b35; }}
        .highlight-card h3 {{ font-size: 0.95em; color: #222; margin-bottom: 8px; line-height: 1.5; }}
        .highlight-card h3 .cat {{ display: inline-block; font-size: 0.72em; padding: 2px 8px; background: #00A86B; color: white; border-radius: 4px; margin-right: 8px; vertical-align: middle; }}
        .highlight-card h3 .imp {{ display: inline-block; font-size: 0.68em; padding: 2px 6px; background: #ff6b35; color: white; border-radius: 4px; margin-left: 6px; vertical-align: middle; font-weight: 700; }}
        .highlight-card .summary {{ font-size: 0.88em; color: #555; margin-bottom: 8px; line-height: 1.7; }}
        .cat-group {{ margin-bottom: 22px; }}
        .cat-group h3 {{ font-size: 0.85em; color: #555; margin-bottom: 8px; padding-left: 10px; border-left: 3px solid #ccc; }}
        .news-row {{ display: flex; align-items: center; gap: 10px; padding: 7px 0; border-bottom: 1px solid #f0f0f0; }}
        .news-row:last-child {{ border-bottom: none; }}
        .news-row .imp-dot {{ font-size: 0.65em; font-weight: 700; padding: 2px 7px; border-radius: 4px; color: white; white-space: nowrap; flex-shrink: 0; }}
        .dot-high {{ background: #dc3545; }}
        .dot-medium {{ background: #fd7e14; }}
        .dot-low {{ background: #aaa; }}
        .news-row a {{ font-size: 0.88em; color: #333; text-decoration: none; flex: 1; }}
        .news-row a:hover {{ color: #00A86B; text-decoration: underline; }}
        .footer {{ text-align: center; color: #aaa; font-size: 0.8em; line-height: 2; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0; }}
        .back-link {{ display: inline-block; margin-bottom: 15px; color: #00A86B; text-decoration: none; font-size: 0.88em; }}
        .back-link:hover {{ text-decoration: underline; }}
        @media (max-width: 600px) {{ .container {{ padding: 15px 12px; }} .card {{ padding: 18px 16px; }} header h1 {{ font-size: 1.4em; }} }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📰 澳門政府新聞總結</h1>
            <p class="subtitle">{date_str} · 共 {total} 則新聞</p>
        </header>
        {ai_card}
        {stats_card}
        {highlights_card}
        {newslist_card}
        <a href="{back_link_path}" class="back-link">← 返回索引頁</a>
        <div class="footer">
            資料來源：澳門特別行政區政府新聞局 (GCS)<br>
            生成時間：{datetime.now().strftime("%Y-%m-%d %H:%M")} (Asia/Macau)<br>
            Provider: OpenClaw | Model: {MODEL}
        </div>
    </div>
</body>
</html>"""
    return html

def save_html(html, date):
    year = date.strftime("%Y")
    month = date.strftime("%m")
    out_dir = OUTPUT_DIR / year / month
    out_dir.mkdir(parents=True, exist_ok=True)
    date_str = date.strftime("%Y-%m-%d")
    out_file = out_dir / f"{date_str}.html"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)
    log(f"HTML saved: {out_file}")
    return out_file

def rebuild_index_pages():
    """Rebuild all month index pages and the main index page."""
    MONTH_NAMES = {"01":"1 月","02":"2 月","03":"3 月","04":"4 月",
                   "05":"5 月","06":"6 月","07":"7 月","08":"8 月",
                   "09":"9 月","10":"10 月","11":"11 月","12":"12 月"}
    MONTH_FULL = {"01":"1","02":"2","03":"3","04":"4",
                  "05":"5","06":"6","07":"7","08":"8",
                  "09":"9","10":"10","11":"11","12":"12"}

    month_template = '''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>澳門政府新聞總結 - {year} 年 {month_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f0f4f8; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 30px 20px; }}
        header {{ background: #00A86B; color: white; border-radius: 12px; padding: 24px 28px; margin-bottom: 24px; }}
        header h1 {{ font-size: 1.5em; margin-bottom: 6px; }}
        header a {{ color: rgba(255,255,255,0.85); text-decoration: none; font-size: 0.88em; }}
        header a:hover {{ text-decoration: underline; }}
        .card {{ background: white; border-radius: 12px; padding: 24px 28px; margin-bottom: 18px; box-shadow: 0 2px 8px rgba(0,0,0,0.07); }}
        .card h2 {{ color: #00A86B; font-size: 0.95em; margin-bottom: 16px; padding-bottom: 10px; border-bottom: 2px solid #e8f5f0; }}
        .day-list {{ list-style: none; }}
        .day-list li {{ display: flex; align-items: center; padding: 10px 0; border-bottom: 1px solid #f0f0f0; }}
        .day-list li:last-child {{ border-bottom: none; }}
        .day-list .date {{ font-weight: 600; color: #888; min-width: 110px; font-size: 0.9em; }}
        .day-list a {{ color: #00A86B; text-decoration: none; font-weight: 600; flex: 1; }}
        .day-list a:hover {{ text-decoration: underline; }}
        .day-list .weekday {{ color: #aaa; font-size: 0.8em; margin-left: 8px; }}
        .back-nav {{ margin-bottom: 20px; }}
        .back-nav a {{ color: #00A86B; text-decoration: none; font-size: 0.88em; }}
        .back-nav a:hover {{ text-decoration: underline; }}
        .footer {{ text-align: center; color: #aaa; font-size: 0.8em; padding-top: 20px; border-top: 1px solid #e0e0e0; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📰 {year} 年 {month_full} 月 新聞總結</h1>
            <a href="../../index.html">← 返回索引頁</a>
        </header>
        <div class="card">
            <h2>📋 {month_name} 新聞列表（共 {count} 天）</h2>
            <ul class="day-list">
{day_rows}            </ul>
        </div>
        <div class="footer">資料來源：澳門特別行政區政府新聞局 (GCS)</div>
    </div>
</body>
</html>'''

    main_index_template = '''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>澳門政府新聞總結 - 索引</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f0f4f8; color: #333; line-height: 1.6; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 30px 20px; }}
        header {{ background: #00A86B; color: white; border-radius: 12px; padding: 28px 32px; margin-bottom: 28px; box-shadow: 0 4px 12px rgba(0,168,107,0.25); }}
        header h1 {{ font-size: 1.7em; margin-bottom: 6px; }}
        header p {{ opacity: 0.88; font-size: 0.9em; }}
        .card {{ background: white; border-radius: 12px; padding: 24px 28px; margin-bottom: 18px; box-shadow: 0 2px 8px rgba(0,0,0,0.07); }}
        .card h2 {{ color: #00A86B; font-size: 1em; margin-bottom: 14px; padding-bottom: 10px; border-bottom: 2px solid #e8f5f0; display: flex; align-items: center; gap: 8px; }}
        .year-section {{ margin-bottom: 24px; }}
        .year-header {{ font-size: 1.15em; font-weight: 700; color: #1a1a1a; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }}
        .year-header .year-badge {{ background: #00A86B; color: white; padding: 2px 12px; border-radius: 20px; font-size: 0.85em; }}
        .month-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 10px; }}
        .month-card {{ background: #f8faf9; border: 1px solid #e0f0e8; border-radius: 10px; padding: 14px 16px; text-decoration: none; color: #333; transition: all 0.2s ease; display: block; }}
        .month-card:hover {{ background: #e8f5f0; border-color: #00A86B; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,168,107,0.15); }}
        .month-card .month-name {{ font-weight: 600; color: #00A86B; font-size: 0.95em; margin-bottom: 4px; }}
        .month-card .month-count {{ font-size: 0.78em; color: #888; }}
        .month-card .month-latest {{ font-size: 0.75em; color: #aaa; margin-top: 3px; }}
        .year-nav {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }}
        .year-nav a {{ padding: 6px 16px; background: #f0f0f0; border-radius: 20px; text-decoration: none; color: #555; font-weight: 600; font-size: 0.88em; transition: all 0.2s; }}
        .year-nav a:hover, .year-nav a.active {{ background: #00A86B; color: white; }}
        .note {{ background: #fffbeb; border-left: 4px solid #ffc107; padding: 14px 18px; border-radius: 0 8px 8px 0; font-size: 0.88em; color: #666; margin-bottom: 20px; }}
        .footer {{ text-align: center; color: #aaa; font-size: 0.8em; padding-top: 20px; border-top: 1px solid #e0e0e0; margin-top: 30px; }}
        .recent-list {{ list-style: none; }}
        .recent-list li {{ display: flex; align-items: center; padding: 9px 0; border-bottom: 1px solid #f0f0f0; }}
        .recent-list li:last-child {{ border-bottom: none; }}
        .recent-list .date {{ font-weight: 600; color: #888; min-width: 110px; font-size: 0.88em; }}
        .recent-list a {{ color: #00A86B; text-decoration: none; font-weight: 600; flex: 1; }}
        .recent-list a:hover {{ text-decoration: underline; }}
        .recent-list .weekday {{ color: #aaa; font-size: 0.8em; margin-left: 8px; }}
        @media (max-width: 600px) {{ .container {{ padding: 15px 12px; }} .month-grid {{ grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); }} }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📰 澳門政府新聞總結</h1>
            <p>澳門特別行政區政府新聞局 (GCS) 每日新聞索引</p>
        </header>
        <div class="note">📅 此頁面會自動更新。每天早上 8 點（澳門時間）會生成前一天的新聞總結。</div>

        <div class="card">
            <h2>📅 最近 7 天</h2>
            <ul class="recent-list">
{recent_html}            </ul>
        </div>

        <div class="card">
            <h2>🗂️ 按月份瀏覽</h2>
            <div class="year-nav" id="yearNav"></div>
            <div id="content"></div>
        </div>
        <div class="footer">資料來源：澳門特別行政區政府新聞局 (GCS)<br>最後更新：{last_update} &nbsp;·&nbsp; 由 OpenClaw AI 自動生成</div>
    </div>
    <script>
    const INDEX_DATA = {index_json};
    function renderIndex() {{
            const nav = document.getElementById('yearNav');
            const content = document.getElementById('content');
            nav.innerHTML = INDEX_DATA.map(y =>
                '<a href="#year-' + y.year + '" onclick="scrollToYear(&#39;' + y.year + '&#39;); return false;">' + y.year + '</a>'
            ).join('');
            content.innerHTML = INDEX_DATA.map(y => {{
                let html = '<div class="year-section" id="year-' + y.year + '">' +
                    '<div class="year-header"><span class="year-badge">' + y.year + '</span></div>' +
                    '<div class="month-grid">';
                html += y.months.map(m => {{
                    return '<a class="month-card" href="' + y.year + '/' + m.month + '/index.html">' +
                        '<div class="month-name">' + y.year + ' 年 ' + m.month_full + ' 月</div>' +
                        '<div class="month-count">' + m.count + ' 篇總結</div>' +
                        '<div class="month-latest">最新：' + m.latest + '</div>' +
                    '</a>';
                }}).join('');
                html += '</div></div>';
                return html;
            }}).join('');
        }}

    function scrollToYear(year) {{
        document.getElementById('year-' + year).scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}
    renderIndex();
    </script>
</body>
</html>'''

    # Collect all year/month data
    import json as _json
    from datetime import datetime as _dt

    index_data = []
    recent_files = []  # [(date_str, href), ...] for recent-days list
    for year_dir in sorted(OUTPUT_DIR.iterdir()):
        if not year_dir.is_dir() or year_dir.name.startswith('.'):
            continue
        year = year_dir.name
        months = []
        for month_dir in sorted(year_dir.iterdir()):
            if not month_dir.is_dir():
                continue
            month = month_dir.name
            files = sorted([f for f in month_dir.glob("*-*-*.html")], reverse=True)
            if not files:
                continue
            latest = files[0].stem  # YYYY-MM-DD
            for f in files:
                recent_files.append((f.stem, year + '/' + month + '/' + f.name))
            months.append({
                "month": month,
                "month_full": MONTH_FULL.get(month, month),
                "label": f"{year} 年 {MONTH_FULL.get(month, month)} 月",
                "count": len(files),
                "latest": latest
            })
            # Build month index
            day_rows = ""
            for f in files:
                date_str = f.stem
                try:
                    wd = ["一","二","三","四","五","六","日"][_dt.strptime(date_str, "%Y-%m-%d").weekday()]
                except:
                    wd = ""
                day_rows += f'                <li><span class="date">{date_str}</span><a href="{f.name}">{date_str}</a><span class="weekday">星期{wd}</span></li>\n'
            month_html = month_template.format(
                year=year, month_name=MONTH_NAMES.get(month, month+" 月"),
                month_full=MONTH_FULL.get(month, month), count=len(files),
                day_rows=day_rows.rstrip()
            )
            (month_dir / "index.html").write_text(month_html, encoding="utf-8")
            log(f"Month index updated: {month_dir / 'index.html'}")
        if months:
            index_data.append({"year": year, "months": months})

    # Sort recent_files by date descending, take last 7
    recent_files.sort(key=lambda x: x[0], reverse=True)
    recent_7 = recent_files[:7]

    # Build recent days HTML
    recent_html = ""
    for date_str, href in recent_7:
        try:
            wd = ["一","二","三","四","五","六","日"][_dt.strptime(date_str, "%Y-%m-%d").weekday()]
        except:
            wd = ""
        recent_html += f'                <li><span class="date">{date_str}</span><a href="{href}">{date_str}</a><span class="weekday">星期{wd}</span></li>\n'

    # Build main index
    last_update = _dt.now().strftime("%Y-%m-%d %H:%M")
    main_html = main_index_template.format(
        index_json=_json.dumps(index_data, ensure_ascii=False),
        last_update=last_update,
        recent_html=recent_html.rstrip() if recent_html else ""
    )
    (OUTPUT_DIR / "index.html").write_text(main_html, encoding="utf-8")
    log(f"Main index updated: {OUTPUT_DIR / 'index.html'}")

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
        subprocess.run(["git", "add", "public/", "data/classification/", "stat/"], cwd=repo, check=True, capture_output=True, text=True)
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

def main(target_date=None):
    log("=" * 60)
    log("Generating daily news summary (OpenClaw agent CLI)...")
    log("=" * 60)
    if target_date is None:
        target_date = datetime.now() - timedelta(days=1)
    log(f"Target date: {target_date.strftime('%Y-%m-%d')}")
    news_data = load_news(target_date)
    if not news_data:
        log("No news data found")
        return 1
    log(f"Loaded {len(news_data)} news items")
    summary = generate_summary(news_data, target_date)
    if not summary:
        log("Classification failed")
        return 1
    html = build_html(summary, target_date, back_link_path="../../index.html")
    save_html(html, target_date)
    save_classification(summary, target_date, news_data)
    rebuild_index_pages()

    # Run classification statistics script
    stats_script = Path(__file__).parent / "generate_classification_stats.py"
    if stats_script.exists():
        log("Running classification statistics script...")
        date_str = target_date.strftime("%Y-%m-%d")
        r = subprocess.run(
            ["python3", str(stats_script), date_str],
            capture_output=True, text=True
        )
        if r.returncode == 0:
            log("Classification stats generated successfully.")
        else:
            log(f"Classification stats script failed: {r.stderr}")

    commit_and_push(target_date)
    log("Done!")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
