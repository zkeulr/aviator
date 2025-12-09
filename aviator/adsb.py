ADSBX_URL = "https://api.adsb.lol/v2/lat/{lat}/lon/{lon}/dist/{dist}/"

def fetch_flight(lat, lon, session, radius_nm=50, timeout=5):
    url = ADSBX_URL.format(lat=lat, lon=lon, dist=radius_nm)
    resp = session.get(url, timeout=timeout)
    data = resp.json().get("ac", [])

    if not data:
        return None

    ac = data[0]

    print(ac)

    return {
        "callsign": (ac.get("flight") or ac.get("call") or "").strip(),
        "speed_kt": ac.get("gs"),
        "heading": ac.get("track"),
    }