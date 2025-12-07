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
FETCH_INTERVAL = 60.0
TICK = 0.05

flights = [{}]
current_weather = {}
display.display("AVIATOR")
is_connected=False
time_label = None
flights_label = None
weather_label = None
last_fetch = -FETCH_INTERVAL

try:
    network.connect()
except:
    pass

def temp_to_color(temp_c: float) -> int:
    """
    Map temperature to a color.
    - Cold (<0°C): Blue
    - Cool (0-15°C): Cyan
    - Warm (16-25°C): Yellow
    - Hot (>25°C): Red
    """
    if temp_c is None:
        return 0xFFFFFF  # default white if no temp
    if temp_c < 0:
        return 0x0000FF  # Blue
    elif temp_c <= 15:
        return 0x00FFFF  # Cyan
    elif temp_c <= 25:
        return 0xFFFF00  # Yellow
    else:
        return 0xFF0000  # Red


while True:
    now = time.monotonic()

    if now - last_fetch >= FETCH_INTERVAL:
        last_fetch = now
        try:
            if network.is_connected() or network.connect():
                flights = adsb.fetch_flights(PURDUE_LOCATION["lat"], PURDUE_LOCATION["lon"])
                current_weather = weather.fetch_weather(PURDUE_LOCATION["lat"], PURDUE_LOCATION["lon"])
        except Exception as e:
            print("fetch error:", e)

        display.clear()
        time_label = display.display("", 1, 5)

        flights_text = str(flights)
        flights_label = display.display(flights_text, 1, 16)

        temp = current_weather.get("temperature")
        temp_color = temp_to_color(temp)
        weather_label = display.display((str(temp) + "C") if temp else "No weather", 1, 27, color=temp_color)

    try:
        tm = time.localtime()
        time_str = f"{tm[1]}/{tm[2]} {tm[3]:02d}:{tm[4]:02d}"
        if time_label is None:
            time_label = display.display(time_str, 1, 5)
        else:
            time_label.text = time_str
    except Exception:
        pass

    try:
        if flights_label is not None:
            display.scroll_step(flights_label)

    except Exception:
        pass

    time.sleep(TICK)
