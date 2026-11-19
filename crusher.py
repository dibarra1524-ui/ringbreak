#!/usr/bin/env python3
"""Crusher - an oddly satisfying physics loop drawn entirely in code.
Usage:  python3 crusher.py            full render -> crusher.mp4
        DRY=1 python3 crusher.py      physics only, prints the crush log
        SEED=7 MULT=8 ROT=3 CRF=22 python3 crusher.py
        RECIPE='{"arena":"hex","fx":"trail"}' python3 crusher.py   (see learn.py for every trait)
"""
import os, math, json, subprocess, wave
import numpy as np, cv2, pymunk
import scenes


def hx(h):
    h = h.lstrip('#')
    return (int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16))  # BGR


# ----------------------------------------------------------------- CONFIG
W, H, FPS, DUR = 1080, 1920, 30, 20.0
SUB, ITER = 10, 12
SEED = int(os.environ.get('SEED', 4))
RECIPE = json.loads(os.environ.get('RECIPE') or '{}')   # the look of this video, chosen by learn.py
MULT = int(os.environ.get('MULT', RECIPE.get('mult', 8)))
DRY = os.environ.get('DRY') == '1'
OUT = os.environ.get('OUT', 'crusher.mp4')

CX, CY = 540.0, 960.0
RING_R, RING_W = 438.0, 5
BALL_R, FIRST_R, FIRST_POS = float(RECIPE.get('ball_r', 9.0)), 17.0, (400.0, 955.0)
MAX_IN_RING, CAP = 1500, 4000

GAP_OPEN = 420.0                 # distance between the two back plates when open
PW, PH, AL, AT = 42.0, 312.0, 118.0, 33.0   # plate w/h, arm length/thickness
CLOSE_T, OPEN_T = 0.5, 1.2
PINCHES = [0.7, 3.1, 5.5, 7.9, 10.3, 12.7, 15.1]
SHRINK = (16.2, 17.0)            # ring collapses into the capsule
FINALE = 17.5
LOOP_PINCH, LOOP_OPEN_T = 19.3, 0.7
CAPSULE = (105.0, 118.0)

PULL, VMAX = float(os.environ.get('PULL', RECIPE.get('pull', 2.0))), 1100.0
BOUNCE = RECIPE.get('bounce', 'normal')    # normal | bouncy | soft
EL_BALL, EL_MACHINE, EL_WALL = {'normal': (0.95, 0.6, 1.0), 'bouncy': (1.0, 0.8, 1.0), 'soft': (0.7, 0.4, 0.85)}[BOUNCE]
FIELD = RECIPE.get('field', 'pull')        # pull | vortex | gravity | tumble | pulse
FORCE = float(RECIPE.get('force', 1.0))    # strength of the field, mutated by learn.py
PEGS = RECIPE.get('pegs', 'none')          # none | arc | field
ASSIST = float(os.environ.get('ASSIST', RECIPE.get('assist', 1.4)))
SPAWN_FRAMES, SPAWN_SPEED, SPAWN_FAN = 9, (250.0, 520.0), 110.0
BLAST_SPEED = (650.0, 1100.0)

