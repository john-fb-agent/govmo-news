#!/bin/bash
# Remove Daily Summary Cron Job

set -e

echo "========================================"
echo "govmo-news - Remove Summary Cron"
echo "========================================"
echo ""

# Remove summary cron jobs
crontab -l 2>/dev/null | grep -v "generate_summary" | crontab - || true

echo "✓ Summary cron job removed successfully"
echo ""
echo "Current cron jobs:"
crontab -l 2>/dev/null || echo "No cron jobs"
echo ""
echo "========================================"
