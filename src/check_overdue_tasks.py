#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check for overdue long-running tasks
Run this periodically via cron to detect stuck tasks
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

STATE_FILE = Path(__file__).parent.parent / "data" / "task-state.json"
NOTIFY_SCRIPT = Path(__file__).parent / "notify_failure.py"

def check_and_notify():
    """Check for overdue tasks and send notification if found"""
    if not STATE_FILE.exists():
        print("No task state file found")
        return 0
    
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        # Only check running tasks
        if state.get("status") != "running":
            print(f"Task status: {state.get('status')} - no action needed")
            return 0
        
        # Check if overdue
        expected_end = datetime.fromisoformat(state["expected_end"])
        now = datetime.now()
        
        if now <= expected_end:
            remaining = (expected_end - now).total_seconds()
            print(f"Task '{state['task_name']}' still running, {int(remaining)}s remaining")
            return 0
        
        # Task is overdue!
        overdue_seconds = int((now - expected_end).total_seconds())
        overdue_minutes = overdue_seconds // 60
        
        error_msg = (
            f"Task '{state['task_name']}' is overdue by {overdue_minutes} minutes. "
            f"Started: {state['started_at']}, Expected end: {state['expected_end']}"
        )
        
        print(f"⚠️ {error_msg}")
        
        # Send notification
        if NOTIFY_SCRIPT.exists():
            subprocess.run(
                ['python3', str(NOTIFY_SCRIPT), 'task_monitor', error_msg],
                capture_output=True,
                timeout=30
            )
            print("✅ Notification sent")
        
        return 1
        
    except Exception as e:
        print(f"❌ Failed to check task state: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(check_and_notify())
