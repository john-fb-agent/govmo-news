#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deduplication Utility
Track processed news IDs to avoid duplicates
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Set, List


class Deduplicator:
    """Manage deduplication of news entries"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.ids_file = self.data_dir / ".processed_ids.json"
        self.processed_ids: Set[str] = set()
        self.load_existing_ids()
    
    def load_existing_ids(self) -> Set[str]:
        """Load previously processed news IDs"""
        if self.ids_file.exists():
            try:
                with open(self.ids_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.processed_ids = set(data.get('ids', []))
            except Exception as e:
                print(f"Error loading IDs: {e}")
                self.processed_ids = set()
        return self.processed_ids
    
    def add_ids(self, ids: List[str]) -> bool:
        """Add new IDs to the processed set"""
        try:
            self.processed_ids.update(ids)
            self._save()
            return True
        except Exception as e:
            print(f"Error adding IDs: {e}")
            return False
    
    def is_duplicate(self, news_id: str) -> bool:
        """Check if a news ID already exists"""
        return news_id in self.processed_ids
    
    def _save(self) -> bool:
        """Save processed IDs to file"""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            data = {
                'ids': list(self.processed_ids),
                'count': len(self.processed_ids),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.ids_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving IDs: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get deduplication statistics"""
        return {
            'total_processed': len(self.processed_ids),
            'ids_file': str(self.ids_file),
            'last_updated': datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Test the deduplicator
    from pathlib import Path
    dedup = Deduplicator(Path("./data/processed"))
    stats = dedup.get_stats()
    print(f"Deduplication stats: {stats}")
