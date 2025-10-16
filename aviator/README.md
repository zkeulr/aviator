# README

Note: the Makefile is configured for Arch Linux and will not work without modification on Windows or Mac.

## Flashing

Follow the instructions for your device [here](https://micropython.org/download/UM_PROS3/).

WebREPL password: `password`.

## Transferring Files

```sh
sudo mpremote fs cp -r *.py :.
sudo mpremote connect /dev/ttyACM0
```