BLACK, WHITE = (0, 0, 0), (255, 255, 255)
STEEL, EDGE, HI, PAD, BOLT = hx('8E9198'), hx('5C5F66'), hx('B9BCC2'), hx('E9A23B'), hx('2E3034')
PALETTES = {   # 9 wave colors each, the last one is the finale blast
    'neon':   ('FF8A1F', '4B2BFF', '3BFF3B', 'FF2D7A', '22C3F5', 'FFF000', 'A01EFF', '1FF58A', 'FF3B1F'),
    'pastel': ('FFB3BA', 'BAE1FF', 'BAFFC9', 'FFDFBA', 'E0BBFF', 'FFFFBA', 'B5EAD7', 'FFC8DD', 'FF9AA2'),
    'fire':   ('FFE066', 'FFC233', 'FFA41F', 'FF861F', 'FF6A1F', 'FF4D1F', 'FF2E2E', 'E0115F', 'FFF3B0'),
    'ice':    ('E0FBFF', 'A5F3FF', '67E8F9', '38BDF8', '60A5FA', '818CF8', 'A78BFA', 'C4B5FD', 'FFFFFF'),
    'candy':  ('FF5FA2', 'FFD23F', '3BCEAC', '9B5DE5', 'F15BB5', 'FEE440', '00BBF9', '00F5D4', 'FF3366'),
    'mono':   ('FFFFFF', 'DADADA', 'FFFFFF', 'C4C4C4', 'FFFFFF', 'DADADA', 'FFFFFF', 'C4C4C4', 'FF2D2D'),
}
BGS = {'black': '000000', 'navy': '070B1F', 'plum': '160821', 'forest': '05130D'}
WAVES = [hx(c) for c in PALETTES[RECIPE.get('palette', 'neon')]]
BGNAME = RECIPE.get('bg', 'black')
THEME = scenes.STYLES.get(BGNAME)            # a themed, animated scene (see scenes.py) instead of a flat colour
BG = hx(BGS.get(BGNAME, '000000'))
RING_COL, RING_GLOW, RIM, WINDOW, COUNTER_COL = WHITE, None, 'plain', 1.0, 'FFFFFF'
if THEME:   # restyle the machine to match the scene
    STEEL, EDGE, HI, BOLT = (hx(c) for c in THEME['jaw'])
    PAD, RING_COL = hx(THEME['pad']), hx(THEME['ring'])
    RING_GLOW = hx(THEME['glow']) if THEME['glow'] else None
    RIM, WINDOW, COUNTER_COL = THEME['rim'], THEME['window'], THEME['counter']
SCENE = None
STITCH, RIM_DARK, RIM_MID, RIM_HI = hx('D22B2B'), hx('262C36'), hx('4A5466'), hx('9AA6B8')
ARENA = RECIPE.get('arena', 'circle')        # outline of the ring
SPIN = int(RECIPE.get('spin', 0)) if ARENA != 'circle' else 0   # symmetry steps the outline turns per loop
ANGLE = float(RECIPE.get('angle', 0))        # the whole machine is drawn turned by this many degrees
FX = RECIPE.get('fx', 'none')                # none | trail | glow | trail+glow
BALL = RECIPE.get('ball', 'solid')           # solid | hollow | shine
SHAKE = int(RECIPE.get('shake', 0))
COUNTER = int(RECIPE.get('counter', 0))
SOUND = RECIPE.get('sound', 'classic')       # classic | penta
TRAIL_DECAY = 0.80
ROT = int(os.environ.get('ROT', 0)) % len(WAVES)   # rotate the color order for variety
WAVES = WAVES[ROT:] + WAVES[:ROT]
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


# ----------------------------------------------------------------- ARENA
NA = 360
TH = np.arange(NA) * 2 * math.pi / NA
COS_TH, SIN_TH = np.cos(TH), np.sin(TH)


def _ngon(k, rc, ph):
    step = 2 * math.pi / k
    r = rc * math.cos(math.pi / k) / np.cos(np.mod(TH - ph, step) - step / 2)
    w = 7                                             # round the corners a little
    return np.convolve(np.concatenate([r[-w:], r, r[:w]]), np.ones(w) / w, 'same')[w:-w]


def _radial(pts):
    """Radius of a convex outline around the centre, sampled at TH."""
    p0, p1 = pts, np.roll(pts, -1, 0)
    e = p1 - p0
    nx, ny = e[:, 1], -e[:, 0]
    num = nx * p0[:, 0] + ny * p0[:, 1]
    sg = np.sign(num.sum())
    nx, ny, num = nx * sg, ny * sg, num * sg
    den = np.outer(COS_TH, nx) + np.outer(SIN_TH, ny)
    tt = np.where(den > 1e-9, num[None, :] / np.where(den > 1e-9, den, 1), np.inf)
    return tt.min(1)


ARENAS = {   # name -> (radii at TH, symmetry order)
    'circle':   (np.full(NA, RING_R), 1),
    'square':   (_ngon(4, 520.0, math.pi / 4), 4),
    'diamond':  (_ngon(4, 500.0, 0.0), 4),
    'pent':     (_ngon(5, 470.0, -math.pi / 2), 5),
    'hex':      (_ngon(6, 462.0, math.pi / 6), 6),
    'oct':      (_ngon(8, 452.0, math.pi / 8), 8),
    'squircle': (410.0 / (np.abs(COS_TH) ** 4 + np.abs(SIN_TH) ** 4) ** 0.25, 4),
}
RAD, SYM = ARENAS[ARENA]
OMEGA = SPIN * (2 * math.pi / SYM) / DUR              # whole symmetry steps per loop keep the loop seamless


