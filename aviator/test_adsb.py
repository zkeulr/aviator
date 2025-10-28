"""
Test helpers for the ADS-B module, including a live reader for RTL1090
Beast binary stream (TCP port 31001). No new files needed.
"""

import socket
import time
import sys
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
    print("-- RAW MODE (sample frames) --")
    sample_frames = [
        "8D4840D6202CC371C32CE0576098",
        "8D40621D58C382D690C8AC2863A7",
        "8D4B96969915560068AC3B284D77",
        "8D40621D58C386435CC412692AD6",
        "8D40621D58C382D690C8AC2863A7",
    ]
    receiver_lat, receiver_lon = 40.0, -86.0
    for frame in sample_frames:
        ok = adsb.ingest_frame(frame[:28], receiver_lat, receiver_lon)
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


def read_from_rtl1090(
    host="127.0.0.1",
    port=31001,
    runtime=60,
    receiver_lat=None,
    receiver_lon=None,
    report_interval_sec=5,
    nearest_n=10,
):
    """
    Connect to RTL1090 Beast binary stream (TCP 31001), extract Mode S long
    frames (14 bytes), and feed them into adsb.ingest_frame.
    """
    print(f"-- RTL1090 Beast stream {host}:{port} --")
    adsb.set_mode("raw")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.connect((host, port))
    print("Connected.")
    print(f"Reporting every {report_interval_sec}s. Press Ctrl+C to stop.")
    # Initial status line so the user sees immediate feedback
    print("Status: 0 DF17 frames | aircraft=0 (with position=0)")

    start = time.time()
    last_report = start
    deadline = None if runtime is None or runtime <= 0 else (start + runtime)
    buf = bytearray()
    frames = 0

    # Use short timeouts so we can print status ticks even if no data arrives
    s.settimeout(1.0)
    try:
        while True:
            if deadline is not None and time.time() >= deadline:
                break
            try:
                chunk = s.recv(4096)
            except socket.timeout:
                chunk = b""

            # Append any data
            if chunk:
                buf.extend(chunk)

            # Parse Beast frames in the buffer
            i = 0
            while i + 2 <= len(buf):
                if buf[i] != 0x1A:
                    i += 1
                    continue
                if i + 1 >= len(buf):
                    break
                mtype = buf[i + 1]
                if mtype not in (0x32, 0x33):
                    if mtype == 0x1A:
                        i += 2
                        continue
                    i += 1
                    continue

                payload_len = 7 if mtype == 0x32 else 14
                needed = 6 + 1 + payload_len

                j = i + 2
                out = bytearray()
                while j < len(buf) and len(out) < needed:
                    b = buf[j]
                    j += 1
                    if b == 0x1A:
                        if j < len(buf):
                            nb = buf[j]
                            if nb == 0x1A:
                                out.append(0x1A)
                                j += 1
                                continue
                            else:
                                j -= 1
                                break
                        else:
                            j -= 1
                            break
                    else:
                        out.append(b)

                if len(out) < needed:
                    break

                # mlat = out[:6]; sig = out[6]
                payload = out[7 : 7 + payload_len]
                if payload_len == 14:
                    # Only forward DF17 (ADS-B extended squitter) frames to our decoder
                    try:
                        df = payload[0] >> 3  # top 5 bits of first byte
                    except Exception:
                        df = None
                    if df == 17:
                        hex_frame = payload.hex().upper()
                        if adsb.ingest_frame(hex_frame, receiver_lat, receiver_lon):
                            frames += 1
                i = j

            if i > 0:
                del buf[:i]

            # Periodic status
            now = time.time()
            if now - last_report >= report_interval_sec:
                # Use receiver coords if provided so dist_km is computed in fetch_flights
                if receiver_lat is not None and receiver_lon is not None:
                    flights = adsb.fetch_flights(receiver_lat, receiver_lon)
                else:
                    flights = adsb.get_flights()

                with_pos = [
                    f for f in flights if f.get("lat") is not None and f.get("lon") is not None
                ]
                print(
                    f"Status: {frames} DF17 frames | aircraft={len(flights)} (with position={len(with_pos)})"
                )

                # Show up to nearest_n closest aircraft with valid positions
                if receiver_lat is not None and receiver_lon is not None and with_pos:
                    # Only keep those with a computed distance
                    with_dist = [f for f in with_pos if f.get("dist_km") is not None]
                    with_dist.sort(key=lambda f: f.get("dist_km"))
                    for f in with_dist[: max(0, int(nearest_n))]:
                        print(
                            "   ",
                            f.get("icao"),
                            f.get("callsign"),
                            f"alt={f.get('alt_ft')}",
                            f"dist_km={f.get('dist_km')}",
                            f"hdg={f.get('heading')}",
                            f"gs={f.get('gs_kt')}",
                            f"lat={f.get('lat')}",
                            f"lon={f.get('lon')}",
                        )
                last_report = now
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        try:
            s.close()
        except Exception:
            pass

    print(f"Done. Total DF17 frames processed: {frames}")
    # Use receiver coords for distance if provided
    flights = (
        adsb.fetch_flights(receiver_lat, receiver_lon)
        if (receiver_lat is not None and receiver_lon is not None)
        else adsb.get_flights()
    )
    print(f"Active aircraft: {len(flights)}")
    for f in flights[:10]:
        print(
            "  ",
            f.get("icao"),
            f.get("callsign"),
            f"alt={f.get('alt_ft')}",
            f"hdg={f.get('heading')}",
            f"gs={f.get('gs_kt')}",
            f"lat={f.get('lat')}",
            f"lon={f.get('lon')}",
            f"dist_km={f.get('dist_km')}",
        )


if __name__ == "__main__":
    # Keep original tests, but allow: python test_adsb.py rtl [seconds]
    if len(sys.argv) > 1 and sys.argv[1].lower().startswith("rtl"):
        secs = int(sys.argv[2]) if len(sys.argv) > 2 else 90
        # Optional lat/lon + report interval + nearestN:
        #   python test_adsb.py rtl 240 40.4259 -86.9081 3 10
        rlat = float(sys.argv[3]) if len(sys.argv) > 3 else None
        rlon = float(sys.argv[4]) if len(sys.argv) > 4 else None
        rint = int(sys.argv[5]) if len(sys.argv) > 5 else 5
        nnear = int(sys.argv[6]) if len(sys.argv) > 6 else 10
        read_from_rtl1090(
            runtime=secs,
            receiver_lat=rlat,
            receiver_lon=rlon,
            report_interval_sec=rint,
            nearest_n=nnear,
        )
    else:
        test_sim()
        test_raw()
