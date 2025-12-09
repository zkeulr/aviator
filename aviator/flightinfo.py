# AviationStack Flight Info Lookup
import http.client
import json
import os

API_KEY = os.getenv("API_KEY")

def get_flights_by_icao24(icao24):
    """
    Fetch flights by ICAO24 from AviationStack API using http.client and filter strictly by ICAO24.
    """
    conn = http.client.HTTPSConnection("api.aviationstack.com")
    url = f"/v1/flights?access_key={API_KEY}&icao24={icao24}"

    try:
        conn.request("GET", url)
        resp = conn.getresponse()
        if resp.status != 200:
            print("Error: AviationStack API request failed.")
            return []

        data = resp.read()
        flights = json.loads(data).get("data", [])
        result = []
        for flight in flights:
            if not isinstance(flight, dict):
                continue

            aircraft = flight.get("aircraft", {})
            if not isinstance(aircraft, dict):
                aircraft = {}

            top_icao24 = flight.get("icao24")
            ac_icao24 = aircraft.get("icao24")

            if (top_icao24 and top_icao24.lower() == icao24.lower()) or (ac_icao24 and ac_icao24.lower() == icao24.lower()):
                departure = flight.get("departure", {})
                if not isinstance(departure, dict):
                    departure = {}

                arrival = flight.get("arrival", {})
                if not isinstance(arrival, dict):
                    arrival = {}

                result.append({
                    "origin": departure.get("airport"),
                    "destination": arrival.get("airport"),
                    "dep_time": departure.get("scheduled"),
                    "arr_time": arrival.get("scheduled"),
                    "status": flight.get("flight_status"),
                })
        return result

    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        conn.close()

def get_flights_by_callsign(callsign):
    """
    Fetch flights by callsign/IATA from AviationStack API using http.client.
    """
    conn = http.client.HTTPSConnection("api.aviationstack.com")
    url = f"/v1/flights?access_key={API_KEY}&flight_icao={callsign}"

    try:
        conn.request("GET", url)
        resp = conn.getresponse()
        if resp.status != 200:
            print("Error: AviationStack API request failed.")
            return []

        data = resp.read()
        flights = json.loads(data).get("data", [])
        result = []
        for flight in flights:
            if not isinstance(flight, dict):
                continue

            departure = flight.get("departure", {})
            if not isinstance(departure, dict):
                departure = {}

            arrival = flight.get("arrival", {})
            if not isinstance(arrival, dict):
                arrival = {}

            result.append({
                "origin": departure.get("airport"),
                "destination": arrival.get("airport"),
                "dep_time": departure.get("scheduled"),
                "arr_time": arrival.get("scheduled"),
                "status": flight.get("flight_status"),
            })
        return result

    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        conn.close()

def main():
    """
    Main function to prompt user for input and fetch flight data.
    """
    user_input = input("Enter flight IATA/callsign or ICAO24 (e.g. AAL817 or ade18c): ").strip()
    if len(user_input) == 6 and all(c in "0123456789abcdefABCDEF" for c in user_input):
        flights = get_flights_by_icao24(user_input)
    else:
        flights = get_flights_by_callsign(user_input)

    if flights:
        for flight in flights:
            print(f"Origin: {flight['origin']}, Destination: {flight['destination']}, Departure: {flight['dep_time']}, Arrival: {flight['arr_time']}, Status: {flight['status']}")
    else:
        print("No matching flights found.")

if __name__ == "__main__":
    main()