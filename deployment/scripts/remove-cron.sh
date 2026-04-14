#!/bin/bash
# Remove Cron Jobs for govmo-news

set -e

echo "========================================"
echo "govmo-news - Remove Cron Jobs"
echo "========================================"
echo ""

# Remove govmo-news cron jobs
crontab -l 2>/dev/null | grep -v "govmo-news" | crontab - || true

echo "✓ Cron jobs removed successfully"
echo ""
echo "Current crontab:"
crontab -l 2>/dev/null || echo "No cron jobs"
echo ""
echo "========================================"
