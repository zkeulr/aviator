# pyright: ignore[reportShadowedImports]

# import adsb
import display
import time

PURDUE_LAT_LON = (40.4237, 86.9212)

# flights = adsb.fetch_flights(PURDUE_LAT_LON)
display.display("INFO")
while True:
    time.sleep(1)

