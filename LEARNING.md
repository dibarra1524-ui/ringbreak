# What the Ringbreak formula has learned

Posts in history: 7. Posts with usable numbers: 7. Random-try rate right now: 40%.

Lift = how far a post scored above or below its neighbours. Positive is good.

## arena

| option | evidence | lift |
|---|---|---|
| circle | 2.3 | +0.56 |
| square | 0.2 | +0.25 |
| diamond | 0.0 | +0.00 |
| oct | 0.0 | +0.00 |
| squircle | 0.6 | -0.19 |
| pent | 0.9 | -0.63 |
| hex | 0.9 | -1.09 |

## spin

| option | evidence | lift |
|---|---|---|
| -1 | 0.2 | +0.25 |
| 0 | 3.3 | +0.15 |
| 1 | 1.6 | -0.94 |

## angle

| option | evidence | lift |
|---|---|---|
| 0 | 3.0 | +0.39 |
| 90 | 0.2 | +0.25 |
| 45 | 0.9 | -0.63 |
| -45 | 0.9 | -1.09 |

## palette

| option | evidence | lift |
|---|---|---|
| fire | 0.5 | +0.71 |
| neon | 2.6 | +0.21 |
| ice | 0.0 | +0.00 |
| candy | 0.0 | +0.00 |
| pastel | 0.9 | -0.63 |
| mono | 0.9 | -1.09 |

## bg

| option | evidence | lift |
|---|---|---|
| black | 1.8 | +0.28 |
| navy | 0.6 | -0.19 |
| forest | 1.6 | -0.29 |
| plum | 0.9 | -0.63 |

## fx

| option | evidence | lift |
|---|---|---|
| glow | 0.7 | +0.81 |
| none | 1.8 | +0.28 |
| trail+glow | 1.6 | -0.59 |
| trail | 0.9 | -1.09 |

## ball

| option | evidence | lift |
|---|---|---|
| shine | 0.7 | +0.81 |
| solid | 2.5 | +0.14 |
| hollow | 1.9 | -1.15 |

## ball_r

| option | evidence | lift |
|---|---|---|
| 9.0 | 2.6 | +0.21 |
| 10.5 | 1.4 | -0.07 |
| 7.5 | 0.9 | -1.09 |

## mult

| option | evidence | lift |
|---|---|---|
| 10 | 0.7 | +0.81 |
| 8 | 2.8 | -0.12 |
| 6 | 1.6 | -0.94 |

## shake

| option | evidence | lift |
|---|---|---|
| 0 | 3.1 | +0.44 |
| 1 | 1.9 | -1.15 |

## counter

| option | evidence | lift |
|---|---|---|
| 0 | 3.1 | +0.44 |
| 1 | 1.9 | -1.15 |

## sound

| option | evidence | lift |
|---|---|---|
| classic | 3.4 | +0.01 |
| penta | 1.6 | -0.59 |

## field

| option | evidence | lift |
|---|---|---|
| pulse | 1.3 | +0.45 |
| pull | 1.8 | +0.28 |
| gravity | 0.0 | +0.00 |
| tumble | 0.9 | -0.63 |
| vortex | 0.9 | -1.09 |

## pegs

| option | evidence | lift |
|---|---|---|
| none | 2.0 | +0.36 |
| arc | 2.1 | -0.44 |
| field | 0.9 | -0.63 |

## bounce

| option | evidence | lift |
|---|---|---|
| normal | 2.3 | +0.56 |
| soft | 0.9 | -0.63 |
| bouncy | 1.7 | -0.77 |

## hook

| option | evidence | lift |
|---|---|---|
| One ball in. Thousands out. | 0.9 | +1.03 |
| How many can the ring hold? | 0.5 | +0.71 |
| It starts with one. | 0.2 | +0.25 |
| Watch it until the end. | 0.0 | +0.00 |
| The last crush is the big one. | 0.0 | +0.00 |
| 1. {m}. {mm}. Then chaos. | 0.0 | +0.00 |
| Count the crushes. | 0.0 | +0.00 |
| It only gets bigger. | 0.0 | +0.00 |
| Which color wave is your favorite? | 0.0 | +0.00 |
| Guess how many balls before it breaks. | 0.0 | +0.00 |
| The ring never survives. | 0.6 | -0.19 |
| Wait for the ring to break. | 0.9 | -0.60 |
| Every crush makes {m} more. | 0.9 | -0.63 |
| Loop it. You won't find the cut. | 0.9 | -1.09 |

## ask

| option | evidence | lift |
|---|---|---|
| Send this to someone who can't stop watching these. | 0.5 | +0.71 |
| Did you spot where the loop restarts? | 0.0 | +0.00 |
| How many balls do you think made it out? | 2.5 | -0.13 |
| Which color wave was the biggest? Tell me below. | 1.1 | -0.42 |
| Guess the final count before you rewatch. | 0.9 | -0.63 |

## Posts

| video | score | lift | views | avg watch | skip |
|---|---|---|---|---|---|
| 001 | 10.71 | +2.16 | 1893 | 13.1s | 0.276 |
| 002 | 8.29 | -1.26 | 171 | 11.4s | 0.366 |
| 003 | 7.30 | -2.25 | 162 | 8.5s | 0.4 |
| 004 | 8.26 | -1.29 | 214 | 12.0s | 0.331 |
| 005 | 8.81 | -0.48 | 429 | 11.2s | 0.304 |
| 006 | 10.70 | +2.15 | 211 | 53.2s | 0.327 |
| 007 | 10.30 | +1.75 | 1647 | 11.9s | 0.31 |

## Physics knobs (drift toward what works)

- force: centre 1.02, spread 0.28
- pull: centre 2.12, spread 0.36
- assist: centre 1.49, spread 0.28

## Retired options

- none yet
