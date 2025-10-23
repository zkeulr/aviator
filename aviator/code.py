import time
import board
import digitalio

# Choose your pin (replace with the actual one you’re using)
pin = digitalio.DigitalInOut(board.IO12)  # Example: GPIO12

# Set it as an output
pin.direction = digitalio.Direction.OUTPUT

# Blink or toggle it
while True:
    pin.value = True   # Turn ON (sets pin HIGH)
    time.sleep(1)
    pin.value = False  # Turn OFF (sets pin LOW)
    time.sleep(1)
