"""flightinfo.py
Look up flight details (origin, destination, times) from OpenSky Network using callsign.
"""

import requests
import time

def lookup_flight_opensky(callsign):
    """
    Look up flight info from OpenSky Network using a callsign (e.g., 'KLM1023').
    Returns dict with origin, destination, departure, arrival, etc. or None if not found.
    """
    now = int(time.time())
    begin = now - 24*3600
    end = now
    url = f"https://opensky-network.org/api/flights/callsign?callsign={callsign}&begin={begin}&end={end}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            flights = resp.json()
            if flights:
                flight = flights[-1]
                return {
                    "callsign": callsign,
                    "icao24": flight.get("icao24"),
                    "origin": flight.get("estDepartureAirport"),
                    "destination": flight.get("estArrivalAirport"),
                    "departure_time": flight.get("firstSeen"),
                    "arrival_time": flight.get("lastSeen"),
                }
            else:
                print(f"[flightinfo] No flight found for callsign {callsign}")
        else:
            print(f"[flightinfo] HTTP error: {resp.status_code}")
    except Exception as e:
        print(f"[flightinfo] Exception: {e}")
    return None

# Example usage:
if __name__ == "__main__":
    info = lookup_flight_opensky("KLM1023")
    print("Flight info:", info)
