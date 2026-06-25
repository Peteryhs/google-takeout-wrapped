import os
import json
from collections import defaultdict
from datetime import datetime

import os
import json
from collections import defaultdict
from datetime import datetime

def analyze_drive(takeout_dir):
    drive_dir = os.path.join(takeout_dir, "Drive")
    total_size = 0
    file_count = 0
    file_types = defaultdict(int)
    file_type_sizes = defaultdict(int)
    largest_files = []
    unnamed_files = []
    timeline = defaultdict(int)
    
    if not os.path.exists(drive_dir):
        print(f"Drive directory not found: {drive_dir}")
        return {}

    for root, dirs, files in os.walk(drive_dir):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Follow symlinks if any, though takeout rarely uses them
            if not os.path.isfile(file_path):
                continue
                
            try:
                stat = os.stat(file_path)
                size = stat.st_size
                mtime = stat.st_mtime
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue
                
            total_size += size
            file_count += 1
            
            # File type breakdown
            _, ext = os.path.splitext(file)
            ext = ext.lower()
            if not ext:
                ext = "no_extension"
            file_types[ext] += 1
            file_type_sizes[ext] += size
            
            # Largest files
            largest_files.append({"name": file, "size": size, "path": file_path.replace(drive_dir, "")})
            
            # Unnamed files analysis
            lower_name = file.lower()
            if "untitled" in lower_name or ext == "no_extension" or lower_name.startswith("copy of untitled"):
                unnamed_files.append({"name": file, "size": size})
            
            # Timeline (Month-Year)
            dt = datetime.fromtimestamp(mtime)
            month_year = dt.strftime("%Y-%m")
            timeline[month_year] += 1

    # Sort largest files
    largest_files = sorted(largest_files, key=lambda x: x["size"], reverse=True)[:20]
    
    # Sort unnamed files by size
    unnamed_files = sorted(unnamed_files, key=lambda x: x["size"], reverse=True)
    
    stats = {
        "total_files": file_count,
        "total_size_bytes": total_size,
        "file_types_count": dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True)),
        "file_types_size": dict(sorted(file_type_sizes.items(), key=lambda x: x[1], reverse=True)),
        "largest_files": largest_files,
        "unnamed_files_count": len(unnamed_files),
        "unnamed_files_sample": unnamed_files[:20],
        "timeline_modifications": dict(sorted(timeline.items()))
    }
    
    print(f"Drive analysis complete. Processed {file_count} files.")
    return stats
