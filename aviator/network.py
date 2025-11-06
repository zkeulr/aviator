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
ntp = adafruit_ntp.NTP(pool, tz_offset=os.getenv("TZ_OFFSET"), cache_seconds=3600)

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
    