def rr_pts(x0, y0, x1, y1, rad, n=8):
    rad = max(0.0, min(rad, (x1 - x0) / 2, (y1 - y0) / 2))
    pts = []
    for cx_, cy_, a0 in ((x1 - rad, y0 + rad, -90), (x1 - rad, y1 - rad, 0),
                         (x0 + rad, y1 - rad, 90), (x0 + rad, y0 + rad, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx_ + rad * math.cos(a), cy_ + rad * math.sin(a)))
    return np.array(pts)


CAPR = _radial(rr_pts(-CAPSULE[0], -CAPSULE[1], CAPSULE[0], CAPSULE[1], CAPSULE[0], 40))


def spun(t):
    return RAD if not OMEGA else np.interp(TH - OMEGA * t, TH, RAD, period=2 * math.pi)


def ring_radii(t):
    """(radii at TH, fill 0..1) while the ring is a free outline, else None."""
    if t < SHRINK[0]:
        return spun(t), 0.0
    if t < SHRINK[1]:
        u = (t - SHRINK[0]) / (SHRINK[1] - SHRINK[0])
        e = u * u * (3 - 2 * u)
        return (1 - e) * spun(t) + e * CAPR, e * e
    if t < LOOP_PINCH:
        return None
    u = min(1.0, (t - LOOP_PINCH) / 0.62)
    k = 1 - (1 - u) ** 3
    return (spun(t) * k, 0.0) if k * RING_R > 1 else None


def ring_pts(t):
    """(outline points, fill) of the ring at time t, or None when it is gone."""
    rr = ring_radii(t)
    if rr is not None:
        return np.stack([CX + rr[0] * COS_TH, CY + rr[0] * SIN_TH], 1), rr[1]
    if SHRINK[1] <= t < FINALE:
        a = min(CAPSULE[0], gap(t) / 2)
        if a > 0.6:
            return rr_pts(CX - a, CY - CAPSULE[1], CX + a, CY + CAPSULE[1], min(a, CAPSULE[1]), 40), 1.0
    return None


def rad_at(rad, x, y):
    return rad[int(round(math.atan2(y - CY, x - CX) / (2 * math.pi) * NA)) % NA]


# ----------------------------------------------------------------- PEGS
def peg_layout():
    """Small fixed bumpers inside the arena, kept out of the jaws' path."""
    if PEGS == 'arc':
        pts = [(300, a) for a in (-122, -90, -58, 58, 90, 122)] + [(200, -90), (200, 90)]
        r = 14.0
    elif PEGS == 'field':
        pts = [(rr, a) for rr, a0 in ((215, -90), (300, -90), (215, 90), (300, 90))
               for a in (a0 - 36, a0, a0 + 36)] + [(330, a) for a in (-145, -35, 35, 145)]
        r = 10.0
    else:
        return []
    inner = float(RAD.min())
    out = []
    for rr, a in pts:
        x, y = CX + rr * math.cos(math.radians(a)), CY + rr * math.sin(math.radians(a))
        if math.hypot(x - CX, y - CY) + r < inner - 14 and abs(y - CY) > PH / 2 + r + 18:
            out.append((x, y, r))
    return out


