import os
import json
import re
from collections import defaultdict

import os
import json
import re
from collections import defaultdict

def parse_date(date_str):
    # Example: "Sunday, February 25, 2024 at 3:24:35 AM UTC"
    # Or maybe it has different formatting.
    # Let's extract Month and Year using regex
    # Regex to catch "February 25, 2024"
    match = re.search(r'([A-Z][a-z]+) \d{1,2}, (\d{4})', date_str)
    if match:
        month_str = match.group(1)
        year_str = match.group(2)
        months = {
            "January": "01", "February": "02", "March": "03", "April": "04",
            "May": "05", "June": "06", "July": "07", "August": "08",
            "September": "09", "October": "10", "November": "11", "December": "12"
        }
        if month_str in months:
            return f"{year_str}-{months[month_str]}"
    return "Unknown"

def analyze_chats(takeout_dir, user_name=""):
    chat_dir = os.path.join(takeout_dir, "Google Chat", "Groups")
    total_messages = 0
    group_stats = []
    user_message_counts = defaultdict(int)
    timeline = defaultdict(int)
    word_counts = defaultdict(int)
    
    if not os.path.exists(chat_dir):
        print(f"Chat directory not found: {chat_dir}")
        return {}

    for group_id in os.listdir(chat_dir):
        group_path = os.path.join(chat_dir, group_id)
        if not os.path.isdir(group_path):
            continue
            
        info_path = os.path.join(group_path, "group_info.json")
        messages_path = os.path.join(group_path, "messages.json")
        
        group_name = group_id
        members = []
        
        if os.path.exists(info_path):
            try:
                with open(info_path, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                    if "name" in info:
                        group_name = info["name"]
                    if "members" in info:
                        members = [m.get("name", m.get("email", "Unknown")) for m in info["members"]]
                        if group_id.startswith("DM"):
                            # Filter out user from the DM name
                            other_members = [m for m in members if user_name.lower() not in m.lower()]
                            if other_members:
                                group_name = f"DM with {', '.join(other_members)}"
            except Exception as e:
                print(f"Error parsing {info_path}: {e}")
                
        msg_count = 0
        if os.path.exists(messages_path):
            try:
                with open(messages_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    messages = data.get("messages", [])
                    for msg in messages:
                        msg_count += 1
                        total_messages += 1
                        
                        creator = msg.get("creator", {}).get("name", "Unknown")
                        user_message_counts[creator] += 1
                        
                        created_date = msg.get("created_date", "")
                        month_year = parse_date(created_date)
                        if month_year != "Unknown":
                            timeline[month_year] += 1
                            
                        text = msg.get("text", "")
                        if text:
                            words = re.findall(r'\b\w+\b', text.lower())
                            for w in words:
                                if len(w) > 3: # skip short words
                                    word_counts[w] += 1
                                    
            except Exception as e:
                print(f"Error parsing {messages_path}: {e}")
                
        group_stats.append({
            "id": group_id,
            "name": group_name,
            "members": members,
            "message_count": msg_count
        })

    # Sort stats
    group_stats = sorted(group_stats, key=lambda x: x["message_count"], reverse=True)
    user_message_counts = dict(sorted(user_message_counts.items(), key=lambda x: x[1], reverse=True))
    timeline = dict(sorted(timeline.items()))
    word_counts = dict(sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:50]) # top 50 words
    
    stats = {
        "total_messages": total_messages,
        "top_groups": group_stats[:10],
        "top_users": user_message_counts,
        "timeline_messages": timeline,
        "top_words": word_counts
    }
    
    print(f"Chat analysis complete. Processed {total_messages} messages.")
    return stats
