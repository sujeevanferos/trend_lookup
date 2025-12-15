
import requests
from bs4 import BeautifulSoup

url = "https://www.dmc.gov.lk/index.php?format=feed&type=rss"
try:
    resp = requests.get(url, timeout=10)
    print(f"Fetched {len(resp.text)} bytes")
    print(f"Content: {resp.text[:500]}")
    
    print("Trying html.parser...")
    soup = BeautifulSoup(resp.text, "html.parser")
    items = soup.find_all("item")
    print(f"Found {len(items)} items with html.parser")
    if items:
        print(f"First item title: {items[0].title.text}")
        
except Exception as e:
    print(f"Error: {e}")