# ----------------------------------------------------------------- PHYSICS
class Sim:
    def __init__(s):
        s.rng = np.random.default_rng(SEED)
        sp = s.space = pymunk.Space()
        sp.gravity, sp.damping, sp.iterations = (0, 0), 1.0, ITER
        s.wall = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        s.wall.position = (CX, CY)
        wx, wy = (RAD + 3) * COS_TH, (RAD + 3) * SIN_TH
        segs = []
        for i in range(0, NA, 2):
            j = (i + 2) % NA
            seg = pymunk.Segment(s.wall, (wx[i], wy[i]), (wx[j], wy[j]), 3)
            seg.elasticity, seg.friction = EL_WALL, 0
            segs.append(seg)
        sp.add(s.wall, *segs)
        s.trail = None
        s.pegs = []           # [x, y, r, shape or None, last hit time, hit color]
        for x, y, r in peg_layout():
            c = pymunk.Circle(sp.static_body, r, (x, y))
            c.elasticity, c.friction = 1.0, 0
            sp.add(c)
            s.pegs.append([x, y, r, c, -9.0, 0])
        s.peg_hits = []
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
        s.early_cap = False
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
                lim = rad_at(spun(t), x, y) - BALL_R - 4
                if d > lim:
                    x, y = CX + (x - CX) * lim / d, CY + (y - CY) * lim / d
                ang = math.radians(s.rng.uniform(-SPAWN_FAN / 2, SPAWN_FAN / 2))
                v = s.rng.uniform(*SPAWN_SPEED)
                s.add_ball((x, y), (sg * math.cos(ang) * v, math.sin(ang) * v), BALL_R, pend[2])
        s.pending = [p for p in s.pending if p[1] > 0 and p[0] > 0]
        # pegs light up when a ball touches them, and vanish as the collapsing ring passes them
        if s.pegs and s.balls:
            P = np.array([(bl[0].position.x, bl[0].position.y) for bl in s.balls])
            R_ = np.array([bl[2] for bl in s.balls])
            for pg in s.pegs:
                if pg[3] is None:
                    continue
                d = np.hypot(P[:, 0] - pg[0], P[:, 1] - pg[1]) - R_ - pg[2]
                i = int(np.argmin(d))
                if d[i] < 2.5:
                    if t - pg[4] > 0.09:
                        s.peg_hits.append(t)
                    pg[4], pg[5] = t, s.balls[i][3]
        if t >= SHRINK[0]:
            rr = ring_radii(t)
            for pg in s.pegs:
                if pg[3] is not None and (rr is None or rad_at(rr[0], pg[0], pg[1]) < math.hypot(pg[0] - CX, pg[1] - CY) + pg[2]):
                    s.space.remove(pg[3])
                    pg[3] = None
        # the collapsing ring swallows every ball it passes
        if t >= SHRINK[0] and s.balls:
            rr = ring_radii(t) if t < SHRINK[1] else None
            keep = []
            for bl in s.balls:
                gone = True
                if rr is not None:
                    p = bl[0].position
                    gone = math.hypot(p.x - CX, p.y - CY) > rad_at(rr[0], p.x, p.y) - bl[2]
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
            s.wall.angle, s.wall.angular_velocity = OMEGA * ts, OMEGA
            for b, sgn in s.jaws:   # kinematic: set position AND velocity every substep
                b.position = (CX - sgn * g0 / 2, CY)
                b.velocity = (-sgn * (g1 - g0) / 2 / dt, 0)
            on = 0.2 <= ts < SHRINK[0]
            pull, gx, gy, tang = (PULL * dt if on else 0.0), 0.0, 0.0, 0.0
            if on and FIELD == 'pulse':      # the pull breathes in and out 4 times per loop
                pull *= 1 + 0.85 * FORCE * math.sin(2 * math.pi * 4 * ts / DUR)
            elif on and FIELD == 'vortex':   # everything swirls around the centre
                tang = 340.0 * FORCE * dt
            elif on and FIELD in ('gravity', 'tumble'):   # gravity pointing down the screen, or turning once per loop
                ga = math.radians(ANGLE) + (2 * math.pi * ts / DUR if FIELD == 'tumble' else 0.0)
                gx, gy = 650.0 * FORCE * dt * math.sin(ga), 650.0 * FORCE * dt * math.cos(ga)
                pull *= 0.55
            if on and any(kd == 'n' and p_ - 1.0 <= ts < p_ - CLOSE_T for p_, _, kd in ALLP):
                pull += ASSIST * PULL * dt          # right before each slam the jaws suck balls in
                gx, gy, tang = gx * 0.3, gy * 0.3, tang * 0.3
            for bl in s.balls:
                body = bl[0]
                v, p = body.velocity, body.position
                vx, vy = v.x, v.y
                sp2 = vx * vx + vy * vy
                if sp2 > VMAX * VMAX:
                    k_ = VMAX / math.sqrt(sp2)
                    vx, vy = vx * k_, vy * k_
                dx, dy = p.x - CX, p.y - CY
                if tang:
                    d = math.hypot(dx, dy) + 1e-6
                    vx, vy = vx - tang * dy / d, vy + tang * dx / d
                body.velocity = (vx - pull * dx + gx, vy - pull * dy + gy)
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
                    if note and s.np < 6:
                        s.early_cap = True
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
_CA, _SA = math.cos(math.radians(ANGLE)), math.sin(math.radians(ANGLE))
SHK = [0.0, 0.0]


