import re
from collections import Counter
from pathlib import Path
import json
import os
import shutil


# save as check_duplicates.py and run: python check_duplicates.py

# p = Path(r"c:/Users/angel/NLP-project/Binoculars/extension/news_link.py")
# text = p.read_text(encoding="utf-8")
# urls = re.findall(r"https?://rezonodwes\.com/\?p=\d+", text)
# cnt = Counter(urls)

# duplicates = {u: c for u, c in cnt.items() if c > 1}
# total_items = len(urls)
# unique_items = len(cnt)
# total_duplicates = sum(c - 1 for c in cnt.values() if c > 1)

# print(f"Total items found: {total_items}")
# print(f"Unique items: {unique_items}")
# print(f"Total duplicate entries (count of extra occurrences): {total_duplicates}")
# if duplicates:
#     print("\nDuplicate URLs and their counts:")
#     for u, c in sorted(duplicates.items(), key=lambda x: -x[1]):
#         print(f"{u}  ->  {c} times")
# else:
#     print("No duplicates found.")


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