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

####
import display
from display import HUB75Display
DEV_PINMAP = {
    "R1": 12,
    "G1": 42,
    "B1": 13,
    "R2": 14,
    "G2": 41,
    "B2": 15,
    "A": 16,
    "B": 39,
    "C": 0,
    #"D": 38,
    "CLK": 21,
    "LAT": 6,
    "OE": 5
}

WROOM_PINMAP = {
    "R1": 11,
    "G1": 10,
    "B1": 9,
    "R2": 5,
    "G2": 8,
    "B2": 18,
    "A": 38,
    "B": 39,
    "C": 40,
    "D": 41,
    "E": 42,
    "CLK": 4,
    "LAT": 12,
    "OE": 17
}

disp = HUB75Display(DEV_PINMAP)

def hello_test():
    print("hello_test")
    text = "HELLO WORLD!"
    disp.clear()
    disp.draw_text(2,4,text,[1,0,0])
    disp.refresh()
    time.sleep_ms(100)
####


def all_on():
    """Turn all safe GPIOs ON (logic high)."""
    for p in pins:
        p.value(1)

def all_off():
    """Turn all safe GPIOs OFF (logic low)."""
    for p in pins:
        p.value(0)

def turn_all_pixels_on():
    """Turn all pixels on the display to white."""
    for y in range(disp.NUM_ROWS):
        for x in range(disp.NUM_COLS):
            disp.set_pixel(x, y, [1, 1, 1])
    disp.refresh()

def main():
    print("main")
    turn_all_pixels_on()

if __name__ == "__main__":
    main()
