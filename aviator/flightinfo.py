import os

API_KEY = os.getenv("API_KEY") 

def fetch_json(url, session):
    """
    Perform HTTPS GET and return JSON safely.
    """
    try:
        response = session.get(url)
        if response.status_code != 200:
            print("API request failed:", response.status_code)
            return None
        data = response.json()
        response.close()
        return data
    except Exception as e:
        print("ERROR:", e)
        return None

def get_flights_by_callsign(callsign, session):
    url = f"https://api.aviationstack.com/v1/flights?access_key={API_KEY}&flight_icao={callsign}"
    data = fetch_json(url, session)
    if not data or "data" not in data:
        return []

    result = []
    for flight in data["data"]:
        departure = flight.get("departure", {}) or {}
        arrival = flight.get("arrival", {}) or {}

        result.append({
            "origin": departure.get("airport"),
            "destination": arrival.get("airport"),
            "dep_time": departure.get("scheduled"),
            "arr_time": arrival.get("scheduled"),
            "status": flight.get("flight_status"),
        })
    return result