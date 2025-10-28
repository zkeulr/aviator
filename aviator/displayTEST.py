import board
import framebufferio
import rgbmatrix
import terminalio
import displayio

# --- Configure matrix ---
matrix = rgbmatrix.RGBMatrix(
    width=64, height=32, bit_depth=4,
    rgb_pins=[board.IO12, board.IO42, board.IO13, board.IO14, board.IO41, board.IO15],
    addr_pins=[board.IO16, board.IO39, board.IO0, board.IO38],
    clock_pin=board.IO21,
    latch_pin=board.IO6,
    output_enable_pin=board.IO5,
)

display = framebufferio.FramebufferDisplay(matrix)

# --- Create a group for all display elements ---
group = displayio.Group()

# --- Create text manually ---
font = terminalio.FONT
text = "Hello, World!"
text_area = displayio.TileGrid(
    font.bitmap,
    pixel_shader=font.palette,
    width=len(text),
    height=1,
    tile_width=font.tile_width,
    tile_height=font.tile_height,
)
# Place the characters
for i, c in enumerate(text):
    text_area[i] = ord(c)

# Move it to position (10, 16)
text_group = displayio.Group(x=10, y=16)
text_group.append(text_area)

# Add to display group
group.append(text_group)
display.show(group)

# Keep running
while True:
    pass
