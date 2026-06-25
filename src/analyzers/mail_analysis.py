import os
import json
import mailbox
from collections import defaultdict
from email.header import decode_header
import email.utils
from datetime import datetime
import re

def decode_str(s):
    if not s:
        return ""
    try:
        decoded_list = decode_header(s)
        res = ""
        for decoded_string, charset in decoded_list:
            if isinstance(decoded_string, bytes):
                if charset:
                    try:
                        res += decoded_string.decode(charset, errors='ignore')
                    except LookupError:
                        res += decoded_string.decode('utf-8', errors='ignore')
                else:
                    res += decoded_string.decode('utf-8', errors='ignore')
            else:
                res += str(decoded_string)
        return res
    except Exception:
        return str(s)

def extract_email_and_name(s):
    if not s:
        return "", ""
    name, email_addr = email.utils.parseaddr(str(s))
    email_addr = email_addr.lower()
    if not name and email_addr:
        name = email_addr.split('@')[0]
    return name.strip(), email_addr

def analyze_mail(takeout_dir):
    mail_file = os.path.join(takeout_dir, "Mail", "All mail Including Spam and Trash.mbox")
    if not os.path.exists(mail_file):
        print(f"Mail file not found: {mail_file}")
        return {}

    top_senders = defaultdict(int)
    top_recipients = defaultdict(int)
    timeline = defaultdict(int)
    subject_words = defaultdict(int)
    total_emails = 0
    
    print("Opening mailbox (this might take a minute)...")
    mbox = mailbox.mbox(mail_file)
    
    # Let's add a limit to not take forever if it's huge, or just process it all.
    # 600MB is around 10k-50k emails, should take maybe 10-30 seconds.
    for i, message in enumerate(mbox):
        total_emails += 1
        if i % 5000 == 0:
            print(f"Processed {i} emails...")
            
        # Parse From
        from_field = message['from']
        if from_field:
            sender_name, sender_email = extract_email_and_name(from_field)
            if sender_email:
                top_senders[f"{sender_name} <{sender_email}>"] += 1
                
        # Parse To
        to_field = message['to']
        if to_field:
            recip_name, recip_email = extract_email_and_name(to_field)
            if recip_email:
                top_recipients[f"{recip_name} <{recip_email}>"] += 1
                
        # Parse Date
        date_field = message['date']
        if date_field:
            try:
                parsed_date = email.utils.parsedate_to_datetime(date_field)
                month_year = parsed_date.strftime("%Y-%m")
                timeline[month_year] += 1
            except Exception:
                pass
                
        # Parse Subject
        subject_field = message['subject']
        if subject_field:
            subject = decode_str(subject_field)
            words = re.findall(r'\b\w+\b', subject.lower())
            for w in words:
                if len(w) > 3:
                    subject_words[w] += 1

    # Sort
    top_senders = dict(sorted(top_senders.items(), key=lambda x: x[1], reverse=True)[:50])
    top_recipients = dict(sorted(top_recipients.items(), key=lambda x: x[1], reverse=True)[:50])
    timeline = dict(sorted(timeline.items()))
    subject_words = dict(sorted(subject_words.items(), key=lambda x: x[1], reverse=True)[:50])
    
    stats = {
        "total_emails": total_emails,
        "top_senders": top_senders,
        "top_recipients": top_recipients,
        "timeline_emails": timeline,
        "top_subject_words": subject_words
    }
    
    print(f"Mail analysis complete. Processed {total_emails} emails.")
    return stats
