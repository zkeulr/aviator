"""adsb.py
ADS-B data layer: supports two modes.

Modes:
  - "sim": synthetic flights (for early development)
  - "raw": ingest & partially decode Mode-S / ADS-B 1090ES DF17 frames

Real-world ADS-B operates at 1090 MHz (NOT 101.9 MHz). The extended
beacon (DF17) is 112 bits (28 hex chars). Full position decoding uses
Compact Position Reporting (CPR) requiring pairing of even/odd frames,
which is beyond this simplified stub. We decode only:
  - Downlink Format (DF)
  - ICAO address
  - Type Code (TC)
  - Barometric altitude (if TC indicates airborne position & Q-bit set)

Later you can add:
  - CPR lat/lon extraction
  - Velocity (ground speed, heading) decoding (TC 19)
  - Flight ID (TC 1–4)

Public API kept minimal:
  set_mode(mode)
  ingest_frame(hex_frame)
  fetch_flights(lat, lon)  # returns list (sim OR raw snapshot)
  get_flights()            # raw snapshot
"""

import time
import math
from typing import List, Dict, Optional, Tuple


MODE = "sim"  # change to "raw" when feeding real frames

# Error tracking
_error_count = 0
_last_error = None

_flights_by_icao: Dict[str, Dict] = {}
# For CPR decoding: store last even/odd frame per ICAO
_cpr_cache: Dict[str, Dict[str, Dict]] = {}  # {icao: {"even": {...}, "odd": {...}}}

# Synthetic list for sim mode
_sim_flights: List[Dict] = []


def set_mode(mode: str) -> None:
	global MODE
	if mode not in ("sim", "raw"):
		raise ValueError("mode must be 'sim' or 'raw'")
	MODE = mode


# --------------------------- SIMULATION MODE --------------------------- 
def _seed_sim(lat: float, lon: float) -> None:
	global _sim_flights
	_sim_flights = [
		{
			"icao": "ABC123",
			"callsign": "SIM1",
			"lat": lat + 0.15,
			"lon": lon - 0.05,
			"alt_ft": 31000,
			"heading": 95,
			"dist_km": 14.2,
			"updated": int(time.time()),
			"mode": "sim",
		},
		{
			"icao": "DEF456",
			"callsign": "SIM2",
			"lat": lat - 0.08,
			"lon": lon + 0.11,
			"alt_ft": 28000,
			"heading": 275,
			"dist_km": 32.8,
			"updated": int(time.time()),
			"mode": "sim",
		},
	]


def _advance_sim():
	now = int(time.time())
	for f in _sim_flights:
		f["heading"] = (f.get("heading", 0) + 2) % 360
		f["updated"] = now


# --------------------------- RAW MODE DECODING ------------------------- 
def _hex_to_bits(hex_frame: str) -> str:
	return "".join(f"{int(c,16):04b}" for c in hex_frame.upper())


def _decode_df(bits: str) -> int:
	return int(bits[0:5], 2)


def _decode_icao(bits: str) -> str:
	# ICAO address bits 9-32 (indices 8..31 zero-based)
	return f"{int(bits[8:32], 2):06X}"


def _decode_type_code(bits: str) -> int:
	# Type code bits 33-37 (indices 32..37)
	return int(bits[32:37], 2)


def _decode_altitude(bits: str, type_code: int) -> Optional[int]:
	# For airborne position messages (TC 9-18) barometric altitude is
	# encoded in bits 41-52 (indices 40..52). Q-bit at bit 48 (index 47).
	if 9 <= type_code <= 18:
		alt_field = bits[40:52]
		q_bit = alt_field[7]  # index 7 within the 12-bit slice
		if q_bit == "1":
			# Remove the Q-bit and reconstruct 11-bit altitude data
			eleven_bits = alt_field[0:7] + alt_field[8:12]
			alt_code = int(eleven_bits, 2)
			# Altitude in feet = alt_code * 25 - 1000 (per spec when Q=1)
			return alt_code * 25 - 1000
	return None
def _decode_cpr(bits: str, type_code: int) -> Optional[Dict]:
	"""Extract CPR lat/lon and frame parity from airborne position frames (TC 9–18).
	Returns dict: {"lat_cpr": int, "lon_cpr": int, "parity": int}
	"""
	if not (9 <= type_code <= 18):
		return None
	# CPR bits: ME bits 14–30 (lat), 31–47 (lon)
	# Global bits: lat 54–70, lon 71–87
	lat_cpr = int(bits[54:71], 2)
	lon_cpr = int(bits[71:88], 2)
	# Parity: ME bit 53 (global bit 53) — 0=even, 1=odd
	parity = int(bits[53], 2)
	return {"lat_cpr": lat_cpr, "lon_cpr": lon_cpr, "parity": parity}


