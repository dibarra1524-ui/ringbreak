# Ringbreak lab procedure

This is what the weekly lab run does. It adds one new kind of physics per week. It never posts anything.

1. Pick the first unchecked idea under "Next up" in IDEAS.md. If it turns out to be impractical, note why
   next to it, leave it unchecked, and take the next one.
2. Build it in crusher.py as a new option of an existing trait or as a new trait. Rules:
   - The default value must reproduce the current behaviour exactly, so old recipes still render the same.
   - Read it from RECIPE like the other traits, and keep the 20 second loop seamless: anything that moves
     must be back where it started at t = 0 when t = 20.
   - Keep physics in physics coordinates and drawing through TX / T1 / circ / ball / fill so machine angle
     and camera shake still work.
3. Register it in learn.py: add the option to TRAITS (and its default to CLASSIC for a new trait). If it is
   visible in a still frame, add a phrase for it in look(). If it has a strength, it can become a GENES entry.
4. Test, and only continue if every check passes:
   - `DRY=1 python3 crusher.py` with no RECIPE gives the same crush log as before the change (seed 5).
   - For the new option on 3 different arenas, at least 6 of 12 seeds pass daily.good().
   - Render one full video with the new option, check with ffprobe (20 s, 1080x1920, audio), look at frames
     near 3 s, 10 s, 15 s and 19.9 s, and compare frame 0 with the last frame to confirm the loop is seamless.
   - Run daily.py once in a scratch copy of the repo (never in the real clone) to confirm the full pipeline.
5. Tick the idea in IDEAS.md (move it to "Built" with one line saying what it does), add two new ideas of
   your own invention at the bottom of "Next up", and commit "Lab: <idea>" to main.
6. If any check fails and cannot be fixed in the run, do not push code. Push only an IDEAS.md note.
