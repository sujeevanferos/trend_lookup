import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# ----------------------------
# Helper Function for RSS Feeds
# ----------------------------
def parse_rss(url, source_name):
    headlines = []
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")

        for item in items:
            headlines.append({
                "title": item.title.text if item.title else None,
                "link": item.link.text if item.link else None,
                "published": item.pubDate.text if item.pubDate else None,
                "source": source_name
            })
    except:
        pass
    return headlines

# ----------------------------
# Helper Function for HTML Pages
# ----------------------------
def parse_html(url, selector, source_name):
    headlines = []
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select(selector)

        for item in items:
            title = item.text.strip()
            link = item.get("href")
            if link and not link.startswith("http"):
                link = url + "/" + link

            headlines.append({
                "title": title,
                "link": link,
                "published": str(datetime.now()),
                "source": source_name
            })
    except:
        pass
    return headlines

# ----------------------------
# Government Sources
# ----------------------------

sources = {
    "Government Press Releases": {
        "type": "rss",
        "url": "https://www.news.lk/news?format=feed&type=rss",
    },
    "Cabinet Decisions": {
        "type": "rss",
        "url": "https://www.news.lk/cabinet-decisions?format=feed&type=rss",
    },
    "DMC Alerts": {
        "type": "html",
        "url": "http://www.dmc.gov.lk/index.php?option=com_content&view=featured",
        "selector": ".contentpaneopen a"
    },
    "Met Department Alerts": {
        "type": "html",
        "url": "https://meteo.gov.lk/",
        "selector": ".all-news a"
    },
    "Central Bank Press Releases": {
        "type": "html",
        "url": "https://www.cbsl.gov.lk/en/press",
        "selector": ".views-row .views-field-title a"
    },
    "Treasury Press Releases": {
        "type": "html",
        "url": "https://www.treasury.gov.lk/web/treasury/press-releases",
        "selector": ".item-title a"
    },
    "Department of Government Information": {
        "type": "html",
        "url": "https://www.dgi.gov.lk/news",
        "selector": ".item-title a"
    },
    "Parliament News": {
        "type": "html",
        "url": "https://www.parliament.lk/en/news/",
        "selector": ".news-item a"
    },
    "Police Media Releases": {
        "type": "html",
        "url": "https://www.police.lk/index.php/news",
        "selector": ".item-title a"
    },
    "Health Ministry News": {
        "type": "html",
        "url": "http://www.health.gov.lk/",
        "selector": "a"
    },
    "Inland Revenue Department Notices": {
        "type": "html",
        "url": "https://www.ird.gov.lk/en/Pages/News.aspx",
        "selector": ".ms-rtestate-field a"
    }
}

# ----------------------------
# Extract All Government News
# ----------------------------

all_government_news = []

for name, src in sources.items():
    print(f"Extracting: {name}")

    if src["type"] == "rss":
        all_government_news.extend(parse_rss(src["url"], name))

    elif src["type"] == "html":
        all_government_news.extend(
            parse_html(src["url"], src["selector"], name)
        )

# ----------------------------
# Export JSON
# ----------------------------

with open("../../jsons/government_news.json", "w", encoding="utf-8") as f:
    json.dump(all_government_news, f, indent=4, ensure_ascii=False)

print("✔ Government news extraction completed!")
print(f"✔ Total items collected: {len(all_government_news)}")
print("✔ Output saved to government_news.json")

