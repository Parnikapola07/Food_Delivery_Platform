import os
import json
import glob
import shutil
import urllib.parse

history_dir = os.path.expandvars(r"%APPDATA%\Code\User\History")
workspace_dir = r"c:\Users\Parnika\OneDrive\Desktop\Flask class\Food Delivery Platform"

entries_files = glob.glob(os.path.join(history_dir, "*", "entries.json"))
print(f"Found {len(entries_files)} entry files")

recovered_count = 0

for ef in entries_files:
    try:
        with open(ef, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        continue
    
    resource = data.get("resource", "")
    resource_unquoted = urllib.parse.unquote(resource)
    
    if "templates" in resource_unquoted and "Food Delivery Platform" in resource_unquoted and resource_unquoted.endswith(".html"):
        parts = resource_unquoted.split("/templates/")
        if len(parts) < 2: continue
        rel_path = "templates/" + parts[-1]
        
        target_path = os.path.join(workspace_dir, os.path.normpath(rel_path))
        
        entries = data.get("entries", [])
        if not entries: continue
        
        entries.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        
        folder = os.path.dirname(ef)
        
        for i, entry in enumerate(entries):
            entry_id = entry.get("id")
            ts = entry.get("timestamp")
            src_file = os.path.join(folder, entry_id)
            if not os.path.exists(src_file): continue
            
            rec_dir = os.path.join(workspace_dir, "recovery", rel_path)
            os.makedirs(rec_dir, exist_ok=True)
            shutil.copy(src_file, os.path.join(rec_dir, f"{ts}_{entry_id}.html"))
            
        recovered_count += 1

print(f"Recovered history for {recovered_count} HTML files into 'recovery' directory.")
