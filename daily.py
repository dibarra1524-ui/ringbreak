#!/usr/bin/env python3
"""daily.py - renders the next Ringbreak video and writes post.json for the posting step.
Asks learn.py for the next look (a recipe that has never been used), finds a seed whose crush log
builds properly with that look, renders it, keeps only the newest 20 videos, and advances state.json
and history.json. Does NOT post or push."""
import json, os, re, subprocess, sys, glob
import learn
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
RAW = 'https://raw.githubusercontent.com/dibarra1524-ui/ringbreak/main/'
def crush_log(seed, rot, recipe):
    env = dict(os.environ, DRY='1', SEED=str(seed), ROT=str(rot), RECIPE=json.dumps(recipe))
    out = subprocess.run([sys.executable, 'crusher.py'], env=env, capture_output=True, text=True, timeout=600).stdout
    crushed = [int(x) for x in re.findall(r'crushed\s+(\d+)', out)]
    fin = re.search(r'red wave (\d+)', out)
    return crushed, int(fin.group(1)) if fin else 0, out


def good(crushed, finale, log, recipe):
    """A run is worth posting if it starts small, builds steadily, and only fills the ring at the very end."""
    capped = [i for i, line in enumerate(log.splitlines()) if 'capped' in line]
    return (len(crushed) == 7 and min(crushed[:3]) >= 1 and finale >= 250 * recipe['mult']
            and crushed[3] <= 40 and not any(i < 7 for i in capped))


def find(st, hist, rot):
    """Try up to 4 fresh recipes, 20 seeds each; fall back to the classic look so a run never comes up empty."""
    seed = max(st['used_seeds']) + 1
    for attempt in range(5):
        recipe = learn.choose(hist)
        if attempt == 4:
            recipe = dict(learn.CLASSIC, hook=recipe['hook'], ask=recipe['ask'], force=1.0, pull=2.0, assist=1.4)
        for _ in range(20):
            crushed, finale, log = crush_log(seed, rot, recipe)
            if good(crushed, finale, log, recipe):
                return recipe, seed, crushed, finale
            seed += 1
            # steer the suck-in strength: too fast -> weaker, too slow -> stronger
            fast = 'capped' in log.split('pinch 7')[0] or (len(crushed) > 3 and crushed[3] > 40)
            lo, hi, _d = learn.GENES['assist']
            recipe['assist'] = round(min(hi, max(lo, recipe['assist'] + (-0.15 if fast else 0.15))), 2)
    sys.exit('no seed with a good crush log found')


def main():
    st = json.load(open('state.json')) if os.path.exists('state.json') else {'next': 2, 'used_seeds': [4]}
    hist = learn.load()
    n = st['next']
    rot = (n - 1) % 9
    recipe, seed, crushed, finale = find(st, hist, rot)
    name = 'videos/%03d-crusher-seed%d-rot%d.mp4' % (n, seed, rot)
    env = dict(os.environ, SEED=str(seed), ROT=str(rot), CRF='22', OUT=name, RECIPE=json.dumps(recipe))
    subprocess.run([sys.executable, 'crusher.py'], env=env, check=True, timeout=1500)
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
    hist['posts'].append({'n': n, 'seed': seed, 'rot': rot, 'recipe': recipe, 'file': name, 'media_id': None})
    learn.save(hist)
    post = {'n': n, 'file': name, 'url': RAW + name, 'caption': learn.caption_for(recipe),
            'seed': seed, 'rot': rot, 'recipe': recipe, 'look': learn.look(recipe),
            'crushed': crushed, 'finale': finale}
    json.dump(post, open('post.json', 'w'), indent=1)
    print(json.dumps(post, indent=1))

if __name__ == '__main__':
    main()
