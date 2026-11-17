# What the Ringbreak formula has learned

Posts in history: 8. Posts with usable numbers: 8. Random-try rate right now: 39%.

Lift = how far a post scored above or below its neighbours. Positive is good.

## arena

| option | evidence | lift |
|---|---|---|
| circle | 2.6 | +1.01 |
| square | 0.5 | +0.66 |
| squircle | 0.9 | +0.25 |
| oct | 0.0 | +0.00 |
| diamond | 0.3 | -0.14 |
| pent | 0.9 | -0.26 |
| hex | 0.9 | -0.72 |

## spin

| option | evidence | lift |
|---|---|---|
| 0 | 3.5 | +0.69 |
| -1 | 0.5 | +0.66 |
| 1 | 2.2 | -0.34 |

## angle

| option | evidence | lift |
|---|---|---|
| 0 | 3.9 | +0.81 |
| 90 | 0.5 | +0.66 |
| 45 | 0.9 | -0.26 |
| -45 | 0.9 | -0.72 |

## palette

| option | evidence | lift |
|---|---|---|
| fire | 1.1 | +0.82 |
| neon | 3.2 | +0.75 |
| ice | 0.0 | +0.00 |
| candy | 0.0 | +0.00 |
| pastel | 0.9 | -0.26 |
| mono | 0.9 | -0.72 |

## bg

| option | evidence | lift |
|---|---|---|
| black | 1.8 | +0.60 |
| forest | 2.2 | +0.48 |
| navy | 1.3 | +0.14 |
| plum | 0.9 | -0.26 |

## fx

| option | evidence | lift |
|---|---|---|
| glow | 1.6 | +1.04 |
| none | 1.8 | +0.60 |
| trail+glow | 1.9 | -0.01 |
| trail | 0.9 | -0.72 |

## ball

| option | evidence | lift |
|---|---|---|
| shine | 1.6 | +1.04 |
| solid | 2.7 | +0.58 |
| hollow | 1.9 | -0.66 |

## ball_r

| option | evidence | lift |
|---|---|---|
| 9.0 | 3.6 | +0.65 |
| 10.5 | 1.7 | +0.52 |
| 7.5 | 0.9 | -0.72 |

## mult

| option | evidence | lift |
|---|---|---|
| 10 | 1.3 | +1.27 |
| 8 | 2.7 | +0.31 |
| 6 | 2.2 | -0.34 |

## shake

| option | evidence | lift |
|---|---|---|
| 0 | 4.4 | +0.92 |
| 1 | 1.9 | -0.66 |

## counter

| option | evidence | lift |
|---|---|---|
| 0 | 4.0 | +1.01 |
| 1 | 2.2 | -0.65 |

## sound

| option | evidence | lift |
|---|---|---|
| classic | 4.3 | +0.57 |
| penta | 1.9 | -0.01 |

## field

| option | evidence | lift |
|---|---|---|
| pulse | 2.2 | +1.05 |
| pull | 1.8 | +0.60 |
| gravity | 0.3 | -0.14 |
| tumble | 0.9 | -0.26 |
| vortex | 0.9 | -0.72 |

## pegs

| option | evidence | lift |
|---|---|---|
| none | 2.6 | +0.69 |
| arc | 2.7 | +0.29 |
| field | 0.9 | -0.26 |

## bounce

| option | evidence | lift |
|---|---|---|
| normal | 2.6 | +1.01 |
| bouncy | 2.7 | -0.02 |
| soft | 0.9 | -0.26 |

## hook

| option | evidence | lift |
|---|---|---|
| One ball in. Thousands out. | 0.9 | +1.14 |
| How many can the ring hold? | 0.8 | +1.07 |
| It starts with one. | 0.5 | +0.66 |
| The ring never survives. | 0.9 | +0.25 |
| The last crush is the big one. | 0.0 | +0.00 |
| 1. {m}. {mm}. Then chaos. | 0.0 | +0.00 |
| Count the crushes. | 0.0 | +0.00 |
| It only gets bigger. | 0.0 | +0.00 |
| Which color wave is your favorite? | 0.0 | +0.00 |
| Guess how many balls before it breaks. | 0.0 | +0.00 |
| Watch it until the end. | 0.3 | -0.14 |
| Wait for the ring to break. | 0.9 | -0.25 |
| Every crush makes {m} more. | 0.9 | -0.26 |
| Loop it. You won't find the cut. | 0.9 | -0.72 |

## ask

| option | evidence | lift |
|---|---|---|
| Send this to someone who can't stop watching these. | 0.8 | +1.07 |
| How many balls do you think made it out? | 2.8 | +0.34 |
| Which color wave was the biggest? Tell me below. | 1.4 | +0.22 |
| Did you spot where the loop restarts? | 0.0 | +0.00 |
| Guess the final count before you rewatch. | 1.3 | -0.31 |

## Posts

| video | score | lift | views | avg watch | skip |
|---|---|---|---|---|---|
| 001 | 10.71 | +2.42 | 1893 | 13.1s | 0.276 |
| 002 | 8.29 | -0.52 | 171 | 11.4s | 0.366 |
| 003 | 7.30 | -1.51 | 162 | 8.5s | 0.4 |
| 004 | 8.26 | -0.55 | 214 | 12.0s | 0.331 |
| 005 | 8.81 | +0.52 | 429 | 11.2s | 0.304 |
| 006 | 10.70 | +2.41 | 212 | 52.9s | 0.331 |
| 007 | 10.30 | +2.00 | 1657 | 11.9s | 0.312 |
| 008 | 8.26 | -0.55 | 259 | 12.3s | 0.264 |

## Physics knobs (drift toward what works)

- force: centre 1.03, spread 0.25
- pull: centre 2.15, spread 0.33
- assist: centre 1.54, spread 0.25

## Retired options

- none yet
