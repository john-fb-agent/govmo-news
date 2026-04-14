#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSS Parser Module
Convert Macau Government News RSS feed from XML to JSON
"""

import feedparser
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class RSSParser:
    """Parse RSS feed and convert to JSON format"""
    
    def __init__(self, rss_url: str = "https://govinfohub.gcs.gov.mo/api/rss/n/zh-hant"):
        self.rss_url = rss_url
        self.feed = None
        
    def fetch(self) -> bool:
        """Fetch RSS feed from URL"""
        try:
            self.feed = feedparser.parse(self.rss_url)
            return self.feed.bozo == 0  # 0 means no parse errors
        except Exception as e:
            print(f"Error fetching RSS: {e}")
            return False
    
    def parse_entries(self) -> List[Dict[str, Any]]:
        """Parse RSS entries into structured format"""
        if not self.feed:
            return []
        
        entries = []
        for entry in self.feed.entries:
            # Use RSS guid for deduplication
            news_id = entry.get("id", entry.get("link", ""))
            
            news_item = {
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "guid": news_id,
                "published": entry.get("published", ""),
                "published_parsed": self._parse_date(entry.get("published_parsed")),
                "summary": entry.get("summary", ""),
                "fetched_at": datetime.now().isoformat()
            }
            entries.append(news_item)
        
        return entries
    
    def _parse_date(self, parsed_date) -> Optional[str]:
        """Convert parsed date to ISO format string"""
        if not parsed_date:
            return None
        try:
            return datetime(
                parsed_date.tm_year,
                parsed_date.tm_mon,
                parsed_date.tm_mday,
                parsed_date.tm_hour,
                parsed_date.tm_min,
                parsed_date.tm_sec
            ).isoformat()
        except:
            return None
    
    def save_raw_xml(self, output_path: str) -> bool:
        """Save raw RSS XML to file"""
        try:
            import requests
            response = requests.get(self.rss_url)
            response.raise_for_status()
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            return True
        except Exception as e:
            print(f"Error saving XML: {e}")
            return False
    
    def save_json(self, entries: List[Dict], output_path: str, by_date: bool = True) -> bool:
        """Save parsed entries as JSON"""
        try:
            if by_date:
                # Organize by year/month/day
                for entry in entries:
                    if entry.get("published_parsed"):
                        date_obj = datetime.fromisoformat(entry["published_parsed"])
                        year = date_obj.strftime("%Y")
                        month = date_obj.strftime("%m")
                        day = date_obj.strftime("%d")
                        
                        output_dir = Path(output_path) / year / month / day
                        output_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Sanitize GUID for filename (replace / and : with -)
                        safe_guid = entry['guid'].replace('/', '-').replace(':', '-').replace('?', '-')
                        output_file = output_dir / f"{safe_guid}.json"
                        if not output_file.exists():  # Skip if already exists (dedup)
                            with open(output_file, 'w', encoding='utf-8') as f:
                                json.dump(entry, f, ensure_ascii=False, indent=2)
            else:
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(entries, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving JSON: {e}")
            return False


if __name__ == "__main__":
    # Test the parser
    parser = RSSParser()
    if parser.fetch():
        entries = parser.parse_entries()
        print(f"Fetched {len(entries)} news items")
        if entries:
            print(f"First item: {entries[0]['title']}")
            print(f"GUID: {entries[0]['guid']}")
    else:
        print("Failed to fetch RSS feed")
