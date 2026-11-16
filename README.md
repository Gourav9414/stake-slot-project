# Clockwork Kingdom — Fortune Foundry

A 5-reel × 3-row, 20-fixed-payline slot prototype targeting 96.00% theoretical RTP.

## Run the local math prototype

```bash
python games/clockwork_kingdom/run.py --spins 10000 --seed 20261116
python -m unittest discover -s tests -v
```

The simulation report is written to `games/clockwork_kingdom/reports/`. The **uncapped** theoretical RTP is calculated analytically from the reel strips, payline paytable, scatter awards, and non-retriggering free-spin expectation. The 5,000× round cap is applied in simulation; its extreme-tail RTP effect is not analytically bounded yet. Monte Carlo results are sample estimates and vary with seed and sample size.

## Stake Engine status

This branch contains a standalone math prototype and deterministic event model using the SDK-style game folder naming. It is **not yet a complete Stake Engine Math SDK publication package**. The official Math SDK's `create_books`, optimizer, generated configs, and RGS format verification still need to be run before this math can be called upload-ready. Do not upload the standalone simulation reports as a certified math package.

The official SDK uses Python 3.12+, expects each game under `games/<game_id>/`, and generates books, lookup tables, and configs from the SDK runner. See the [official Math SDK](https://github.com/engineio/math-sdk) and [quick-start](https://stake-engine.com/docs/math/quick-start).
