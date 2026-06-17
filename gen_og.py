#!/usr/bin/env python3
"""Generate og.png — the 1200x630 link-preview card for the office league.
Score-agnostic branding. Run once; commit og.png.  Needs Pillow."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1200, 630
HERE = os.path.dirname(os.path.abspath(__file__))


def font(name, size):
    for path in (f"C:/Windows/Fonts/{name}", f"/usr/share/fonts/truetype/dejavu/{name}"):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


BOLD, REG = "arialbd.ttf", "arial.ttf"

img = Image.new("RGB", (W, H))
g = ImageDraw.Draw(img)
top, bot = (16, 26, 52), (10, 14, 26)
for y in range(H):
    t = y / (H - 1)
    g.line([(0, y), (W, y)], fill=tuple(int(top[i] * (1 - t) + bot[i] * t) for i in range(3)))

glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([-160, -220, 540, 360], fill=(61, 165, 255, 75))
gd.ellipse([W - 540, -240, W + 160, 340], fill=(46, 224, 106, 80))
img = Image.alpha_composite(img.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(120))).convert("RGB")
d = ImageDraw.Draw(img)


def center(y, text, fnt, fill):
    d.text(((W - d.textlength(text, font=fnt)) / 2, y), text, font=fnt, fill=fill)


center(150, "F I F A   W O R L D   C U P   2 0 2 6", font(BOLD, 30), (147, 160, 196))

tf = font(BOLD, 116)
segs = [("AIP ", (238, 242, 255)), ("League", (46, 224, 106))]
total = sum(d.textlength(s, font=tf) for s, _ in segs)
x, ty = (W - total) / 2, 240
for s, col in segs:
    d.text((x, ty), s, font=tf, fill=col)
    x += d.textlength(s, font=tf)

center(420, "12 managers · all 48 teams · one champion", font(REG, 38), (210, 218, 245))
center(498, "Win +3      Draw +1      Loss 0", font(BOLD, 30), (147, 160, 196))

out = os.path.join(HERE, "og.png")
img.save(out)
print("saved", out, img.size)
