"""scenes.py - themed, gently animated backgrounds for Ringbreak, each with a matching machine style.

Every scene is drawn entirely in code (no images), is a little different for every seed, and every
motion repeats a whole number of times per 20 second loop so the video still loops seamlessly.

    Scene(name, seed).frame(t)  -> 1080x1920 BGR uint8 background for time t
    STYLES[name]                -> how the ring, jaws, pads and counter are restyled to match
"""
import math
import numpy as np
import cv2

W, H, DUR = 1080, 1920, 20.0
CX, CY = 540.0, 960.0
TAU = 2 * math.pi


# ------------------------------------------------------------------ the matching machine styles
# ring/glow/pad/jaw colours are hex RGB. window = how much the scene is dimmed inside the ring so the
# balls stay the star. rim: plain | porthole (metal band with bolts) | stitch (baseball seams).
STYLES = {
    'nebula':     dict(ring='BDF6FF', glow='3FD3FF', rim='plain', window=0.42, pad='3FD3FF',
                       jaw=('6E7787', '3E4552', 'B4BECE', '23272F'), counter='E6FBFF',
                       desc='a deep-space nebula in magenta and teal with twinkling stars',
                       ring_desc='glowing pale-cyan'),
    'ringplanet': dict(ring='FFE6B5', glow='FFB347', rim='plain', window=0.40, pad='FFB347',
                       jaw=('8F8A84', '57534E', 'CBC6BF', '2E2B28'), counter='FFF1D6',
                       desc='a starfield with a huge banded ringed planet at the bottom and a small moon',
                       ring_desc='glowing pale-gold'),
    'hyperspace': dict(ring='E4F5FF', glow='4FA3FF', rim='plain', window=0.50, pad='4FA3FF',
                       jaw=('C3C9D2', '7A828E', 'F2F5F9', '4A5160'), counter='E4F5FF',
                       desc='blue-white hyperspace star streaks rushing out from the centre',
                       ring_desc='glowing electric-blue'),
    'twinsuns':   dict(ring='FFE0B0', glow='FF8A3C', rim='plain', window=0.40, pad='FF6A2B',
                       jaw=('A89782', '6B5E4E', 'DCCBB2', '3B3229'), counter='FFF0DA',
                       desc='a desert planet at dusk with two setting suns over layered dunes',
                       ring_desc='warm sandy-gold glowing'),
    'hangar':     dict(ring='D2DAE5', glow=None, rim='porthole', window=0.45, pad='FFC640',
                       jaw=('8E9198', '5C5F66', 'B9BCC2', '2E3034'), counter='FFC640',
                       desc='a sci-fi hangar bay opening onto space, with ceiling light strips and blinking red beacons',
                       ring_desc='thick bolted metal porthole'),
    'ballpark':   dict(ring='F4F1E8', glow=None, rim='stitch', window=0.38, pad='D7263D',
                       jaw=('8E9198', '5C5F66', 'B9BCC2', '2E3034'), counter='scoreboard',
                       desc='a baseball park at night: light towers, packed stands, outfield wall and striped grass',
                       ring_desc='baseball-white with red stitches'),
    'synthwave':  dict(ring='FF8AD8', glow='FF2E97', rim='plain', window=0.45, pad='01CDFE',
                       jaw=('5E4E8E', '2E2152', 'A08FDA', '1A1030'), counter='7DF3FF',
                       desc='a synthwave sunset: striped retro sun, purple mountains and a scrolling neon grid',
                       ring_desc='glowing hot-pink neon'),
    'neoncity':   dict(ring='9EFBFF', glow='00E5FF', rim='plain', window=0.42, pad='FF2A6D',
                       jaw=('6B7280', '3A3F4A', 'AEB4C0', '1F2229'), counter='9EFBFF',
                       desc='a rainy neon city skyline at night with lit windows and glowing signs',
                       ring_desc='glowing cyan neon'),
}
NAMES = list(STYLES)


