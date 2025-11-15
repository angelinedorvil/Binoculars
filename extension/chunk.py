import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')  # prevent Unicode issues on Windows

FILES = {
    "extension/cc_news.jsonl": "extension/chunked_news.jsonl",
    "extension/essays.jsonl": "extension/chunked_essays.jsonl",
    "extension/_blogs.jsonl": "extension/chunked_blogs.jsonl"
}

CHUNK_SIZE = 4000
MIN_CHUNK_SIZE = 250   # merge threshold


def smart_chunk_text(text, size):
    chunks = []
    n = len(text)
    i = 0

    while i < n:
        # Tentative end index
        end = min(i + size, n)

        # If we are in the middle of a word, scan forward until whitespace
        while end < n and (text[end].isalnum() or text[end] in ("'", "-")):
            end += 1

        # Now scan forward until we hit whitespace (true word boundary)
        while end < n and not text[end].isspace():
            end += 1

        chunks.append(text[i:end])
        i = end

        # Skip leading whitespace to keep chunks clean
        while i < n and text[i].isspace():
            i += 1

    return chunks


def merge_small_chunks(chunks, min_size=250):
    if len(chunks) <= 1:
        return chunks

    merged = []
    for chunk in chunks:
        if merged and len(chunk) < min_size:
            merged[-1] += " " + chunk
        else:
            merged.append(chunk)

    return merged


def process_file(in_path, out_path, chunk_size):
    with open(in_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(out_path, "w", encoding="utf-8") as out:
        for line in lines:
            entry = json.loads(line)
            text = entry.get("text", "")

            if len(text) <= chunk_size:
                entry["description"] = (entry.get("description") or "") + " | chunk 1 of 1"
                out.write(json.dumps(entry, ensure_ascii=False) + "\n")
                print(f"Text length {len(text)} within chunk size, skipping chunking for {entry.get('url', '')}.")
                continue

            # Split into chunks
            chunks = smart_chunk_text(text, chunk_size)

            # Merge small final chunks
            chunks = merge_small_chunks(chunks, MIN_CHUNK_SIZE)

            total = len(chunks)

            for i, chunk in enumerate(chunks, start=1):
                new_entry = entry.copy()
                new_entry["text"] = chunk
                new_entry["description"] = f"chunk {i} of {total}"
                out.write(json.dumps(new_entry, ensure_ascii=False) + "\n")

            print(f"Chunked text from {entry.get('url', '')} into {total} chunks.")

    print(f"Done. Saved chunked dataset -> {out_path}")


for in_file, out_file in FILES.items():
    process_file(in_file, out_file, CHUNK_SIZE)
