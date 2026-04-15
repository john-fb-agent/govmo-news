#!/bin/bash
# Remove Auto-Push Cron Job

set -e

echo "========================================"
echo "govmo-news - Remove Auto-Push Cron"
echo "========================================"
echo ""

# Remove auto-push cron jobs
crontab -l 2>/dev/null | grep -v "auto-push" | crontab - || true

echo "✓ Auto-push cron job removed successfully"
echo ""
echo "Current cron jobs:"
crontab -l 2>/dev/null || echo "No cron jobs"
echo ""
echo "========================================"
