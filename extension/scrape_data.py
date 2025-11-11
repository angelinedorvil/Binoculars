import requests
from bs4 import BeautifulSoup
import json
import pdfkit
import PyPDF2
import tempfile
import datetime
from urllib.parse import urlparse
from news_link import news_links  # Importing the list of news links
from essays_link import essays_link  # Importing the list of essay links

def extract_html_text(url):
    """Try to scrape HTML page and extract title, text, description."""
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
        raw_text = " ".join([t.get_text(" ", strip=True) for t in article_tags])
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
        # raw_text already captured above
        if raw_text.strip() == "":
            return None  # signals "fallback to PDF"

        return {
            "title": title,
            "text": raw_text,
            "description": description
        }
    except:
        return None


def extract_pdf_text(url):
    """Fallback: convert webpage to PDF then extract text."""
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_pdf:
            pdfkit.from_url(url, tmp_pdf.name)

            reader = PyPDF2.PdfReader(tmp_pdf.name)

            pdf_text = ""
            for page in reader.pages:
                pdf_text += page.extract_text() + "\n"

        # Title fallback for PDF
        words = pdf_text.split()
        title_fallback = " ".join(words[:12]) + "..." if len(words) > 0 else None

        return {
            "title": title_fallback,
            "text": pdf_text,
            "description": None
        }
    except:
        return None


def scrape_to_json(url):
    """Main pipeline matching CC-News structure."""
    data = extract_html_text(url)

    # If HTML extraction failed or empty → fallback to PDF
    if not data:
        print("HTML empty → falling back to PDF extraction…")
        data = extract_pdf_text(url)

    if not data:
        return None  # fully failed

    parsed = urlparse(url)

    return {
        "title": data["title"],
        "text": data["text"],
        "description": data["description"],
        "domain": parsed.netloc,
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": url,
        "image_url": None  # Optional – CC-News doesn't always have it
    }


# ----------------
# Main execution
# ----------------
news_urls = news_links  # Using the imported list of news links
essay_urls = essays_link  # Using the imported list of essay links
with open("extension\essays.jsonl", "a", encoding="utf-8") as f:
    for url in essay_urls:
        result = scrape_to_json(url)
        # check if url is already in cc_news.jsonl
        if url in open("extension\essays.jsonl", "r", encoding="utf-8").read():
            print(f"URL already exists in essays.jsonl, skipping: {url}")
            continue
        else:
            # append to cc_news.jsonl
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
