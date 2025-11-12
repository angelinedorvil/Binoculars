import requests
from bs4 import BeautifulSoup
import json
import datetime
from urllib.parse import urlparse
from news_link import news_links  # Importing the list of news links
from essays_link import essays_link  # Importing the list of essay links
from blogs_link import blogs_link  # Importing the list of blog links

def extract_html_text(url):
    """Try to scrape HTML page and extract full text (title + body) and description."""
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "html.parser")

        # ---- TITLE FALLBACK LOGIC ----
        title = None

        # 1. <title>
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        # 2. <h1>
        if not title:
            h1 = soup.find("h1")
            if h1:
                title = h1.get_text(strip=True)

        # 3. First 10–15 words of article text
        article_tags = soup.find_all(["p", "article"])
        raw_text = " ".join(
            [t.get_text(" ", strip=True) for t in article_tags]
        )
        if not title and raw_text:
            title = " ".join(raw_text.split()[:12]) + "..."

        # ---- DESCRIPTION ----
        description = None
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            description = meta_desc["content"].strip()
        else:
            og_desc = soup.find("meta", property="og:description")
            if og_desc and og_desc.get("content"):
                description = og_desc["content"].strip()

        # ---- TEXT ----
        if raw_text.strip() == "":
            return None  # signals "fallback to PDF"

        # COMBINE TITLE AND TEXT INTO ONE TEXT BLOCK
        if title:
            combined_text = f"{title}\n\n{raw_text}"
        else:
            combined_text = raw_text

        parsed = urlparse(url)
        return {
            "text": combined_text,
            "description": description,
            "domain": parsed.netloc,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "url": url,
            "image_url": None  # Optional – CC-News doesn't always have it
        }

    except Exception as e:
        print("extract_html_text error:", e)
        return None

def extract_multiple(url):
    """
    Extract multiple poems from a Potomitan page that contains several poems.
    Returns a list of dicts with only:
        - text  (title + poem body)
        - description (always None here)
    """

    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return []

        soup = BeautifulSoup(r.text, "html.parser")

        # Classes that act as poem titles
        TITLE_CLASSES = {"titlepage2r", "titlepage2b", "textemanuelg", "textemanuel"}

        poems = []
        current_title = None
        current_lines = []

        def save_current():
            """Save one complete poem entry."""
            if current_title and current_lines:
                poem_body = "\n".join(current_lines).strip()

                # ✅ Combine title + poem into the final text block
                combined_text = f"{current_title.strip()}\n\n{poem_body}"
                parsed = urlparse(url)
                poems.append({
                    "text": combined_text,
                    "description": None,
                    "domain": parsed.netloc,
                    "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "url": url,
                    "image_url": None  # Optional – CC-News doesn't always have it

                })

        # Scan ALL tags in order — not only <p>
        for tag in soup.find_all(True):

            # ---- Detect any poem title fragments inside this tag ----
            title_fragments = []

            # Look for <span class="titlepage2*">
            for span in tag.find_all("span", class_=lambda c: c in TITLE_CLASSES if c else False):
                text = span.get_text(" ", strip=True)
                if text:
                    title_fragments.append(text)

            # Also detect a title if the tag itself has title classes
            tag_classes = set(tag.get("class", []))
            if tag_classes & TITLE_CLASSES:
                text = tag.get_text(" ", strip=True)
                if text:
                    title_fragments.append(text)

            # ---- If this tag contains a title, start a new poem ----
            if title_fragments:
                save_current()  # store previous poem
                current_title = " ".join(title_fragments)
                current_lines = []
                continue

            # ---- Otherwise, collect text as poem content ----
            if current_title:
                text = tag.get_text(" ", strip=True)
                if text:
                    current_lines.append(text)

        # Save the last poem
        save_current()

        return poems

    except Exception as e:
        print("Error in extract_multiple:", e)
        return []


# ----------------
# Main execution
# ----------------
news_urls = news_links  # Using the imported list of news links
essay_urls = essays_link  # Using the imported dictionary of essay links
blog_urls = blogs_link  # Using the imported dictionary of blog links
with open("extension\_blogs.jsonl", "a", encoding="utf-8") as f:
    for url in blog_urls:
        if blog_urls[url] == "multiple":
            results = extract_multiple(url)
            for result in results:
                # check if url is already in cc_news.jsonl
                if result["text"] in open("extension\_blogs.jsonl", "r", encoding="utf-8").read():
                    print(f"text already exists in blogs.jsonl, skipping: {result["text"][:10]}...")
                    continue
                else:
                    # append to cc_news.jsonl
                    f.write(json.dumps(result, ensure_ascii=False) + "\n")
            print(f"Extracted {len(results)} blog from {url}")
            continue
    
        result = extract_html_text(url)
        # check if url is already in cc_news.jsonl
        if url in open("extension\_blogs.jsonl", "r", encoding="utf-8").read():
            print(f"URL already exists in blogs.jsonl, skipping: {url}")
            continue
        else:
            # append to cc_news.jsonl
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
