from network import requests

WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude={lat}&longitude={lon}"
    "&current_weather=true"
    "&hourly=snowfall,rain,cloud_cover,"
    "temperature_850hPa,temperature_700hPa,temperature_500hPa,temperature_300hPa,temperature_250hPa,"
    "windspeed_850hPa,windspeed_700hPa,windspeed_500hPa,windspeed_300hPa,windspeed_250hPa,"
    "winddirection_850hPa,winddirection_700hPa,winddirection_500hPa,winddirection_300hPa,winddirection_250hPa"
)

# Altitude → Pressure Level lookup
ALT_LEVELS = [
    (7500,  "850hPa"),
    (15000, "700hPa"),
    (25000, "500hPa"),
    (32000, "300hPa"),
    (99999, "250hPa")
]

def pressure_for_alt(alt_ft):
    for limit, level in ALT_LEVELS:
        if alt_ft < limit:
            return level
    return "850hPa"

def fetch_weather(lat, lon, altitude_ft=None):
    url = WEATHER_URL.format(lat=lat, lon=lon)
    print("[weather] Fetching:", url)

    try:
        resp = requests.get(url)
        if resp.status_code != 200:
            print("[weather] HTTP error:", resp.status_code)
            return None

        data = resp.json()
        current = data.get("current_weather", {})
        hourly = data.get("hourly", {})

        # Find the current index in hourly data
        times = hourly.get("time", [])
        idx = times.index(current["time"]) if current.get("time") in times else 0

        # Build combined surface response
        result = {
            "time": current.get("time"),
            "surface_temp": current.get("temperature"),
            "surface_windspeed": current.get("windspeed"),
            "surface_winddirection": current.get("winddirection"),
            "surface_weathercode": current.get("weathercode"),
            "rain": hourly.get("rain", [None])[idx],
            "snowfall": hourly.get("snowfall", [None])[idx],
            "cloud_cover": hourly.get("cloud_cover", [None])[idx]
        }

        # Add altitude weather if requested
        if altitude_ft is not None:
            level = pressure_for_alt(altitude_ft)
            result.update({
                "altitude_ft": altitude_ft,
                "pressure_level": level,
                "alt_temp": hourly.get(f"temperature_{level}", [None])[idx],
                "alt_windspeed": hourly.get(f"windspeed_{level}", [None])[idx],
                "alt_winddirection": hourly.get(f"winddirection_{level}", [None])[idx]
            })

        return result

    except Exception as e:
        print("[weather] Exception:", e)
        return None
