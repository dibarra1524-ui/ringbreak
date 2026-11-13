#!/usr/bin/env python3
"""daily.py - renders the next Ringbreak video and writes post.json for the posting step.
Picks the next color rotation, finds a seed whose crush log builds properly, renders it,
keeps only the newest 20 videos, and advances state.json. Does NOT post or push."""
import json, os, re, subprocess, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
RAW = 'https://raw.githubusercontent.com/dibarra1524-ui/ringbreak/main/'
CAPTIONS = [
    "One ball in. Thousands out.",
    "Wait for the ring to break.",
    "It starts with one.",
    "Every crush makes 8 more.",
    "How many can the ring hold?",
    "Watch it until the end.",
    "The last crush is the big one.",
    "One. Eight. Sixty-four. Then chaos.",
    "The ring never survives.",
    "Count the crushes.",
    "It only gets bigger.",
    "Which color wave is your favorite?",
    "Loop it. You won't find the cut.",
    "Guess how many balls before it breaks.",
]
TAGS = "#oddlysatisfying #satisfying #physics #simulation #loop"

def crush_log(seed, rot):
    env = dict(os.environ, DRY='1', SEED=str(seed), ROT=str(rot))
    out = subprocess.run([sys.executable, 'crusher.py'], env=env, capture_output=True, text=True, timeout=600).stdout
    crushed = [int(x) for x in re.findall(r'crushed\s+(\d+)', out)]
    fin = re.search(r'red wave (\d+)', out)
    return crushed, int(fin.group(1)) if fin else 0, out

def main():
    st = json.load(open('state.json')) if os.path.exists('state.json') else {'next': 2, 'used_seeds': [4]}
    n = st['next']
    rot = (n - 1) % 9
    seed = max(st['used_seeds']) + 1
    for _ in range(40):
        crushed, finale, log = crush_log(seed, rot)
        if len(crushed) == 7 and min(crushed[:3]) >= 1 and finale >= 2000:
            break
        seed += 1
    else:
        sys.exit('no seed with a good crush log found')
    name = 'videos/%03d-crusher-seed%d-rot%d.mp4' % (n, seed, rot)
    env = dict(os.environ, SEED=str(seed), ROT=str(rot), CRF='22', OUT=name)
    subprocess.run([sys.executable, 'crusher.py'], env=env, check=True, timeout=1200)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', name],
                               capture_output=True, text=True).stdout or 0)
    if not (19.5 < dur < 20.5) or os.path.getsize(name) < 500_000:
        os.remove(name)
        sys.exit('render check failed: duration %s' % dur)
    for old in sorted(glob.glob('videos/*.mp4'))[:-20]:
        os.remove(old)
    st['next'] = n + 1
    st['used_seeds'].append(seed)
    json.dump(st, open('state.json', 'w'), indent=1)
    post = {'n': n, 'file': name, 'url': RAW + name, 'caption': CAPTIONS[(n - 1) % len(CAPTIONS)] + '\n\n' + TAGS,
            'seed': seed, 'rot': rot, 'crushed': crushed, 'finale': finale}
    json.dump(post, open('post.json', 'w'), indent=1)
    print(json.dumps(post, indent=1))

if __name__ == '__main__':
    main()
