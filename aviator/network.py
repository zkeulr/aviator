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

def init_ntp(tz_offset=None):
    global ntp
    """Initialize the adafruit_ntp.NTP object after WiFi is connected."""

    try:
        if tz_offset is None:
            if os.getenv("CIRCUITPY_TZ_OFFSET"):
                tz_offset = int(os.getenv("CIRCUITPY_TZ_OFFSET"))
                print("tz_offset:", tz_offset)
            else:
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
        init_ntp() # this line causes it to hang indefinitely if, for instance, worldtimeapi can't be reached
        # if we never initialize network time, the time never displays
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
