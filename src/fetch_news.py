#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main News Fetcher Script
Fetches Macau Government News RSS and converts to JSON

Schedule: Daily at 09:00, 11:00, 13:00, 15:00, 17:00 (Macau Time GMT+8)
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime
import logging
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from rss_parser import RSSParser

# Configure logging
base_dir = Path(__file__).parent.parent
data_dir = base_dir / "data"
data_dir.mkdir(parents=True, exist_ok=True)

# Log to file only (cron will capture output)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(data_dir / "fetch.log", encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def load_existing_guids(processed_dir: Path) -> set:
    """Load all existing news GUIDs from processed directory"""
    existing_guids = set()
    
    if not processed_dir.exists():
        return existing_guids
    
    # Walk through all JSON files and collect GUIDs
    # Each file contains a list of news entries for one day
    for json_file in processed_dir.rglob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for entry in data:
                        if 'guid' in entry:
                            existing_guids.add(entry['guid'])
        except Exception as e:
            logger.warning(f"Error reading {json_file}: {e}")
    
    return existing_guids


def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("Starting news fetch job")
    logger.info(f"Execution time: {datetime.now().isoformat()}")
    
    try:
        # Paths
        base_dir = Path(__file__).parent.parent
        processed_dir = base_dir / "data" / "processed"
        
        # Ensure directories exist
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize parser
        parser = RSSParser()
        
        # Fetch RSS feed
        logger.info(f"Fetching RSS from: {parser.rss_url}")
        if not parser.fetch():
            logger.error("Failed to fetch RSS feed")
            send_notification("fetch_news.py", "Failed to fetch RSS feed")
            return 1
        
        logger.info(f"RSS feed fetched successfully")
        
        # Skip raw XML saving (not needed)
        
        # Parse entries
        entries = parser.parse_entries()
        logger.info(f"Parsed {len(entries)} news entries")
        
        if not entries:
            logger.info("No news entries found")
            return 0
        
        # Load existing GUIDs for deduplication
        existing_guids = load_existing_guids(processed_dir)
        logger.info(f"Existing news GUIDs in database: {len(existing_guids)}")
        
        # Filter out duplicates using RSS guid
        new_entries = [e for e in entries if e['guid'] not in existing_guids]
        duplicate_count = len(entries) - len(new_entries)
        
        logger.info(f"New entries: {len(new_entries)}, Duplicates skipped: {duplicate_count}")
        
        # Save new entries
        if new_entries:
            if parser.save_json(new_entries, str(processed_dir), by_date=True):
                logger.info(f"Saved {len(new_entries)} new entries to JSON")
            else:
                logger.error("Failed to save JSON files")
                send_notification("fetch_news.py", "Failed to save JSON files")
                return 1
        else:
            logger.info("No new entries to save (all duplicates)")
        
        # Summary
        logger.info("=" * 60)
        logger.info("Fetch job completed successfully")
        logger.info(f"Total entries: {len(entries)}")
        logger.info(f"New entries saved: {len(new_entries)}")
        logger.info(f"Duplicates skipped: {duplicate_count}")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        logger.error(f"❌ CRITICAL ERROR: {error_msg}")
        send_notification("fetch_news.py", error_msg)
        return 1


def send_notification(script_name: str, error_message: str):
    """Send failure notification via notify_failure.py"""
    notify_script = Path(__file__).parent / "notify_failure.py"
    if notify_script.exists():
        try:
            subprocess.run(
                ['python3', str(notify_script), script_name, error_message],
                capture_output=True,
                timeout=30
            )
        except Exception as e:
            logger.warning(f"⚠️ Failed to send notification: {e}")


if __name__ == "__main__":
    sys.exit(main())
