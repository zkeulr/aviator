import board
import displayio
import framebufferio
import rgbmatrix
from adafruit_display_text import label
# from adafruit_bitmap_font import bitmap_font
import terminalio

# Release any previous displays
displayio.release_displays()

RGB_PINS = (
    board.IO12, # R1
    board.IO42, # G1
    board.IO13, # B1
    board.IO14, # R2
    board.IO41, # G2
    board.IO15 # B2
)

ADDR_PINS = (
    board.IO16, # A
    board.IO39, # B
    board.IO0, # C
    board.IO38 # D
)

CLOCK_PIN = board.IO21
LATCH_PIN = board.IO6
OE_PIN = board.IO5

matrix = rgbmatrix.RGBMatrix(
    width=64,
    height=32,
    bit_depth=6, # Higher = smoother gradients, more RAM use
    rgb_pins=RGB_PINS,
    addr_pins=ADDR_PINS,
    clock_pin=CLOCK_PIN,
    latch_pin=LATCH_PIN,
    output_enable_pin=OE_PIN,
    doublebuffer=True,
)
framebuffer_display = framebufferio.FramebufferDisplay(matrix, auto_refresh=True)

def display(text: str) -> None:
    text_label = label.Label(
        terminalio.FONT,
        text=text,
        color=0x00FF00,
        x=2,
        y=16
    )
    group = displayio.Group()
    group.append(text_label)
    framebuffer_display.root_group = group