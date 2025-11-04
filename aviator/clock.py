import network
import adafruit_ntp

response = network.requests.get("http://worldtimeapi.org/api/ip")
data = response.json()
offset_str = data["utc_offset"]  # e.g. "+01:30"
sign = 1 if offset_str[0] == '+' else -1
hours = int(offset_str[1:3])
minutes = int(offset_str[4:6])
tz_offset = sign * (hours + minutes / 60)

ntp = adafruit_ntp.NTP(network.pool, tz_offset=tz_offset, cache_seconds=3600)

# occasionally sample network time