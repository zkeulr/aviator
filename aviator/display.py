import board
import displayio
import framebufferio
import rgbmatrix
from adafruit_display_text import label
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
BIT_DEPTH = 1
DISPLAY_WIDTH = 64

matrix = rgbmatrix.RGBMatrix(
    width=64,
    height=32,
    bit_depth=BIT_DEPTH, # Higher = smoother gradients, more RAM use
    rgb_pins=RGB_PINS,
    addr_pins=ADDR_PINS,
    clock_pin=CLOCK_PIN,
    latch_pin=LATCH_PIN,
    output_enable_pin=OE_PIN,
    doublebuffer=True,
)
framebuffer_display = framebufferio.FramebufferDisplay(matrix, auto_refresh=True)
_root_group = displayio.Group()
framebuffer_display.root_group = _root_group

def clear() -> None:
    """Remove all children from the root group."""
    global _root_group
    _root_group.pop() if len(_root_group) > 0 else None
    _root_group = displayio.Group()
    framebuffer_display.root_group = _root_group


def display(text: str, x: int = 0, y: int = 0, color: int = 0x00FF00, replace: bool = False, index: int | None = None) -> label.Label | None:
    """
    Add a label to the persistent root group.
    - If replace is True, clear existing children first.
    - If index is provided, insert at that position (lower index -> behind).
    """
    global _root_group
    if replace:
        clear()

    text_label = label.Label(
        terminalio.FONT,
        text=text,
        color=color,
        x=x,
        y=y
    )

    if text_label.bounding_box[2] > DISPLAY_WIDTH - 2:
        text_label.x = DISPLAY_WIDTH
        setattr(text_label, "_scroll_speed", 1)
        print(text, "_scroll_speed set to 1")

    if index is None:
        _root_group.append(text_label)
    else:
        _root_group.insert(index, text_label)

    return text_label

def scroll_step(lbl: label.Label, dx: int | None = None) -> None:
    """
    Advance a scrolling label left by dx pixels. If dx is None uses the label's
    _scroll_speed attribute (set by display(..., scroll=True, scroll_speed=...)).
    When the label has fully scrolled off the left edge it is reset to start from
    the right edge again for continuous scrolling.
    """
    if dx is None:
        dx = getattr(lbl, "_scroll_speed", 1)
    # move left
    lbl.x = lbl.x - dx
    # label width
    try:
        w = lbl.bounding_box[2] or 0
    except Exception:
        w = 0
    # if completely off-screen to the left, reset to right edge
    if lbl.x + w < 0:
        lbl.x = DISPLAY_WIDTH

def display_pixels(pixels, x: int = 0, y: int = 0, replace: bool = False, index: int | None = None) -> None:
    """
    Draw pixel data to the display.

    pixels: iterable of (px, py, color) tuples where color is 0xRRGGBB int.
    x, y: offsets applied to the whole pixel set.
    replace: if True, clears existing root group first.
    index: insert position in the root group (lower index -> behind).
    """
    global _root_group
    if replace:
        clear()

    pix_list = list(pixels)
    if not pix_list:
        return

    xs = [p[0] for p in pix_list]
    ys = [p[1] for p in pix_list]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width = max_x - min_x + 1
    height = max_y - min_y + 1

    # Build palette of unique colors
    color_to_index = {}
    unique_colors = []
    for _, _, col in pix_list:
        if col not in color_to_index:
            color_to_index[col] = len(unique_colors)
            unique_colors.append(col)

    palette = displayio.Palette(len(unique_colors))
    for i, col in enumerate(unique_colors):
        palette[i] = col

    bitmap = displayio.Bitmap(width, height, len(unique_colors))
    for px, py, col in pix_list:
        ix = px - min_x
        iy = py - min_y
        # guard against out-of-range just in case
        if 0 <= ix < width and 0 <= iy < height:
            bitmap[ix, iy] = color_to_index[col]

    tile = displayio.TileGrid(bitmap, pixel_shader=palette, x=x + min_x, y=y + min_y)
    if index is None:
        _root_group.append(tile)
    else:
        _root_group.insert(index, tile)