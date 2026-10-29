#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Command-job entry point for the daily summary cron.

Runs generate_summary.py, then prints a short human-readable digest to
stdout. The cron job's command payload announces that stdout to Telegram,
so this replaces the old agent turn (which cost ~114 model calls) with
~7 model calls plus a few lines of text formatting.

Exit codes follow generate_summary.py: 0 on success or no-op, non-zero on
failure, so cron run status stays meaningful.
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE = Path(__file__).parent.parent
CLASSIFICATION_DIR = BASE / "data" / "classification"


def run_summary():
    """Run generate_summary.py; return its exit code."""
    r = subprocess.run(
        [sys.executable, str(BASE / "src" / "generate_summary.py")],
        cwd=str(BASE),
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        sys.stderr.write(r.stdout)
        sys.stderr.write(r.stderr)
    return r.returncode


def build_digest(date):
    """Format the digest, or return None if this date has no classification."""
    cls_file = CLASSIFICATION_DIR / f"{date.strftime('%Y-%m-%d')}.json"
    if not cls_file.exists():
        return None
    data = json.loads(cls_file.read_text(encoding="utf-8"))
    news = data.get("news", [])
    if not news:
        return None

    counts = {}
    for n in news:
        cat = n.get("category") or "未分類"
        counts[cat] = counts.get(cat, 0) + 1
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))

    imp = {3: 0, 2: 0, 1: 0}
    for n in news:
        k = int(n.get("importance") or 1)
        imp[k] = imp.get(k, 0) + 1

    lines = [
        "📰 澳門政府新聞總結 — " + date.strftime("%Y-%m-%d"),
        f"共 {len(news)} 則新聞 · {len(ordered)} 個分類",
        "",
        "分類統計：",
    ]
    for cat, n in ordered:
        lines.append(f"  {cat} — {n}")
    lines.append("")
    lines.append(f"重要性：高 {imp.get(3, 0)} · 中 {imp.get(2, 0)} · 低 {imp.get(1, 0)}")

    highs = [n for n in news if int(n.get("importance") or 1) == 3]
    if highs:
        lines.append("")
        lines.append("🔥 重點新聞：")
        for n in highs[:5]:
            lines.append(f"  · {n.get('title', '')}")

    lines.append("")
    lines.append(
        "頁面：public/"
        + date.strftime("%Y/%m/%Y-%m-%d.html")
    )
    return "\n".join(lines)


def main():
    target = datetime.now() - timedelta(days=1)

    code = run_summary()
    if code != 0:
        print(f"❌ 每日總結失敗（{target.strftime('%Y-%m-%d')}），exit={code}")
        print("詳見 data/summary.log")
        return code

    digest = build_digest(target)
    if digest is None:
        print(f"⚠️ {target.strftime('%Y-%m-%d')} 無分類資料，請檢查 data/summary.log")
        return 0

    print(digest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