def _cprNL(lat: float) -> int:
	# Table from ICAO Doc 9871, Appendix B
	if lat < 0:
		lat = -lat
	if lat < 10.47047130:
		return 59
	if lat < 14.82817437:
		return 58
	if lat < 18.18626357:
		return 57
	if lat < 21.02939493:
		return 56
	if lat < 23.54504487:
		return 55
	if lat < 25.82924707:
		return 54
	if lat < 27.93898710:
		return 53
	if lat < 29.91135686:
		return 52
	if lat < 31.77209708:
		return 51
	if lat < 33.53993436:
		return 50
	if lat < 35.22899598:
		return 49
	if lat < 36.85025108:
		return 48
	if lat < 38.41241892:
		return 47
	if lat < 39.92256684:
		return 46
	if lat < 41.38651832:
		return 45
	if lat < 42.80914012:
		return 44
	if lat < 44.19454951:
		return 43
	if lat < 45.54626723:
		return 42
	if lat < 46.86733252:
		return 41
	if lat < 48.16039128:
		return 40
	if lat < 49.42776439:
		return 39
	if lat < 50.67150166:
		return 38
	if lat < 51.89342469:
		return 37
	if lat < 53.09516153:
		return 36
	if lat < 54.27817472:
		return 35
	if lat < 55.44378444:
		return 34
	if lat < 56.59318756:
		return 33
	if lat < 57.72747354:
		return 32
	if lat < 58.84763776:
		return 31
	if lat < 59.95459277:
		return 30
	if lat < 61.04917774:
		return 29
	if lat < 62.13216659:
		return 28
	if lat < 63.20427479:
		return 27
	if lat < 64.26616523:
		return 26
	if lat < 65.31845310:
		return 25
	if lat < 66.36171008:
		return 24
	if lat < 67.39646774:
		return 23
	if lat < 68.42322022:
		return 22
	if lat < 69.44242631:
		return 21
	if lat < 70.45451075:
		return 20
	if lat < 71.45986473:
		return 19
	if lat < 72.45884545:
		return 18
	if lat < 73.45177442:
		return 17
	if lat < 74.43893416:
		return 16
	if lat < 75.42056257:
		return 15
	if lat < 76.39684391:
		return 14
	if lat < 77.36789461:
		return 13
	if lat < 78.33374083:
		return 12
	if lat < 79.29428225:
		return 11
	if lat < 80.24923213:
		return 10
	if lat < 81.19801349:
		return 9
	if lat < 82.13956981:
		return 8
	if lat < 83.07199445:
		return 7
	if lat < 83.99173563:
		return 6
	if lat < 84.89583158:
		return 5
	if lat < 85.78102276:
		return 4
	if lat < 86.64231607:
		return 3
	if lat < 87.47308768:
		return 2
	if lat < 88.26416571:
		return 1
	return 0


def _decode_cpr_position(icao: str) -> Optional[Tuple[float, float]]:
	"""If both even and odd frames exist for ICAO, decode lat/lon."""
	cache = _cpr_cache.get(icao)
	if not cache or "even" not in cache or "odd" not in cache:
		return None
	# Extract CPR fields
	lat_even = cache["even"]["lat_cpr"]
	lon_even = cache["even"]["lon_cpr"]
	lat_odd = cache["odd"]["lat_cpr"]
	lon_odd = cache["odd"]["lon_cpr"]
	t_even = cache["even"]["ts"]
	t_odd = cache["odd"]["ts"]
	# Use most recent frame
	if t_even > t_odd:
		ts = t_even
	else:
		ts = t_odd
	# CPR algorithm
	# See ICAO Doc 9871, Appendix B
	# Airborne: NZ = 15, Dlat_even = 360/60, Dlat_odd = 360/59
	Dlat_even = 360.0 / 60.0
	Dlat_odd = 360.0 / 59.0
	j = math.floor((59 * lat_even - 60 * lat_odd) / (2 ** 17))
	lat = Dlat_even * ((lat_even + j) % 60)
	lat_odd_val = Dlat_odd * ((lat_odd + j) % 59)
	# Use most recent frame's parity to select lat
	if t_even > t_odd:
		lat = lat
		ni = _cprNL(lat)
		m = math.floor((lon_even * (ni - 1) - lon_odd * ni) / (2 ** 17))
		if ni > 0:
			lon = (360.0 / ni) * ((lon_even + m) % ni)
		else:
			lon = None
	else:
		lat = lat_odd_val
		ni = _cprNL(lat)
		m = math.floor((lon_even * (ni - 1) - lon_odd * ni) / (2 ** 17))
		if ni > 0:
			lon = (360.0 / ni) * ((lon_odd + m) % ni)
		else:
			lon = None
	return (lat, lon)


