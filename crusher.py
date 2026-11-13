#!/usr/bin/env python3
"""Crusher - an oddly satisfying physics loop drawn entirely in code.
Usage:  python3 crusher.py            full render -> crusher.mp4
        DRY=1 python3 crusher.py      physics only, prints the crush log
        SEED=7 MULT=8 python3 crusher.py
"""
import os, math, subprocess, wave
import numpy as np, cv2, pymunk


def hx(h):
    h = h.lstrip('#')
    return (int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16))  # BGR


# ----------------------------------------------------------------- CONFIG
W, H, FPS, DUR = 1080, 1920, 30, 20.0
SUB, ITER = 10, 12
SEED = int(os.environ.get('SEED', 4))
MULT = int(os.environ.get('MULT', 8))
DRY = os.environ.get('DRY') == '1'
OUT = os.environ.get('OUT', 'crusher.mp4')

CX, CY = 540.0, 960.0
RING_R, RING_W = 438.0, 5
BALL_R, FIRST_R, FIRST_POS = 9.0, 17.0, (400.0, 955.0)
MAX_IN_RING, CAP = 1500, 4000

GAP_OPEN = 420.0                 # distance between the two back plates when open
PW, PH, AL, AT = 42.0, 312.0, 118.0, 33.0   # plate w/h, arm length/thickness
CLOSE_T, OPEN_T = 0.5, 1.2
PINCHES = [0.7, 3.1, 5.5, 7.9, 10.3, 12.7, 15.1]
SHRINK = (16.2, 17.0)            # ring collapses into the capsule
FINALE = 17.5
LOOP_PINCH, LOOP_OPEN_T = 19.3, 0.7
CAPSULE = (105.0, 118.0)

PULL, VMAX = float(os.environ.get('PULL', 2.0)), 1100.0
EL_BALL, EL_MACHINE, EL_WALL = 0.95, 0.6, 1.0
SPAWN_FRAMES, SPAWN_SPEED, SPAWN_FAN = 9, (250.0, 520.0), 110.0
BLAST_SPEED = (650.0, 1100.0)

BLACK, WHITE = (0, 0, 0), (255, 255, 255)
STEEL, EDGE, HI, PAD, BOLT = hx('8E9198'), hx('5C5F66'), hx('B9BCC2'), hx('E9A23B'), hx('2E3034')
WAVES = [hx(c) for c in ('FF8A1F', '4B2BFF', '3BFF3B', 'FF2D7A', '22C3F5',
                         'FFF000', 'A01EFF', '1FF58A', 'FF3B1F')]
RED = len(WAVES) - 1

ALLP = [(p, OPEN_T, 'n') for p in PINCHES] + [(FINALE, OPEN_T, 'f'), (LOOP_PINCH, LOOP_OPEN_T, 'l')]
EPS = 1e-9


def gap(t):
    for p, ot, _ in ALLP:
        if p - CLOSE_T <= t < p:
            u = (t - (p - CLOSE_T)) / CLOSE_T
            return GAP_OPEN * (1 - u ** 3)            # ease-in cubic slam
        if p <= t < p + ot:
            u = (t - p) / ot
            return GAP_OPEN * (u * u * (3 - 2 * u))   # smooth reopen
    return GAP_OPEN


def ring_shape(t):
    """(half-width, half-height, fill 0..1) of the ring, or None when it is gone."""
    if t < SHRINK[0]:
        return RING_R, RING_R, 0.0
    if t < SHRINK[1]:
        u = (t - SHRINK[0]) / (SHRINK[1] - SHRINK[0])
        e = u * u * (3 - 2 * u)
        return RING_R + (CAPSULE[0] - RING_R) * e, RING_R + (CAPSULE[1] - RING_R) * e, e * e
    if t < FINALE:
        a = min(CAPSULE[0], gap(t) / 2)
        return (a, CAPSULE[1], 1.0) if a > 0.6 else None
    if t < LOOP_PINCH:
        return None
    u = min(1.0, (t - LOOP_PINCH) / 0.62)
    r = RING_R * (1 - (1 - u) ** 3)
    return (r, r, 0.0) if r > 1 else None


