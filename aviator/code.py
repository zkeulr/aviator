# pyright: ignore[reportShadowedImports]

import adsb
import display
import time
import json
import weather

json_errors = {}
PURDUE_LOCATION = {"lat": 40.4237, "lon": 86.9212}
networks = []

with open('log.json', 'w') as f:
    f.write("Booting")
    f.flush()

import wifi

try:
    for network in wifi.radio.start_scanning_networks():
        networks.append(network)
    wifi.radio.stop_scanning_networks()
    networks = sorted(networks, key=lambda net: net.rssi, reverse=True)

    with open('errors.json', 'w') as f:
            for network in networks:
                json_errors.update({network.ssid: network.rssi})
                json.dump(json_errors, f)
except:
    pass

while True:
    try:
        flights = adsb.fetch_flights(PURDUE_LOCATION["lat"], PURDUE_LOCATION["lon"])
        weather = weather.fetch_weather(PURDUE_LOCATION["lat"], PURDUE_LOCATION["lon"])
        display.display(str(flights) + str(weather))
        time.sleep(1)
    except Exception as e:
        json_errors.update({time.time(): e})
        with open('errors.json', 'w') as f:
            json.dump(json_errors, f)

