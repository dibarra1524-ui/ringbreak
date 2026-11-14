#!/usr/bin/env python3
"""learn.py - the formula that decides what each Ringbreak video looks like, and learns from results.

Every video is a "recipe": one option per trait (outline shape, spin, machine angle, palette, effects ...).
Every post's Instagram numbers are turned into one score. Each trait option keeps a running estimate of
how much it lifts or hurts that score, and the next recipe is drawn by Thompson sampling: options that
have done well are picked more often, untested options still get tried, and no look is ever repeated.

  python3 learn.py ingest metrics.json   update history.json with fresh Instagram numbers, rewrite LEARNING.md
  python3 learn.py posted N MEDIA_ID     remember the Instagram media id of video N
  python3 learn.py report                print what has been learned so far
  python3 learn.py pick                  print the recipe it would choose right now (changes nothing)
"""
import json, math, os, random, statistics, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
HIST = os.path.join(HERE, 'history.json')

CAPTIONS = [
    "One ball in. Thousands out.",
    "Wait for the ring to break.",
    "It starts with one.",
    "Every crush makes {m} more.",
    "How many can the ring hold?",
    "Watch it until the end.",
    "The last crush is the big one.",
    "1. {m}. {mm}. Then chaos.",
    "The ring never survives.",
    "Count the crushes.",
    "It only gets bigger.",
    "Which color wave is your favorite?",
    "Loop it. You won't find the cut.",
    "Guess how many balls before it breaks.",
]
ASKS = [
    "How many balls do you think made it out?",
    "Which color wave was the biggest? Tell me below.",
    "Did you spot where the loop restarts?",
    "Send this to someone who can't stop watching these.",
    "Guess the final count before you rewatch.",
]

# ------------------------------------------------------------------ the traits a video can vary
TRAITS = {
    'arena':   ['circle', 'square', 'diamond', 'pent', 'hex', 'oct', 'squircle'],
    'spin':    [0, 1, -1],
    'angle':   [0, 90, 45, -45],
    'palette': ['neon', 'pastel', 'fire', 'ice', 'candy', 'mono'],
    'bg':      ['black', 'navy', 'plum', 'forest'],
    'fx':      ['none', 'trail', 'glow', 'trail+glow'],
    'ball':    ['solid', 'hollow', 'shine'],
    'ball_r':  [7.5, 9.0, 10.5],
    'mult':    [6, 8, 10],
    'shake':   [0, 1],
    'counter': [0, 1],
    'sound':   ['classic', 'penta'],
    'hook':    list(range(len(CAPTIONS))),
    'ask':     list(range(len(ASKS))),
}
VISUAL = [k for k in TRAITS if k not in ('hook', 'ask')]
CLASSIC = {'arena': 'circle', 'spin': 0, 'angle': 0, 'palette': 'neon', 'bg': 'black', 'fx': 'none',
           'ball': 'solid', 'ball_r': 9.0, 'mult': 8, 'shake': 0, 'counter': 0, 'sound': 'classic'}
NAMES = {'arena': {'circle': 'circle', 'square': 'square', 'diamond': 'diamond', 'pent': 'pentagon',
                   'hex': 'hexagon', 'oct': 'octagon', 'squircle': 'rounded square'}}

# ------------------------------------------------------------------ the score
# One number per post, built from what Instagram reports for a Reel. Rates matter more than raw size so a
# post is not rewarded just for being older. Change the weights here to change what "good" means.
WEIGHTS = {'views': 1.0,        # ln(1 + views)
           'retention': 2.0,    # average watch time / video length (above 1 means people looped it)
           'hold': 2.0,         # 1 - skip rate (share of viewers who stayed past 3 seconds)
           'engagement': 25.0}  # (likes + 3 comments + 4 saves + 5 shares) per view, capped at 0.2
VIDEO_MS = 20000.0
MIN_AGE_H, FULL_AGE_H = 6.0, 48.0   # younger than 6 h: ignored; weight grows to 1 at 48 h
HALF_LIFE = 40                      # posts; older results slowly count for less


def load():
    if os.path.exists(HIST):
        return json.load(open(HIST))
    return {'posts': []}


def save(h):
    json.dump(h, open(HIST, 'w'), indent=1)


def now():
    return datetime.now(timezone.utc)


def parse_ts(s):
    s = s.replace('Z', '+00:00')
    if len(s) > 5 and s[-5] in '+-' and s[-3] != ':':
        s = s[:-2] + ':' + s[-2:]
    return datetime.fromisoformat(s)