def TX(pts):
    """Physics coordinates -> screen: turn the machine by ANGLE around the centre, add camera shake."""
    pts = np.asarray(pts, float)
    if ANGLE:
        dx, dy = pts[:, 0] - CX, pts[:, 1] - CY
        pts = np.stack([CX + dx * _CA - dy * _SA, CY + dx * _SA + dy * _CA], 1)
    return pts + SHK


def T1(x, y):
    if ANGLE:
        dx, dy = x - CX, y - CY
        x, y = CX + dx * _CA - dy * _SA, CY + dx * _SA + dy * _CA
    return x + SHK[0], y + SHK[1]


def fill(img, pts, col):
    cv2.fillPoly(img, [np.round(TX(pts) * 16).astype(np.int32)], col, cv2.LINE_AA, 4)


def circ(img, x, y, r, col):
    x, y = T1(x, y)
    cv2.circle(img, (int(round(x * 16)), int(round(y * 16))), max(1, int(round(r * 16))), col, -1, cv2.LINE_AA, 4)


def ball(img, x, y, r, col):
    x, y = T1(x, y)
    c = (int(round(x * 16)), int(round(y * 16)))
    if BALL == 'hollow':
        cv2.circle(img, c, max(1, int(round((r - 1.5) * 16))), col, 3, cv2.LINE_AA, 4)
        return
    cv2.circle(img, c, max(1, int(round(r * 16))), col, -1, cv2.LINE_AA, 4)
    if BALL == 'shine':
        cv2.circle(img, (int(round((x - 0.32 * r) * 16)), int(round((y - 0.32 * r) * 16))),
                   max(1, int(round(0.27 * r * 16))), WHITE, -1, cv2.LINE_AA, 4)


def hline(img, x0, x1, y, col, th=2):
    (xa, ya), (xb, yb) = T1(x0, y), T1(x1, y)
    cv2.line(img, (int(xa * 16), int(ya * 16)), (int(xb * 16), int(yb * 16)), col, th, cv2.LINE_AA, 4)


SEGS = {'0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc', '5': 'afgcd',
        '6': 'afgedc', '7': 'abc', '8': 'abcdefg', '9': 'abcdfg'}


def draw_counter(img, n):
    """Seven-segment ball counter at the top of the frame (always upright)."""
    txt = str(int(n))
    dw, dh, th, sp = 46, 84, 10, 18
    x = W / 2 - (len(txt) * dw + (len(txt) - 1) * sp) / 2
    y, m = 292.0, dh / 2
    col = (240, 240, 240)
    if THEME and COUNTER_COL == 'scoreboard':   # right-aligned in four fixed slots
        txt = txt.rjust(4)
        x = W / 2 - (4 * dw + 3 * sp) / 2
    if THEME:   # a dark plate keeps the digits readable over the scene
        x0, x1 = int(W / 2 - 4 * (dw + sp) / 2 - 34), int(W / 2 + 4 * (dw + sp) / 2 + 34)
        board = COUNTER_COL == 'scoreboard'
        reg = img[int(y) - 26:int(y + dh) + 26, x0:x1]
        cv2.addWeighted(reg, 0.35 if not board else 0.12, np.zeros_like(reg), 0, 0, dst=reg)
        if board:
            cv2.rectangle(img, (x0, int(y) - 26), (x1, int(y + dh) + 26), hx('3B4466'), 4, cv2.LINE_AA)
            for k in range(4):     # unlit segments, like a real scoreboard
                xx = W / 2 - (4 * dw + 3 * sp) / 2 + k * (dw + sp)
                for (a0, b0, a1, b1) in ((xx + 4, y, xx + dw - 4, y + th), (xx + 4, y + m - th / 2, xx + dw - 4, y + m + th / 2),
                                         (xx + 4, y + dh - th, xx + dw - 4, y + dh), (xx, y + 4, xx + th, y + m - 3),
                                         (xx + dw - th, y + 4, xx + dw, y + m - 3), (xx, y + m + 3, xx + th, y + dh - 4),
                                         (xx + dw - th, y + m + 3, xx + dw, y + dh - 4)):
                    cv2.rectangle(img, (int(a0), int(b0)), (int(a1), int(b1)), (18, 26, 40), -1)
        col = hx('FFB000') if board else hx(COUNTER_COL)
    for ch in txt:
        rects = {'a': (x + 4, y, x + dw - 4, y + th), 'g': (x + 4, y + m - th / 2, x + dw - 4, y + m + th / 2),
                 'd': (x + 4, y + dh - th, x + dw - 4, y + dh), 'f': (x, y + 4, x + th, y + m - 3),
                 'b': (x + dw - th, y + 4, x + dw, y + m - 3), 'e': (x, y + m + 3, x + th, y + dh - 4),
                 'c': (x + dw - th, y + m + 3, x + dw, y + dh - 4)}
        for k, (x0, y0, x1, y1) in rects.items():
            if k in SEGS.get(ch, ''):
                cv2.rectangle(img, (int(x0), int(y0)), (int(x1), int(y1)), col, -1, cv2.LINE_AA)
        x += dw + sp


