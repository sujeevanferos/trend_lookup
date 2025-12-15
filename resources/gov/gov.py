import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

OUTPUT_DIR = "../../jsons"

GOV_SOURCES = [
    {
        "name": "Disaster Management Centre",
        "url": "https://www.dmc.gov.lk/index.php?format=feed&type=rss",
        "type": "rss"
    },
    {
        "name": "News.lk",
        "url": "https://www.news.lk/",
        "type": "html",
        "selector": "h3 a"   # news title links
    },
    {
        "name": "Department of Government Information (DGI)",
        "url": "https://www.dgi.gov.lk/",
        "type": "html",
        "selector": "h3 a"
    },
    {
        "name": "Central Bank",
        "url": "https://www.cbsl.gov.lk/en/news/what_s_new",
        "type": "html",
        "selector": ".view-content .views-row a"
    },
    {
        "name": "Treasury - Press Releases",
        "url": "https://www.treasury.gov.lk/web/press-releases",
        "type": "html",
        "selector": "a"
    }
]


def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def save_json(filename, data):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved JSON → {path}")


def extract_rss(source):
    print(f"[RSS] Fetching {source['name']}")

    try:
        resp = requests.get(source["url"], timeout=10)
        
        # Try to parse with XML parser first, then fallbacks
        soup = None
        try:
            soup = BeautifulSoup(resp.text, "xml")
        except Exception as e:
            print(f"Warning: XML parser failed ({e}), trying lxml...")
            try:
                soup = BeautifulSoup(resp.text, "lxml")
            except Exception as e2:
                print(f"Warning: lxml parser failed ({e2}), trying html.parser...")
                soup = BeautifulSoup(resp.text, "html.parser")

        items = []
        # Handle both case-sensitive (XML) and case-insensitive (HTML) tags
        # In XML parser, tags are preserved. In HTML parser, they might be lowercased.
        # We search for "item" which is standard RSS.
        found_items = soup.find_all("item")
        
        for item in found_items:
            # Helper to safely get text from a tag that might be missing
            def get_text(tag_name):
                t = item.find(tag_name)
                return t.text.strip() if t else None

            items.append({
                "title": get_text("title"),
                "url": get_text("link"),
                "summary": get_text("description") or "",
                "published": get_text("pubDate"),
                "source": source["name"],
                "fetched_at": datetime.utcnow().isoformat()
            })

        return items

    except Exception as e:
        print(f"RSS error {source['name']}: {e}")
        return []


def extract_html(source):
    print(f"[HTML] Fetching {source['name']}")

    try:
        resp = requests.get(source["url"], timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        items = []
        for tag in soup.select(source.get("selector", "a")):
            title = tag.text.strip()
            link = tag.get("href")

            if not title or not link:
                continue

            if link.startswith("/"):
                base = source["url"].rstrip("/")
                link = base + link

            items.append({
                "title": title,
                "url": link,
                "summary": "",
                "published": None,
                "source": source["name"],
                "fetched_at": datetime.utcnow().isoformat()
            })

        return items

    except Exception as e:
        print(f"HTML error {source['name']}: {e}")
        return []


def run_gov_collector():
    ensure_output_dir()

    all_data = []

    for source in GOV_SOURCES:
        if source["type"] == "rss":
            entries = extract_rss(source)
        else:
            entries = extract_html(source)

        all_data.extend(entries)

    save_json("government_news.json", all_data)


if __name__ == "__main__":
    run_gov_collector()