# ----------------------------------------------------------------- PHYSICS
class Sim:
    def __init__(s):
        s.rng = np.random.default_rng(SEED)
        sp = s.space = pymunk.Space()
        sp.gravity, sp.damping, sp.iterations = (0, 0), 1.0, ITER
        n, R = 160, RING_R + 3
        for i in range(n):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            seg = pymunk.Segment(sp.static_body, (CX + R * math.cos(a0), CY + R * math.sin(a0)),
                                 (CX + R * math.cos(a1), CY + R * math.sin(a1)), 3)
            seg.elasticity, seg.friction = EL_WALL, 0
            sp.add(seg)
        s.jaws = []
        for sgn in (1, -1):   # +1 = left jaw (arms point +x), -1 = right jaw
            b = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
            shapes = []
            for u0, y0, u1, y1 in ((-PW, -PH / 2, 0, PH / 2), (0, -PH / 2, AL, -PH / 2 + AT),
                                   (0, PH / 2 - AT, AL, PH / 2)):
                xa, xb = sorted((sgn * u0, sgn * u1))
                sh = pymunk.Poly(b, [(xa, y0), (xb, y0), (xb, y1), (xa, y1)])
                sh.elasticity, sh.friction = EL_MACHINE, 0
                shapes.append(sh)
            b.position = (CX - sgn * GAP_OPEN / 2, CY)
            sp.add(b, *shapes)
            s.jaws.append((b, sgn))
        s.balls = []          # [body, shape, r, color]
        s.captured = []       # (fx, y, r, color) - sealed in the jaws, drawn squashed
        s.pending = []        # [remaining, frames_left, color, total]
        s.sealed, s.np = False, 0
        s.absorbed, s.parts, s.part_pending = 0, None, None
        s.log, s.spawn_events, s.flash_frame = [], [], None
        s.total_spawned = 1
        s.add_ball(FIRST_POS, (0, 0), FIRST_R, 0)

    def add_ball(s, pos, vel, r, ci):
        b = pymunk.Body(1.0, pymunk.moment_for_circle(1.0, 0, r))
        b.position, b.velocity = pos, vel
        sh = pymunk.Circle(b, r)
        sh.elasticity, sh.friction = EL_BALL, 0
        s.space.add(b, sh)
        s.balls.append([b, sh, r, ci])

    def remove(s, bl):
        s.space.remove(bl[0], bl[1])

    def begin_frame(s, t, f):
        g = gap(t)
        # stream out newly multiplied balls just outside the jaws
        for pend in s.pending:
            k = math.ceil(pend[0] / pend[1])
            pend[0] -= k
            pend[1] -= 1
            depth = min(170.0, 20 + 0.2 * pend[3])
            yspan = min(270.0, 150 + 0.15 * pend[3])
            for _ in range(k):
                sg = -1 if s.rng.random() < 0.5 else 1
                x = CX + sg * (g / 2 + PW + BALL_R + 2 + s.rng.random() * depth)
                y = CY + s.rng.uniform(-yspan, yspan)
                d = math.hypot(x - CX, y - CY)
                lim = RING_R - BALL_R - 4
                if d > lim:
                    x, y = CX + (x - CX) * lim / d, CY + (y - CY) * lim / d
                ang = math.radians(s.rng.uniform(-SPAWN_FAN / 2, SPAWN_FAN / 2))
                v = s.rng.uniform(*SPAWN_SPEED)
                s.add_ball((x, y), (sg * math.cos(ang) * v, math.sin(ang) * v), BALL_R, pend[2])
        s.pending = [p for p in s.pending if p[1] > 0 and p[0] > 0]
        # the collapsing ring swallows every ball it passes
        if t >= SHRINK[0] and s.balls:
            sh = ring_shape(t)
            keep = []
            for bl in s.balls:
                gone = True
                if t < SHRINK[1] and sh:
                    a, b_, _ = sh
                    rc = min(a, b_)
                    p = bl[0].position
                    qx, qy = abs(p.x - CX) - (a - rc), abs(p.y - CY) - (b_ - rc)
                    d = math.hypot(max(qx, 0), max(qy, 0)) + min(max(qx, qy), 0) - rc
                    gone = d > -bl[2]
                if gone:
                    s.remove(bl)
                    s.absorbed += 1
                else:
                    keep.append(bl)
            s.balls = keep
        # finale particles (no collisions, they just blast off screen)
        if s.parts is not None:
            s.parts[0] += s.parts[1] / FPS
        if s.part_pending:
            k = math.ceil(s.part_pending[0] / s.part_pending[1])
            s.part_pending[0] -= k
            s.part_pending[1] -= 1
            ang = s.rng.uniform(0, 2 * math.pi, k)
            sp = s.rng.uniform(*BLAST_SPEED, k)
            vel = np.stack([np.cos(ang) * sp, np.sin(ang) * sp], 1)
            pos = np.stack([np.full(k, CX), CY + s.rng.uniform(-120, 120, k)], 1) + vel * s.rng.uniform(0, 1 / FPS, (k, 1))
            if s.parts is None:
                s.parts = [pos, vel]
            else:
                s.parts = [np.vstack([s.parts[0], pos]), np.vstack([s.parts[1], vel])]
            if s.part_pending[1] <= 0 or s.part_pending[0] <= 0:
                s.part_pending = None

    def advance(s, t):
        dt = 1.0 / (FPS * SUB)
        for k in range(SUB):
            ts = t + k * dt
            g0, g1 = gap(ts), gap(ts + dt)
            for b, sgn in s.jaws:   # kinematic: set position AND velocity every substep
                b.position = (CX - sgn * g0 / 2, CY)
                b.velocity = (-sgn * (g1 - g0) / 2 / dt, 0)
            pull = PULL * dt if 0.2 <= ts < SHRINK[0] else 0.0
            for bl in s.balls:
                body = bl[0]
                v, p = body.velocity, body.position
                vx, vy = v.x, v.y
                sp2 = vx * vx + vy * vy
                if sp2 > VMAX * VMAX:
                    k_ = VMAX / math.sqrt(sp2)
                    vx, vy = vx * k_, vy * k_
                body.velocity = (vx - pull * (p.x - CX), vy - pull * (p.y - CY))
            s.space.step(dt)
            if s.np >= len(ALLP):
                continue
            p, _, kind = ALLP[s.np]
            if not s.sealed and ts >= p - CLOSE_T - EPS and g1 <= 2 * AL:
                s.sealed = True      # arms overlap: the box is sealed
                L, keep = CX - g1 / 2, []
                for bl in s.balls:
                    pos = bl[0].position
                    if L - 2 <= pos.x <= CX + g1 / 2 + 2 and abs(pos.y - CY) <= PH / 2:
                        s.captured.append((min(1, max(0, (pos.x - L) / g1)), pos.y, bl[2], bl[3]))
                        s.remove(bl)
                    else:
                        keep.append(bl)
                s.balls = keep
            if ts + dt >= p - EPS:   # the pinch
                if kind == 'n':
                    crushed = len(s.captured)
                    n = max(0, min(crushed * MULT, MAX_IN_RING - len(s.balls)))
                    ci = (s.np + 1) % len(WAVES)
                    if n:
                        s.pending.append([n, SPAWN_FRAMES, ci, n])
                    s.total_spawned += n
                    note = '' if n == crushed * MULT else '  [ring full, capped]'
                    s.log.append(f'pinch {s.np + 1} @ {p:5.1f}s: crushed {crushed:4d} -> spawned {n:4d} (x{MULT}), '
                                 f'in ring {len(s.balls) + n:4d}{note}')
                    s.spawn_events.append((p, n))
                elif kind == 'f':
                    n = min(CAP, s.absorbed * MULT)
                    s.part_pending = [n, 6]
                    s.flash_frame = int(round(p * FPS))
                    s.log.append(f'finale  @ {p:5.1f}s: ring swallowed {s.absorbed} -> red wave {n} (x{MULT}, cap {CAP})')
                    s.spawn_events.append((p, n))
                s.captured = []
                s.sealed = False
                s.np += 1


