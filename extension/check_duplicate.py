import re
from collections import Counter
from pathlib import Path

# save as check_duplicates.py and run: python check_duplicates.py

p = Path(r"c:/Users/angel/NLP-project/Binoculars/extension/news_link.py")
text = p.read_text(encoding="utf-8")
urls = re.findall(r"https?://rezonodwes\.com/\?p=\d+", text)
cnt = Counter(urls)

duplicates = {u: c for u, c in cnt.items() if c > 1}
total_items = len(urls)
unique_items = len(cnt)
total_duplicates = sum(c - 1 for c in cnt.values() if c > 1)

print(f"Total items found: {total_items}")
print(f"Unique items: {unique_items}")
print(f"Total duplicate entries (count of extra occurrences): {total_duplicates}")
if duplicates:
    print("\nDuplicate URLs and their counts:")
    for u, c in sorted(duplicates.items(), key=lambda x: -x[1]):
        print(f"{u}  ->  {c} times")
else:
    print("No duplicates found.")
