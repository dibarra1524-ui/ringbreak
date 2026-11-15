# What the Ringbreak formula has learned

Posts in history: 4. Posts with usable numbers: 4. Random-try rate right now: 44%.

Lift = how far a post scored above or below its neighbours. Positive is good.

## arena

| option | evidence | lift |
|---|---|---|
| circle | 1.3 | +0.89 |
| square | 0.0 | +0.00 |
| diamond | 0.0 | +0.00 |
| oct | 0.0 | +0.00 |
| squircle | 0.0 | +0.00 |
| pent | 0.3 | -0.01 |
| hex | 0.4 | -0.30 |

## spin

| option | evidence | lift |
|---|---|---|
| 0 | 1.7 | +0.77 |
| -1 | 0.0 | +0.00 |
| 1 | 0.4 | -0.30 |

## angle

| option | evidence | lift |
|---|---|---|
| 0 | 1.3 | +0.89 |
| 90 | 0.0 | +0.00 |
| 45 | 0.3 | -0.01 |
| -45 | 0.4 | -0.30 |

## palette

| option | evidence | lift |
|---|---|---|
| neon | 1.3 | +0.89 |
| fire | 0.0 | +0.00 |
| ice | 0.0 | +0.00 |
| candy | 0.0 | +0.00 |
| pastel | 0.3 | -0.01 |
| mono | 0.4 | -0.30 |

## bg

| option | evidence | lift |
|---|---|---|
| black | 1.3 | +0.89 |
| navy | 0.0 | +0.00 |
| plum | 0.3 | -0.01 |
| forest | 0.4 | -0.30 |

## fx

| option | evidence | lift |
|---|---|---|
| none | 1.3 | +0.89 |
| glow | 0.0 | +0.00 |
| trail+glow | 0.3 | -0.01 |
| trail | 0.4 | -0.30 |

## ball

| option | evidence | lift |
|---|---|---|
| solid | 1.3 | +0.89 |
| shine | 0.0 | +0.00 |
| hollow | 0.8 | -0.25 |

## ball_r

| option | evidence | lift |
|---|---|---|
| 9.0 | 1.3 | +0.89 |
| 10.5 | 0.3 | -0.01 |
| 7.5 | 0.4 | -0.30 |

## mult

| option | evidence | lift |
|---|---|---|
| 8 | 1.7 | +0.77 |
| 10 | 0.0 | +0.00 |
| 6 | 0.4 | -0.30 |

## shake

| option | evidence | lift |
|---|---|---|
| 0 | 1.3 | +0.89 |
| 1 | 0.8 | -0.25 |

## counter

| option | evidence | lift |
|---|---|---|
| 0 | 1.3 | +0.89 |
| 1 | 0.8 | -0.25 |

## sound

| option | evidence | lift |
|---|---|---|
| classic | 1.7 | +0.59 |
| penta | 0.3 | -0.01 |

## field

| option | evidence | lift |
|---|---|---|
| pull | 1.3 | +0.89 |
| gravity | 0.0 | +0.00 |
| pulse | 0.0 | +0.00 |
| tumble | 0.3 | -0.01 |
| vortex | 0.4 | -0.30 |

## pegs

| option | evidence | lift |
|---|---|---|
| none | 1.3 | +0.89 |
| field | 0.3 | -0.01 |
| arc | 0.4 | -0.30 |

## bounce

| option | evidence | lift |
|---|---|---|
| normal | 1.3 | +0.89 |
| soft | 0.3 | -0.01 |
| bouncy | 0.4 | -0.30 |

## hook

| option | evidence | lift |
|---|---|---|
| One ball in. Thousands out. | 0.8 | +1.11 |
| Wait for the ring to break. | 0.5 | +0.01 |
| It starts with one. | 0.0 | +0.00 |
| How many can the ring hold? | 0.0 | +0.00 |
| Watch it until the end. | 0.0 | +0.00 |
| The last crush is the big one. | 0.0 | +0.00 |
| 1. {m}. {mm}. Then chaos. | 0.0 | +0.00 |
| The ring never survives. | 0.0 | +0.00 |
| Count the crushes. | 0.0 | +0.00 |
| It only gets bigger. | 0.0 | +0.00 |
| Which color wave is your favorite? | 0.0 | +0.00 |
| Guess how many balls before it breaks. | 0.0 | +0.00 |
| Every crush makes {m} more. | 0.3 | -0.01 |
| Loop it. You won't find the cut. | 0.4 | -0.30 |

## ask

| option | evidence | lift |
|---|---|---|
| How many balls do you think made it out? | 1.3 | +0.71 |
| Which color wave was the biggest? Tell me below. | 0.5 | +0.01 |
| Did you spot where the loop restarts? | 0.0 | +0.00 |
| Send this to someone who can't stop watching these. | 0.0 | +0.00 |
| Guess the final count before you rewatch. | 0.3 | -0.01 |

## Posts

| video | score | lift | views | avg watch | skip |
|---|---|---|---|---|---|
| 001 | 10.72 | +2.44 | 1892 | 13.1s | 0.275 |
| 002 | 8.31 | +0.03 | 170 | 11.5s | 0.361 |
| 003 | 7.31 | -1.00 | 161 | 8.6s | 0.396 |
| 004 | 8.28 | -0.03 | 213 | 12.1s | 0.327 |

## Physics knobs (drift toward what works)

- force: centre 1.00, spread 0.33
- pull: centre 2.00, spread 0.42
- assist: centre 1.40, spread 0.33

## Retired options

- none yet
