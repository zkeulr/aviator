"""Fetch ADS-B traffic from the internet (adsb.lol by default).

This bypasses the local SDR by polling either:
    * https://adsb.lol community API (default, no auth, ADS-B Exchange-style data)
    * OpenSky `/states/all` (when `--source opensky`)

Usage examples:
        # adsb.lol (default)
        python net_adsb.py --lat 40.4259 --lon -86.9081 --radius-nm 150

        # OpenSky with OAuth client credentials
        python net_adsb.py --source opensky --lat 40.4259 --lon -86.9081 \
                --client-id juanesv06-api-client --client-secret <secret>
"""
#?
from __future__ import annotations

import argparse
import math
import os
import sys
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

import requests

OPEN_SKY_URL = "https://opensky-network.org/api/states/all"
TOKEN_URL = "https://auth.opensky-network.org/oauth/token"
ADSBX_URL_TEMPLATE = "https://api.adsb.lol/v2/lat/{lat}/lon/{lon}/dist/{dist}/"
MPS_TO_KT = 1.9438444924406046
M_TO_FT = 3.28084

_TOKEN_CACHE: Dict[str, Any] = {"token": None, "expires_at": 0.0}


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def _get_oauth_token(client_id: str, client_secret: str, timeout: int = 10) -> str:
    now = time.time()
    cached = _TOKEN_CACHE
    if cached["token"] and now < cached["expires_at"]:
        return cached["token"]
    resp = requests.post(
        TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
        timeout=timeout,
    )
    resp.raise_for_status()
    payload = resp.json()
    token = payload.get("access_token")
    if not token:
        raise RuntimeError("OpenSky token response missing access_token")
    expires_in = payload.get("expires_in", 300)
    cached["token"] = token
    cached["expires_at"] = now + max(30, int(expires_in) - 30)
    return token


def fetch_adsbx(
    center_lat: float,
    center_lon: float,
    radius_nm: float,
    timeout: int = 10,
) -> Sequence[Dict[str, Any]]:
    url = ADSBX_URL_TEMPLATE.format(lat=center_lat, lon=center_lon, dist=radius_nm)
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    payload = resp.json() or {}
    return payload.get("ac") or []


def normalize_adsbx(
    aircraft: Sequence[Dict[str, Any]],
    ref_lat: Optional[float] = None,
    ref_lon: Optional[float] = None,
) -> List[Dict[str, Any]]:
    flights: List[Dict[str, Any]] = []
    for ac in aircraft:
        lat = ac.get("lat")
        lon = ac.get("lon")
        if lat is None or lon is None:
            continue
        alt = ac.get("alt_baro") or ac.get("alt_geom")
        spd = ac.get("gs")
        track = ac.get("track")
        rec: Dict[str, Any] = {
            "icao": (ac.get("icao") or "").upper(),
            "callsign": (ac.get("flight") or ac.get("call") or "").strip(),
            "lat": lat,
            "lon": lon,
            "alt_ft": round(float(alt)) if isinstance(alt, (int, float)) else None,
            "gs_kt": round(float(spd)) if isinstance(spd, (int, float)) else None,
            "heading": round(float(track)) % 360 if isinstance(track, (int, float)) else None,
            "last_contact": ac.get("seen"),
            "time_position": ac.get("seen_pos"),
            "on_ground": ac.get("gnd"),
            "source": "adsbx",
        }
        if ref_lat is not None and ref_lon is not None:
            rec["dist_km"] = round(_haversine(ref_lat, ref_lon, lat, lon), 2)
        flights.append(rec)
    flights.sort(key=lambda x: x.get("dist_km", 1e9))
    return flights


def fetch_states(
    center_lat: float,
    center_lon: float,
    delta_deg: float,
    username: Optional[str] = None,
    password: Optional[str] = None,
    token: Optional[str] = None,
    timeout: int = 10,
) -> Sequence[List[Any]]:
    """Call OpenSky REST API and return the raw `states` array."""
    lamin = max(-90.0, center_lat - delta_deg)
    lamax = min(90.0, center_lat + delta_deg)
    lomin = center_lon - delta_deg
    lomax = center_lon + delta_deg
    params = {
        "lamin": lamin,
        "lamax": lamax,
        "lomin": lomin,
        "lomax": lomax,
    }
    auth = (username, password) if (username and password and not token) else None
    headers = {"Authorization": f"Bearer {token}"} if token else None
    resp = requests.get(OPEN_SKY_URL, params=params, auth=auth, headers=headers, timeout=timeout)
    resp.raise_for_status()
    payload = resp.json()
    return payload.get("states") or []