def _haversine(lat1, lon1, lat2, lon2):
	"""Compute great-circle distance (km) between two lat/lon points."""
	R = 6371.0
	phi1 = math.radians(lat1)
	phi2 = math.radians(lat2)
	dphi = math.radians(lat2 - lat1)
	dlambda = math.radians(lon2 - lon1)
	a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
	return R * c
	# For airborne position messages (TC 9-18) barometric altitude is
	# encoded in bits 41-52 (indices 40..52). Q-bit at bit 48 (index 47).
	if 9 <= type_code <= 18:
		alt_field = bits[40:52]
		q_bit = alt_field[7]  # index 7 within the 12-bit slice
		if q_bit == "1":
			# Remove the Q-bit and reconstruct 11-bit altitude data
			eleven_bits = alt_field[0:7] + alt_field[8:12]
			alt_code = int(eleven_bits, 2)
			# Altitude in feet = alt_code * 25 - 1000 (per spec when Q=1)
			return alt_code * 25 - 1000
	return None


def _decode_callsign(bits: str, type_code: int) -> Optional[str]:
	"""Decode callsign for Type Codes 1-4 (Aircraft Identification).

	Layout (ME bits numbering):
	  1-5   Type Code (1-4)
	  6-8   Emitter category (ignored here)
	  9-56  Eight 6-bit character codes (48 bits)
	We map subset of IA-5 per ICAO Doc 9871.
	"""
	if not (1 <= type_code <= 4):
		return None
	# ME starts at global bit index 32. Char field begins at ME bit 9 => global index 32 + 8 = 40
	char_bits = bits[40:88]  # 48 bits
	chars: List[str] = []
	for i in range(0, 48, 6):
		val = int(char_bits[i:i+6], 2)
		chars.append(_map_callsign_char(val))
	callsign = "".join(chars).strip()
	return callsign or None


def _map_callsign_char(v: int) -> str:
	if v == 0:
		return " "
	if 1 <= v <= 26:
		return chr(ord('A') + v - 1)
	if 48 <= v <= 57:
		return chr(ord('0') + v - 48)
	# Common extra codes (some tables map 32 to space, 27='/') – keep simple.
	if v == 32:
		return " "
	return " "


def _decode_velocity(bits: str, type_code: int) -> Tuple[Optional[int], Optional[int]]:
	"""Decode ground speed & track from Type Code 19 subtype 1/2 (simplified).

	This is an approximate implementation: handles ground speed subtypes with
	East-West & North-South velocity components (10-bit magnitudes + sign).
	Returns (track_deg, speed_kt) or (None, None) if not decodable.
	"""
	if type_code != 19:
		return None, None
	# ME bits start at global bit 33 => index 32. Subtype is ME bits 6-8 => bits[37:40]
	subtype = int(bits[37:40], 2)
	if subtype not in (1, 2):  # Only ground speed variants
		return None, None
	# According to spec (approx):
	# EW direction bit at ME bit 14 (global idx 32+13=45)
	# EW velocity mag bits ME 15-24 => global 46-55
	# NS direction bit ME 25 (global 32+24=56)
	# NS velocity mag bits ME 26-35 => global 57-66
	try:
		ew_dir = int(bits[45], 2)  # 0 = East, 1 = West
		ew_mag = int(bits[46:56], 2)
		ns_dir = int(bits[56], 2)  # 0 = North, 1 = South
		ns_mag = int(bits[57:67], 2)
	except (ValueError, IndexError):
		return None, None
	if ew_mag == 0 and ns_mag == 0:
		return None, None
	# Per spec, value 0 indicates 'not available'; positive values subtract 1.
	if ew_mag > 0:
		ew_mag -= 1
	if ns_mag > 0:
		ns_mag -= 1
	# Apply direction
	vx = ew_mag * ( -1 if ew_dir == 1 else 1 )  # West negative
	vy = ns_mag * ( -1 if ns_dir == 1 else 1 )  # South negative
	speed = int(round(math.sqrt(vx * vx + vy * vy)))
	# Track angle: 0 deg = North, increase clockwise -> convert from atan2
	# atan2(x, y) if we want 0=N. We'll use atan2(vx, vy)
	angle = math.degrees(math.atan2(vx, vy))
	if angle < 0:
		angle += 360
	track = int(round(angle)) % 360
	return track, speed


