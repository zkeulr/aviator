# pyright: ignore[reportShadowedImports]

import adsb
import display
import network
import time
import weather

PURDUE_LOCATION = {"lat": 40.4237, "lon": 86.9212}
LOGO = """
..%%%%...%%..%%..%%%%%%...%%%%...%%%%%%...%%%%...%%%%%..
.%%..%%..%%..%%....%%....%%..%%....%%....%%..%%..%%..%%.
.%%%%%%..%%..%%....%%....%%%%%%....%%....%%..%%..%%%%%..
.%%..%%...%%%%.....%%....%%..%%....%%....%%..%%..%%..%%.
.%%..%%....%%....%%%%%%..%%..%%....%%.....%%%%...%%..%%.
........................................................
"""

json_errors = {}
is_connected = False


display.display(LOGO)
is_connected = network.connect()
print(is_connected)



while True:
    try:
        flights = adsb.fetch_flights(PURDUE_LOCATION["lat"], PURDUE_LOCATION["lon"])
        current_weather = weather.fetch_weather(PURDUE_LOCATION["lat"], PURDUE_LOCATION["lon"])

        now = time.localtime()

        display.display("Date: {}/{}/{}".format(now[1], now[2], now[0]) + str(flights) + str(current_weather['temperature']))
        print(str(flights) + str(current_weather['temperature']))
        time.sleep(10)
    except Exception as e:
        json_errors.update({time.time(): e})
        print(json_errors)

