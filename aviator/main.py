from machine import Pin
import time

SAFE_PINS = [
    0, 1, 2, 3, 4, 5, 6, 7,
    8, 9, 10, 11, 12, 13, 14, 15,
    16, 17, 18, 19, 20, 21,
    33, 34, 35, 36, 37, 38, 39, 40,
    41, 42, 43, 44, 45, 46, 47, 48
]

# Create output Pin objects for each GPIO
pins = []
for pin_num in SAFE_PINS:
    try:
        pin = Pin(pin_num, Pin.OUT)
        pins.append(pin)
    except ValueError:
        # Skip pins that cannot be configured as GPIO (e.g., reserved)
        print(f"Skipping invalid pin {pin_num}")

def all_on():
    """Turn all safe GPIOs ON (logic high)."""
    for p in pins:
        p.value(1)

def all_off():
    """Turn all safe GPIOs OFF (logic low)."""
    for p in pins:
        p.value(0)

def main():
    print("Starting GPIO toggle loop...")
    while True:
        all_on()
        print("All pins ON")
        time.sleep(1)
        all_off()
        print("All pins OFF")
        time.sleep(1)

if __name__ == "__main__":
    main()