def ball_count(sim, t):
    if t >= 19.6:
        return 1
    if sim.parts is not None or sim.part_pending:
        return (len(sim.parts[0]) if sim.parts is not None else 0) + (sim.part_pending[0] if sim.part_pending else 0)
    return len(sim.balls) + len(sim.captured) + sim.absorbed + sum(p[0] for p in sim.pending)


def draw_rail(img, face, sgn):
    xo = face - sgn * PW
    xa, xb = (0.0, xo) if sgn > 0 else (xo, float(W))
    if ANGLE:                                   # turned machine: the rails just run off screen
        xa, xb = (CX - 1400.0, xo) if sgn > 0 else (xo, CX + 1400.0)
    fill(img, rr_pts(xa, CY - 8, xb, CY + 8, 0), EDGE)
    fill(img, rr_pts(xa, CY - 6, xb, CY + 6, 0), STEEL)
    hline(img, xa, xb, CY - 5, HI)
    if ANGLE:
        return
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


def _out(P, d):
    """Push screen points d pixels away from the machine centre."""
    c = np.array(T1(CX, CY))
    v = P - c
    return P + v / np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-6) * d


def draw_ring_themed(img, pts, fa):
    P = TX(pts)
    Q = np.round(P * 16).astype(np.int32)
    full = len(pts) == NA          # a free outline (not the final capsule)
    if fa > 0:
        if fa >= 1:
            cv2.fillPoly(img, [Q], RING_COL, cv2.LINE_AA, 4)
        else:
            ov = img.copy()
            cv2.fillPoly(ov, [Q], RING_COL, cv2.LINE_AA, 4)
            cv2.addWeighted(ov, fa, img, 1 - fa, 0, img)
    if RING_GLOW is not None:
        sm = np.zeros((H // 4, W // 4, 3), np.uint8)
        cv2.polylines(sm, [np.round(P / 4 * 16).astype(np.int32)], True, RING_GLOW, 4, cv2.LINE_AA, 4)
        sm = cv2.GaussianBlur(sm, (0, 0), 3.5)
        cv2.add(img, cv2.convertScaleAbs(cv2.resize(sm, (W, H), interpolation=cv2.INTER_LINEAR), alpha=1.8), dst=img)
    if RIM == 'porthole' and full:
        def pl(d, col, th):
            cv2.polylines(img, [np.round(_out(P, d) * 16).astype(np.int32)], True, col, th, cv2.LINE_AA, 4)
        pl(18, RIM_DARK, 30)
        pl(16, RIM_MID, 20)
        pl(9, RIM_HI, 2)
        pl(32, RIM_DARK, 3)
        B = _out(P, 18)[::20]
        for x, y in B:
            cv2.circle(img, (int(x * 16), int(y * 16)), 5 * 16, RIM_DARK, -1, cv2.LINE_AA, 4)
            cv2.circle(img, (int((x - 1.2) * 16), int((y - 1.2) * 16)), 3 * 16, RIM_HI, -1, cv2.LINE_AA, 4)
    cv2.polylines(img, [Q], True, RING_COL, RING_W + (2 if THEME else 0), cv2.LINE_AA, 4)
    if RIM == 'stitch' and full:
        c = np.array(T1(CX, CY))
        for i in range(0, NA, 9):
            p = P[i]
            n = (p - c) / max(1e-6, np.linalg.norm(p - c))
            tg = np.array([-n[1], n[0]])
            for side in (-1, 1):
                a = p + n * side * 5 + tg * 4
                b = p + n * side * 15 - tg * 4
                cv2.line(img, (int(a[0] * 16), int(a[1] * 16)), (int(b[0] * 16), int(b[1] * 16)), STITCH, 3, cv2.LINE_AA, 4)


def draw(sim, t, f):
    g = gap(t)
    sh = ring_pts(t)
    if SCENE is not None:
        img = SCENE.frame(t)
        if sh and WINDOW < 1:          # dim the scene inside the ring so the balls stay the star
            m = np.zeros((H, W), np.uint8)
            cv2.fillPoly(m, [np.round(TX(sh[0]) * 16).astype(np.int32)], 255, cv2.LINE_8, 4)
            cv2.copyTo(cv2.convertScaleAbs(img, alpha=WINDOW), m, img)
    else:
        img = np.full((H, W, 3), BG, np.uint8)
    collapsing = SHRINK[0] <= t < FINALE
    SHK[0] = SHK[1] = 0.0
    if SHAKE:
        for p, _, kind in ALLP:
            if 0 <= t - p < 0.3:
                amp = {'n': 9.0, 'f': 28.0, 'l': 6.0}[kind] * (1 - (t - p) / 0.3) ** 2
                SHK[0], SHK[1] = amp * math.cos(f * 2.4), amp * math.sin(f * 2.4)

    def draw_ring():
        if not sh:
            return
        pts, fa = sh
        if THEME:
            draw_ring_themed(img, pts, fa)
            return
        if fa > 0:
            if fa >= 1:
                fill(img, pts, WHITE)
            else:
                ov = img.copy()
                fill(ov, pts, WHITE)
                cv2.addWeighted(ov, fa, img, 1 - fa, 0, img)
        cv2.polylines(img, [np.round(TX(pts) * 16).astype(np.int32)], True, WHITE, RING_W, cv2.LINE_AA, 4)

    if not collapsing:
        draw_ring()
    for _, sgn in sim.jaws:
        draw_rail(img, CX - sgn * g / 2, sgn)
    rr_now = ring_radii(t) if t >= LOOP_PINCH else None
    for x, y, r, shape, hit, hc in sim.pegs:
        if shape is None and not (rr_now is not None and rad_at(rr_now[0], x, y) > math.hypot(x - CX, y - CY) + r):
            continue
        k = max(0.0, 1 - (t - hit) / 0.3)
        circ(img, x, y, r + 3 * k, EDGE)
        col = tuple(int(STEEL[i] + (WAVES[hc][i] - STEEL[i]) * k) for i in range(3))
        circ(img, x, y, r - 2.5 + 3 * k, col)
        circ(img, x - 0.3 * r, y - 0.3 * r, 0.22 * r, HI)
    lay = img if FX == 'none' else np.zeros((H, W, 3), np.uint8)
    for body, _, r, ci in sim.balls:
        p = body.position
        ball(lay, p.x, p.y, r, WAVES[ci])
    if sim.parts is not None:
        P = sim.parts[0]
        ok = (np.abs(P[:, 0] - CX) < 1150) & (np.abs(P[:, 1] - CY) < 1150)
        for x, y in P[ok]:
            ball(lay, x, y, BALL_R, WAVES[RED])
    if FX != 'none':
        if 'trail' in FX:
            if sim.trail is None:
                sim.trail = lay
            else:
                faded = cv2.subtract(cv2.convertScaleAbs(sim.trail, alpha=TRAIL_DECAY), (3, 3, 3, 0))
                sim.trail = cv2.max(lay, faded)
            lay = sim.trail
        al = np.minimum(255, lay.max(axis=2).astype(np.uint16) * 5 // 4)
        img = np.minimum(255, img.astype(np.uint16) * (255 - al)[:, :, None] // 255 + lay).astype(np.uint8)
        if 'glow' in FX:
            sm = cv2.GaussianBlur(cv2.resize(lay, (W // 4, H // 4), interpolation=cv2.INTER_AREA), (0, 0), 5)
            img = cv2.add(img, cv2.convertScaleAbs(cv2.resize(sm, (W, H), interpolation=cv2.INTER_LINEAR), alpha=0.9))
    if collapsing:
        draw_ring()
    if sim.captured:      # squashed balls inside the sealed jaws
        k = max(g / (2 * AL), 0.05)
        L = CX - g / 2
        for fx, y, r, ci in sim.captured:
            ex, ey = T1(L + fx * g, y)
            cv2.ellipse(img, (int(ex * 16), int(ey * 16)),
                        (max(8, int(r * k * 16)), int(r * (1 + 0.5 * (1 - k)) * 16)),
                        ANGLE, 0, 360, WAVES[ci], -1, cv2.LINE_AA, 4)
    if t >= 19.6:         # the lonely first ball returns so the loop is seamless
        u = min(1.0, (t - 19.6) / 0.33)
        c1, c3 = 1.70158, 2.70158
        ball(img, FIRST_POS[0], FIRST_POS[1], FIRST_R * (1 + c3 * (u - 1) ** 3 + c1 * (u - 1) ** 2), WAVES[0])
    for _, sgn in sim.jaws:
        draw_jaw(img, CX - sgn * g / 2, sgn)
    if COUNTER:
        draw_counter(img, ball_count(sim, t))
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
    for pi, (p, cnt) in enumerate(sim.spawn_events):                 # 14 tiny pops, 22 ms apart
        if cnt <= 0:
            continue
        for j in range(14):
            tt = np.arange(int(0.04 * sr)) / sr
            hz = rng.uniform(500, 1500)
            if SOUND == 'penta':                                     # pops climb a pentatonic scale instead
                k = pi + j
                hz = 392.0 * 2 ** (((0, 2, 4, 7, 9)[k % 5] + 12 * ((k // 5) % 2)) / 12)
            add(p + 0.035 + j * 0.022, np.sin(2 * np.pi * hz * tt) * np.exp(-tt / (0.014 if SOUND == 'penta' else 0.008)),
                0.22 + 0.14 * min(1, cnt / 500))
    last = -1.0
    for t0 in sim.peg_hits:                                          # glassy tick when a peg is hit
        if t0 - last < 0.045:
            continue
        last = t0
        tt = np.arange(int(0.05 * sr)) / sr
        add(t0, np.sin(2 * np.pi * rng.uniform(2300, 3300) * tt) * np.exp(-tt / 0.012), 0.09)
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
    global SCENE
    sim = Sim()
    if THEME and not DRY:
        SCENE = scenes.Scene(BGNAME, SEED)
    stills = [float(x) for x in os.environ.get('STILLS', '').split(',') if x]   # STILLS=5,15 -> PNGs only, no video
    nframes = int(DUR * FPS)
    pipe = None
    if not DRY and not stills:
        pipe = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24',
                                 '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', os.environ.get('CRF', '17'),
                                 '-pix_fmt', 'yuv420p', '-preset', 'veryfast', '_video.mp4'], stdin=subprocess.PIPE)
    for f in range(nframes):
        t = f / FPS
        sim.begin_frame(t, f)
        if stills:
            if any(abs(t - s) < 0.5 / FPS for s in stills):
                cv2.imwrite('%s_%04.1f.png' % (OUT.rsplit('.', 1)[0], t), draw(sim, t, f))
            if t > max(stills):
                break
        elif pipe:
            pipe.stdin.write(draw(sim, t, f).tobytes())
        sim.advance(t)
        if DRY and (sim.early_cap or (sim.np == 4 and sim.spawn_events[-1][1] > 40 * MULT)):
            break                 # grew far too fast - no need to finish a test run
    print(f'seed {SEED}, pull {PULL}, recipe {json.dumps(RECIPE)}')
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
