import wifi
import os
import socketpool
import ssl
import adafruit_requests
import adafruit_ntp
import rtc

radio = wifi.radio
pool = socketpool.SocketPool(wifi.radio)
ssl_context = ssl.create_default_context()
requests = adafruit_requests.Session(pool, ssl_context)
ntp = None

def get_tz_offset():
    resp = requests.get("http://worldtimeapi.org/api/ip")
    data = resp.json()
    # "+HH:MM" or "-HH:MM"
    s = data["utc_offset"]
    sign = 1 if s[0] == "+" else -1
    hours = int(s[1:3])
    minutes = int(s[4:6]) if len(s) >= 6 else 0
    return sign * (hours * 3600 + minutes * 60)

def init_ntp(tz_offset=None):
    global ntp
    """Initialize the adafruit_ntp.NTP object after WiFi is connected."""
    if tz_offset is None:
        try:
            tz_offset = get_tz_offset()
        except Exception as e:
            print(e)
            tz_offset = 0

    ntp = adafruit_ntp.NTP(pool, tz_offset=tz_offset, cache_seconds=3600)
    return ntp

def connect(ssid=None, password=None) -> bool: 
    if not ssid:
        ssid = os.getenv("CIRCUITPY_WIFI_SSID")
    if not password:
        password = os.getenv("CIRCUITPY_WIFI_PASSWORD")
    
    try:
        radio.connect(ssid, password)
        init_ntp()
        return True
    except Exception as e:
        print(e)
        return False
    
def is_connected(host="1.1.1.1", port=53, timeout=3) -> bool:
    """
    Return True if the device can reach the given host:port (default Cloudflare DNS).
    Uses a short TCP connect to verify internet access.
    """
    try:
        # quick check if WiFi has an IP assigned
        if not getattr(radio, "ipv4_address", None):
            return False
        s = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False
