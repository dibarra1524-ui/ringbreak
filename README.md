# Ringbreak

Physics loop videos rendered entirely from code (Python, pymunk, OpenCV, ffmpeg).

- `crusher.py` renders a 20 second 1080x1920 loop with sound. `SEED=5 python3 crusher.py` gives a different run.
- `videos/` holds the rendered files that get posted.
- `daily.py` renders the next video (new seed and color order), checks it, and writes `post.json` with the public link and caption. `state.json` tracks what has been made.
