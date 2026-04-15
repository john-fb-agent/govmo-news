#!/bin/bash
# Auto-Push to GitHub
# Run this daily to push news data to GitHub (no fetch, just push)
# Schedule: 22:00 daily (data already fetched at 17:00)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
LOG_FILE="$PROJECT_DIR/data/auto-push.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log "========================================"
log "Starting auto-push"
log "========================================"

cd "$PROJECT_DIR"

# Step 1: Check for changes (no fetch, data already fetched at 17:00)
log "Checking for changes..."
git add data/processed/
changes=$(git status --porcelain data/processed/ | wc -l)

if [ "$changes" -eq 0 ]; then
    log "No new changes to commit"
    log "========================================"
    log "Auto-push completed (no changes)"
    log "========================================"
    log ""
    log "Note: No fetch performed (data already fetched at 17:00)"
    exit 0
fi

log "Found $changes file(s) with changes"

# Step 2: Commit changes
log "Committing changes..."
git add data/processed/
git commit -m "data: 自動更新新聞數據 ($(date '+%Y-%m-%d'))

🤖 Model: qwen/qwen3.5-plus" >> "$LOG_FILE" 2>&1

if [ $? -ne 0 ]; then
    log "ERROR: Commit failed"
    exit 1
fi
log "Commit completed"

# Step 3: Push to GitHub
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
log ""
log "Note: No fetch performed (data already fetched at 17:00)"
