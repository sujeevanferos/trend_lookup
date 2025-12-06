import requests
import time

API_KEY = "4c965b492403638103035076b8290158"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"

DISTRICTS = {
    "Colombo": (6.9271, 79.8612),
    "Kandy": (7.2906, 80.6337),
    "Galle": (6.0535, 80.2210),
    "Jaffna": (9.6615, 80.0255),
}

def get_weather_for_district(name, lat, lon):
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        res = requests.get(BASE_URL, params=params, timeout=10)
        data = res.json()

        # DEBUG: print errors from API
        if "cod" in data and data["cod"] != 200:
            print(f"\n❌ API returned error for {name}:")
            print(data)
            return {"district": name, "error": data.get("message", "Unknown API error")}

        weather_desc = data["weather"][0]["description"]

        return {
            "district": name,
            "weather": weather_desc,
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"]
        }

    except Exception as e:
        return {"district": name, "error": str(e)}


if __name__ == "__main__":
    print("Fetching Sri Lanka district-wise weather...\n")

    for district, (lat, lon) in DISTRICTS.items():
        print(f"Getting data for {district}...")
        result = get_weather_for_district(district, lat, lon)
        print(result)
        time.sleep(1)