def _update_raw_flight(icao: str, frame: str, type_code: int, altitude: Optional[int], callsign: Optional[str], velocity: Tuple[Optional[int], Optional[int]], cpr: Optional[Dict], receiver_lat: Optional[float]=None, receiver_lon: Optional[float]=None):
	now = int(time.time())
	rec = _flights_by_icao.get(icao)
	if not rec:
		rec = {
			"icao": icao,
			"callsign": callsign,
			"lat": None,
			"lon": None,
			"alt_ft": altitude,
			"heading": velocity[0],
			"gs_kt": velocity[1],
			"dist_km": None,
			"updated": now,
			"mode": "raw",
			"last_tc": type_code,
		}
		_flights_by_icao[icao] = rec
	else:
		if altitude is not None:
			rec["alt_ft"] = altitude
		if callsign:
			rec["callsign"] = callsign
		if velocity[0] is not None:
			rec["heading"] = velocity[0]
		if velocity[1] is not None:
			rec["gs_kt"] = velocity[1]
		rec["last_tc"] = type_code
		rec["updated"] = now
	# CPR cache update
	if cpr:
		parity = "even" if cpr["parity"] == 0 else "odd"
		if icao not in _cpr_cache:
			_cpr_cache[icao] = {}
		_cpr_cache[icao][parity] = {"lat_cpr": cpr["lat_cpr"], "lon_cpr": cpr["lon_cpr"], "ts": now}
		pos = _decode_cpr_position(icao)
		if pos:
			rec["lat"], rec["lon"] = pos
			# Compute distance if receiver location given
			if receiver_lat is not None and receiver_lon is not None:
				rec["dist_km"] = round(_haversine(receiver_lat, receiver_lon, rec["lat"], rec["lon"]), 2)
	# Store last raw frame for debugging
	rec["raw_frame"] = frame


def ingest_frame(hex_frame: str, receiver_lat: Optional[float]=None, receiver_lon: Optional[float]=None) -> bool:
	"""Ingest a single 112-bit DF17 frame (28 hex chars) in RAW mode.

	Returns True if frame parsed and accepted, else False.
	Logs errors and tracks error count.
	"""
	global _error_count, _last_error
	if MODE != "raw":
		return False
	hf = hex_frame.strip().upper()
	if len(hf) != 28:
		_error_count += 1
		_last_error = f"Frame length error: got {len(hf)} chars"
		print(f"[adsb] ERROR: { _last_error }")
		return False
	try:
		bits = _hex_to_bits(hf)
	except ValueError as e:
		_error_count += 1
		_last_error = f"Hex decode error: {e}"
		print(f"[adsb] ERROR: { _last_error }")
		return False
	if len(bits) != 112:
		_error_count += 1
		_last_error = f"Bit length error: got {len(bits)} bits"
		print(f"[adsb] ERROR: { _last_error }")
		return False
	try:
		df = _decode_df(bits)
		if df != 17:  # Only handle extended squitter
			_error_count += 1
			_last_error = f"DF error: got DF={df}"
			print(f"[adsb] ERROR: { _last_error }")
			return False
		icao = _decode_icao(bits)
		tc = _decode_type_code(bits)
		altitude = _decode_altitude(bits, tc)
		callsign = _decode_callsign(bits, tc)
		velocity = _decode_velocity(bits, tc)
		cpr = _decode_cpr(bits, tc)
		_update_raw_flight(icao, hf, tc, altitude, callsign, velocity, cpr, receiver_lat, receiver_lon)
		return True
	except Exception as e:
		_error_count += 1
		_last_error = f"General decode error: {e}"
		print(f"[adsb] ERROR: { _last_error }")
		return False
# --------------------------- PUBLIC ACCESSORS --------------------------
def get_error_count() -> int:
	return _error_count

def get_last_error() -> Optional[str]:
	return _last_error



# --------------------------- PUBLIC ACCESSORS --------------------------
def fetch_flights(lat: float, lon: float) -> List[Dict]:
	"""Return list of flight dicts for current mode.

	sim mode: updates and returns synthetic flights near (lat, lon)
	raw mode: returns snapshot of decoded flights (lat/lon, dist_km if available)
	"""
	if MODE == "sim":
		if not _sim_flights:
			_seed_sim(lat, lon)
		else:
			_advance_sim()
		return list(_sim_flights)
	# RAW: Optionally update dist_km for all flights if lat/lon available
	for rec in _flights_by_icao.values():
		if rec.get("lat") is not None and rec.get("lon") is not None:
			rec["dist_km"] = round(_haversine(lat, lon, rec["lat"], rec["lon"]), 2)
	return list(_flights_by_icao.values())

def get_flights() -> List[Dict]:
	return fetch_flights(0.0, 0.0)


__all__ = [
	"set_mode",
	"ingest_frame",
	"fetch_flights",
	"get_flights",
]


