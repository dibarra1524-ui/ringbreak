#!/usr/bin/env python3
"""Ring Breaker profile picture, drawn in code. python3 brand/make_logo.py"""
import cairo, math, colorsys, random, os
S = 1080
C = S / 2
HERE = os.path.dirname(os.path.abspath(__file__))
def hx(h): return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
WAVES = [hx(c) for c in ('FF8A1F', '4B2BFF', '3BFF3B', 'FF2D7A', '22C3F5', 'FFF000', 'A01EFF', '1FF58A', 'FF3B1F')]
R, RW = 398, 50
GAP = (-64, -30)          # degrees, the broken section (up and to the right)

def glow(c, x, y, r, rgb, a):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *rgb, a); g.add_color_stop_rgba(1, *rgb, 0)
    c.set_source(g); c.arc(x, y, r, 0, 2 * math.pi); c.fill()

def ball(c, x, y, r, rgb):
    glow(c, x, y, r * 2.6, rgb, 0.45)
    c.arc(x, y, r, 0, 2 * math.pi); c.set_source_rgb(*rgb); c.fill()
    c.arc(x - r * 0.3, y - r * 0.32, r * 0.28, 0, 2 * math.pi); c.set_source_rgba(1, 1, 1, 0.55); c.fill()

def hue(deg):
    return colorsys.hsv_to_rgb(((deg + 200) % 360) / 360, 0.95, 1.0)

def arc_seg(c, a0, a1, width, alpha, r=R, cx=C, cy=C):
    c.set_line_width(width); c.set_line_cap(cairo.LINE_CAP_BUTT)
    d = a0
    while d < a1:
        e = min(d + 2, a1)
        c.arc(cx, cy, r, math.radians(d), math.radians(e + 0.6))
        c.set_source_rgba(*hue(d), alpha); c.stroke()
        d = e

def text(c, s, y, width, fill, font='Inter Black'):
    c.select_font_face(font, cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(200); e = c.text_extents(s)
    size = 200 * width / e.width
    c.set_font_size(size); e = c.text_extents(s)
    x = -e.width / 2 - e.x_bearing
    c.move_to(x, y); c.text_path(s)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_source_rgba(0.02, 0, 0.08, 1); c.set_line_width(34); c.stroke_preserve()
    c.set_source_rgba(1, 1, 1, 0.9); c.set_line_width(7); c.stroke_preserve()
    c.set_source_rgba(0.02, 0, 0.08, 1); c.set_line_width(3); c.stroke_preserve()
    if isinstance(fill, tuple):
        c.set_source_rgb(*fill)
    else:
        g = cairo.LinearGradient(-width / 2, 0, width / 2, 0)
        for i, col in enumerate(fill):
            g.add_color_stop_rgb(i / (len(fill) - 1), *col)
        c.set_source(g)
    c.fill()
    return size

def main():
    rnd = random.Random(11)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, S, S)
    c = cairo.Context(surf)
    g = cairo.RadialGradient(C, C, 60, C, C, 780)
    g.add_color_stop_rgb(0, *hx('3A0F86')); g.add_color_stop_rgb(0.55, *hx('14043A')); g.add_color_stop_rgb(1, *hx('040110'))
    c.set_source(g); c.paint()
    # burst rays behind everything, fanning out of the break
    mid = math.radians((GAP[0] + GAP[1]) / 2)
    for k in range(26):
        a = mid + rnd.uniform(-0.95, 0.95)
        w = rnd.uniform(0.012, 0.05)
        c.move_to(C + 150 * math.cos(a), C + 150 * math.sin(a))
        c.line_to(C + 900 * math.cos(a - w), C + 900 * math.sin(a - w))
        c.line_to(C + 900 * math.cos(a + w), C + 900 * math.sin(a + w))
        c.close_path(); c.set_source_rgba(*WAVES[k % 9], 0.10); c.fill()
    # ring: glow layers then the solid rainbow band with a white-hot core
    import numpy as np, cv2
    lay = cairo.ImageSurface(cairo.FORMAT_ARGB32, S, S)
    arc_seg(cairo.Context(lay), GAP[1], 360 + GAP[0], RW + 26, 1.0)
    arr = np.ndarray((S, S, 4), np.uint8, lay.get_data())
    arr[:] = cv2.GaussianBlur(arr.copy(), (0, 0), 34)
    lay.mark_dirty()
    c.set_operator(cairo.OPERATOR_ADD)
    for _ in range(2):
        c.set_source_surface(lay, 0, 0); c.paint_with_alpha(0.95)
    c.set_operator(cairo.OPERATOR_OVER)
    arc_seg(c, GAP[1], 360 + GAP[0], RW, 1.0)
    c.set_line_width(9); c.set_source_rgba(1, 1, 1, 0.75)
    c.arc(C, C, R, math.radians(GAP[1] + 1.5), math.radians(360 + GAP[0] - 1.5)); c.stroke()
    # shards flying off the break
    for (da, dist, rot, ln) in ((-58, 78, 0.5, 11), (-47, 132, -0.7, 9), (-36, 84, 0.35, 10), (-50, 205, 1.1, 6)):
        a = math.radians(da)
        px, py = C + (R + dist) * math.cos(a), C + (R + dist) * math.sin(a)
        c.save(); c.translate(px, py); c.rotate(rot)
        for w, al in ((RW, 1.0),):
            arc_seg(c, da - ln / 2, da + ln / 2, w * (0.85 if ln < 8 else 1), al, cx=-R * math.cos(a), cy=-R * math.sin(a))
        c.restore()
    # balls packed against the inside of the ring
    placed = []
    for _ in range(4000):
        if len(placed) > 150: break
        rr = rnd.uniform(215, R - RW / 2 - 16); a = rnd.uniform(0, 2 * math.pi)
        x, y, r = C + rr * math.cos(a), C + rr * math.sin(a), rnd.choice((13, 15, 17, 20, 23))
        if abs(y - C) < 185 and abs(x - C) < 372: continue
        if any((x - px) ** 2 + (y - py) ** 2 < (r + pr + 3) ** 2 for px, py, pr in placed): continue
        placed.append((x, y, r)); ball(c, x, y, r, WAVES[len(placed) % 9])
    # balls blasting out through the break
    for k in range(64):
        a = mid + rnd.gauss(0, 0.27); d = rnd.uniform(R - 60, R + 250)
        ball(c, C + d * math.cos(a), C + d * math.sin(a), rnd.choice((11, 14, 17, 21, 26)) * (1.15 - (d - R + 60) / 700), WAVES[k % 9])
    # wordmark
    c.save(); c.translate(C, C); c.rotate(math.radians(-7))
    glow(c, 0, 0, 430, hx('14043A'), 0.9)
    text(c, 'RING', -18, 520, (1, 1, 1))
    text(c, 'BREAKER', 152, 664, [hx('FFF000'), hx('FF8A1F'), hx('FF2D7A')])
    c.restore()
    surf.write_to_png(os.path.join(HERE, 'ring_breaker_1080.png'))

if __name__ == '__main__':
    main()