# ----------------------------------------------------------------- DRAWING
def rr_pts(x0, y0, x1, y1, rad, n=8):
    rad = max(0.0, min(rad, (x1 - x0) / 2, (y1 - y0) / 2))
    pts = []
    for cx_, cy_, a0 in ((x1 - rad, y0 + rad, -90), (x1 - rad, y1 - rad, 0),
                         (x0 + rad, y1 - rad, 90), (x0 + rad, y0 + rad, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx_ + rad * math.cos(a), cy_ + rad * math.sin(a)))
    return np.array(pts)


def fill(img, pts, col):
    cv2.fillPoly(img, [np.round(pts * 16).astype(np.int32)], col, cv2.LINE_AA, 4)


def circ(img, x, y, r, col):
    cv2.circle(img, (int(round(x * 16)), int(round(y * 16))), max(1, int(round(r * 16))), col, -1, cv2.LINE_AA, 4)


def hline(img, x0, x1, y, col, th=2):
    cv2.line(img, (int(x0 * 16), int(y * 16)), (int(x1 * 16), int(y * 16)), col, th, cv2.LINE_AA, 4)


def draw_rail(img, face, sgn):
    xo = face - sgn * PW
    xa, xb = (0.0, xo) if sgn > 0 else (xo, float(W))
    fill(img, rr_pts(xa, CY - 8, xb, CY + 8, 0), EDGE)
    fill(img, rr_pts(xa, CY - 6, xb, CY + 6, 0), STEEL)
    hline(img, xa, xb, CY - 5, HI)
    ca, cb = (-12.0, 18.0) if sgn > 0 else (W - 18.0, W + 12.0)
    fill(img, rr_pts(ca, CY - 26, cb, CY + 26, 9), EDGE)
    fill(img, rr_pts(ca + 2, CY - 24, cb - 2, CY + 24, 7), STEEL)


