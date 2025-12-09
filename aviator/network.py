import wifi
import os
import socketpool
import ssl
import adafruit_requests
import adafruit_ntp
import rtc
import time

radio = wifi.radio
pool = socketpool.SocketPool(wifi.radio)
ssl_context = ssl.create_default_context()
requests = adafruit_requests.Session(pool, ssl_context)
ntp = None

def get_tz_offset():
    """
    Returns timezone UTC offset in seconds based on public IP.
    Example return: -18000 (for UTC-5)
    Returns None on failure.
    """
    try:
        url = "https://ipapi.co/json/"
        response = requests.get(url)
        if response.status_code != 200:
            print("Failed timezone lookup:", response.status_code)
            return None
        
        data = response.json()
        response.close()

        offset_hours = data.get("utc_offset")  # Format like "+0100" or "-0500"
        if not offset_hours:
            return None

        # Convert "+0530" → hours + minutes
        sign = -1 if offset_hours.startswith("-") else 1
        hours = int(offset_hours[1:3])
        minutes = int(offset_hours[3:5])
        total_seconds = sign * (hours * 3600 + minutes * 60)

        return total_seconds

    except Exception as e:
        print("Error getting timezone offset:", e)
        return None

def init_ntp(tz_offset=None):
    global ntp
    """Initialize the adafruit_ntp.NTP object after WiFi is connected."""

    try:
        if tz_offset is None:
            if os.getenv("CIRCUITPY_TZ_OFFSET"):
                tz_offset = int(os.getenv("CIRCUITPY_TZ_OFFSET"))
                print("tz_offset:", tz_offset)
            else:
                try:
                    tz_offset = get_tz_offset()
                except Exception as e:
                    print(e)
                    tz_offset = 0

            ntp = adafruit_ntp.NTP(pool, tz_offset=tz_offset, cache_seconds=3600)
            utc_time_struct = ntp.datetime
            utc_timestamp = time.mktime(utc_time_struct)
            local_timestamp = utc_timestamp + tz_offset
            local_time_struct = time.localtime(local_timestamp)
            rtc.RTC().datetime = local_time_struct

    except Exception as e:
        print(e)

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
    
def get_lat_lon():
    try:
        url = "https://ipapi.co/json/"
        response = requests.get(url)
        if response.status_code != 200:
            print("Failed to lookup location:", response.status_code)
            return None, None
        
        data = response.json()
        response.close()

        lat = data.get("latitude")
        lon = data.get("longitude")

        if lat is not None and lon is not None:
            return float(lat), float(lon)
        return None, None

    except Exception as e:
        print("Error getting lat/lon:", e)
        return None, None

    
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
