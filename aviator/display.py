from machine import Pin
import utime


PINMAP = {
    "R1": 2,
    "G1": 4,
    "B1": 5,
    "R2": 12,
    "G2": 13,
    "B2": 14,
    "A": 15,
    "B": 16,
    "C": 17,
    "D": 18,
    "CLK": 19,
    "LAT": 21,
    "OE": 22
}

# Setup pins
pins = {name: Pin(num, Pin.OUT) for name, num in PINMAP.items()}

# Display size
WIDTH = 64
HEIGHT = 32

# Create a framebuffer (RGB tuples)
frame = [[[0,0,0] for _ in range(WIDTH)] for _ in range(HEIGHT)]

def set_pixel(x, y, r, g, b):
    """Set pixel color in framebuffer."""
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        frame[y][x] = [r, g, b]

def show():
    """Render the framebuffer to the HUB75 display."""
    for row in range(16):  # half of 32-pixel panel
        # Set address lines (A-D)
        pins["A"].value(row & 1)
        pins["B"].value((row >> 1) & 1)
        pins["C"].value((row >> 2) & 1)
        pins["D"].value((row >> 3) & 1)

        # Disable output while shifting
        pins["OE"].on()

        # Shift out pixel data for one row
        for col in range(WIDTH):
            top = frame[row][col]
            bottom = frame[row + 16][col]

            pins["R1"].value(top[0])
            pins["G1"].value(top[1])
            pins["B1"].value(top[2])

            pins["R2"].value(bottom[0])
            pins["G2"].value(bottom[1])
            pins["B2"].value(bottom[2])

            # Clock pulse
            pins["CLK"].on()
            pins["CLK"].off()

        # Latch data
        pins["LAT"].on()
        pins["LAT"].off()

        # Enable output for a short period
        pins["OE"].off()
        utime.sleep_us(100)
        pins["OE"].on()

# test animation
def fill_color(r, g, b):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            set_pixel(x, y, r, g, b)

def color_cycle():
    while True:
        fill_color(1, 0, 0)
        show()
        utime.sleep(0.5)
        fill_color(0, 1, 0)
        show()
        utime.sleep(0.5)
        fill_color(0, 0, 1)
        show()
        utime.sleep(0.5)

color_cycle()