def raw_score(m):
    v = float(m.get('media_views') or 0)
    wt, sk = m.get('media_reel_avg_watch_time'), m.get('media_reel_skip_rate')
    ret = min(2.0, float(wt) / VIDEO_MS) if wt is not None else 0.5
    sk = float(sk) if sk is not None else 0.5
    hold = 1.0 - (sk / 100.0 if sk > 1 else sk)
    eng = (float(m.get('media_like_count') or 0) + 3 * float(m.get('media_comments_count') or 0)
           + 4 * float(m.get('media_saved') or 0) + 5 * float(m.get('media_shares') or 0)) / max(v, 1.0)
    return (WEIGHTS['views'] * math.log1p(v) + WEIGHTS['retention'] * ret + WEIGHTS['hold'] * hold
            + WEIGHTS['engagement'] * min(eng, 0.2))


def scored(h):
    """Posts with usable numbers -> list of (post, lift, weight). lift = score minus the median of its
    neighbours, so account growth over time does not look like a trait getting better."""
    t = now()
    out = []
    for p in h['posts']:
        if not p.get('metrics') or not p.get('posted_at'):
            continue
        age = (t - parse_ts(p['posted_at'])).total_seconds() / 3600
        if age < MIN_AGE_H:
            continue
        p['score'] = round(raw_score(p['metrics']), 4)
        out.append([p, 0.0, min(1.0, age / FULL_AGE_H)])
    for i, row in enumerate(out):
        near = [o[0]['score'] for j, o in enumerate(out) if j != i and abs(j - i) <= 10]
        row[1] = row[0]['score'] - (statistics.median(near) if near else row[0]['score'])
        row[0]['lift'] = round(row[1], 4)
    return out


def stats(h):
    """trait -> option -> [evidence weight, posterior mean lift]; plus the noise level sigma."""
    rows = scored(h)
    last_n = max([p['n'] for p in h['posts']] or [0])
    acc = {k: {json.dumps(o): [0.0, 0.0] for o in opts} for k, opts in TRAITS.items()}
    for p, lift, w in rows:
        w *= 0.5 ** ((last_n - p['n']) / HALF_LIFE)
        for k in TRAITS:
            key = json.dumps(p.get('recipe', {}).get(k, CLASSIC.get(k)))
            if key in acc[k]:
                acc[k][key][0] += w
                acc[k][key][1] += w * lift
    for k in acc:
        for key, a in acc[k].items():
            a[1] = a[1] / (a[0] + 1.0)        # prior: one imaginary average post per option
    lifts = [r[1] for r in rows]
    sigma = max(0.5, statistics.pstdev(lifts)) if len(lifts) >= 2 else 1.0
    return acc, sigma, len(rows)


def explore_rate(n_scored):
    return max(0.08, 0.5 * 0.97 ** n_scored)   # starts at 50% random, settles at 8%


def signature(r):
    return json.dumps([r.get(k, CLASSIC[k]) for k in VISUAL])


def choose(h=None, rng=None):
    """Pick the recipe for the next video."""
    h = h or load()
    rng = rng or random.Random()
    acc, sigma, n_scored = stats(h)
    eps = explore_rate(n_scored)
    past = [dict(CLASSIC, **p.get('recipe', {})) for p in h['posts']]
    used = {signature(r) for r in past}
    recent = past[-6:]
    r = None
    for attempt in range(600):
        r = {}
        for k, opts in TRAITS.items():
            if rng.random() < eps:
                r[k] = rng.choice(opts)
            else:   # Thompson sampling: draw a plausible lift for every option, keep the best draw
                r[k] = max(opts, key=lambda o: rng.gauss(acc[k][json.dumps(o)][1],
                                                           sigma / math.sqrt(acc[k][json.dumps(o)][0] + 1.0)))
        if r['arena'] == 'circle':
            r['spin'] = 0
        if int(r['angle']) == 90:
            r['counter'] = 0                   # the vertical rail runs through the counter's spot
        if r['palette'] == 'mono' and (r['hook'] == 11 or r['ask'] == 1):
            continue                           # no "which color" captions on a black-and-white video
        need = 3 if attempt < 300 else 2 if attempt < 500 else 1
        if signature(r) in used:
            continue
        if any(sum(r[k] != q.get(k) for k in VISUAL) < need for q in recent):
            continue
        if recent and attempt < 500 and (r['arena'] == recent[-1].get('arena') or r['palette'] == recent[-1].get('palette')):
            continue
        if attempt < 500 and (r['hook'] in [q.get('hook') for q in recent[-4:]] or (recent and r['ask'] == recent[-1].get('ask'))):
            continue
        break
    return r


def caption_for(r):
    m = r.get('mult', 8)
    about = "A satisfying physics simulation made entirely with code. New loop twice a day."
    tags = "#oddlysatisfying #satisfying #physicssimulation #simulation #loop"   # Instagram allows 5
    return "\n\n".join([CAPTIONS[r['hook']].format(m=m, mm=m * m), ASKS[r['ask']], about, tags])