def draw_jaw(img, face, sgn):
    hp = PH / 2

    def R(u0, y0, u1, y1, rad, col, inset=0.0):
        xa, xb = sorted((face + sgn * u0, face + sgn * u1))
        fill(img, rr_pts(xa + inset, CY + y0 + inset, xb - inset, CY + y1 - inset, rad), col)

    parts = ((-PW, -hp, 0, hp), (-6, -hp, AL, -hp + AT), (-6, hp - AT, AL, hp))
    for p in parts:
        R(*p, 7, EDGE)
    for p in parts:
        R(*p, 5, STEEL, 2)
    xs = sorted((face + sgn * (-PW + 7), face + sgn * (AL - 7)))
    hline(img, xs[0], xs[1], CY - hp + 3.5, HI)
    xs = sorted((face + sgn * 3, face + sgn * (AL - 7)))
    hline(img, xs[0], xs[1], CY + hp - AT + 3.5, HI)
    # orange pads on every face that touches balls
    R(-5, -hp + AT + 2, 0, hp - AT - 2, 2, PAD)
    R(2, -hp + AT - 5, AL - 3, -hp + AT, 2, PAD)
    R(2, hp - AT, AL - 3, hp - AT + 5, 2, PAD)
    R(AL - 5, -hp + 4, AL, -hp + AT - 7, 2, PAD)
    R(AL - 5, hp - AT + 7, AL, hp - 4, 2, PAD)
    for y in (-105, 0, 105):
        circ(img, face - sgn * PW / 2, CY + y, 4.5, BOLT)
    for u in (30, 62, 94):
        circ(img, face + sgn * u, CY - hp + 14, 3.2, BOLT)
        circ(img, face + sgn * u, CY + hp - 12, 3.2, BOLT)


def draw(sim, t, f):
    img = np.zeros((H, W, 3), np.uint8)
    g = gap(t)
    sh = ring_shape(t)
    collapsing = SHRINK[0] <= t < FINALE

    def draw_ring():
        if not sh:
            return
        a, b, fa = sh
        pts = rr_pts(CX - a, CY - b, CX + a, CY + b, min(a, b), 40)
        if fa > 0:
            if fa >= 1:
                fill(img, pts, WHITE)
            else:
                ov = img.copy()
                fill(ov, pts, WHITE)
                cv2.addWeighted(ov, fa, img, 1 - fa, 0, img)
        cv2.polylines(img, [np.round(pts * 16).astype(np.int32)], True, WHITE, RING_W, cv2.LINE_AA, 4)

    if not collapsing:
        draw_ring()
    for _, sgn in sim.jaws:
        draw_rail(img, CX - sgn * g / 2, sgn)
    for body, _, r, ci in sim.balls:
        p = body.position
        circ(img, p.x, p.y, r, WAVES[ci])
    if sim.parts is not None:
        P = sim.parts[0]
        ok = (P[:, 0] > -20) & (P[:, 0] < W + 20) & (P[:, 1] > -20) & (P[:, 1] < H + 20)
        for x, y in P[ok]:
            circ(img, x, y, BALL_R, WAVES[RED])
    if collapsing:
        draw_ring()
    if sim.captured:      # squashed balls inside the sealed jaws
        k = max(g / (2 * AL), 0.05)
        L = CX - g / 2
        for fx, y, r, ci in sim.captured:
            cv2.ellipse(img, (int((L + fx * g) * 16), int(y * 16)),
                        (max(8, int(r * k * 16)), int(r * (1 + 0.5 * (1 - k)) * 16)),
                        0, 0, 360, WAVES[ci], -1, cv2.LINE_AA, 4)
    if t >= 19.6:         # the lonely orange ball returns so the loop is seamless
        u = min(1.0, (t - 19.6) / 0.33)
        c1, c3 = 1.70158, 2.70158
        circ(img, FIRST_POS[0], FIRST_POS[1], FIRST_R * (1 + c3 * (u - 1) ** 3 + c1 * (u - 1) ** 2), WAVES[0])
    for _, sgn in sim.jaws:
        draw_jaw(img, CX - sgn * g / 2, sgn)
    if sim.flash_frame is not None and 0 <= f - sim.flash_frame < 5:
        a = 0.55 * (1 - (f - sim.flash_frame) / 5)
        img = cv2.addWeighted(img, 1 - a, np.full_like(img, 255), a, 0)
    return img


