import os
import json

import os
import json

def analyze_classroom(takeout_dir):
    classroom_dir = os.path.join(takeout_dir, "Classroom", "Classes")
    classes = []
    clubs_and_extracurriculars = []
    academics = []
    
    if not os.path.exists(classroom_dir):
        print(f"Classroom directory not found: {classroom_dir}")
        return {}

    for class_folder in os.listdir(classroom_dir):
        class_path = os.path.join(classroom_dir, class_folder)
        if not os.path.isdir(class_path):
            continue
            
        data_path = os.path.join(class_path, "Class data.json")
        if os.path.exists(data_path):
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    name = data.get("name", class_folder)
                    subject = data.get("subject", "")
                    
                    classes.append({
                        "name": name,
                        "subject": subject
                    })
                    
                    # Basic categorization logic
                    lower_name = name.lower()
                    lower_subject = subject.lower()
                    if "club" in lower_name or "deca" in lower_name or "council" in lower_name or "team" in lower_name:
                        clubs_and_extracurriculars.append(name)
                    else:
                        academics.append(name)
            except Exception as e:
                print(f"Error parsing {data_path}: {e}")
                
    stats = {
        "total_classes": len(classes),
        "clubs_and_extracurriculars_count": len(clubs_and_extracurriculars),
        "academics_count": len(academics),
        "clubs_list": clubs_and_extracurriculars,
        "academics_list": academics,
        "all_classes": classes
    }
    
    print(f"Classroom analysis complete. Processed {len(classes)} classes.")
    return stats