def look(r):
    """Plain-words description of what the frame should show, for the visual check before posting."""
    bits = ['a white %s outline%s on a %s background' % (
        NAMES['arena'][r['arena']], ' (slowly turning)' if r['spin'] else '',
        {'black': 'black', 'navy': 'very dark blue', 'plum': 'very dark purple', 'forest': 'very dark green'}[r['bg']])]
    bits.append('%s %s-palette balls' % ({'solid': 'solid', 'hollow': 'hollow ring-shaped', 'shine': 'shiny'}[r['ball']], r['palette']))
    bits.append('two grey jaws ' + {0: 'on a horizontal rail', 90: 'on a vertical rail', 45: 'on a diagonal rail',
                                    -45: 'on a diagonal rail'}[int(r['angle'])])
    if 'trail' in r['fx']:
        bits.append('short motion trails behind the balls')
    if 'glow' in r['fx']:
        bits.append('a soft glow around the balls')
    if r['counter']:
        bits.append('a white digital ball counter near the top')
    return '; '.join(bits)


# ------------------------------------------------------------------ commands
def ingest(path):
    rows = json.load(open(path))
    if isinstance(rows, dict):
        rows = rows.get('data') or rows.get('result') or []
    h = load()
    by_id = {str(p.get('media_id')): p for p in h['posts'] if p.get('media_id')}
    hit = 0
    for row in rows:
        p = by_id.get(str(row.get('media_id')))
        if not p:
            continue
        hit += 1
        p['metrics'] = {k: v for k, v in row.items() if k.startswith('media_') and k != 'media_id'}
        p['metrics_at'] = now().isoformat(timespec='seconds')
        if row.get('timestamp'):
            p['posted_at'] = row['timestamp']
    scored(h)
    save(h)
    print('updated numbers for %d of %d posts' % (hit, len(h['posts'])))
    report(h)


def posted(n, media_id):
    h = load()
    for p in h['posts']:
        if p['n'] == int(n):
            p['media_id'] = str(media_id)
            p['posted_at'] = p.get('posted_at') or now().isoformat(timespec='seconds')
            save(h)
            print('recorded media id %s for video %03d' % (media_id, int(n)))
            return
    sys.exit('video %s is not in history.json' % n)


def report(h=None):
    h = h or load()
    acc, sigma, n_scored = stats(h)
    rows = scored(h)
    lines = ['# What the Ringbreak formula has learned', '',
             'Posts in history: %d. Posts with usable numbers: %d. Random-try rate right now: %d%%.'
             % (len(h['posts']), n_scored, round(100 * explore_rate(n_scored))), '',
             'Lift = how far a post scored above or below its neighbours. Positive is good.', '']
    best = []
    for k, opts in TRAITS.items():
        lines += ['## ' + k, '', '| option | evidence | lift |', '|---|---|---|']
        for o in sorted(opts, key=lambda o: -acc[k][json.dumps(o)][1]):
            w, m = acc[k][json.dumps(o)]
            label = CAPTIONS[o] if k == 'hook' else ASKS[o] if k == 'ask' else o
            lines.append('| %s | %.1f | %+.2f |' % (label, w, m))
            if w >= 1.5:
                best.append((m, k, label))
        lines.append('')
    if rows:
        lines += ['## Posts', '', '| video | score | lift | views | avg watch | skip |', '|---|---|---|---|---|---|']
        for p, lift, w in rows:
            m = p['metrics']
            lines.append('| %03d | %.2f | %+.2f | %s | %.1fs | %s |' % (
                p['n'], p['score'], lift, m.get('media_views'),
                float(m.get('media_reel_avg_watch_time') or 0) / 1000, m.get('media_reel_skip_rate')))
    open(os.path.join(HERE, 'LEARNING.md'), 'w').write('\n'.join(lines) + '\n')
    best.sort(reverse=True)
    if best:
        print('learned so far (%d scored posts): best %s; weakest %s' % (
            n_scored, ', '.join('%s=%s (%+.2f)' % (k, l, m) for m, k, l in best[:3]),
            ', '.join('%s=%s (%+.2f)' % (k, l, m) for m, k, l in best[-2:])))
    else:
        print('learned so far: %d scored posts, not enough repeats of any option yet - still exploring' % n_scored)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'report'
    if cmd == 'ingest':
        ingest(sys.argv[2])
    elif cmd == 'posted':
        posted(sys.argv[2], sys.argv[3])
    elif cmd == 'pick':
        r = choose()
        print(json.dumps(r), '\n' + look(r))
    else:
        report()
