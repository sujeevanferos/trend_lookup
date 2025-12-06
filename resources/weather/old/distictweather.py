import requests
import feedparser
import time

# ----------------------------------------------------
# CONFIG
# ----------------------------------------------------
API_KEY = "58026a0357fd52d79e21b62df67b19fe"  # Replace with your OpenWeather free API key
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Coordinates for Sri Lankan districts (approximate center points)
DISTRICTS = {
    "Colombo": (6.9271, 79.8612),
    "Gampaha": (7.0897, 80.0074),
    "Kalutara": (6.5854, 79.9607),
    "Kandy": (7.2906, 80.6337),
    "Matale": (7.4650, 80.6234),
    "Nuwara Eliya": (6.9497, 80.7891),
    "Galle": (6.0535, 80.2210),
    "Matara": (5.9549, 80.5549),
    "Hambantota": (6.1246, 81.1185),
    "Jaffna": (9.6615, 80.0255),
    "Kilinochchi": (9.3803, 80.3769),
    "Mannar": (8.9800, 79.9047),
    "Vavuniya": (8.7482, 80.4971),
    "Mullaitivu": (9.2671, 80.8140),
    "Batticaloa": (7.7300, 81.7000),
    "Ampara": (7.3000, 81.6667),
    "Trincomalee": (8.5710, 81.2335),
    "Kurunegala": (7.4863, 80.3620),
    "Puttalam": (8.0400, 79.8400),
    "Anuradhapura": (8.3114, 80.4037),
    "Polonnaruwa": (7.9403, 81.0188),
    "Badulla": (6.9897, 81.0550),
    "Monaragala": (6.8727, 81.3485),
    "Ratnapura": (6.7056, 80.3847),
    "Kegalle": (7.2500, 80.3500)
}

# ----------------------------------------------------
# FUNCTIONS
# ----------------------------------------------------

def get_weather_for_district(name, lat, lon):
    """Fetch weather data from OpenWeather for given coordinates."""
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"
    }
    try:
        res = requests.get(BASE_URL, params=params, timeout=10)
        data = res.json()

        weather = data.get("weather", [{}])[0].get("description", "Unknown")
        temp = data.get("main", {}).get("temp", None)
        humidity = data.get("main", {}).get("humidity", None)
        wind = data.get("wind", {}).get("speed", None)
        alerts = data.get("alerts", [])

        return {
            "district": name,
            "weather": weather,
            "temperature": temp,
            "humidity": humidity,
            "wind_speed": wind,
            "alerts": alerts
        }

    except Exception as e:
        return {"district": name, "error": str(e)}


def get_government_disaster_alerts():
    """Fetch Sri Lanka Disaster Management Centre RSS feed."""
    RSS_URL = "http://www.dmc.gov.lk/index.php?format=feed&type=rss"
    try:
        feed = feedparser.parse(RSS_URL)
        alerts = []
        for entry in feed.entries:
            alerts.append({
                "title": entry.title,
                "description": entry.description,
                "published": entry.published
            })
        return alerts
    except Exception as e:
        return [{"error": str(e)}]


# ----------------------------------------------------
# MAIN DATA COLLECTION
# ----------------------------------------------------

if __name__ == "__main__":
    print("Fetching Sri Lanka district-wise weather...\n")
    results = []

    for district, (lat, lon) in DISTRICTS.items():
        print(f"Getting data for {district}...")
        info = get_weather_for_district(district, lat, lon)
        results.append(info)
        time.sleep(1)  # Respect API rate limits (free tier)

    print("\nFetching Government Disaster Alerts...\n")
    gov_alerts = get_government_disaster_alerts()

    # ----------------------------------------------------
    # OUTPUT SECTION
    # ----------------------------------------------------
    print("\n================ WEATHER REPORT ================\n")
    for r in results:
        if "error" in r:
            print(f"[{r['district']}] ERROR: {r['error']}")
            continue

        print(f"--- {r['district']} ---")
        print(f"Weather: {r['weather']}")
        print(f"Temperature: {r['temperature']}°C")
        print(f"Humidity: {r['humidity']}%")
        print(f"Wind Speed: {r['wind_speed']} m/s")

        if r["alerts"]:
            print("⚠️ Weather Alerts:")
            for a in r["alerts"]:
                print(f" - {a.get('event', 'N/A')}: {a.get('description', '')}")
        print()

    print("\n================ GOVERNMENT WARNINGS ================\n")
    if not gov_alerts:
        print("No government alerts found.")
    else:
        for a in gov_alerts:
            print(f"⚠️ {a.get('title', '')}")
            print(a.get("description", ""))
            print(f"Published: {a.get('published', '')}\n")

