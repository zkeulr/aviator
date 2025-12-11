import math

ADSBX_URL = "https://api.adsb.lol/v2/lat/{lat}/lon/{lon}/dist/{dist}/"

def _haversine(lat1, lon1, lat2, lon2):
    """Return great-circle distance in nautical miles."""
    R_nm = 3440.065  # Earth radius in nautical miles
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R_nm * c

def fetch_flight(lat, lon, session, radius_nm=50, timeout=5):
    url = ADSBX_URL.format(lat=lat, lon=lon, dist=radius_nm)
    resp = session.get(url, timeout=timeout)
    data = resp.json().get("ac", [])

    if not data:
        return None

    # Compute distance for each aircraft, then select the nearest
    closest = min(
        data,
        key=lambda ac: _haversine(
            lat, lon,
            ac.get("lat") or 0,
            ac.get("lon") or 0
        )
    )

    print(closest)

    return {
        "callsign": (closest.get("flight") or closest.get("call") or "").strip(),
        "speed_kt": closest.get("gs"),
        "heading": closest.get("track"),
        "alt_ft": closest.get("alt_geom") or closest.get("alt_baro")
    }
