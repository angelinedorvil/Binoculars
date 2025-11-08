import json
import time
import requests

INPUT_FILE = "extension/cc_news.jsonl"
OUTPUT_FILE = "extension/cc_news_bloom3b.jsonl"

HF_API_KEY = "YOUR_HF_KEY_HERE"

BLOOM3B_ENDPOINT = "https://api-inference.huggingface.co/models/bigscience/bloom-3b"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# -------------------------
# Call HF API for continuation
# -------------------------
def generate_continuation(text, max_new_tokens=200):
    payload = {
        "inputs": text,
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": 0.0,
            "do_sample": False
        }
    }

    response = requests.post(BLOOM3B_ENDPOINT, headers=HEADERS, json=payload)

    if response.status_code != 200:
        print("Error:", response.text)
        return None

    try:
        return response.json()[0]["generated_text"][len(text):].strip()
    except:
        return None


# -------------------------
# Main Loop
# -------------------------
seen_urls = set()
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                seen_urls.add(entry["url"])
            except:
                continue

with open(INPUT_FILE, "r", encoding="utf-8") as f_in, \
     open(OUTPUT_FILE, "a", encoding="utf-8") as f_out:

    for line in f_in:
        data = json.loads(line)

        # 1. Skip if already processed
        if data["url"] in seen_urls:
            continue

        text = data["text"]

        # 2. Generate continuation
        continuation = generate_continuation(text)

        if continuation is None or continuation.strip() == "":
            print("Skipping due to empty output:", data["url"])
            continue

        # 3. Insert into dictionary
        data["bloom3b_generated_text_wo_prompt"] = continuation

        # 4. Write to output
        f_out.write(json.dumps(data, ensure_ascii=False) + "\n")

        print(f"Processed {data['url']}")

        time.sleep(1)  # avoid rate limits
