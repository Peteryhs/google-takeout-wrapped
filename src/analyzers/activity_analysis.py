import os
import json
import re
from collections import defaultdict

import os
import json
import re
from collections import defaultdict

def analyze_activity(takeout_dir):
    activity_file = os.path.join(takeout_dir, "My Activity", "Drive", "MyActivity.html")
    if not os.path.exists(activity_file):
        print(f"Activity file not found: {activity_file}")
        return {}

    # To calculate the "Night Owl Index" we just count activity by hour of the day
    hour_counts = defaultdict(int)
    total_activities = 0
    
    # Regex to match: Jan 19, 2026, 2:18:10 PM EDT
    # There is often a weird unicode space before AM/PM
    pattern = re.compile(r"([A-Z][a-z]{2})\s+(\d{1,2}),\s+(\d{4}),\s+(\d{1,2}):(\d{2}):(\d{2})\s*([AP]M)")
    
    try:
        with open(activity_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        matches = pattern.findall(content)
        for match in matches:
            total_activities += 1
            month, day, year, hour_str, minute, second, am_pm = match
            
            hour = int(hour_str)
            if am_pm == "PM" and hour != 12:
                hour += 12
            elif am_pm == "AM" and hour == 12:
                hour = 0
                
            hour_counts[hour] += 1
            
    except Exception as e:
        print(f"Error parsing {activity_file}: {e}")
        return {}

    # Format the hour counts
    formatted_hours = {}
    for h in range(24):
        formatted_hours[f"{h:02d}:00"] = hour_counts.get(h, 0)
        
    stats = {
        "total_activities": total_activities,
        "activity_by_hour": formatted_hours
    }
    
    print(f"Activity analysis complete. Processed {total_activities} activities.")
    return stats
