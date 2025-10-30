# pyright: ignore[reportShadowedImports]

# import adsb
import display
import network
import time
import os
# import weather

PURDUE_LOCATION = {"lat": 40.4237, "lon": 86.9212}

json_errors = {}
is_connected = False

is_connected = network.connect()
print(is_connected)

# DEBUG
network.test_connection()
network.test_requests()

while True:
    try:
        # flights = adsb.fetch_flights(PURDUE_LOCATION["lat"], PURDUE_LOCATION["lon"])
        # weather = weather.fetch_weather(PURDUE_LOCATION["lat"], PURDUE_LOCATION["lon"])
        # display.display(str(flights) + str(weather))
        time.sleep(1)
    except Exception as e:
        json_errors.update({time.time(): e})
        print(json_errors)

