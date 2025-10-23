# pyright: ignore[reportShadowedImports]

import adsb
import display
import time
import json

json_errors = {}
PURDUE_LOCATION = {"lat": 40.4237, "lon": 86.9212}

while True:
    try:
        flights = adsb.fetch_flights(PURDUE_LOCATION["lat"], PURDUE_LOCATION["lon"])
        display.display(str(flights))
        time.sleep(1)
    except Exception as e:
        json_errors.update({time.time: e})
        with open('errors.json', 'w') as f:
            json.dump(json_errors, f)