# ------------------------------------------------------------------ small helpers (float RGB 0..1)
def C(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.0


def BGR(h, k=1.0):
    c = C(h) * 255 * k
    return (int(min(255, c[2])), int(min(255, c[1])), int(min(255, c[0])))


def to_u8(img):
    return (np.clip(img, 0, 1)[:, :, ::-1] * 255 + 0.5).astype(np.uint8)


def vgrad(stops, w=W, h=H):
    ys = np.arange(h, dtype=np.float32)
    col = np.stack([np.interp(ys, [s[0] for s in stops], [C(s[1])[i] for s in stops]) for i in range(3)], 1)
    return np.repeat(col[:, None, :], w, 1).astype(np.float32)


def noise(rng, cells, octaves=5, pers=0.55, w=W, h=H):
    """Smooth fractal noise in 0..1."""
    sw, sh = w // 4, h // 4
    acc = np.zeros((sh, sw), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        c = max(2, int(cells * 2 ** o))
        g = rng.random((max(2, int(c * h / w)) + 1, c + 1)).astype(np.float32)
        acc += amp * cv2.resize(g, (sw, sh), interpolation=cv2.INTER_CUBIC)
        tot += amp
        amp *= pers
    acc = cv2.GaussianBlur(acc / tot, (0, 0), 2)
    acc = cv2.resize(acc, (w, h), interpolation=cv2.INTER_LINEAR)
    return (acc - acc.min()) / (acc.max() - acc.min() + 1e-6)


def mix(img, col, a):
    a = np.clip(a, 0, 1)[..., None]
    img *= (1 - a)
    img += a * C(col)


def glow(img, x, y, r, col, s=1.0, p=2.0):
    """Add a soft radial light (in place) on a float image."""
    hh, ww = img.shape[:2]
    R = int(r * 3.2)
    x0, x1, y0, y1 = max(0, int(x - R)), min(ww, int(x + R)), max(0, int(y - R)), min(hh, int(y + R))
    if x0 >= x1 or y0 >= y1:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    d = np.sqrt((xx - x) ** 2 + (yy - y) ** 2) / r
    img[y0:y1, x0:x1] += (s * np.exp(-d ** p))[..., None] * C(col)


def sprite(r, col, s=1.0, p=2.0):
    """A small glow patch (uint8 BGR) to be added onto frames."""
    R = int(r * 3)
    pt = np.zeros((2 * R, 2 * R, 3), np.float32)
    glow(pt, R, R, r, col, s, p)
    return (np.clip(pt, 0, 1)[:, :, ::-1] * 255).astype(np.uint8)


def blit_add(img, spr, x, y, k=1.0):
    R = spr.shape[0] // 2
    x0, y0 = int(x) - R, int(y) - R
    sx0, sy0 = max(0, -x0), max(0, -y0)
    x1, y1 = min(W, x0 + 2 * R), min(H, y0 + 2 * R)
    if x1 <= max(0, x0) or y1 <= max(0, y0):
        return
    src = spr[sy0:sy0 + (y1 - max(0, y0)), sx0:sx0 + (x1 - max(0, x0))]
    if k != 1.0:
        src = cv2.convertScaleAbs(src, alpha=k)
    reg = img[max(0, y0):y1, max(0, x0):x1]
    cv2.add(reg, src, dst=reg)


def pt16(x, y):
    return (int(round(x * 16)), int(round(y * 16)))


def dot(img, x, y, r, col):
    cv2.circle(img, pt16(x, y), max(1, int(round(r * 16))), col, -1, cv2.LINE_AA, 4)


def poly(img, pts, col):
    cv2.fillPoly(img, [np.round(np.asarray(pts) * 16).astype(np.int32)], col, cv2.LINE_AA, 4)


def line(img, a, b, col, th=1):
    cv2.line(img, pt16(*a), pt16(*b), col, th, cv2.LINE_AA, 4)


def wave(t, k, ph=0.0):
    """sin with k whole cycles per loop."""
    return math.sin(TAU * k * t / DUR + ph)


class Stars:
    """Twinkling stars: baked dim ones plus a set redrawn each frame."""

    def __init__(self, rng, n, y0=0, y1=H, mask=None, tint=('FFFFFF', 'CFE3FF', 'FFE6C7')):
        self.rng = rng
        xs, ys = rng.uniform(0, W, n), rng.uniform(y0, y1, n)
        if mask is not None:
            keep = mask[np.clip(ys.astype(int), 0, H - 1), np.clip(xs.astype(int), 0, W - 1)] > 0.5
            xs, ys = xs[keep], ys[keep]
        self.x, self.y = xs, ys
        self.r = rng.uniform(1.0, 2.4, len(xs)) * (1 + 0.8 * (rng.random(len(xs)) < 0.06))
        self.b = rng.uniform(0.45, 1.0, len(xs))
        self.k = rng.integers(1, 5, len(xs))
        self.ph = rng.uniform(0, TAU, len(xs))
        self.col = [BGR(tint[i % len(tint)]) for i in rng.integers(0, len(tint), len(xs))]

    def bake_dust(self, img_u8, n, y0=0, y1=H, mask=None):
        xs, ys = self.rng.uniform(0, W, n), self.rng.uniform(y0, y1, n)
        for x, y, b in zip(xs, ys, self.rng.uniform(0.15, 0.55, n)):
            if mask is not None and mask[min(H - 1, int(y)), min(W - 1, int(x))] < 0.5:
                continue
            v = int(255 * b)
            img_u8[int(y), int(x)] = np.maximum(img_u8[int(y), int(x)], (v, v, v))

    def draw(self, img, t, dim=1.0):
        lay = np.zeros_like(img)
        for x, y, r, b, k, ph, c in zip(self.x, self.y, self.r, self.b, self.k, self.ph, self.col):
            a = dim * b * (0.55 + 0.45 * math.sin(TAU * k * t / DUR + ph))
            dot(lay, x, y, r, (int(c[0] * a), int(c[1] * a), int(c[2] * a)))
        cv2.max(img, lay, dst=img)


# ------------------------------------------------------------------ the scenes
class Scene:
    def __init__(self, name, seed=0):
        self.name, self.style = name, STYLES[name]
        self.rng = np.random.default_rng(seed * 7919 + NAMES.index(name) * 104729)
        getattr(self, '_build_' + name)()

    def frame(self, t):
        img = self.base.copy()
        getattr(self, '_anim_' + self.name)(img, t)
        return img

    # ---------------------------------------------------- deep space nebula
    def _build_nebula(self):
        rng, M = self.rng, 48
        w, h = W + 2 * M, H + 2 * M
        img = vgrad([(0, '03040C'), (h * 0.5, '070A1C'), (h, '04040E')], w, h)
        n1, n2, n3, n4 = (noise(rng, c, w=w, h=h) for c in (2.2, 2.8, 1.6, 3.4))
        hues = [('C2185B', 'E040FB'), ('0097A7', '26C6DA'), ('5E35B1', '7C4DFF'), ('D84315', 'FF7043')]
        order = rng.permutation(len(hues))
        a, b = hues[order[0]], hues[order[1]]
        mix(img, '3A1C71', 0.45 * n3 ** 1.4)
        mix(img, a[0], 0.85 * np.clip((n1 - 0.38) * 2.0, 0, 1) ** 1.5)
        mix(img, b[0], 0.75 * np.clip((n2 - 0.42) * 2.2, 0, 1) ** 1.5)
        mix(img, a[1], 0.55 * np.clip((n1 - 0.62) * 3.0, 0, 1) ** 2)
        mix(img, b[1], 0.45 * np.clip((n2 - 0.66) * 3.0, 0, 1) ** 2)
        img *= (1 - 0.75 * np.clip((n4 - 0.55) * 2.6, 0, 1) ** 1.2)[..., None]     # dark dust lanes
        img *= 0.62
        for _ in range(3):
            glow(img, rng.uniform(0.1, 0.9) * w, rng.choice([rng.uniform(0.05, 0.25), rng.uniform(0.75, 0.95)]) * h,
                 rng.uniform(160, 320), a[1], 0.18)
        u8 = to_u8(img)
        self.stars = Stars(rng, 150)
        st = Stars(rng, 0)
        st.rng = rng
        st.bake_dust(u8, 2600, 0, h)
        for _ in range(4):        # a few bright stars with diffraction spikes
            x, y = rng.uniform(60, w - 60), rng.choice([rng.uniform(60, 520), rng.uniform(1420, h - 60)])
            L = rng.uniform(40, 80)
            cv2.add(u8, (0, 0, 0, 0), dst=u8)
            for dx, dy in ((1, 0), (0, 1)):
                line(u8, (x - L * dx, y - L * dy), (x + L * dx, y + L * dy), (190, 200, 210), 1)
            spr = sprite(9, 'DDEEFF', 0.9)
            R = spr.shape[0] // 2
            reg = u8[int(y) - R:int(y) + R, int(x) - R:int(x) + R]
            if reg.shape == spr.shape:
                cv2.add(reg, spr, dst=reg)
        self.big, self.M = u8, M
        self.base = u8[M:M + H, M:M + W].copy()

    def _anim_nebula(self, img, t):
        dx, dy = 22 * math.cos(TAU * t / DUR), 14 * math.sin(TAU * t / DUR)
        mat = np.float32([[1, 0, -(self.M + dx)], [0, 1, -(self.M + dy)]])
        cv2.warpAffine(self.big, mat, (W, H), dst=img, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        self.stars.draw(img, t)

    # ---------------------------------------------------- ringed gas giant
    def _build_ringplanet(self):
        rng = self.rng
        img = vgrad([(0, '02030A'), (H * 0.6, '060818'), (H, '0A0A14')])
        band = noise(rng, 1.4)
        mix(img, '1C2450', 0.35 * np.clip((band - 0.4) * 1.6, 0, 1))      # faint milky band
        u8 = to_u8(img)
        self.stars = Stars(rng, 0)
        self.stars.bake_dust(u8, 1800)
        img = u8[:, :, ::-1].astype(np.float32) / 255
        px, py, pr = rng.uniform(700, 880), rng.uniform(1700, 1800), rng.uniform(520, 600)
        tilt = math.radians(rng.uniform(-22, -12))
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        dx, dy = (xx - px) / pr, (yy - py) / pr
        d2 = dx * dx + dy * dy
        inside = d2 < 1
        # bands follow the ring plane
        lat = (-dx * math.sin(tilt) + dy * math.cos(tilt))
        nz = noise(rng, 3.0)
        warp = lat + 0.05 * (nz - 0.5)
        tones = [C('F2DDB5'), C('D9A66E'), C('B9784A'), C('EBC690'), C('8E5634'), C('F5E3C4')]
        f = (np.sin(warp * 22) * 0.5 + 0.5) * 0.55 + (np.sin(warp * 7.3 + 1.3) * 0.5 + 0.5) * 0.45
        idx = np.clip(f * (len(tones) - 1), 0, len(tones) - 1.001)
        i0 = idx.astype(int)
        fr = (idx - i0)[..., None]
        T = np.stack(tones)
        surf = T[i0] * (1 - fr) + T[i0 + 1] * fr
        nzv = np.sqrt(np.clip(1 - d2, 0, 1))
        L = np.array([-0.55, -0.62, 0.56], np.float32)
        L /= np.linalg.norm(L)
        lam = np.clip(dx * L[0] + dy * L[1] + nzv * L[2], 0, 1)
        shade = (0.06 + 1.05 * lam ** 0.9)[..., None]
        planet = surf * shade
        rim = np.clip(1 - nzv, 0, 1) ** 3 * np.clip(lam * 2.5, 0, 1)
        planet += rim[..., None] * C('FFD9A0') * 0.6
        edge = np.clip((1 - np.sqrt(d2)) * pr / 1.5, 0, 1)[..., None]
        img = img * (1 - edge) + planet * edge
        glow_a = np.exp(-np.clip(np.sqrt(d2) - 1, 0, None) * 9) * (~inside)
        img += (glow_a * 0.25)[..., None] * C('FFB070')
        # rings
        ux = dx * math.cos(tilt) + dy * math.sin(tilt)
        uy = -dx * math.sin(tilt) + dy * math.cos(tilt)
        rho = np.sqrt(ux ** 2 + (uy / 0.2) ** 2)
        prof = np.zeros_like(rho)
        for r0, r1, a in ((1.25, 1.42, 0.55), (1.45, 1.78, 0.85), (1.82, 1.88, 0.35), (1.92, 2.15, 0.6)):
            prof += a * np.clip(np.minimum(rho - r0, r1 - rho) * 60, 0, 1)
        prof *= 0.75 + 0.25 * np.sin(rho * 140)
        prof = np.clip(prof, 0, 1)
        hidden = inside & (uy < 0)                       # back half of the rings goes behind the planet
        prof[hidden] = 0
        shadow = (~inside) | (uy > 0)
        rcol = C('E9D2AE') * (0.35 + 0.65 * np.clip(0.6 - ux * 0.25, 0, 1))[..., None]
        a = (prof * 0.9 * shadow)[..., None]
        img = img * (1 - a) + rcol * a
        # moon
        mx, my, mr = rng.uniform(120, 260), rng.uniform(250, 420), rng.uniform(34, 52)
        mdx, mdy = (xx - mx) / mr, (yy - my) / mr
        md2 = mdx ** 2 + mdy ** 2
        mz = np.sqrt(np.clip(1 - md2, 0, 1))
        ml = np.clip(mdx * L[0] + mdy * L[1] + mz * L[2], 0, 1)
        mn = noise(rng, 6)
        mcol = (C('B8B3AA') * (0.75 + 0.3 * mn[..., None])) * (0.04 + ml[..., None])
        me = np.clip((1 - np.sqrt(md2)) * mr / 1.5, 0, 1)[..., None]
        img = img * (1 - me) + mcol * me
        self.base = to_u8(img)
        self.mask = (~inside & (prof < 0.05)).astype(np.float32)
        self.stars = Stars(rng, 130, 0, 1500, mask=self.mask)
        self.shoot = (rng.uniform(150, 900), rng.uniform(80, 400), rng.uniform(0.2, 0.8), rng.uniform(3, 16))

    def _anim_ringplanet(self, img, t):
        self.stars.draw(img, t)
        x0, y0, ang, t0 = self.shoot                      # one shooting star per loop
        u = (t - t0) / 0.7
        if 0 <= u <= 1:
            L = 260
            hx_, hy_ = x0 + math.cos(ang) * L * u * 1.5, y0 + math.sin(ang) * L * u * 1.5
            for i in range(10):
                k = (1 - i / 10) * math.sin(math.pi * u)
                a = (hx_ - math.cos(ang) * 14 * i, hy_ - math.sin(ang) * 14 * i)
                b = (hx_ - math.cos(ang) * 14 * (i + 1), hy_ - math.sin(ang) * 14 * (i + 1))
                v = int(255 * k)
                line(img, a, b, (v, v, v), 2)

    # ---------------------------------------------------- hyperspace tunnel
    def _build_hyperspace(self):
        rng = self.rng
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt((xx - CX) ** 2 + (yy - CY) ** 2)
        img = np.zeros((H, W, 3), np.float32)
        img += (np.exp(-d / 520) * 0.55)[..., None] * C('0B2A6B')
        img += (np.exp(-d / 180) * 0.35)[..., None] * C('8FC8FF')
        ang = np.arctan2(yy - CY, xx - CX)
        rays = noise(rng, 6)
        img += ((0.5 + 0.5 * np.sin(ang * 23 + rays * 6)) * np.exp(-d / 900) * 0.12)[..., None] * C('3D7BFF')
        vign = np.clip(d / 1250, 0, 1) ** 2
        img *= (1 - 0.6 * vign)[..., None]
        self.base = to_u8(img)
        n = 340
        self.a = rng.uniform(0, TAU, n)
        self.u0 = rng.random(n)
        self.k = rng.integers(2, 5, n)
        self.w = rng.choice([1, 1, 2, 2, 3], n)
        self.tint = [BGR(c) for c in rng.choice(['FFFFFF', 'CFE6FF', '9CC8FF', 'B9A8FF'], n)]

    def _anim_hyperspace(self, img, t):
        lay = np.zeros_like(img)
        for a, u0, k, w, c in zip(self.a, self.u0, self.k, self.w, self.tint):
            u = (u0 + k * t / DUR) % 1.0
            r0 = 60 + 1300 * u ** 2.4
            L = 20 + 520 * u ** 2.2
            b = min(1.0, u * 2.2)
            ca, sa = math.cos(a), math.sin(a)
            col = (int(c[0] * b), int(c[1] * b), int(c[2] * b))
            line(lay, (CX + ca * r0, CY + sa * r0), (CX + ca * (r0 + L), CY + sa * (r0 + L)), col, int(w))
        cv2.add(img, lay, dst=img)

    # ---------------------------------------------------- twin suns over desert dunes
    def _build_twinsuns(self):
        rng = self.rng
        hz = 1610.0
        img = vgrad([(0, '0C0822'), (480, '231340'), (980, '5A2556'), (1300, 'A4415A'), (1480, 'E0744A'),
                     (hz, 'F59A5A'), (H, '2A1420')])
        haze = noise(rng, 2.0)
        mix(img, 'FF9A5A', 0.18 * np.clip((haze - 0.5) * 2, 0, 1) * (np.arange(H) > 900)[:, None] * (np.arange(H) < hz)[:, None])
        s1 = (rng.uniform(300, 420), hz - rng.uniform(30, 60), rng.uniform(58, 70))
        s2 = (s1[0] + rng.uniform(190, 260), hz - rng.uniform(80, 120), rng.uniform(36, 46))
        for x, y, r in (s1, s2):
            glow(img, x, y, r * 4.0, 'FF7A3C', 0.22, 1.3)
            glow(img, x, y, r * 1.6, 'FFC27A', 0.35, 1.8)
        u8 = to_u8(img)
        self.stars = Stars(rng, 70, 0, 760, tint=('FFFFFF', 'FFE6C7'))
        self.stars.bake_dust(u8, 700, 0, 800)
        for (x, y, r), col in ((s1, 'FFF2D0'), (s2, 'FFE7B0')):
            dot(u8, x, y, r, BGR(col))
        # two moons high in the sky
        for _ in range(2):
            x, y, r = rng.uniform(120, 960), rng.uniform(120, 420), rng.uniform(14, 30)
            dot(u8, x, y, r, BGR('E7D9F0', 0.85))
            dot(u8, x + r * 0.35, y - r * 0.2, r * 0.92, BGR('231340'))
        # layered dunes, far (hazy) to near (dark)
        xs = np.arange(0, W + 8, 8, dtype=np.float32)
        layers = [(hz - 10, 26, '9A4A58'), (hz + 50, 40, '6B2E44'), (hz + 140, 60, '45203A'), (hz + 250, 70, '28132A')]
        for yb, amp, col in layers:
            p = rng.uniform(0, TAU, 3)
            ys = yb - amp * (0.6 * np.sin(xs / W * TAU * rng.uniform(0.6, 1.2) + p[0])
                             + 0.3 * np.sin(xs / W * TAU * rng.uniform(1.8, 2.6) + p[1])
                             + 0.1 * np.sin(xs / W * TAU * 5 + p[2]))
            pts = np.concatenate([np.stack([xs, ys], 1), [[W + 8, H + 4], [-8, H + 4]]])
            poly(u8, pts, BGR(col))
            crest = np.stack([xs, ys + 1.5], 1)
            cv2.polylines(u8, [np.round(crest * 16).astype(np.int32)], False, BGR('FFB070', 0.55), 2, cv2.LINE_AA, 4)
        self.base = u8
        self.sun_spr = [sprite(r * 1.4, 'FFB060', 0.22) for _, _, r in (s1, s2)]
        self.suns = (s1, s2)
        n = 140
        self.sx, self.sy = rng.uniform(0, W, n), rng.uniform(hz - 40, H, n)
        self.sk, self.sr = rng.integers(1, 4, n), rng.uniform(1.0, 2.2, n)
        self.sph = rng.uniform(0, TAU, n)

    def _anim_twinsuns(self, img, t):
        self.stars.draw(img, t, 0.8)
        for (x, y, r), spr, k in zip(self.suns, self.sun_spr, (1, 2)):
            blit_add(img, spr, x, y, 0.6 + 0.4 * (0.5 + 0.5 * wave(t, k)))
        lay = np.zeros_like(img)
        for x, y, k, r, ph in zip(self.sx, self.sy, self.sk, self.sr, self.sph):   # drifting sand
            xx = (x + k * (W + 40) * t / DUR) % (W + 40) - 20
            yy = y + 6 * math.sin(TAU * k * t / DUR + ph)
            dot(lay, xx, yy, r, BGR('FFC890', 0.4))
        cv2.add(img, lay, dst=img)

    # ---------------------------------------------------- sci-fi hangar bay
    def _build_hangar(self):
        rng = self.rng
        img = vgrad([(0, '161B24'), (500, '0F131A'), (1560, '0B0E13'), (H, '07090C')])
        pn = noise(rng, 8, 2)
        img *= (0.85 + 0.3 * pn)[..., None]
        u8 = to_u8(img)
        D = (60, 430, 1020, 1530)                    # the open bay door
        bay = np.zeros((H, W), np.float32)
        cv2.rectangle(bay, (D[0], D[1]), (D[2], D[3]), 1.0, -1)
        # space through the door
        sp = vgrad([(0, '020309'), (H, '050716')])
        mix(sp, '2B1B5E', 0.35 * noise(rng, 2.0) ** 2)
        px, py, pr = rng.uniform(150, 350), D[3] + rng.uniform(380, 520), rng.uniform(700, 820)
        glow(sp, px, py, pr * 1.02, '3D8BFF', 0.6, 10)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        dd = np.sqrt((xx - px) ** 2 + (yy - py) ** 2) / pr
        lim = np.clip((1 - dd) * pr / 2, 0, 1)[..., None]
        pl = (C('163A7A') * (0.25 + 0.75 * np.clip(1 - (1 - dd) * 6, 0, 1))[..., None]
              + C('7FC4FF') * np.clip(1 - (1 - dd) * 40, 0, 1)[..., None] * 0.5)
        sp = sp * (1 - lim) + pl * lim
        sp8 = to_u8(sp)
        Stars(rng, 0).bake_dust(sp8, 1400)
        self.stars = Stars(rng, 90, D[1], D[3], mask=bay)
        m = bay[..., None] > 0.5
        u8 = np.where(m, sp8, u8)
        # wall panel seams and rivets
        for x in range(0, W, 180):
            line(u8, (x, 0), (x, D[1] - 30), (30, 26, 22), 2)
        for y in (80, 220, 360):
            line(u8, (0, y), (W, y), (30, 26, 22), 2)
        for y in range(D[1] + 60, D[3], 160):
            line(u8, (0, y), (D[0] - 24, y), (30, 26, 22), 2)
            line(u8, (D[2] + 24, y), (W, y), (30, 26, 22), 2)
        # door frame with bevel
        for o, col in ((26, (44, 40, 36)), (20, (78, 72, 66)), (6, (120, 112, 104)), (2, (26, 24, 22))):
            cv2.rectangle(u8, (D[0] - o, D[1] - o), (D[2] + o, D[3] + o), col, 4, cv2.LINE_AA)
        # hazard stripes on the sill
        y0, y1 = D[3] + 26, D[3] + 64
        cv2.rectangle(u8, (0, y0), (W, y1), (20, 20, 20), -1)
        for x in range(-60, W + 60, 56):
            poly(u8, [(x, y1), (x + 28, y1), (x + 28 + 38, y0), (x + 38, y0)], BGR('F2B630', 0.9))
        # floor grid in perspective
        hz, vx = float(y1), CX
        flo = np.zeros((H, W, 3), np.uint8)
        for i in range(-14, 15):
            line(flo, (vx + i * 30, hz), (vx + i * 260, H), (70, 64, 58), 1)
        z = 1.0
        while True:
            y = hz + 900 / z
            if y < hz + 4:
                break
            if y < H:
                line(flo, (0, y), (W, y), (70, 64, 58), 1)
            z += 0.6
        cv2.add(u8, flo, dst=u8)
        # ceiling light strips
        lights = np.zeros((H, W, 3), np.float32)
        for y, w_ in ((60, 860), (170, 760), (280, 660)):
            cv2.rectangle(lights, (int(CX - w_ / 2), y - 5), (int(CX + w_ / 2), y + 5), (1.0, 0.95, 0.85), -1)
        lights = cv2.GaussianBlur(lights, (0, 0), 14) * 1.4 + lights
        u8 = cv2.add(u8, (np.clip(lights, 0, 1) * 255).astype(np.uint8))
        # floor reflections of the ceiling lights
        refl = np.zeros((H, W, 3), np.float32)
        cv2.rectangle(refl, (int(CX - 300), y1 + 30), (int(CX + 300), H), (0.55, 0.5, 0.45), -1)
        refl = cv2.GaussianBlur(refl, (0, 0), 60) * 0.35
        u8 = cv2.add(u8, (refl * 255).astype(np.uint8))
        self.base = u8
        self.beacons = [(D[0] - 13, D[1] - 13), (D[2] + 13, D[1] - 13), (D[0] - 13, D[3] + 13), (D[2] + 13, D[3] + 13)]
        self.bspr = sprite(26, 'FF2A2A', 0.9)

    def _anim_hangar(self, img, t):
        self.stars.draw(img, t)
        for i, (x, y) in enumerate(self.beacons):
            on = (t * 8 / DUR + i * 0.5) % 1.0          # 8 blinks per loop, pairs alternate
            k = max(0.0, 1 - on * 2.2)
            dot(img, x, y, 7, (40 + int(60 * k), 40 + int(60 * k), 90 + int(165 * k)))
            if k > 0:
                blit_add(img, self.bspr, x, y, k)

    # ---------------------------------------------------- baseball park at night
    def _build_ballpark(self):
        rng = self.rng
        img = vgrad([(0, '04060E'), (600, '0A1128'), (1200, '17214A'), (1290, '26346A')])
        for x in (110, 970):
            glow(img, x, 225, 260, 'C9D8FF', 0.35, 1.3)
            glow(img, x, 225, 90, 'FFFFFF', 0.4, 1.5)
        haze = noise(rng, 2.5)
        mix(img, '9FB4FF', 0.08 * haze * (np.arange(H) < 1300)[:, None])
        # light beams down to the field
        beams = np.zeros((H, W), np.float32)
        for x in (110, 970):
            poly(beams, [(x - 90, 225), (x + 90, 225), (CX + (x - CX) * 0.1 + 260, 1900), (CX + (x - CX) * 0.1 - 260, 1900)], 1.0)
        beams = cv2.GaussianBlur(beams, (0, 0), 40)
        img += (beams * 0.06)[..., None] * C('DDE6FF')
        u8 = to_u8(img)
        Stars(rng, 0).bake_dust(u8, 160, 0, 700)
        # stands (bleachers) with crowd
        S0, S1 = 1285, 1555
        cv2.rectangle(u8, (0, S0), (W, S1), BGR('141A33'), -1)
        for i, y in enumerate(range(S0, S1, 22)):
            cv2.rectangle(u8, (0, y), (W, y + 20), BGR('1B2242' if i % 2 else '161C38'), -1)
        n = 5200
        cx, cy = rng.uniform(0, W, n), rng.uniform(S0 + 6, S1 - 4, n)
        pal = ['C0392B', '2E86C1', 'F4F6F7', 'F1C40F', '1E8449', '7D3C98', 'E67E22', 'D7DBDD', '34495E']
        for x, y, c, r in zip(cx, cy, rng.choice(pal, n), rng.uniform(2.2, 3.6, n)):
            k = 0.35 + 0.3 * (y - S0) / (S1 - S0)
            dot(u8, x, y, r, BGR(c, k))
        for y in (S0, S0 + 132):
            cv2.rectangle(u8, (0, y - 3), (W, y + 3), BGR('3B4466'), -1)       # rails / deck edge
        # light towers
        for x in (110, 970):
            cv2.rectangle(u8, (x - 7, 280), (x + 7, S0), BGR('2A2F40'), -1)
            cv2.rectangle(u8, (x - 112, 160), (x + 112, 290), BGR('1E2230'), -1)
            for i in range(7):
                for j in range(4):
                    lx, ly = x - 96 + i * 32, 178 + j * 30
                    dot(u8, lx, ly, 10, BGR('FFFDF2'))
        lamps = np.zeros((H, W, 3), np.float32)
        for x in (110, 970):
            cv2.rectangle(lamps, (x - 105, 168), (x + 105, 280), (0.9, 0.95, 1.0), -1)
        lamps = cv2.GaussianBlur(lamps, (0, 0), 22) * 0.9
        u8 = cv2.add(u8, (np.clip(lamps, 0, 1) * 255).astype(np.uint8))
        # yellow line, outfield wall, warning track, grass
        cv2.rectangle(u8, (0, S1), (W, S1 + 8), BGR('F4D03F'), -1)
        cv2.rectangle(u8, (0, S1 + 8), (W, 1650), BGR('0D3B2A'), -1)
        for x in range(0, W, 120):
            line(u8, (x, S1 + 8), (x, 1650), BGR('082A1D'), 2)
        txt = str(rng.choice([400, 405, 410, 395]))
        (tw, th), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_DUPLEX, 2.0, 4)
        cv2.putText(u8, txt, (int(CX - tw / 2), 1640), cv2.FONT_HERSHEY_DUPLEX, 2.0, BGR('F4F1E8', 0.9), 4, cv2.LINE_AA)
        cv2.rectangle(u8, (0, 1650), (W, 1705), BGR('7A4A2A'), -1)
        yy, xx = np.mgrid[1705:H, 0:W].astype(np.float32)
        th_ = np.arctan2(xx - CX, yy - 1100)
        stripe = (np.floor(th_ / 0.11) % 2).astype(np.float32)
        g1, g2 = C('1F7A35'), C('17602A')
        grass = g1 * stripe[..., None] + g2 * (1 - stripe[..., None])
        lit = 0.55 + 0.55 * np.exp(-((xx - CX) / 520) ** 2) * np.clip((yy - 1705) / 200, 0.3, 1)
        grass = grass * lit[..., None] * (0.92 + 0.16 * noise(rng, 30, 2, h=H - 1705))[..., None]
        u8[1705:] = to_u8(grass)
        self.base = u8
        k = 60
        self.fx, self.fy = rng.uniform(0, W, k), rng.uniform(S0 + 6, S1 - 6, k)
        self.ft = rng.uniform(0, DUR, k)
        self.fspr = sprite(6, 'FFFFFF', 0.8)
        self.lspr = sprite(70, 'E6EEFF', 0.25)

    def _anim_ballpark(self, img, t):
        for x, y, t0 in zip(self.fx, self.fy, self.ft):      # camera flashes in the crowd
            u = ((t - t0) % DUR) / 0.18
            if u < 1:
                dot(img, x, y, 3, (255, 255, 255))
                blit_add(img, self.fspr, x, y, 1 - u)
        for i, x in enumerate((110, 970)):                    # light banks shimmer a touch
            blit_add(img, self.lspr, x, 225, 0.5 + 0.5 * (0.5 + 0.5 * wave(t, 3 + i, i)))

    # ---------------------------------------------------- synthwave sunset
    def _build_synthwave(self):
        rng = self.rng
        hz = 1560.0
        img = vgrad([(0, '07021A'), (500, '1A0636'), (1000, '4A0D5E'), (1400, 'B0246E'), (hz, 'FF5E8A'), (H, '0A0318')])
        sx, sy, sr = CX, hz - 10, rng.uniform(320, 370)
        glow(img, sx, sy, sr * 1.35, 'FF3D8B', 0.45, 1.4)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt((xx - sx) ** 2 + (yy - sy) ** 2)
        v = np.clip((yy - (sy - sr)) / (2 * sr), 0, 1)
        sun = (C('FFE45E') * (1 - v)[..., None] + C('FF2E97') * v[..., None])
        rel = (yy - (sy - sr * 0.15)) / sr
        gaps = (rel > 0) & ((np.mod(rel * 9, 1.0)) < np.clip(rel * 0.9, 0, 0.6))
        a = (np.clip((sr - d) * 0.8, 0, 1) * (~gaps) * (yy < hz))[..., None]
        img = img * (1 - a) + sun * a
        u8 = to_u8(img)
        self.stars = Stars(rng, 90, 0, 900, tint=('FFFFFF', 'FFC6F0', 'C6E8FF'))
        self.stars.bake_dust(u8, 500, 0, 900)
        xs = np.arange(0, W + 10, 10, dtype=np.float32)
        for yb, amp, col, rimc in ((hz, 160, '2A0B4A', 'FF4FB8'), (hz, 90, '160628', 'B04BFF')):
            p = rng.uniform(0, TAU, 3)
            m = np.abs(np.sin(xs / W * math.pi * rng.uniform(2.5, 4) + p[0])) ** 1.5
            ys = yb - amp * (0.75 * m + 0.25 * np.abs(np.sin(xs / W * TAU * 4.3 + p[1])))
            pts = np.concatenate([np.stack([xs, ys], 1), [[W + 10, hz], [-10, hz]]])
            poly(u8, pts, BGR(col))
            cv2.polylines(u8, [np.round(np.stack([xs, ys], 1) * 16).astype(np.int32)], False, BGR(rimc, 0.8), 2, cv2.LINE_AA, 4)
        cv2.rectangle(u8, (0, int(hz)), (W, H), BGR('0A0318'), -1)
        hg = np.zeros((H, W, 3), np.float32)
        cv2.rectangle(hg, (0, int(hz) - 2), (W, int(hz) + 2), (1, 0.4, 1), -1)
        hg = cv2.GaussianBlur(hg, (0, 0), 18) * 1.2
        self.base = cv2.add(u8, (np.clip(hg, 0, 1) * 255).astype(np.uint8))
        self.hz = hz

    def _anim_synthwave(self, img, t):
        self.stars.draw(img, t, 0.8)
        hz = self.hz
        g = np.zeros((H - int(hz), W, 3), np.uint8)
        col = BGR('FF2BD6')
        for i in range(-16, 17):
            line(g, (CX + i * 34, 0), (CX + i * 300, H - hz), col, 2)
        s = (8 * t / DUR) % 1.0                        # 8 grid rows scroll past per loop
        for j in range(40):
            z = 0.35 + (j + 1 - s) * 0.5
            y = 330 / z
            if y < 2:
                break
            if y < H - hz:
                line(g, (0, y), (W, y), col, 2)
        sm = cv2.GaussianBlur(cv2.resize(g, (W // 4, (H - int(hz)) // 4)), (0, 0), 2)
        g = cv2.add(g, cv2.resize(sm, (W, H - int(hz))))
        reg = img[int(hz):]
        cv2.add(reg, g, dst=reg)

    # ---------------------------------------------------- rainy neon city
    def _build_neoncity(self):
        rng = self.rng
        img = vgrad([(0, '04030B'), (700, '0D0820'), (1400, '24103A'), (H, '120818')])
        haze = noise(rng, 2.2)
        mix(img, '5B1E6E', 0.25 * haze * np.clip((np.arange(H) - 800) / 900, 0, 1)[:, None])
        u8 = to_u8(img)
        win_cols = ['FFC46B', 'FFDFA0', '6BE0FF', 'FF7AC8', 'F8F8FF']
        self.flick = []
        signs = []
        for layer, (n, top, cb, lit, wc) in enumerate(((22, (650, 1250), '1B1530', 0.18, 0.45),
                                                       (13, (120, 1500), '0A0714', 0.28, 0.9))):
            x = -40.0
            while x < W + 40:
                bw = rng.uniform(70, 170) if layer else rng.uniform(50, 130)
                top_y = rng.uniform(*top)
                if layer and abs(x + bw / 2 - CX) < 360:
                    top_y = max(top_y, rng.uniform(1150, 1500))     # keep tall towers to the sides
                cv2.rectangle(u8, (int(x), int(top_y)), (int(x + bw), H), BGR(cb), -1)
                if layer and rng.random() < 0.5:                    # antenna
                    line(u8, (x + bw / 2, top_y), (x + bw / 2, top_y - rng.uniform(40, 120)), BGR(cb), 3)
                    self.flick.append((x + bw / 2, top_y - 100, 'tip'))
                ww, wh, gx, gy = 9, 12, rng.choice([16, 20, 24]), rng.choice([22, 26, 30])
                for wy in np.arange(top_y + 18, H - 20, gy):
                    for wx in np.arange(x + 10, x + bw - 14, gx):
                        if rng.random() < lit:
                            c = BGR(rng.choice(win_cols), wc * rng.uniform(0.5, 1.0))
                            cv2.rectangle(u8, (int(wx), int(wy)), (int(wx + ww), int(wy + wh)), c, -1)
                            if layer and rng.random() < 0.02:
                                self.flick.append((wx, wy, c))
                if layer and rng.random() < 0.45 and top_y < 1700:
                    sx = x + bw * rng.uniform(0.2, 0.6)
                    sy = rng.uniform(top_y + 40, min(H - 200, top_y + 500))
                    signs.append((sx, sy, rng.choice(['FF2A6D', '00E5FF', 'B967FF', 'FFD300'])))
                x += bw + rng.uniform(2, 20)
        gl = np.zeros((H, W, 3), np.float32)
        for sx, sy, c in signs:
            h_ = rng.uniform(110, 200)
            cv2.rectangle(gl, (int(sx), int(sy)), (int(sx + 22), int(sy + h_)), tuple(float(v) for v in C(c)[::-1]), -1)
        soft = cv2.GaussianBlur(gl, (0, 0), 26) * 1.6
        u8 = cv2.add(u8, (np.clip(soft + gl * 0.9, 0, 1) * 255).astype(np.uint8))
        self.base = u8
        self.signs = signs
        n = 420
        self.rx, self.ry = rng.uniform(-100, W + 100, n), rng.uniform(0, H + 120, n)
        self.rk, self.rl = rng.integers(5, 9, n), rng.uniform(22, 48, n)
        self.rb = rng.uniform(0.25, 0.6, n)
        self.tip = sprite(10, 'FF2A2A', 0.9)

    def _anim_neoncity(self, img, t):
        for x, y, c in self.flick:
            if c == 'tip':
                k = max(0.0, 1 - ((t * 5 / DUR + x / W) % 1.0) * 3)
                if k > 0:
                    blit_add(img, self.tip, x, y, k)
            elif wave(t, 7, x * 0.1) > 0.6:
                cv2.rectangle(img, (int(x), int(y)), (int(x + 9), int(y + 12)), (10, 8, 14), -1)
        slope = 0.18
        for x, y, k, L, b in zip(self.rx, self.ry, self.rk, self.rl, self.rb):   # rain
            yy = (y + k * (H + 120) * t / DUR) % (H + 120) - 60
            xx = x - slope * yy
            v = int(200 * b)
            line(img, (xx, yy), (xx - slope * L, yy - L), (v, int(v * 0.9), int(v * 0.8)), 1)


if __name__ == '__main__':      # preview: python3 scenes.py [seed]  -> _scenes.png contact sheet
    import sys
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    tiles = [cv2.resize(Scene(n, seed).frame(7.3), (270, 480), interpolation=cv2.INTER_AREA) for n in NAMES]
    sheet = np.vstack([np.hstack(tiles[:4]), np.hstack(tiles[4:])])
    cv2.imwrite('_scenes.png', sheet)
    print('wrote _scenes.png')
