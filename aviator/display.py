import machine
import time

WIDTH = 64
HEIGHT = 32
FONT = {
    "A": [0x1E, 0x05, 0x05, 0x1E, 0x00],
    "B": [0x1F, 0x15, 0x15, 0x0A, 0x00],
    "C": [0x0E, 0x11, 0x11, 0x11, 0x00],
    "D": [0x1F, 0x11, 0x11, 0x0E, 0x00],
    "E": [0x1F, 0x15, 0x15, 0x11, 0x00],
    "H": [0x1F, 0x04, 0x04, 0x1F, 0x00],
    "L": [0x1F, 0x10, 0x10, 0x10, 0x00],
    "O": [0x0E, 0x11, 0x11, 0x0E, 0x00],
    "R": [0x1F, 0x05, 0x0D, 0x12, 0x00],
    "W": [0x1F, 0x08, 0x04, 0x08, 0x1F],
    " ": [0x00, 0x00, 0x00, 0x00, 0x00]
}

class HUB75Display:
    def __init__(self,pinmap):
        self.CLK = machine.Pin(pinmap["CLK"], machine.Pin.OUT)
        self.LAT = machine.Pin(pinmap["LAT"], machine.Pin.OUT)
        self.OE  = machine.Pin(pinmap["OE"], machine.Pin.OUT)

        self.R1 = machine.Pin(pinmap["R1"], machine.Pin.OUT)
        self.G1 = machine.Pin(pinmap["G1"], machine.Pin.OUT)
        self.B1 = machine.Pin(pinmap["B1"], machine.Pin.OUT)
        
        self.R2 = machine.Pin(pinmap["R2"], machine.Pin.OUT)
        self.G2 = machine.Pin(pinmap["G2"], machine.Pin.OUT)
        self.B2 = machine.Pin(pinmap["B2"], machine.Pin.OUT)

        self.ADDR = [
            machine.Pin(pinmap["A"], machine.Pin.OUT),
            machine.Pin(pinmap["B"], machine.Pin.OUT),
            machine.Pin(pinmap["C"], machine.Pin.OUT),
            machine.Pin(pinmap["D"], machine.Pin.OUT),
            machine.Pin(pinmap["E"], machine.Pin.OUT)
        ]
        self.NUM_ROWS= 32
        self.NUM_COLS= 64
        self.frame = [[[0, 0, 0] for _ in range(self.NUM_COLS)] for _ in range(self.NUM_ROWS)]

        self.OE.on()
        self.LAT.off()
        self.CLK.off()
        
    def select_row(self, row):
        for i in range(5):
            bit = (row >> i) & 1
            self.ADDR[i].value(bit)

    def pulse(self, pin):
        pin.on()
        pin.off()

    def set_pixel(self, x, y, color):
        if 0 <= x < self.NUM_COLS and 0 <= y < self.NUM_ROWS:
            self.frame[y][x] = color

    def draw_text(self, x, y, text, color):
        """Draws simple 5x7 text onto the framebuffer"""
        for char in text:
            bitmap = FONT.get(char.upper(), FONT[" "])
            for col, bits in enumerate(bitmap):
                for row in range(7):
                    if bits & (1 << row):
                        self.set_pixel(x + col, y + row, color)
            x += 6  # spacing between characters

    def refresh(self):
        for row in range(self.NUM_ROWS // 2):
            self.select_row(row)
            self.OE.on()
            for col in range(self.NUM_COLS):
                top = self.frame[row][col]
                bot = self.frame[row + 16][col]
                # Upper half
                self.R1.value(top[0])
                self.G1.value(top[1])
                self.B1.value(top[2])
                # Bottom half
                self.R2.value(bot[0])
                self.G2.value(bot[1])
                self.B2.value(bot[2])
                self.pulse(self.CLK)
            self.pulse(self.LAT)
            self.OE.off()
            time.sleep_us(200)
            self.OE.on()

    def clear(self):
        for y in range(self.NUM_ROWS):
            for x in range(self.NUM_COLS):
                self.frame[y][x] = [0, 0, 0]
