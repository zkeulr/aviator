import wifi
import os
import ipaddress
import socketpool
import ssl
import adafruit_requests

radio = wifi.radio

def connect(ssid=None, password=None):
    if not ssid:
        ssid = os.getenv("CIRCUITPY_WIFI_SSID")
    if not password:
        password = os.getenv("CIRCUITPY_WIFI_PASSWORD")
        
    radio.connect(ssid, password)


def test_connection():
    connect()

    print(f"Connected to {os.getenv('CIRCUITPY_WIFI_SSID')}")
    print(f"My IP address: {wifi.radio.ipv4_address}")

    ping_ip = ipaddress.IPv4Address("8.8.8.8")
    ping = wifi.radio.ping(ip=ping_ip)

    if ping is None:
        print("Could not ping 'google.com'")
        return False
    
    print(f"Pinging 'google.com' took: {ping * 1000} ms")
    return True

def test_requests():
    connect()

    # Create socket pool and SSL context using built-in modules
    pool = socketpool.SocketPool(wifi.radio)
    ssl_context = ssl.create_default_context()

    # Create the requests session
    requests = adafruit_requests.Session(pool, ssl_context)

    # Perform the test request
    response = requests.get("http://wifitest.adafruit.com/testwifi/index.html")
    print("Response:", response.text)
    response.close()