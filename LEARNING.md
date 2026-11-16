# What the Ringbreak formula has learned

Posts in history: 6. Posts with usable numbers: 6. Random-try rate right now: 42%.

Lift = how far a post scored above or below its neighbours. Positive is good.

## arena

| option | evidence | lift |
|---|---|---|
| circle | 2.2 | +0.80 |
| squircle | 0.5 | +0.17 |
| square | 0.0 | +0.00 |
| diamond | 0.0 | +0.00 |
| oct | 0.0 | +0.00 |
| pent | 0.8 | -0.24 |
| hex | 0.9 | -0.71 |

## spin

| option | evidence | lift |
|---|---|---|
| 0 | 3.0 | +0.53 |
| -1 | 0.0 | +0.00 |
| 1 | 1.4 | -0.46 |

## angle

| option | evidence | lift |
|---|---|---|
| 0 | 2.7 | +0.76 |
| 90 | 0.0 | +0.00 |
| 45 | 0.8 | -0.24 |
| -45 | 0.9 | -0.71 |

## palette

| option | evidence | lift |
|---|---|---|
| fire | 0.3 | +0.60 |
| neon | 2.3 | +0.60 |
| ice | 0.0 | +0.00 |
| candy | 0.0 | +0.00 |
| pastel | 0.8 | -0.24 |
| mono | 0.9 | -0.71 |

## bg

| option | evidence | lift |
|---|---|---|
| black | 1.8 | +0.61 |
| navy | 0.5 | +0.17 |
| forest | 1.2 | -0.24 |
| plum | 0.8 | -0.24 |

## fx

| option | evidence | lift |
|---|---|---|
| none | 1.8 | +0.61 |
| glow | 0.3 | +0.60 |
| trail+glow | 1.3 | -0.08 |
| trail | 0.9 | -0.71 |

## ball

| option | evidence | lift |
|---|---|---|
| shine | 0.3 | +0.60 |
| solid | 2.3 | +0.60 |
| hollow | 1.7 | -0.66 |

## ball_r

| option | evidence | lift |
|---|---|---|
| 9.0 | 2.3 | +0.60 |
| 10.5 | 1.1 | +0.17 |
| 7.5 | 0.9 | -0.71 |

## mult

| option | evidence | lift |
|---|---|---|
| 10 | 0.3 | +0.60 |
| 8 | 2.7 | +0.36 |
| 6 | 1.4 | -0.46 |

## shake

| option | evidence | lift |
|---|---|---|
| 0 | 2.7 | +0.76 |
| 1 | 1.7 | -0.66 |

## counter

| option | evidence | lift |
|---|---|---|
| 0 | 2.7 | +0.76 |
| 1 | 1.7 | -0.66 |

## sound

| option | evidence | lift |
|---|---|---|
| classic | 3.1 | +0.30 |
| penta | 1.3 | -0.08 |

## field

| option | evidence | lift |
|---|---|---|
| pull | 1.8 | +0.61 |
| pulse | 0.8 | +0.58 |
| gravity | 0.0 | +0.00 |
| tumble | 0.8 | -0.24 |
| vortex | 0.9 | -0.71 |

## pegs

| option | evidence | lift |
|---|---|---|
| none | 1.8 | +0.61 |
| arc | 1.7 | -0.10 |
| field | 0.8 | -0.24 |

## bounce

| option | evidence | lift |
|---|---|---|
| normal | 2.2 | +0.80 |
| soft | 0.8 | -0.24 |
| bouncy | 1.4 | -0.46 |

## hook

| option | evidence | lift |
|---|---|---|
| One ball in. Thousands out. | 0.9 | +1.16 |
| How many can the ring hold? | 0.3 | +0.60 |
| The ring never survives. | 0.5 | +0.17 |
| It starts with one. | 0.0 | +0.00 |
| Watch it until the end. | 0.0 | +0.00 |
| The last crush is the big one. | 0.0 | +0.00 |
| 1. {m}. {mm}. Then chaos. | 0.0 | +0.00 |
| Count the crushes. | 0.0 | +0.00 |
| It only gets bigger. | 0.0 | +0.00 |
| Which color wave is your favorite? | 0.0 | +0.00 |
| Guess how many balls before it breaks. | 0.0 | +0.00 |
| Every crush makes {m} more. | 0.8 | -0.24 |
| Wait for the ring to break. | 0.9 | -0.25 |
| Loop it. You won't find the cut. | 0.9 | -0.71 |

## ask

| option | evidence | lift |
|---|---|---|
| Send this to someone who can't stop watching these. | 0.3 | +0.60 |
| How many balls do you think made it out? | 2.3 | +0.35 |
| Did you spot where the loop restarts? | 0.0 | +0.00 |
| Guess the final count before you rewatch. | 0.8 | -0.24 |
| Which color wave was the biggest? Tell me below. | 0.9 | -0.25 |

## Posts

| video | score | lift | views | avg watch | skip |
|---|---|---|---|---|---|
| 001 | 10.71 | +2.42 | 1893 | 13.1s | 0.276 |
| 002 | 8.29 | -0.52 | 171 | 11.4s | 0.366 |
| 003 | 7.30 | -1.51 | 162 | 8.5s | 0.4 |
| 004 | 8.26 | -0.55 | 214 | 12.0s | 0.331 |
| 005 | 8.81 | +0.52 | 429 | 11.2s | 0.304 |
| 006 | 10.70 | +2.41 | 211 | 53.2s | 0.327 |

## Physics knobs (drift toward what works)

- force: centre 1.02, spread 0.28
- pull: centre 2.12, spread 0.36
- assist: centre 1.45, spread 0.28

## Retired options

- none yet
