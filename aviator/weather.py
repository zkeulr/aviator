"""
weather.py
Weather data layer for MicroPython (ESP32): fetches current weather for a given lat/lon using Open-Meteo API.

API: https://api.open-meteo.com/v1/forecast?latitude=LAT&longitude=LON&current_weather=true
No API key required.

Public API:
    fetch_weather(lat, lon)
"""

# Conditional import for MicroPython (urequests) or CPython (requests)
try:
    import urequests as requests  # MicroPython
except ImportError:
    import requests  # CPython fallback for desktop testing

SURFACE_URL = "https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
ALTITUDE_URL = "https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_850hPa,temperature_700hPa,temperature_500hPa,temperature_300hPa,temperature_250hPa,windspeed_850hPa,windspeed_700hPa,windspeed_500hPa,windspeed_300hPa,windspeed_250hPa,winddirection_850hPa,winddirection_700hPa,winddirection_500hPa,winddirection_300hPa,winddirection_250hPa"

def fetch_weather(lat, lon, altitude_ft=None):
    print("[weather] fetch_weather called with lat=", lat, "lon=", lon, "alt_ft=", altitude_ft)
    
    # Get surface weather
    surface_url = SURFACE_URL.format(lat=lat, lon=lon)
    print("[weather] Fetching surface:", surface_url)
    
    try:
        resp = requests.get(surface_url)
        print("[weather] Surface HTTP status:", resp.status_code)
        if resp.status_code != 200:
            print("[weather] Surface HTTP error:", resp.status_code)
            return None
            
        surface_data = resp.json()
        surface = surface_data.get("current_weather", {})
        print("[weather] surface weather:", surface)
        
        # If no altitude requested, return surface only
        if altitude_ft is None:
            return surface
            
        # Get altitude weather
        altitude_url = ALTITUDE_URL.format(lat=lat, lon=lon)
        print("[weather] Fetching altitude:", altitude_url)
        
        resp_alt = requests.get(altitude_url)
        print("[weather] Altitude HTTP status:", resp_alt.status_code)
        if resp_alt.status_code != 200:
            print("[weather] Altitude HTTP error - returning surface only")
            return surface
            
        altitude_data = resp_alt.json()
        hourly = altitude_data.get("hourly", {})
        
        # Map altitude to pressure level
        if altitude_ft < 7500:
            level = "850hPa"
            temp_key = "temperature_850hPa"
            wind_speed_key = "windspeed_850hPa" 
            wind_dir_key = "winddirection_850hPa"
        elif altitude_ft < 15000:
            level = "700hPa"
            temp_key = "temperature_700hPa"
            wind_speed_key = "windspeed_700hPa"
            wind_dir_key = "winddirection_700hPa"
        elif altitude_ft < 25000:
            level = "500hPa"
            temp_key = "temperature_500hPa"
            wind_speed_key = "windspeed_500hPa"
            wind_dir_key = "winddirection_500hPa"
        elif altitude_ft < 32000:
            level = "300hPa"
            temp_key = "temperature_300hPa"
            wind_speed_key = "windspeed_300hPa"
            wind_dir_key = "winddirection_300hPa"
        else:
            level = "250hPa"
            temp_key = "temperature_250hPa"
            wind_speed_key = "windspeed_250hPa"
            wind_dir_key = "winddirection_250hPa"
        
        # Extract current hour data (first entry)
        altitude_weather = {
            "temperature": hourly.get(temp_key, [None])[0],
            "windspeed": hourly.get(wind_speed_key, [None])[0], 
            "winddirection": hourly.get(wind_dir_key, [None])[0],
            "pressure_level": level,
            "altitude_ft": altitude_ft
        }
        
        print("[weather] altitude weather:", altitude_weather)
        
        return {
            "surface": surface,
            "altitude": altitude_weather
        }
        
    except Exception as e:
        print("[weather] Exception:", e)
        return None

# Test block - function is now defined BEFORE this runs
if __name__ == "__main__":
    # Test surface weather
    print("=== SURFACE WEATHER ===")
    result = fetch_weather(40.7128, -74.0060)
    print("Surface result:", result)
    
    # Test high altitude weather (30,000 ft)
    print("\n=== HIGH ALTITUDE WEATHER (30,000 ft) ===")
    result_alt = fetch_weather(40.7128, -74.0060, 30000)
    print("Altitude result:", result_alt)
