#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Log failure notification for heartbeat check
Writes to a file that the agent checks during heartbeats
"""

import sys
import json
from pathlib import Path
from datetime import datetime

NOTIFICATION_FILE = Path(__file__).parent.parent / "data" / "cron-failures.json"

def log_failure(script_name: str, error_message: str):
    """Log failure to JSON file for heartbeat monitoring"""
    timestamp = datetime.now().isoformat()
    
    # Load existing failures
    failures = []
    if NOTIFICATION_FILE.exists():
        try:
            with open(NOTIFICATION_FILE, 'r', encoding='utf-8') as f:
                failures = json.load(f)
        except:
            failures = []
    
    # Add new failure
    failures.append({
        "timestamp": timestamp,
        "script": script_name,
        "error": error_message,
        "notified": False
    })
    
    # Keep only last 10 failures
    failures = failures[-10:]
    
    # Save
    with open(NOTIFICATION_FILE, 'w', encoding='utf-8') as f:
        json.dump(failures, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Failure logged to {NOTIFICATION_FILE}")
    return True

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        script_name = sys.argv[1]
        error_message = sys.argv[2]
        log_failure(script_name, error_message)
    else:
        print("Usage: notify_failure.py <script_name> <error_message>")
        sys.exit(1)