def normalize_states(
    states: Sequence[Sequence[Any]],
    ref_lat: Optional[float] = None,
    ref_lon: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """Convert OpenSky `states` entries to the dictionary format we use."""
    flights: List[Dict[str, Any]] = []
    for entry in states:
        if not entry or len(entry) < 17:
            continue
        lon = entry[5]
        lat = entry[6]
        if lat is None or lon is None:
            continue
        geo_alt = entry[13]
        baro_alt = entry[7]
        alt_m = geo_alt if geo_alt is not None else baro_alt
        speed_mps = entry[9]
        heading = entry[10]
        d: Dict[str, Any] = {
            "icao": (entry[0] or "").upper(),
            "callsign": (entry[1] or "").strip(),
            "origin_country": entry[2],
            "lat": lat,
            "lon": lon,
            "alt_ft": round(alt_m * M_TO_FT) if alt_m is not None else None,
            "gs_kt": round(speed_mps * MPS_TO_KT) if speed_mps is not None else None,
            "heading": round(heading) % 360 if heading is not None else None,
            "last_contact": entry[4],
            "time_position": entry[3],
            "on_ground": entry[8],
            "source": "opensky",
        }
        if ref_lat is not None and ref_lon is not None:
            d["dist_km"] = round(_haversine(ref_lat, ref_lon, lat, lon), 2)
        flights.append(d)
    flights.sort(key=lambda x: x.get("dist_km", 1e9))
    return flights


def poll_loop(args: argparse.Namespace) -> None:
    source = args.source.lower()
    username = args.username or os.getenv("OPENSKY_USERNAME")
    password = args.password or os.getenv("OPENSKY_PASSWORD")
    client_id = args.client_id or os.getenv("OPENSKY_CLIENT_ID")
    client_secret = args.client_secret or os.getenv("OPENSKY_CLIENT_SECRET")

    if source == "adsbx":
        print(f"[net_adsb] Using ADS-B Exchange public API, radius {args.radius_nm} nm")
    elif client_id and client_secret:
        print(f"[net_adsb] Using OAuth client {client_id}")
    elif username:
        print(f"[net_adsb] Using legacy basic auth user={username}")
    else:
        print("[net_adsb] Using anonymous OpenSky access (1 req / 10 s limit)")

    end_time = None if args.duration <= 0 else (time.time() + args.duration)
    iteration = 0
    while True:
        if end_time is not None and time.time() >= end_time:
            break
        try:
            if source == "adsbx":
                raw = fetch_adsbx(args.lat, args.lon, args.radius_nm)
                flights = normalize_adsbx(raw, args.lat, args.lon)
            else:
                token = None
                if client_id and client_secret:
                    token = _get_oauth_token(client_id, client_secret)
                raw_states = fetch_states(
                    args.lat,
                    args.lon,
                    args.delta,
                    username=username,
                    password=password,
                    token=token,
                )
                flights = normalize_states(raw_states, args.lat, args.lon)
            coverage = (
                f"{args.radius_nm} nm radius"
                if source == "adsbx"
                else f"+/-{args.delta} deg box"
            )
            print(f"[{time.strftime('%H:%M:%S')}] got {len(flights)} flights ({coverage})")
            for f in flights[: args.nearest]:
                print(
                    "   ",
                    f["icao"],
                    f.get("callsign"),
                    f"alt={f.get('alt_ft')} ft",
                    f"gs={f.get('gs_kt')} kt",
                    f"dist={f.get('dist_km')} km",
                    f"lat={f.get('lat'):.4f}",
                    f"lon={f.get('lon'):.4f}",
                )
        except requests.HTTPError as e:
            print(f"[net_adsb] HTTP {e.response.status_code}: {e.response.text[:160]}")
        except Exception as e:  # noqa: BLE001
            print(f"[net_adsb] error: {e}")
        iteration += 1
        time.sleep(args.interval)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Poll an online ADS-B data source")
    parser.add_argument("--source", choices=("adsbx", "opensky"), default="adsbx", help="Data source")
    parser.add_argument("--lat", type=float, required=True, help="Center latitude")
    parser.add_argument("--lon", type=float, required=True, help="Center longitude")
    parser.add_argument(
        "--delta",
        type=float,
        default=1.5,
        help="Half-size of bounding box in degrees (default 1.5)",
    )
    parser.add_argument(
        "--radius-nm",
        type=float,
        default=150.0,
        help="Search radius in NM for ADS-B Exchange source (default 150)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=10,
        help="Polling interval seconds (respect OpenSky rate limits)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=0,
        help="Total seconds to run (0 = continuous)",
    )
    parser.add_argument(
        "--nearest",
        type=int,
        default=10,
        help="Number of closest flights to print each poll",
    )
    parser.add_argument("--username", help="OpenSky username (legacy basic auth)", default=None)
    parser.add_argument("--password", help="OpenSky password (legacy basic auth)", default=None)
    parser.add_argument("--client-id", help="OpenSky OAuth client ID", default=None)
    parser.add_argument("--client-secret", help="OpenSky OAuth client secret", default=None)
    return parser


if __name__ == "__main__":
    parser = build_arg_parser()
    cli_args = parser.parse_args()
    try:
        poll_loop(cli_args)
    except KeyboardInterrupt:
        sys.exit(0)
