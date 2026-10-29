#!/usr/bin/env bash
# Self-test for govmo-news daily summary cron paths that were NOT live-tested:
#   1. delivery path: command-job stdout actually reaches Telegram (announce)
#   2. digest build against real classification data
#   3. malformed-input behaviour
# Read-only against real data; scratch work happens under /tmp.

set -uo pipefail
REPO=/home/js/.openclaw/workspace/github-repos/govmo-news

echo "🧪 govmo-news cron self-test $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "[1/3] DELIVERY PATH — if you can read this in Telegram, command-job announce works."
echo ""

WORK=/tmp/govmo-selftest-$$
rm -rf "$WORK"; mkdir -p "$WORK/data/classification"
cp -a "$REPO/src" "$WORK/src"
cp -a "$REPO/data/classification/." "$WORK/data/classification/" 2>/dev/null

TARGET=$(date -d yesterday +%Y-%m-%d)
if [ -f "$WORK/data/classification/$TARGET.json" ]; then
  OUT=$(cd "$WORK" && timeout 60 python3 -c "
import sys, datetime; sys.path.insert(0,'src')
import daily_digest as d
print(d.build_digest(datetime.date.fromisoformat('$TARGET')))
" 2>&1)
  if echo "$OUT" | grep -q '澳門政府新聞總結'; then
    echo "[2/3] DIGEST BUILD: PASS ($TARGET formatted from classification JSON)"
  else
    echo "[2/3] DIGEST BUILD: FAIL — $OUT"
  fi
else
  echo "[2/3] DIGEST BUILD: SKIP (no classification for $TARGET)"
fi

echo 'not json' > "$WORK/data/classification/1999-01-01.json"
BAD=$(cd "$WORK" && timeout 60 python3 -c "
import sys, datetime; sys.path.insert(0,'src')
import daily_digest as d
try:
    print('RETURNED', repr(d.build_digest(datetime.date(1999,1,1))))
except Exception as e:
    print('RAISED', type(e).__name__)
" 2>&1 | tail -1)
echo "[3/3] MALFORMED INPUT: $BAD"

rm -rf "$WORK"
echo ""
echo "Real summary data untouched."
