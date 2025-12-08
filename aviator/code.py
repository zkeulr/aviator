# pyright: ignore[reportShadowedImports]

# ISSUES: see comments
import adsb
import display
import network
import time
import weather

PURDUE_LOCATION = {"lat": 40.4237, "lon": -86.9212}
FETCH_INTERVAL = 10.0
TICK = 0.05

flights = [{}]
current_weather = {}
print("Displaying logo...")
display.display("AVIATOR", 12, 16)

time_label = None
flights_label = None
weather_label = None
last_fetch = -FETCH_INTERVAL

# will hang forever if network not present
try:
    print("Trying to connect to network...")
    if network.connect():
        print("Connected successfully")
    else:
        print("Not connected")
except Exception as e:
    print(e)
finally:
    display.clear()

def temp_to_color(temp_c: float) -> int:
    if temp_c is None:
        return 0xFFFFFF
    if temp_c < 0:
        return 0x0000FF
    elif temp_c <= 15:
        return 0x00FFFF
    elif temp_c <= 25:
        return 0xFFFF00
    else:
        return 0xFF0000

while True:
    now = time.monotonic()

    # Fetch new data only if interval has passed
    if now - last_fetch >= FETCH_INTERVAL:
        print("Fetching new data")
        last_fetch = now
        try:
            try:
                print("Testing network connectivity")
                connected = network.is_connected()
            except Exception as e:
                print("Error checking connection:", e)
                connected = False

            if connected:
                print("Network connected")
                print("Fetching flights")
                new_flights = adsb.fetch_flights(PURDUE_LOCATION["lat"], PURDUE_LOCATION["lon"])
                # this call freezes the display for a bit, which is noticeable only with scrolling
                print("Fetching weather")
                new_weather = weather.fetch_weather(PURDUE_LOCATION["lat"], PURDUE_LOCATION["lon"])

                # Only update if fetch succeeds
                print("Updating flights and weather")
                flights = new_flights
                current_weather = new_weather

                # Update flights display
                flights_text = "\n".join(
                    f"{f.get('callsign','---')[:6]} {f.get('altitude','?')}ft {f.get('speed','?')}kt"
                    for f in flights[:5]
                ) or "No flights"
                if flights_label is None:
                    flights_label = display.display(flights_text, 1, 16)
                else:
                    flights_label.text = flights_text

                # Update weather display
                temp = current_weather.get("temperature")
                temp_color = temp_to_color(temp)
                weather_text = f"{temp}C" if temp is not None else "No weather"
                if weather_label is None:
                    weather_label = display.display(weather_text, 2, 27, color=temp_color)
                else:
                    weather_label.text = weather_text
                    weather_label.color = temp_color
            else:
                print("Not connected to the network")
                if flights_label is None:
                    flights_label = display.display("No connection", 1, 16, color=0xFF0000)
                try:
                    print("Trying to connect to network...")
                    if network.connect():
                        print("Connected successfully")
                    else:
                        print("Not connected")
                except Exception as e:
                    print(e)


        except Exception as e:
            print("Fetch failed, keeping last data:", e)

    # time is not displaying
    try:
        tm = time.localtime()
        time_str = f"{tm[1]:02d}/{tm[2]:02d} {tm[3]:02d}:{tm[4]:02d}"
        if time_label is None:
            time_label = display.display(time_str, 2, 10)
        else:
            time_label.text = time_str
    except Exception as e:
        print("Time update error:", e)

    # Scroll flights. This could be done based on if the flights text is too long
    try:
        if flights_label is not None:
            display.scroll_step(flights_label)
    except Exception as e:
        print("Scroll error:", e)

    time.sleep(TICK)
