# Ringbreak

Physics loop videos rendered entirely from code (Python, pymunk, OpenCV, ffmpeg).

- `crusher.py` renders a 20 second 1080x1920 loop with sound. `SEED=5 python3 crusher.py` gives a different run.
- `videos/` holds the rendered files that get posted.
- `daily.py` renders the next video (new seed and color order), checks it, and writes `post.json` with the public link and caption. `state.json` tracks what has been made.
- `learn.py` is the formula that keeps every post different and learns what works. Each video is a recipe (outline shape, spin, machine angle, palette, background, trails/glow, ball style and size, multiplier, camera shake, ball counter, sound, caption). `python3 learn.py ingest metrics.json` scores past posts from their Instagram numbers; `daily.py` then asks it for a recipe that has never been used, weighted toward what has scored well. `history.json` is its memory and `LEARNING.md` is a readable summary of what it has learned. The score weights are at the top of `learn.py`.
- Physics options per video: central pull, vortex, gravity, tumbling gravity or a pulsing pull; bumper pegs; bouncy or soft balls. Field strength, pull and the jaws' suck-in strength are continuous knobs that drift toward the values of the best posts.
- `IDEAS.md` is the never-ending list of new physics to build; `LAB.md` is the procedure the weekly lab run follows to build and test one idea per week. New options get extra airtime and weak ones are retired automatically.
- `scenes.py` draws the themed backgrounds (deep-space nebula, ringed planet, hyperspace, twin-sun desert, sci-fi hangar, night ballpark, synthwave, rainy neon city). Each is gently animated, loops seamlessly, changes a little with every seed, and restyles the ring, jaws, pads and counter to match. They are options of the `bg` trait, so the formula tests them against the flat colours and keeps what performs. `python3 scenes.py 7` writes a contact sheet; `STILLS=4,12 python3 crusher.py` writes test frames instead of a video.
