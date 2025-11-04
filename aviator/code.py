# pyright: ignore[reportShadowedImports]

import adsb
import display
import network
import time
import weather

# We can get this from the network,
# doesn't need to be manually set
PURDUE_LOCATION = {"lat": 40.4237, "lon": 86.9212}
# Logo must fit within 32x16 pixels
LOGO = """
AVIATOR
"""

display.display(LOGO, 1, 1)

is_connected = network.connect()

while True:
    try:
        flights = adsb.fetch_flights(PURDUE_LOCATION["lat"], PURDUE_LOCATION["lon"])
        current_weather = weather.fetch_weather(PURDUE_LOCATION["lat"], PURDUE_LOCATION["lon"])

        current_time = ntp.datetime

        display.display(time.strftime("%Y-%m-%d %H:%M:%S", current_time) + str(flights) + str(current_weather['temperature']), 2, 16)
        print(str(flights) + str(current_weather['temperature']))
        time.sleep(10)
    except Exception as e:
        print({time.time(): e})
