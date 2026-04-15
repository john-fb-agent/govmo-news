#!/bin/bash
# Setup Daily Summary Cron Job
# Schedule: Daily at 8:00 AM

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
SUMMARY_SCRIPT="$PROJECT_DIR/src/generate_summary.py"

echo "========================================"
echo "govmo-news - Daily Summary Cron Setup"
echo "========================================"
echo ""

echo "Project directory: $PROJECT_DIR"
echo "Summary script: $SUMMARY_SCRIPT"
echo ""

# Check if summary script exists
if [ ! -f "$SUMMARY_SCRIPT" ]; then
    echo "❌ Error: generate_summary.py not found!"
    exit 1
fi

# Make sure it's executable
chmod +x "$SUMMARY_SCRIPT"

# Add cron job (8 AM daily)
CRON_JOB="0 8 * * * cd $PROJECT_DIR && python3 $SUMMARY_SCRIPT"

echo "Installing cron job:"
echo "  $CRON_JOB"
echo ""

# Install cron job
(crontab -l 2>/dev/null | grep -v "generate_summary" || true; echo "$CRON_JOB") | crontab -

echo "✓ Summary cron job installed successfully"
echo ""
echo "Current cron jobs:"
crontab -l | grep -E "govmo-news"
echo ""
echo "========================================"
echo "Setup complete!"
echo "========================================"
echo ""
echo "Next summary generation: Tomorrow at 8:00 AM"
echo ""
echo "To view summary logs:"
echo "  tail -f $PROJECT_DIR/data/summary.log"
echo ""
echo "To remove summary cron job:"
echo "  $SCRIPT_DIR/remove-summary-cron.sh"
echo ""
