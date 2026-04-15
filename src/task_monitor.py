#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task Monitor - Track long-running task status
Write task state at start, update at completion
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

STATE_FILE = Path(__file__).parent.parent / "data" / "task-state.json"

def task_start(task_name: str, timeout_seconds: int = 600):
    """Record task start time and expected completion"""
    now = datetime.now()
    expected_end = now + timedelta(seconds=timeout_seconds)
    
    state = {
        "task_name": task_name,
        "started_at": now.isoformat(),
        "expected_end": expected_end.isoformat(),
        "timeout_seconds": timeout_seconds,
        "status": "running",
        "completed_at": None,
        "error": None
    }
    
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Task '{task_name}' started, expected end: {expected_end.strftime('%H:%M:%S')}")

def task_complete(task_name: str, success: bool = True, error: str = None):
    """Mark task as completed"""
    state = {
        "task_name": task_name,
        "started_at": None,
        "expected_end": None,
        "timeout_seconds": None,
        "status": "completed" if success else "failed",
        "completed_at": datetime.now().isoformat(),
        "error": error
    }
    
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    
    status_str = "completed" if success else "failed"
    print(f"✅ Task '{task_name}' {status_str}")

def task_timeout(task_name: str, error: str = "Task timed out"):
    """Mark task as timed out"""
    state = {
        "task_name": task_name,
        "started_at": None,
        "expected_end": None,
        "timeout_seconds": None,
        "status": "timeout",
        "completed_at": datetime.now().isoformat(),
        "error": error
    }
    
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    
    print(f"⚠️ Task '{task_name}' timed out")

def check_overdue() -> dict | None:
    """Check if any task is overdue (past expected end time)"""
    if not STATE_FILE.exists():
        return None
    
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        if state.get("status") != "running":
            return None
        
        expected_end = datetime.fromisoformat(state["expected_end"])
        now = datetime.now()
        
        if now > expected_end:
            overdue_seconds = (now - expected_end).total_seconds()
            return {
                "task_name": state["task_name"],
                "started_at": state["started_at"],
                "expected_end": state["expected_end"],
                "overdue_seconds": int(overdue_seconds),
                "status": "overdue"
            }
        
        return None
    except Exception as e:
        print(f"❌ Failed to check task state: {e}")
        return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        action = sys.argv[1]
        task_name = sys.argv[2]
        
        if action == "start":
            timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 600
            task_start(task_name, timeout)
        elif action == "complete":
            success = sys.argv[3] == "true" if len(sys.argv) > 3 else True
            error = sys.argv[4] if len(sys.argv) > 4 else None
            task_complete(task_name, success, error)
        elif action == "timeout":
            error = sys.argv[3] if len(sys.argv) > 3 else "Task timed out"
            task_timeout(task_name, error)
        elif action == "check":
            result = check_overdue()
            if result:
                print(json.dumps(result, indent=2))
            else:
                print("No overdue tasks")
    else:
        print("Usage: task_monitor.py <start|complete|timeout|check> <task_name> [timeout_seconds] [success] [error]")
        sys.exit(1)
