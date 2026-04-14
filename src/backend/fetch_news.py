#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main News Fetcher Script
Fetches Macau Government News RSS and converts to JSON

Schedule: Daily at 09:00, 11:00, 13:00, 15:00, 17:00 (Macau Time GMT+8)
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.rss_parser import RSSParser
from utils.dedup import Deduplicator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/fetch.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("Starting news fetch job")
    logger.info(f"Execution time: {datetime.now().isoformat()}")
    
    # Paths
    base_dir = Path(__file__).parent.parent.parent
    raw_dir = base_dir / "data" / "raw"
    processed_dir = base_dir / "data" / "processed"
    
    # Ensure directories exist
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize parser
    parser = RSSParser()
    
    # Fetch RSS feed
    logger.info(f"Fetching RSS from: {parser.rss_url}")
    if not parser.fetch():
        logger.error("Failed to fetch RSS feed")
        return 1
    
    logger.info(f"RSS feed fetched successfully")
    
    # Save raw XML
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_xml_path = raw_dir / f"rss_{timestamp}.xml"
    if parser.save_raw_xml(str(raw_xml_path)):
        logger.info(f"Raw XML saved to: {raw_xml_path}")
    else:
        logger.warning("Failed to save raw XML")
    
    # Parse entries
    entries = parser.parse_entries()
    logger.info(f"Parsed {len(entries)} news entries")
    
    if not entries:
        logger.info("No news entries found")
        return 0
    
    # Load existing IDs for deduplication
    dedup = Deduplicator(processed_dir)
    existing_ids = dedup.load_existing_ids()
    logger.info(f"Existing news IDs in database: {len(existing_ids)}")
    
    # Filter out duplicates
    new_entries = [e for e in entries if e['id'] not in existing_ids]
    duplicate_count = len(entries) - len(new_entries)
    
    logger.info(f"New entries: {len(new_entries)}, Duplicates skipped: {duplicate_count}")
    
    # Save new entries
    if new_entries:
        if parser.save_json(new_entries, str(processed_dir), by_date=True):
            logger.info(f"Saved {len(new_entries)} new entries to JSON")
            
            # Update dedup database
            dedup.add_ids([e['id'] for e in new_entries])
            logger.info("Updated deduplication database")
        else:
            logger.error("Failed to save JSON files")
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


if __name__ == "__main__":
    sys.exit(main())
