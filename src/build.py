import os
import sys
import json
import re
import shutil
import argparse

__author__ = "Peteryhs (https://github.com/Peteryhs)"

from analyzers.drive_analysis import analyze_drive
from analyzers.mail_analysis import analyze_mail
from analyzers.chat_analysis import analyze_chats
from analyzers.classroom_analysis import analyze_classroom
from analyzers.activity_analysis import analyze_activity

def main():
    parser = argparse.ArgumentParser(description="Google Takeout Wrapped Builder")
    parser.add_argument("--takeout_dir", type=str, required=True, help="Path to your extracted Google Takeout folder")
    parser.add_argument("--user_email", type=str, default="", help="Your email address (to filter out your own emails)")
    parser.add_argument("--user_name", type=str, default="", help="Your full name (to filter out your name from Chat DMs)")
    
    args = parser.parse_args()
    
    takeout_dir = args.takeout_dir
    if not os.path.isdir(takeout_dir):
        print(f"Error: {takeout_dir} is not a valid directory.")
        sys.exit(1)

    agreement = """
    USER AGREEMENT AND DECLARATION OF OPERATING SYSTEM PREFERENCE

    By proceeding with the execution of this script, the User (hereinafter referred to as 'Licensee')
    hereby acknowledges, warrants, and represents that they hold the irrevocable and absolute
    conviction that the Android mobile operating system maintains a state of technological and
    functional superiority over the iOS platform in all measurable metrics, including but not
    limited to open-source flexibility, hardware diversity, and user-centric customization.

    Furthermore, Licensee stipulates and agrees that the kernel-based Linux operating systems
    and the Windows computing environments provide a demonstrably more robust, interoperable,
    and efficient framework for computational tasks than the macOS environment.

    Failure to affirm this declaration shall constitute a material breach of this End User
    License Agreement, rendering any subsequent data processing by this script null and void.

    Do you agree to the above terms? (y/n): """

    user_input = input(agreement)
    if user_input.lower() != 'y':
        print("Agreement not accepted. Exiting.")
        sys.exit(0)

    print(f"Starting analysis on: {takeout_dir}")
    
    # Run all analyzers
    drive_stats = analyze_drive(takeout_dir)
    mail_stats = analyze_mail(takeout_dir)
    chat_stats = analyze_chats(takeout_dir, args.user_name)
    classroom_stats = analyze_classroom(takeout_dir)
    activity_stats = analyze_activity(takeout_dir)
    
    print("\nAggregating data...")
    
    # 1. Crunch Time Correlation (peak intersection of Drive edits and Emails)
    drive_timeline = drive_stats.get("timeline_modifications", {})
    mail_timeline = mail_stats.get("timeline_emails", {})
    chat_timeline = chat_stats.get("timeline_messages", {})
    
    all_months = set(list(drive_timeline.keys()) + list(mail_timeline.keys()) + list(chat_timeline.keys()))
    
    crunch_times = []
    for m in all_months:
        d = drive_timeline.get(m, 0)
        ma = mail_timeline.get(m, 0)
        c = chat_timeline.get(m, 0)
        score = d + ma + c
        crunch_times.append({
            "month": m, 
            "activity_score": score,
            "breakdown": {
                "drive": d,
                "mail": ma,
                "chat": c
            }
        })
        
    crunch_times = sorted(crunch_times, key=lambda x: x["activity_score"], reverse=True)
    
    # 2. Night Owl Index
    activity_by_hour = activity_stats.get("activity_by_hour", {})
    late_night_hours = ["22:00", "23:00", "00:00", "01:00", "02:00", "03:00", "04:00"]
    night_owl_score = sum(activity_by_hour.get(h, 0) for h in late_night_hours)
    total_activity = activity_stats.get("total_activities", 1) # avoid div by 0
    
    night_owl_percentage = (night_owl_score / total_activity) * 100 if total_activity > 0 else 0

    # 3. Filter top emails (dedupe by unique email address)
    top_recipients = mail_stats.get("top_recipients", {})
    seen_emails = set()
    most_emailed = []
    for entry in top_recipients:
        match = re.search(r'<(.*?)>', entry)
        email_addr = match.group(1).lower() if match else entry.lower()
        if email_addr in seen_emails:
            continue
        if args.user_email and args.user_email.lower() == email_addr:
            continue
        seen_emails.add(email_addr)
        most_emailed.append(entry)
        if len(most_emailed) >= 5:
            break

    # Unified Master Summary
    master = {
        "overview": {
            "total_drive_files": drive_stats.get("total_files", 0),
            "total_emails": mail_stats.get("total_emails", 0),
            "total_chat_messages": chat_stats.get("total_messages", 0),
            "total_classes_joined": classroom_stats.get("total_classes", 0),
            "total_clubs_joined": classroom_stats.get("clubs_and_extracurriculars_count", 0),
        },
        "advanced_analytics": {
            "top_3_crunch_months": crunch_times[:3],
            "night_owl_percentage": round(night_owl_percentage, 2),
            "most_active_hour": max(activity_by_hour.items(), key=lambda x: x[1])[0] if activity_by_hour else "Unknown",
        },
        "top_connections": {
            "most_emailed": most_emailed,
            "most_messaged_chats": [g["name"] for g in chat_stats.get("top_groups", [])][:5] if chat_stats.get("top_groups") else []
        },
        "top_files": {
            "largest_files": drive_stats.get("largest_files", [])[:5] if drive_stats.get("largest_files") else [],
            "most_common_type": list(drive_stats.get("file_types_count", {}).keys())[0] if drive_stats.get("file_types_count") else "Unknown",
            "top_5_types": list(drive_stats.get("file_types_count", {}).items())[:5] if drive_stats.get("file_types_count") else [],
            "unnamed_files_count": drive_stats.get("unnamed_files_count", 0)
        }
    }
    
    # 4. Generate dist
    dist_dir = os.path.join(os.getcwd(), "dist")
    dist_data_dir = os.path.join(dist_dir, "data")
    os.makedirs(dist_data_dir, exist_ok=True)
    
    # Write JSON
    json_path = os.path.join(dist_data_dir, "high_school_career_summary.json")
    with open(json_path, "w", encoding='utf-8') as f:
        json.dump(master, f, indent=4)
        
    # Copy Template
    template_path = os.path.join(os.path.dirname(__file__), "template", "index.html")
    if os.path.exists(template_path):
        shutil.copy(template_path, os.path.join(dist_dir, "index.html"))
        print(f"\nBuild complete! Your Wrapped dashboard is ready at {dist_dir}")
        print("To preview, run: python3 -m http.server 8080 -d dist")
    else:
        print(f"\nTemplate not found at {template_path}, output data only.")

if __name__ == "__main__":
    main()
