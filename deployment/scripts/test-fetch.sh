#!/bin/bash
# Test News Fetch Script
# Run a manual test of the news fetcher

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
VENV_DIR="$PROJECT_DIR/venv"

echo "========================================"
echo "govmo-news - Test Fetch"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ -d "$VENV_DIR" ]; then
    PYTHON="$VENV_DIR/bin/python"
else
    PYTHON="python3"
fi

echo "Running fetch script..."
echo ""

cd "$PROJECT_DIR"
$PYTHON src/backend/fetch_news.py

echo ""
echo "========================================"
echo "Test complete!"
echo "========================================"
echo ""
echo "Check data/processed/ for output files"
echo "Check data/fetch.log for detailed logs"
echo ""
