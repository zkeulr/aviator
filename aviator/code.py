# pyright: ignore[reportShadowedImports]

import adsb
import display
import network
import time
import adafruit_ntp
import weather

# We can get this from the network,
# doesn't need to be manually set
PURDUE_LOCATION = {"lat": 40.4237, "lon": 86.9212}
# Logo must fit within 32x16 pixels
LOGO = """
AVIATOR
"""

display.display(LOGO)

is_connected = network.connect()

response = network.requests.get("http://worldtimeapi.org/api/ip")
data = response.json()
datetime_str = data["datetime"]
timezone = data["timezone"]

ntp = adafruit_ntp.NTP(pool, tz_offset=0, cache_seconds=3600)

# do this occasionally
if is_connected:
    try:
        ntptime.settime()
    except:
        pass


while True:
    try:
        flights = adsb.fetch_flights(PURDUE_LOCATION["lat"], PURDUE_LOCATION["lon"])
        current_weather = weather.fetch_weather(PURDUE_LOCATION["lat"], PURDUE_LOCATION["lon"])

        now = time.localtime()

        display.display("Date: {}/{}/{}".format(now[1], now[2], now[0]) + str(flights) + str(current_weather['temperature']), 2, 16)
        print(str(flights) + str(current_weather['temperature']))
        time.sleep(10)
    except Exception as e:
        json_errors.update({time.time(): e})
        print(json_errors)
