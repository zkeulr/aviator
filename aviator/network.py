import wifi
import os
import socketpool
import ssl
import adafruit_requests
import adafruit_ntp

radio = wifi.radio
pool = socketpool.SocketPool(wifi.radio)
ssl_context = ssl.create_default_context()
requests = adafruit_requests.Session(pool, ssl_context)

def get_tz_offset():
    response = requests.get("http://worldtimeapi.org/api/ip")
    data = response.json()
    offset_str = data["raw_offset"]
    tz_offset = int(offset_str)
    return tz_offset

def init_ntp():
    """Initialize the adafruit_ntp.NTP object after WiFi is connected."""
    global ntp
    env = os.getenv("TZ_OFFSET")
    if env:
        try:
            tz_offset = int(env)
        except Exception:
            tz_offset = 0
    else:
        tz_offset = get_tz_offset()
    ntp = adafruit_ntp.NTP(pool, tz_offset=tz_offset, cache_seconds=3600)
    return ntp

def connect(ssid=None, password=None) -> bool: 
    if not ssid:
        ssid = os.getenv("CIRCUITPY_WIFI_SSID")
    if not password:
        password = os.getenv("CIRCUITPY_WIFI_PASSWORD")
    
    try:
        radio.connect(ssid, password)
        return True
    except Exception as e:
        print(e)
        return False