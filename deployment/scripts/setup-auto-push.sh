#!/bin/bash
# Setup Auto-Push Cron Job
# Schedule: Daily at 10:00 PM (22:00) Macau Time

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
AUTO_PUSH_SCRIPT="$PROJECT_DIR/deployment/scripts/auto-push.sh"

echo "========================================"
echo "govmo-news - Auto-Push Cron Setup"
echo "========================================"
echo ""

echo "Project directory: $PROJECT_DIR"
echo "Auto-push script: $AUTO_PUSH_SCRIPT"
echo ""

# Check if auto-push script exists
if [ ! -f "$AUTO_PUSH_SCRIPT" ]; then
    echo "❌ Error: auto-push.sh not found!"
    exit 1
fi

# Make sure it's executable
chmod +x "$AUTO_PUSH_SCRIPT"

# Add cron job (10 PM daily)
CRON_JOB="0 22 * * * cd $PROJECT_DIR && $AUTO_PUSH_SCRIPT"

echo "Installing cron job:"
echo "  $CRON_JOB"
echo ""

# Install cron job
(crontab -l 2>/dev/null | grep -v "auto-push" || true; echo "$CRON_JOB") | crontab -

echo "✓ Auto-push cron job installed successfully"
echo ""
echo "Current cron jobs:"
crontab -l | grep -E "govmo-news|auto-push"
echo ""
echo "========================================"
echo "Setup complete!"
echo "========================================"
echo ""
echo "Next auto-push: Tonight at 10:00 PM"
echo ""
echo "To view auto-push logs:"
echo "  tail -f $PROJECT_DIR/data/auto-push.log"
echo ""
echo "To remove auto-push cron job:"
echo "  $SCRIPT_DIR/remove-auto-push.sh"
echo ""