# ----------------------------------------------------------------- SOUND
def make_audio(sim, path):
    sr = 44100
    n = int(DUR * sr)
    a = np.zeros(n + 3 * sr)
    rng = np.random.default_rng(1)

    def add(t0, sig, gain):
        i = max(0, int(round(t0 * sr)))
        a[i:i + len(sig)] += sig * gain

    for p, _, _ in ALLP:
        tt = np.arange(int(CLOSE_T * sr)) / sr                       # jaw whir 120 -> 380 Hz
        ph = 2 * np.pi * np.cumsum(120 + 260 * tt / CLOSE_T) / sr
        add(p - CLOSE_T, (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph)) * (0.12 + 0.88 * (tt / CLOSE_T) ** 2), 0.2)
        tt = np.arange(int(0.3 * sr)) / sr                           # metal clunk
        add(p, rng.standard_normal(len(tt)) * np.exp(-tt / 0.012) * 0.7 + np.sin(2 * np.pi * 85 * tt) * np.exp(-tt / 0.07)
            + 0.35 * np.sin(2 * np.pi * 1750 * tt) * np.exp(-tt / 0.03), 0.7)
    for p, cnt in sim.spawn_events:                                  # 14 tiny pops, 22 ms apart
        if cnt <= 0:
            continue
        for j in range(14):
            tt = np.arange(int(0.04 * sr)) / sr
            add(p + 0.035 + j * 0.022, np.sin(2 * np.pi * rng.uniform(500, 1500) * tt) * np.exp(-tt / 0.008),
                0.22 + 0.14 * min(1, cnt / 500))
    tt = np.arange(int(1.6 * sr)) / sr                               # deep boom on the finale
    ph = 2 * np.pi * np.cumsum(55 * np.exp(-tt * 0.6) + 28) / sr
    noise = np.convolve(rng.standard_normal(len(tt)), np.ones(200) / 200, 'same') * 8
    add(FINALE, np.sin(ph) * np.exp(-tt / 0.45) + 0.5 * noise * np.exp(-tt / 0.25), 1.3)
    tail = a[n:]
    a = a[:n]
    a[:len(tail)] += tail                                            # wrap the tail so the loop is clean
    a *= 10 ** (-1.5 / 20) / np.max(np.abs(a))
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((a * 32767).astype(np.int16).tobytes())


# ----------------------------------------------------------------- MAIN
def main():
    sim = Sim()
    nframes = int(DUR * FPS)
    pipe = None
    if not DRY:
        pipe = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24',
                                 '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '17',
                                 '-pix_fmt', 'yuv420p', '-preset', 'veryfast', '_video.mp4'], stdin=subprocess.PIPE)
    for f in range(nframes):
        t = f / FPS
        sim.begin_frame(t, f)
        if pipe:
            pipe.stdin.write(draw(sim, t, f).tobytes())
        sim.advance(t)
    print(f'seed {SEED}, pull {PULL}')
    print('\n'.join(sim.log))
    if pipe:
        pipe.stdin.close()
        pipe.wait()
        make_audio(sim, '_audio.wav')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', '_video.mp4', '-i', '_audio.wav', '-c:v', 'copy',
                        '-c:a', 'aac', '-b:a', '192k', '-shortest', OUT], check=True)
        os.remove('_video.mp4')
        os.remove('_audio.wav')
        print('wrote', OUT)


if __name__ == '__main__':
    main()
