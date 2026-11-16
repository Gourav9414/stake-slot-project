# Game Design Document — Clockwork Kingdom: Fortune Foundry

**Status:** Proposal for Project Owner approval  
**Target platform:** Stake Engine  
**Game type:** 5-reel video slot · 3 rows · 20 fixed paylines  
**Target theoretical RTP:** 96.00% (subject to exact math simulation and Stake review)

## 1. Game concept

Players enter a lost clockwork kingdom where a royal foundry turns ancient gears into treasure. The visual direction is polished fantasy-steampunk: brass machinery, glowing runes, jewel-toned symbols, and clear high-contrast win feedback. The tone is adventurous rather than horror-themed. The interface will be designed for desktop and mobile.

## 2. Core gameplay

- **Grid:** 5 reels × 3 visible rows.
- **Lines:** 20 fixed paylines, shown in a payline guide; each line is evaluated from left to right.
- **Wins:** Three or more matching symbols on adjacent reels, starting on reel 1, along an enabled payline. Only the highest applicable combination per line is paid; line wins are summed.
- **Wild:** The Clockwork Crown substitutes for all regular paying symbols. It does not substitute for the Scatter.
- **Scatter:** The Timepiece pays anywhere on the visible grid and triggers the free-spins feature.
- **Round flow:** One paid base-game spin resolves to a complete, precomputed outcome. Free-spin rounds are part of that outcome sequence and must resume/replay from recorded events.

## 3. Symbols and provisional paytable

All values below are **multipliers of one line bet**, not total-spin bet. These are design starting values only; final values and reel/outcome weights will be tuned together to reach the RTP target.

| Symbol | 3 of a kind | 4 of a kind | 5 of a kind |
|---|---:|---:|---:|
| Royal Crown (Wild) | 5× | 20× | 100× |
| Phoenix | 4× | 15× | 60× |
| Gear | 3× | 10× | 40× |
| Key | 2× | 8× | 30× |
| A | 1.5× | 5× | 20× |
| K | 1× | 4× | 15× |
| Q | 0.8× | 3× | 10× |
| J | 0.5× | 2× | 8× |

Scatter awards and any special-symbol interactions will be defined in the math specification before implementation. The table is deliberately provisional: it does not, by itself, establish a 96% RTP.

## 4. Bonus feature

**Time Rift Free Spins**
- 3 Scatters: 10 free spins.
- 4 Scatters: 15 free spins.
- 5 Scatters: 20 free spins.
- Free spins use the same 5×3 grid and 20 paylines.
- A retrigger rule, if retained after math review, will be explicitly capped and represented in the recorded outcome events.
- No bonus buy, gamble feature, player-controlled cash-out, or progressive jackpot is proposed for the initial release.

## 5. Math and volatility targets

| Metric | Design target |
|---|---:|
| Theoretical overall RTP | **96.00%** |
| Base-game RTP contribution | 72.00% |
| Free-spins RTP contribution | 24.00% |
| Volatility | Medium-high |
| Base-game hit frequency | Initial target 25–30% |
| Maximum win | Proposed cap 5,000× total bet |

The RTP split, hit frequency, volatility, bonus frequency, and maximum-win cap are targets to validate—not measured results. The math team will generate a reproducible outcome distribution, run at least 1,000,000 simulated paid rounds per mode/configuration where supported, calculate confidence intervals and contribution breakdowns, and reconcile every probability, payout, and event record. If the exact math cannot meet all targets simultaneously, the Project Owner will be shown the trade-offs before any design change.

## 6. Technical and Stake Engine requirements

- Use the Stake Engine Math SDK/framework and its current official project template; confirm exact required filenames and package schema against the SDK version before coding.
- Generate static, weighted, precomputed round outcomes. The frontend must display the selected outcome and must not independently generate or alter gambling results.
- Use integer-safe payout/probability representations where required by the SDK; validate CSV/table/book parity and mode weights.
- Integrate through the Stake Engine RGS flow: authenticate session, request/play the round, present returned events, and settle/end the round. Never hardcode the runtime RGS URL.
- Persist sufficient event/progress data for interrupted-round recovery and replay. Replay must reproduce the stored round, not regenerate it.
- Separate math logic, game state, configuration, generated math assets, and frontend presentation. Keep secrets and credentials out of the repository.

## 7. Approval gates and delivery plan

1. **Design approval (this PR):** Approve theme, grid, paylines, symbols, bonus direction, and target metrics.
2. **Math prototype:** Implement the SDK-compatible game model; verify deterministic outcomes, payout accounting, RTP, volatility, and maximum win. Submit simulation evidence for review.
3. **Playable client and RGS:** Build the 5×3 interface, event playback, mobile layout, authentication, settlement, interruption recovery, and replay.
4. **Compliance and submission QA:** Run SDK validators, regression tests, math parity checks, and Stake review preparation. No claim of approval or certification until Stake confirms it.

**Owner decisions requested:** Approve or revise the proposed theme, provisional paytable direction, free-spins awards, 96.00% RTP target, medium-high volatility, and 5,000× proposed max-win cap. No implementation work begins until the Project Owner explicitly approves this design.
