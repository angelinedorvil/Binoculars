import re
from collections import Counter
from pathlib import Path
import json
import os
import shutil

def migrate_jsonl_combine_title_text(path):
    temp_path = path + ".tmp"

    with open(path, "r", encoding="utf-8") as infile, \
         open(temp_path, "w", encoding="utf-8") as outfile:

        for line in infile:
            line = line.strip()
            if not line:
                continue

            obj = json.loads(line)

            title = obj.get("title")
            text = obj.get("text")

            # If either is missing, skip or keep as is
            if title and text:
                combined = f"{title}\n\n{text}"
            elif text:
                combined = text
            else:
                combined = ""

            # Build the new JSON entry
            new_entry = {
                "text": combined,
                "description": obj.get("description"),
                "domain": obj.get("domain"),
                "date": obj.get("date"),
                "url": obj.get("url"),
                "image_url": obj.get("image_url")
            }

            outfile.write(json.dumps(new_entry, ensure_ascii=False) + "\n")

    # Backup the original just in case
    backup_path = path + ".bak"
    shutil.copy(path, backup_path)

    # Replace original with migrated file
    shutil.move(temp_path, path)

    print(f"Migration complete.\nBackup saved at: {backup_path}")

migrate_jsonl_combine_title_text("extension/essays.jsonl")
migrate_jsonl_combine_title_text("extension/cc_news.jsonl")