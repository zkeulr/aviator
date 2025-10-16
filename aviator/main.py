# main.py - Integration of ADS-B, networking, display, etc.

# Currently, these tests are functional:
# test_adsb
# test_display
# test_fallback
# test_save_restore()

import time
import json

# ADS-B decoder module
import adsb

# Display module (HUB75 LED matrix)
from display import HUB75Display

# Weather and flight info modules
import weather
import flightinfo

# Network (MicroPython)
try:
    import network
except ImportError:
    network = None  # Running in CircuitPython environment instead of MicroPython

# Attempt to use urequests if available
try:
    import urequests as requests
except ImportError:
    import requests

WIFI_SSID = "David's iPhone (5)"  
# WIFI_USERNAME = "pulrich"
WIFI_PASS = "password"

# Initialize the LED matrix display with a pin mapping (set actual GPIO pins for your board)
DISPLAY_PINMAP = {
    "CLK": 0, "LAT": 1, "OE": 2,
    "R1": 3, "G1": 4, "B1": 5,
    "R2": 6, "G2": 7, "B2": 8,
    "A": 9, "B": 10, "C": 11
}
disp = HUB75Display(DISPLAY_PINMAP)

# -------------------------------------------------------------------
# Test functions to demonstrate functionality:

def test_network():
    """Attempt Wi-Fi connection and fetch Purdue homepage HTML."""
    if network is None:
        print("Network module not available.")
        return
    nic = network.WLAN(network.WLAN.IF_STA)
    nic.active(True)
    print("Connecting to Wi-Fi SSID:", WIFI_SSID)
    # MicroPython connect (note: enterprise auth may require different handling)
    try:
        nic.connect(WIFI_SSID, WIFI_PASS)  # WPA2-PSK; enterprise with username not natively supported
    except Exception as e:
        print("Wi-Fi connect error (ignoring enterprise credential):", e)
    # Wait up to 15 seconds for connection
    start = time.time()
    while not nic.isconnected() and time.time() - start < 15:
        time.sleep(1)
    if nic.isconnected():
        ip, subnet, gw, dns = nic.ifconfig()
        print("Connected. IP config:", (ip, subnet, gw, dns))
        try:
            r = requests.get("https://www.purdue.edu", timeout=5)
            print("Fetched Purdue homepage, HTTP status:", r.status_code)
            print("Content snippet:", r.text[:100])
        except Exception as e:
            print("HTTP fetch error:", e)
    else:
        print("Failed to connect to Wi-Fi within timeout.")

def test_adsb():
    """Run ADS-B decoder in simulation mode and print flight data."""
    adsb.set_mode("sim")
    flights = adsb.fetch_flights(40.0, -86.0)
    print("Simulated ADS-B flights near (40.0, -86.0):")
    for f in flights:
        print(f"  ICAO {f['icao']}: callsign={f.get('callsign')}, "
              f"alt={f.get('alt_ft')} ft, lat={f.get('lat'):.3f}, lon={f.get('lon'):.3f}, "
              f"heading={f.get('heading')}")
    # Reset mode to raw for other operations if needed
    adsb.set_mode("raw")

def test_weather():
    """Fetch and print current weather for a given location."""
    lat, lon = 40.0, -86.0
    print(f"Fetching weather for ({lat}, {lon}):")
    result = weather.fetch_weather(lat, lon)
    print("Weather data:", result)

def test_flightinfo():
    """Lookup sample flight info using OpenSky API."""
    callsign = "KLM1023"
    print(f"Looking up flight info for callsign {callsign}:")
    info = flightinfo.lookup_flight_opensky(callsign)
    print("Flight info:", info)

def test_display():
    """Draw sample text on the LED matrix to verify display output."""
    disp.clear()
    disp.draw_text(0, 0, "HELLO", [1, 1, 1])   # White color
    disp.draw_text(0, 8, "WORLD", [0, 1, 0])   # Green color
    disp.refresh()
    print("Displayed 'HELLO WORLD' on the LED matrix.")

def test_fallback():
    """Display fallback state (current time + 'NO SIGNAL') on the LED matrix."""
    disp.clear()
    t = time.localtime()
    time_str = "{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5])
    disp.draw_text(0, 0, time_str, [1, 1, 1])       # White time
    disp.draw_text(0, 8, "NO SIGNAL", [1, 0, 0])    # Red message
    disp.refresh()
    print(f"Displayed fallback mode: time {time_str} and NO SIGNAL.")

def test_save_restore():
    """Save current flight list to persistent storage and reload it."""
    flights = adsb.fetch_flights(40.0, -86.0)
    state = {'flights': flights}
    # Save to flash (state.json)
    with open('state.json', 'w') as f:
        json.dump(state, f)
    print(f"Saved {len(flights)} flights to state.json.")
    # Load back
    with open('state.json', 'r') as f:
        loaded = json.load(f)
    print("Loaded state, flights:", loaded.get('flights'))