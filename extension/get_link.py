import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from essays_link import essays_link

def extract_creole_links(index_url, header_text="Créole"):
    """Return all links under the column labeled 'Créole' (Poèmes + Divers)."""

    r = requests.get(index_url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")

    all_links = []

    # Find ANY header whose cleaned text is exactly "Créole"
    headers = soup.find_all(lambda tag: tag.name in ("h2", "h3") 
                                         and tag.get_text(strip=True) == header_text)

    for header in headers:
        # 1. Find the <tr> containing the headers (Creole / English / French)
        header_row = header.find_parent("tr")
        if not header_row:
            continue

        # 2. Find the column index of this header within that row
        tds = header_row.find_all("td")
        try:
            col_index = tds.index(header.find_parent("td"))
        except ValueError:
            continue  # shouldn't happen, but safe

        # 3. Find the next <tr> that actually has the links
        content_row = header_row.find_next_sibling("tr")
        if not content_row:
            continue

        content_cells = content_row.find_all("td")
        if col_index >= len(content_cells):
            continue

        creole_td = content_cells[col_index]

        # 4. Extract all <a> tags in that column
        for a in creole_td.find_all("a", href=True):
            full_url = urljoin(index_url, a["href"])
            all_links.append(full_url)

    return all_links



index_page = "https://www.potomitan.info/ayiti/lafontan/index.php"

new_links = extract_creole_links(index_page)

# Dedupe while keeping order
updated = essays_link[:]
for link in new_links:
    if link not in updated:
        updated.append(link)

# Print so you can manually paste back into essays_link.py
print("\nUpdated essays_link list:\n")
print("essays_link = [")
for url in updated:
    print(f'    "{url}",')
print("]")
