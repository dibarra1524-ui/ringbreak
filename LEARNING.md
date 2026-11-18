# What the Ringbreak formula has learned

Posts in history: 9. Posts with usable numbers: 9. Random-try rate right now: 38%.

Lift = how far a post scored above or below its neighbours. Positive is good.

## arena

| option | evidence | lift |
|---|---|---|
| circle | 2.7 | +0.78 |
| square | 0.8 | +0.76 |
| oct | 0.0 | +0.00 |
| squircle | 0.9 | -0.19 |
| diamond | 0.5 | -0.39 |
| pent | 0.9 | -0.57 |
| hex | 0.9 | -1.02 |

## spin

| option | evidence | lift |
|---|---|---|
| -1 | 0.6 | +0.68 |
| 0 | 3.8 | +0.43 |
| 1 | 2.3 | -0.87 |

## angle

| option | evidence | lift |
|---|---|---|
| 90 | 0.6 | +0.68 |
| 0 | 4.3 | +0.42 |
| 45 | 0.9 | -0.57 |
| -45 | 0.9 | -1.02 |

## palette

| option | evidence | lift |
|---|---|---|
| fire | 1.4 | +0.59 |
| neon | 3.3 | +0.37 |
| candy | 0.2 | +0.22 |
| ice | 0.0 | +0.00 |
| pastel | 0.9 | -0.57 |
| mono | 0.9 | -1.02 |

## bg

| option | evidence | lift |
|---|---|---|
| forest | 2.7 | +0.40 |
| black | 1.8 | +0.31 |
| navy | 1.4 | -0.39 |
| plum | 0.9 | -0.57 |

## fx

| option | evidence | lift |
|---|---|---|
| glow | 2.2 | +0.87 |
| none | 1.8 | +0.31 |
| trail+glow | 1.9 | -0.51 |
| trail | 0.9 | -1.02 |

## ball

| option | evidence | lift |
|---|---|---|
| shine | 2.2 | +0.87 |
| solid | 2.7 | +0.13 |
| hollow | 1.8 | -1.08 |

## ball_r

| option | evidence | lift |
|---|---|---|
| 10.5 | 1.9 | +0.33 |
| 9.0 | 4.0 | +0.26 |
| 7.5 | 0.9 | -1.02 |

## mult

| option | evidence | lift |
|---|---|---|
| 10 | 1.6 | +1.22 |
| 8 | 2.7 | -0.07 |
| 6 | 2.5 | -0.75 |

## shake

| option | evidence | lift |
|---|---|---|
| 0 | 4.8 | +0.53 |
| 1 | 2.0 | -0.93 |

## counter

| option | evidence | lift |
|---|---|---|
| 0 | 4.3 | +0.69 |
| 1 | 2.5 | -0.97 |

## sound

| option | evidence | lift |
|---|---|---|
| classic | 4.9 | +0.29 |
| penta | 1.9 | -0.51 |

## field

| option | evidence | lift |
|---|---|---|
| pulse | 2.5 | +0.79 |
| pull | 1.8 | +0.31 |
| gravity | 0.7 | -0.20 |
| tumble | 0.9 | -0.57 |
| vortex | 0.9 | -1.02 |

## pegs

| option | evidence | lift |
|---|---|---|
| none | 2.9 | +0.36 |
| arc | 2.8 | -0.07 |
| field | 1.1 | -0.40 |

## bounce

| option | evidence | lift |
|---|---|---|
| normal | 2.9 | +0.81 |
| bouncy | 3.0 | -0.45 |
| soft | 0.9 | -0.57 |

## hook

| option | evidence | lift |
|---|---|---|
| How many can the ring hold? | 0.9 | +1.05 |
| One ball in. Thousands out. | 0.9 | +1.01 |
| It starts with one. | 0.6 | +0.68 |
| It only gets bigger. | 0.2 | +0.22 |
| The last crush is the big one. | 0.0 | +0.00 |
| 1. {m}. {mm}. Then chaos. | 0.0 | +0.00 |
| Count the crushes. | 0.0 | +0.00 |
| Which color wave is your favorite? | 0.0 | +0.00 |
| Guess how many balls before it breaks. | 0.0 | +0.00 |
| The ring never survives. | 0.9 | -0.19 |
| Watch it until the end. | 0.5 | -0.39 |
| Wait for the ring to break. | 0.9 | -0.55 |
| Every crush makes {m} more. | 0.9 | -0.57 |
| Loop it. You won't find the cut. | 0.9 | -1.02 |

## ask

| option | evidence | lift |
|---|---|---|
| Send this to someone who can't stop watching these. | 0.9 | +1.05 |
| Which color wave was the biggest? Tell me below. | 1.7 | +0.13 |
| Did you spot where the loop restarts? | 0.0 | +0.00 |
| How many balls do you think made it out? | 2.7 | -0.11 |
| Guess the final count before you rewatch. | 1.4 | -0.70 |

## Posts

| video | score | lift | views | avg watch | skip |
|---|---|---|---|---|---|
| 001 | 10.71 | +2.16 | 1893 | 13.1s | 0.276 |
| 002 | 8.29 | -1.17 | 171 | 11.4s | 0.366 |
| 003 | 7.30 | -2.16 | 162 | 8.5s | 0.4 |
| 004 | 8.26 | -1.19 | 214 | 12.0s | 0.331 |
| 005 | 8.81 | -0.39 | 429 | 11.2s | 0.304 |
| 006 | 10.70 | +2.15 | 212 | 52.9s | 0.331 |
| 007 | 10.30 | +1.74 | 1657 | 11.9s | 0.312 |
| 008 | 8.26 | -1.20 | 259 | 12.3s | 0.264 |
| 009 | 10.10 | +1.55 | 1876 | 10.8s | 0.328 |

## Physics knobs (drift toward what works)

- force: centre 1.03, spread 0.25
- pull: centre 2.17, spread 0.33
- assist: centre 1.51, spread 0.25

## Retired options

- none yet
