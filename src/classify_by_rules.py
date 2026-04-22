#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rule-based news classification (fallback for slow AI)
Maps departments and keywords to categories
"""
import json
from pathlib import Path
from datetime import datetime

# Department to category mapping
DEPT_CATEGORY = {
    "金融管理局": "金融財政",
    "財政局": "金融財政",
    "經濟及科技發展局": "經濟產業",
    "招商投資促進局": "經濟產業",
    "貿易投資促進局": "經濟產業",
    "文化局": "文化體育",
    "體育局": "文化體育",
    "旅遊局": "文化體育",
    "澳門博物館": "文化體育",
    "教育及青年發展局": "教育發展",
    "高等教育局": "教育發展",
    "澳門大學": "教育發展",
    "澳門理工大學": "教育發展",
    "澳門旅遊大學": "教育發展",
    "澳門科技大學": "教育發展",
    "澳門城市大學": "教育發展",
    "科學技術發展基金": "科技創新",
    "科技基金": "科技創新",
    "郵電局": "科技創新",
    "交通事務局": "交通運輸",
    "海事及水務局": "交通運輸",
    "公共建設局": "交通運輸",
    "土地工務局": "交通運輸",
    "治安警察局": "政府管治",
    "司法警察局": "政府管治",
    "海關": "政府管治",
    "法務局": "政府管治",
    "行政公職局": "政府管治",
    "政府總部事務局": "政府管治",
    "新聞局": "政府管治",
    "市政署": "社會服務",
    "衛生局": "社會服務",
    "社會工作局": "社會服務",
    "勞工事務局": "人才發展",
    "人才發展委員會": "人才發展",
    "警察總局": "國家安全",
    "保安部隊": "國家安全",
    "消防局": "國家安全",
}

# Keyword to category mapping
KEYWORD_CATEGORY = {
    "金融": "金融財政",
    "銀行": "金融財政",
    "保險": "金融財政",
    "基金": "金融財政",
    "投資": "經濟產業",
    "招商": "經濟產業",
    "會展": "經濟產業",
    "中小企": "經濟產業",
    "科技": "科技創新",
    "創新": "科技創新",
    "AI": "科技創新",
    "人工智能": "科技創新",
    "數碼": "科技創新",
    "文化": "文化體育",
    "藝術": "文化體育",
    "體育": "文化體育",
    "旅遊": "文化體育",
    "博物館": "文化體育",
    "教育": "教育發展",
    "學校": "教育發展",
    "大學": "教育發展",
    "培訓": "教育發展",
    "交通": "交通運輸",
    "巴士": "交通運輸",
    "道路": "交通運輸",
    "基建": "交通運輸",
    "政府": "政府管治",
    "政策": "政府管治",
    "法規": "政府管治",
    "立法會": "政府管治",
    "醫療": "社會服務",
    "衛生": "社會服務",
    "社保": "社會服務",
    "房屋": "社會服務",
    "人才": "人才發展",
    "就業": "人才發展",
    "青年": "人才發展",
    "國安": "國家安全",
    "保安": "國家安全",
}

def classify_news(title, department=None):
    """Classify a single news item by rules"""
    
    # First try department mapping
    if department:
        for dept, category in DEPT_CATEGORY.items():
            if dept in department:
                return category
    
    # Then try title keywords
    for keyword, category in KEYWORD_CATEGORY.items():
        if keyword in title:
            return category
    
    # Default to 其他
    return "其他"

def determine_importance(title, summary=""):
    """Determine importance by keywords"""
    high_keywords = ["新政策", "重大", "突發", "緊急", "首次", "啟用", "開幕", "拜會", "訪問"]
    
    text = title + summary
    for kw in high_keywords:
        if kw in text:
            return 3  # High
    
    # Medium: regular activities, data releases
    if any(kw in text for kw in ["統計", "數據", "報告", "會議", "活動"]):
        return 2  # Medium
    
    return 1  # Low

def main():
    # Load news data
    news_file = Path(__file__).parent.parent / "data" / "processed" / "2026" / "04" / "21.json"
    if not news_file.exists():
        print(f"❌ News file not found: {news_file}")
        return 1
    
    with open(news_file, 'r', encoding='utf-8') as f:
        news_data = json.load(f)
    
    print(f"📰 Loaded {len(news_data)} news items")
    
    # Classify each item
    classified = []
    category_counts = {}
    
    for news in news_data:
        title = news.get("title", "")
        department = news.get("department", "")
        link = news.get("link", "")
        summary = news.get("summary", "")
        
        category = classify_news(title, department)
        importance = determine_importance(title, summary)
        
        classified.append({
            "guid": news.get("guid", ""),
            "title": title,
            "category": category,
            "importance": importance,
            "link": link
        })
        
        category_counts[category] = category_counts.get(category, 0) + 1
    
    # Save classification
    output_dir = Path(__file__).parent.parent / "data" / "classification"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "2026-04-21.json"
    classification_data = {
        "date": "2026-04-21",
        "news": classified,
        "category_stats": category_counts,
        "generated_at": datetime.now().isoformat(),
        "method": "rule-based"
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(classification_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Classification saved to: {output_file}")
    print(f"📊 Category breakdown:")
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {cat}: {count}")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
