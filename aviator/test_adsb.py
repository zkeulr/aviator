"""test_adsb.py
Simple manual test harness for adsb.py raw + sim modes.

Usage (desktop):
  python test_adsb.py
"""

import time
import adsb


def test_sim():
    adsb.set_mode("sim")
    print("-- SIM MODE --")
    for _ in range(3):
        flights = adsb.fetch_flights(40.0, -86.0)
        print("sim flights:")
        for f in flights:
            print("  ", f["icao"], f.get("alt_ft"), f.get("heading"))
        time.sleep(1)


def test_raw():
    adsb.set_mode("raw")
    print("-- RAW MODE --")
    sample_frames = [
        # Common example DF17 frames (length 28 hex chars). These may or may not contain altitude TC.
        "8D4840D6202CC371C32CE0576098",  # ICAO 4840D6
        "8D40621D58C382D690C8AC2863A7",  # ICAO 40621D
        "8D4B96969915560068AC3B284D77",  # Random example
        # Adding two frames for same ICAO, one even, one odd, for CPR decode
        "8D40621D58C386435CC412692AD6",  # ICAO 40621D, even
        "8D40621D58C382D690C8AC2863A7",  # ICAO 40621D, odd
    ]
    receiver_lat, receiver_lon = 40.0, -86.0
    for frame in sample_frames:
        ok = adsb.ingest_frame(frame[:28], receiver_lat, receiver_lon)  # 28 chars
        print("ingest", frame[:28], ok)
    flights = adsb.fetch_flights(receiver_lat, receiver_lon)
    for f in flights:
        print(
            "raw flight:",
            f["icao"],
            "callsign=", f.get("callsign"),
            "alt_ft=", f.get("alt_ft"),
            "lat=", f.get("lat"),
            "lon=", f.get("lon"),
            "dist_km=", f.get("dist_km"),
            "hdg=", f.get("heading"),
            "gs=", f.get("gs_kt"),
            "last_tc=", f.get("last_tc"),
        )


if __name__ == "__main__":
    test_sim()
    test_raw()
