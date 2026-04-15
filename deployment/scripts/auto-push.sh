#!/bin/bash
# Auto-fetch and Push to GitHub
# Run this daily to fetch latest news and push to GitHub

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
LOG_FILE="$PROJECT_DIR/data/auto-push.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log "========================================"
log "Starting auto-fetch and push"
log "========================================"

cd "$PROJECT_DIR"

# Step 1: Fetch latest news
log "Fetching latest news..."
python3 src/fetch_news.py >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log "ERROR: Fetch failed"
    exit 1
fi
log "Fetch completed"

# Step 2: Check for changes
log "Checking for changes..."
git add data/processed/
changes=$(git status --porcelain data/processed/ | wc -l)

if [ "$changes" -eq 0 ]; then
    log "No new changes to commit"
    log "========================================"
    log "Auto-push completed (no changes)"
    log "========================================"
    exit 0
fi

log "Found $changes file(s) with changes"

# Step 3: Commit changes
log "Committing changes..."
git add data/processed/
git commit -m "data: 自動更新新聞數據 ($(date '+%Y-%m-%d'))

🤖 Model: qwen/qwen3.5-plus" >> "$LOG_FILE" 2>&1

if [ $? -ne 0 ]; then
    log "ERROR: Commit failed"
    exit 1
fi
log "Commit completed"

# Step 4: Push to GitHub
log "Pushing to GitHub..."
git push >> "$LOG_FILE" 2>&1

if [ $? -ne 0 ]; then
    log "ERROR: Push failed"
    exit 1
fi
log "Push completed"

log "========================================"
log "Auto-push completed successfully"
log "========================================"
