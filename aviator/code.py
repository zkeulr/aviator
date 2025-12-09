# pyright: ignore[reportShadowedImports]

# ISSUES: see comments
import adsb
import display
import network
import time
import weather

PURDUE_LOCATION = {"lat": 40.4237, "lon": -86.9212}
FETCH_INTERVAL = 30.0 # 120
TICK = 0.05

flights = [{}]
current_weather = {}
print("Displaying logo...")
display.display("AVIATOR", 12, 16)

time_label = None
flight_label = None
velocity_label = None
weather_label = None
weather_emoji_label = None
last_fetch = -FETCH_INTERVAL
first_pass = True

def temp_to_color(temp_c):
    if temp_c is None:
        return 0xFFFFFF
    if temp_c < 0:
        return 0x0000FF
    elif temp_c <= 20:
        return 0x00FFFF
    elif temp_c <= 35:
        return 0xFFFF00
    else:
        return 0xFF0000
    
def heading_to_arrow(heading):
    arrow = ""
    if heading < 45:
        arrow = "NE"
    elif heading < 90:
        arrow = "E"
    elif heading < 135:
        arrow = "SE"
    elif heading < 180:
        arrow = "S"
    elif heading < 225:
        arrow = "SW"
    elif heading < 270:
        arrow = "W" 
    elif heading < 315:
        arrow = "NW"
    else:
        arrow = "N"

    return arrow

def speed_to_color(speed):
    if speed_kt < 200:
        speed_color = 0xFFFFFF
    elif speed_kt < 400:
        speed_color = 0x0000FF
    elif speed_kt < 600:
        speed_color = 0x00FF00
    else:
        speed_color = 0xFF0000

    return speed_color

# First pass to initialize everything while logo displays
try:
    print("Trying to connect to network...")
    if network.connect():
        print("Connected successfully")
    else:
        print("Not connected")
    
    new_flight = adsb.fetch_flight(
                       PURDUE_LOCATION["lat"],
                       PURDUE_LOCATION["lon"],
                       session=network.requests,
                       radius_nm=150.0)

    new_weather = weather.fetch_weather(PURDUE_LOCATION["lat"], PURDUE_LOCATION["lon"])

except Exception as e:
    print(e)
finally:
    display.clear()

while True:
    now = time.monotonic()

    # Fetch new data only if interval has passed
    if now - last_fetch >= FETCH_INTERVAL:
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
                print("Fetching flight")

                # Fetch block
                if flight_label is not None:
                    flight_label.text = "" # clear so it doesn't appear to freeze

                if first_pass:
                    first_pass = False
                else:
                    try:
                        new_flight = adsb.fetch_flight(
                            PURDUE_LOCATION["lat"],
                            PURDUE_LOCATION["lon"],
                            session=network.requests,
                            radius_nm=150.0,
                        )                            
                    except Exception as e:
                        print("net_adsb failed,", e)
                        
                    print("Fetching weather")
                    new_weather = weather.fetch_weather(PURDUE_LOCATION["lat"], PURDUE_LOCATION["lon"])
                    print(new_weather)


                # Only update if fetch succeeds
                print("Updating flights and weather")
                flight = new_flight
                current_weather = new_weather

                # Update flights display
                try:
                    flight_text = f"{flight.get('callsign','---')[:6]}"
                    if new_flight.get("emergency") and new_flight.get("emergency") is not 'none':
                        print("Emergency:", new_flight.get("emergency"))
                        flight_text += " IS IN DISTRESS!"
                except:
                    flight_text = "No flights"

                if flight_label is None:
                    print("Creating flight_label")
                    
                    flight_label = display.display(flight_text, 1, 16, color=0xFFFFFF, scroll=True)
                else:
                    flight_label.text = flight_text

                # calculate heading, change based on speed
                try:
                    heading = int(flight.get("heading"))
                    print("heading:", heading)
                    velocity_string = heading_to_arrow(heading)

                    speed_kt = int(flight.get("speed_kt", 0))
                    print(speed_kt)
                    speed_color = speed_to_color(speed_kt)

                    if velocity_label is None:
                        velocity_label = display.display(text=velocity_string, x=50, y=5, color=speed_color)
                    else:
                        print("Updating velocity_label.text to", velocity_string)
                        velocity_label.text = velocity_string
                        velocity_label.color = speed_color
                            
                except Exception as e:
                   print("Exception in calculating and setting velocity,", e, speed_kt, heading)

                # Update weather display
                temp = current_weather.get("surface_temp")
                temp_color = temp_to_color(temp)
                weather_text = f"{temp}C" if temp is not None else "No weather"
                if weather_label is None:
                    weather_label = display.display(weather_text, 2, 27, color=temp_color)
                else:
                    print("Updating weather_label.text to", weather_text)
                    weather_label.text = weather_text
                    weather_label.color = temp_color

                rain = current_weather.get("rain")
                print("Rain:", rain)
                cloud_cover = current_weather.get("cloud_cover")
                print("Cloud cover:", cloud_cover)
                snowfall = current_weather.get("snowfall")
                print("Snowfall:", snowfall)

                # ☀️☁️⛅⛈️🌤️🌥️🌦️🌧️🌨️🌩️☔❄️
                weather_emoji = ""
                if float(current_weather.get("rain")) < 1:
                    weather_emoji = "☔"
                elif float(current_weather.get("snowfall")) > 0.0:
                    weather_emoji = "❄️"
                elif float(current_weather.get("cloud_cover")) > 50:
                    weather_emoji = "☁️"
                else: 
                    weather_emoji = "☀️"

                if weather_emoji_label is None:
                    weather_emoji_label = display.display_emoji(string=weather_emoji, x=3+weather_label.bounding_box[2], y=21)
                else:
                    print("Updating weather_emoji_label.text to", weather_emoji)
                    weather_emoji_label.text = weather_emoji

                # let's display the velocity of the plane with an emoji as well
                # ⬆️↗️➡️↘️⬇️↙️⬅️↖️

            else:
                if first_pass:
                    first_pass = False
                    display.clear()
                print("Not connected to the network")
                if flight_label is None:
                    flight_label = display.display("No connection", 1, 16, color=0xFF0000, scroll=True)
                try:
                    print("Trying to connect to network...")
                    if network.connect():
                        print("Connected successfully")
                        connected = True
                    else:
                        print("Not connected")
                except Exception as e:
                    print(e)


        except Exception as e:
            print("Fetch failed, keeping last data:", e)

    # time is not displaying
    try:
        tm = time.localtime()
        time_str = f"{tm[3]:02d}:{tm[4]:02d}" # Will not display if too long, e.g. including {tm[1]:02d}/{tm[2]:02d} 
        if time_label is None:
            time_label = display.display(time_str, 2, 5)
        else:
            time_label.text = time_str
    except Exception as e:
        print("Time update error:", e)

    # Scroll flights. This could be done based on if the flights text is too long
    # The text stops scrolling during calls to the weather or checking the network
    # This is very noticeable and not acceptable
    try:
        if flight_label is not None:
            flight_label.update()
    except Exception as e:
        print("Scroll error:", e)

    time.sleep(TICK)
