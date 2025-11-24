# README

## NOTE

CircuitPython does not support WPA2-Enterprise, which PAL3.0 requires. See [https://github.com/adafruit/circuitpython/issues/7083](https://github.com/adafruit/circuitpython/issues/7083). Until this is patched, this project will use a GrapheneOS phone as a WiFi extender.

## Libraries

Libraries on the device are managed with [`circup`](https://aur.archlinux.org/packages/circup).
To automatically install all modules imported by `code.py`, run `circup install --auto`.

## Connect

To connect, run

```sh
screen -L $(ls /dev/ttyACM* | head -1)
```

To disconnect, press `CTRL+A` then `CTRL+D`.

## Configure

Create `settings.toml` and fill in the following variables. The
specific names are important.

```toml
CIRCUITPY_WIFI_SSID = "Aviator"
CIRCUITPY_WIFI_PASSWORD = "password"
```
