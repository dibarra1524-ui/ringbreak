#!/usr/bin/env python3
"""brand.py - turns a regular Ringbreak post into a paid "any video" brand-campaign post.

campaign/brands.json lists brand campaigns David joined on Content Rewards that accept any video
(for example make.fun). The scout keeps it current: status "open" or "paused", the creator
requirement, and the brand logo saved to brand/campaigns/<id>.png.

If one campaign is open and has its logo, the daily post gets:
  - an end card over the last seconds: brand logo + a call to visit the brand (the ring break stays visible above it)
  - a caption that starts with "#ad", keeps the hook, and adds the brand's call to action + link
    (Instagram allows 5 hashtags, so one of ours is dropped to make room for #ad)

  python3 brand.py active                 print the campaign that would be used (or "none")
  python3 brand.py apply VIDEO CAPTIONFILE  overlay the end card in place and rewrite the caption file
"""
import json, os, subprocess, sys, tempfile
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
BRANDS = os.path.join(HERE, 'campaign', 'brands.json')
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def load():
    try:
        return json.load(open(BRANDS))
    except (OSError, ValueError):
        return []


def active():
    """First campaign that is open, has a logo on disk, and has not passed its end date. Rotates fairly by
    picking the open campaign used least recently (campaign/brand_submissions.md)."""
    now = datetime.now(timezone.utc).date().isoformat()
    ok = [c for c in load() if c.get('status') == 'open' and c.get('logo')
          and os.path.exists(os.path.join(HERE, c['logo'])) and (not c.get('ends') or c['ends'] >= now)]
    if not ok:
        return None
    log = ''
    p = os.path.join(HERE, 'campaign', 'brand_submissions.md')
    if os.path.exists(p):
        log = open(p).read()
    return min(ok, key=lambda c: log.rfind('| ' + c['id'] + ' |'))


def caption(base, c):
    """hook / ask / about / tags  ->  #ad hook / ask / brand cta + link / tags (5 hashtags max incl. #ad)."""
    parts = base.split('\n\n')
    tags = parts[-1].split() if parts[-1].startswith('#') else []
    body = parts[:-1] if tags else parts
    brand_tags = [c['hashtag']] if c.get('hashtag') else []
    tags = (brand_tags + tags)[:4]
    out = ['#ad ' + body[0]] + body[1:2] + [c['cta'] + '\n' + c['link']]
    return '\n\n'.join(out + ([' '.join(tags)] if tags else []))


def dur(path):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                                capture_output=True, text=True).stdout or 0)


def overlay(video, c):
    """End card on the bottom third for the last c['card_seconds'] (default 4) seconds, fading in."""
    d = dur(video)
    secs = float(c.get('card_seconds', 4))
    t0 = max(0.0, d - secs)
    logo = os.path.join(HERE, c['logo'])
    with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as f:
        f.write(c.get('card_text', 'Visit ' + c['link'].replace('https://', '').rstrip('/')))
        txt = f.name
    out = video + '.brand.mp4'
    fc = ("[0:v]drawbox=x=0:y=ih*0.70:w=iw:h=ih*0.21:color=black@0.72:t=fill:enable='gte(t,{t0})',"
          "drawtext=fontfile={font}:textfile={txt}:fontsize=60:fontcolor=white:x=(w-tw)/2:y=h*0.835:"
          "enable='gte(t,{t0})'[bg];"
          "[1:v]scale=-1:150,format=rgba,fade=in:st={t0}:d=0.4:alpha=1[lg];"
          "[bg][lg]overlay=x=(W-w)/2:y=H*0.715:enable='gte(t,{t0})'[v]").format(t0=t0, font=FONT, txt=txt)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-loop', '1', '-t', str(d), '-i', logo,
                    '-filter_complex', fc, '-map', '[v]', '-map', '0:a?', '-c:a', 'copy',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22', '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart', out], check=True, timeout=900)
    os.remove(txt)
    os.replace(out, video)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'active'
    c = active()
    if cmd == 'active':
        print(json.dumps(c) if c else 'none')
    elif cmd == 'apply':
        if not c:
            print('none'); return
        video, capfile = sys.argv[2], sys.argv[3]
        overlay(video, c)
        open(capfile, 'w').write(caption(open(capfile).read(), c))
        print(c['id'])


if __name__ == '__main__':
    main()
