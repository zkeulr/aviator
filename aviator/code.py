# pyright: ignore[reportShadowedImports]

import adsb
import display
import network
import time
import weather
import rtc


# We can get this from the network,
# doesn't need to be manually set
PURDUE_LOCATION = {"lat": 40.4237, "lon": 86.9212}
# Logo must fit within 32x16 pixels
LOGO = """
Aviator
"""

display.display(LOGO, 1, 1)

is_connected = network.connect()
if (is_connected):
    network.init_ntp()
    t = network.ntp.datetime
    rtc.RTC().datetime = (t[0], t[1], t[2], t[6], t[3], t[4], t[5], 0)



while True:
    try:
        flights = adsb.fetch_flights(PURDUE_LOCATION["lat"], PURDUE_LOCATION["lon"])
        current_weather = weather.fetch_weather(PURDUE_LOCATION["lat"], PURDUE_LOCATION["lon"])

        # current_time = time.localtime()
        # print("time:", current_time)
        # time_str = f"{current_time[3]}: {current_time[4]}"

        current_time = rtc.RTC().datetime
        print("time:", current_time)
        time_str = f"{current_time[3]}: {current_time[4]}"

        display.clear()
        display.display(time_str, 1, 5)
        display.display(str(flights), 1, 16)
        display.display(str(current_weather['temperature']), 1, 27)

        time.sleep(15)
    except Exception as e:
        print({time.time(): e})
