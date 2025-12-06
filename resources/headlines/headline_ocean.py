import requests
import feedparser
import json
from datetime import datetime
import yt_key

# ----------------------------------------------
# CONFIG
# ----------------------------------------------

OUTPUT_FILE = "../../jsons/sri_lanka_news.json"
YOUTUBE_API_KEY = yt_key.YOUTUBE  # free quota

# RSS sources (Sri Lanka)
RSS_FEEDS = [
    "https://www.adaderana.lk/rss/latest_news",
    "https://www.hirunews.lk/rss/english.xml",
    "https://colombogazette.com/feed/",
    "https://economynext.com/feed/",
    "https://www.newsfirst.lk/feed/",
    "https://www.dailynews.lk/feed/",
]

# Google News RSS for Sri Lanka
GOOGLE_NEWS_RSS = [
    "https://news.google.com/rss/search?q=Sri+Lanka&hl=en&gl=LK&ceid=LK:en",
    "https://news.google.com/rss/search?q=Sri+Lanka+economy&hl=en&gl=LK&ceid=LK:en",
    "https://news.google.com/rss/search?q=Sri+Lanka+government&hl=en&gl=LK&ceid=LK:en",
]

# YouTube Sri Lankan news channels
YOUTUBE_CHANNELS = [
    "UCNwz7hM0USJgd59jSPTcX5Q",  # Ada Derana
    "UC0hHx5j2jQD1nZ4YslcIFPA",  # Hiru News
    "UC7wfilQIdG6m4aJRZ3t0uCQ",  # NewsFirst
    "UCm6VPcWn3U-IvfQeSeQk5Ww",  # Sirasa TV
]

# ----------------------------------------------
# 1. RSS PARSER
# ----------------------------------------------
def scrape_rss():
    print("[+] Fetching RSS feeds...")
    all_news = []

    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                all_news.append({
                    "source": "rss",
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.get("published", None),
                })
        except Exception as e:
            print("RSS error:", e)
    return all_news


# ----------------------------------------------
# 2. GOOGLE NEWS RSS
# ----------------------------------------------
def scrape_google_news():
    print("[+] Fetching Google News...")
    data = []
    for url in GOOGLE_NEWS_RSS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                data.append({
                    "source": "google_news",
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.get("published", None),
                })
        except:
            pass
    return data


# ----------------------------------------------
# 3. YouTube News Headlines
# ----------------------------------------------
def scrape_youtube():
    print("[+] Fetching YouTube news...")
    results = []

    for channel_id in YOUTUBE_CHANNELS:
        url = (
            "https://www.googleapis.com/youtube/v3/search"
            f"?key={YOUTUBE_API_KEY}"
            f"&channelId={channel_id}"
            "&part=snippet&id"
            "&order=date"
            "&maxResults=50"
        )
        try:
            r = requests.get(url).json()

            if "items" in r:
                for item in r["items"]:
                    title = item["snippet"]["title"]
                    video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}" if "videoId" in item.get("id", {}) else None
                    
                    results.append({
                        "source": "youtube",
                        "title": title,
                        "link": video_url,
                        "published": item["snippet"]["publishedAt"]
                    })
        except:
            pass

    return results


# ----------------------------------------------
# 4. GDELT Global News Filter for Sri Lanka
# ----------------------------------------------
def scrape_gdelt():
    print("[+] Fetching GDELT data...")

    url = "http://api.gdeltproject.org/api/v2/doc/doc?query=Sri%20Lanka&mode=ArtList&format=json&maxrecords=250"
    try:
        data = requests.get(url).json()
        articles = data.get("articles", [])
        result = []

        for a in articles:
            result.append({
                "source": "gdelt",
                "title": a.get("title"),
                "link": a.get("url"),
                "published": a.get("seendate")
            })
        return result
    except:
        return []


# -----------------------------------------------------
# (REMOVED) REDDIT API — COMMENTED OUT
# -----------------------------------------------------

"""
# import praw

def scrape_reddit():
    print("[+] Fetching Reddit (DISABLED — Approval Required)")

    reddit = praw.Reddit(
        client_id="YOUR_ID",
        client_secret="YOUR_SECRET",
        user_agent="SLNewsCollector by u/YOURNAME"
    )

    subreddits = ["srilanka", "SriLankaNews", "SriLankaPolitics"]

    data = []
    for sub in subreddits:
        subreddit = reddit.subreddit(sub)
        for post in subreddit.hot(limit=100):
            data.append({
                "source": "reddit",
                "title": post.title,
                "link": f"https://reddit.com{post.permalink}",
                "published": datetime.utcfromtimestamp(post.created_utc).isoformat(),
            })
    return data
"""


# -----------------------------------------------------
# MASTER AGGREGATOR
# -----------------------------------------------------
def main():
    print("================================")
    print("   SRI LANKA NEWS SCRAPER")
    print("   (Reddit Removed)")
    print("================================")

    combined = []

    combined += scrape_rss()
    combined += scrape_google_news()
    combined += scrape_youtube()
    combined += scrape_gdelt()

    # Future:
    # combined += scrape_reddit()   # re-enable when approved

    print(f"\n[✓] Total collected: {len(combined)} headlines")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=4, ensure_ascii=False)

    print(f"[✓] Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

