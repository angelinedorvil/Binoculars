import json
import datetime
from essays_titles import essays_titles

TEXT_FILE = "extension/essays2.txt"        # path to your text file
OUTPUT_FILE = "extension/essays.jsonl"  # where we append JSONL
TITLES = essays_titles

def load_existing_titles(path):
    """Prevent duplicates."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return {json.loads(line)["text"][:10] for line in f}
    except FileNotFoundError:
        return set()


def extract_poems(text, titles):
    poems = []
    n = len(titles)

    for i in range(n):
        title = titles[i]

        # Find start index of this poem
        start = text.find(title)
        if start == -1:
            print(f"[WARNING] Title not found in text: {title}")
            continue

        # Find start of next title OR end of file
        if i < n - 1:
            next_title = titles[i + 1]
            end = text.find(next_title, start + len(title))
            if end == -1:
                end = len(text)
        else:
            end = len(text)

        # Slice poem body
        poem_body = text[start + len(title):end].strip()

        # Clean up
        poem_body = poem_body.replace("\r", "").strip()

        combined_text = f"{title.strip()}\n\n{poem_body.strip()}"

        poems.append({
            "text": combined_text,
            "description": None,
            "domain": "poetry-site",
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "url": None,
            "image_url": None
        })

    return poems


# ---------------------------------------------------
# MAIN
# ---------------------------------------------------

# Load entire text file
with open(TEXT_FILE, "r", encoding="utf-8") as f:
    raw_text = f.read()

existing = load_existing_titles(OUTPUT_FILE)

poems = extract_poems(raw_text, TITLES)

with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
    for p in poems:
        if p["text"] in existing:
            print(f"Skipping duplicate: {p['text'][:10]}...")
            continue

        f.write(json.dumps(p, ensure_ascii=False) + "\n")
        existing.add(p["text"][:10])

print(f"Saved {len(poems)} poems.")
