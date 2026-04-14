#!/bin/bash
# Setup Cron Jobs for govmo-news
# Schedule: Daily at 09:00, 11:00, 13:00, 15:00, 17:00 (Macau Time GMT+8)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
VENV_DIR="$PROJECT_DIR/venv"
PYTHON=""

echo "========================================"
echo "govmo-news - Cron Job Setup"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ -d "$VENV_DIR" ]; then
    echo "✓ Virtual environment found"
    PYTHON="$VENV_DIR/bin/python"
else
    echo "⚠ Virtual environment not found, using system Python"
    PYTHON="python3"
fi

# Get absolute path to fetch script
FETCH_SCRIPT="$PROJECT_DIR/src/fetch_news.py"
LOG_FILE="$PROJECT_DIR/data/cron.log"

echo "Project directory: $PROJECT_DIR"
echo "Python: $PYTHON"
echo "Fetch script: $FETCH_SCRIPT"
echo "Log file: $LOG_FILE"
echo ""

# Create cron jobs
CRON_JOBS=(
    "0 9 * * * cd $PROJECT_DIR && $PYTHON $FETCH_SCRIPT >> $LOG_FILE 2>&1"
    "0 11 * * * cd $PROJECT_DIR && $PYTHON $FETCH_SCRIPT >> $LOG_FILE 2>&1"
    "0 13 * * * cd $PROJECT_DIR && $PYTHON $FETCH_SCRIPT >> $LOG_FILE 2>&1"
    "0 15 * * * cd $PROJECT_DIR && $PYTHON $FETCH_SCRIPT >> $LOG_FILE 2>&1"
    "0 17 * * * cd $PROJECT_DIR && $PYTHON $FETCH_SCRIPT >> $LOG_FILE 2>&1"
)

echo "Installing cron jobs:"
for job in "${CRON_JOBS[@]}"; do
    echo "  $job"
done
echo ""

# Install cron jobs
(crontab -l 2>/dev/null | grep -v "govmo-news" || true; printf "%s\n" "${CRON_JOBS[@]}") | crontab -

echo "✓ Cron jobs installed successfully"
echo ""
echo "Current crontab:"
crontab -l | grep "govmo-news" || echo "No govmo-news cron jobs found"
echo ""
echo "========================================"
echo "Setup complete!"
echo "========================================"
echo ""
echo "To verify cron is running:"
echo "  systemctl status cron"
echo ""
echo "To view cron logs:"
echo "  tail -f $LOG_FILE"
echo ""
echo "To remove cron jobs:"
echo "  $SCRIPT_DIR/remove-cron.sh"
echo ""
