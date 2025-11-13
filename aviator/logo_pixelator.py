from PIL import Image

# Load your image
im = Image.open("sr24db3a82b18cc.png").convert("RGB")
im = im.resize((64, 32), Image.NEAREST)  # Fit your display

pixels = []
for y in range(im.height):
    for x in range(im.width):
        r, g, b = im.getpixel((x, y))
        color = (r << 16) | (g << 8) | b
        pixels.append((x, y, color))

# Save as Python code snippet
with open("logo_pixels.py", "w") as f:
    f.write("logo_pixels = [\n")
    for x, y, c in pixels:
        f.write(f"    ({x}, {y}, 0x{c:06X}),\n")
    f.write("]\n")

print("Done! Wrote logo_pixels.py")
