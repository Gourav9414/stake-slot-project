# Clockwork Kingdom — Math Review Notes

**Engine stage:** Standalone deterministic math prototype  
**Target:** 96.00% uncapped theoretical RTP  
**Reel geometry:** 5 reels × 3 visible rows  
**Paylines:** 20 fixed left-to-right lines  
**Round cap:** 5,000× total bet

## Reel strips

Each reel has 50 stops and the same symbol inventory, independently shuffled:

| Symbol | Stops per reel |
|---|---:|
| Wild (W) | 1 |
| Phoenix (PHX) | 2 |
| Gear (GEAR) | 4 |
| Key (KEY) | 5 |
| A | 8 |
| K | 8 |
| Q | 10 |
| J | 10 |
| Scatter (S) | 2 |
| **Total** | **50** |

Each reel stop reveals three consecutive symbols, wrapping at the end of the strip. Reel stops are independent across reels.

## Win evaluation

- A payline win requires at least three matching symbols from reel 1 onward.
- Wild substitutes for every regular paying symbol, but not Scatter.
- For each line, the highest-paying eligible symbol combination is paid once.
- Line paytable amounts are multiplied by the line stake (total bet / 20).
- Scatter pays anywhere on the 15-cell visible board: 3 = 2×, 4 = 10×, 5+ = 50× total bet.
- 3 Scatters award 10 free spins; 4 award 15; 5+ award 20.
- Free spins use the same strips and paytable. They do not retrigger.
- The completed paid round is capped at 5,000× the paid bet.

## Analytical calibration

The script enumerates all 9⁵ symbol combinations for a single line using exact reel-symbol frequencies, and separately convolves the five reel-stop distributions to calculate the exact scatter-count distribution. It then solves one global paytable scale so the **uncapped** expected return, including scatter awards and expected free-spin returns, equals 96.00%.

| Contribution | Uncapped RTP |
|---|---:|
| Line wins, including free-spin line wins | 88.5218% |
| Scatter awards, including free-spin scatter awards | 7.4782% |
| **Total** | **96.0000%** |

The calibrated global scale applied to the provisional GDD paytable is 11.16089551766943. The actual scaled values are recorded in each simulation report under `math.paytable`.

**Important limitation:** The 5,000× round cap is applied to simulated paid rounds, but the cap's impact on the extreme tail has not been analytically bounded. Therefore 96.00% is the exact *uncapped* analytical RTP, not yet a certified post-cap RTP.

## Reproducible simulation evidence

Seed: `20261116`; bet: 1 virtual unit per paid round.

| Measure | 10,000 rounds | 100,000 rounds |
|---|---:|---:|
| Empirical RTP | 91.51195% | 96.34430% |
| 95% normal interval | 86.8219%–96.2020% | 94.6722%–98.0164% |
| Hit rate | 43.890% | 43.861% |
| Free-spin trigger rate | 1.910% | 1.970% |
| Average free spins per paid round | 0.2040 | 0.20985 |
| Maximum observed round win | 35.44× | 95.26× |

The 10,000-round sample is noisy and lands below target; its interval includes 96%. The 100,000-round estimate is 96.3443%, also consistent with the analytical target. Neither finite sample replaces the exact calculation or the SDK's publication checks.

## Reviewer checklist

- 5 reel strips × 50 stops; only configured symbols present.
- 20 unique paylines; all line positions are within rows 0–2.
- Wild does not substitute for Scatter.
- Wins require leftmost consecutive matches; no gaps are bridged.
- Free spins do not retrigger.
- RNG seed makes the local simulation reproducible.
- Non-positive bets are rejected.
- Completed round payout is capped.
- Unit tests and reproducible simulation run in CI.

## Remaining Stake Engine work

This standalone runner does not yet call the official Math SDK's `create_books`, optimizer, config generation, or RGS format verifier. Its JSON reports are development evidence, not publish files. Before Stake submission, the SDK-native game adapter and official generated books/lookup tables must be produced and validated, and the post-cap weighted RTP must be checked.
