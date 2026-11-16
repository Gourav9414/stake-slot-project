# Clockwork Kingdom — Fortune Foundry

A 5-reel × 3-row, 20-fixed-payline slot prototype targeting 96.00% theoretical RTP.

## Play the local virtual-credit prototype

From the repository root:

```bash
python -m http.server 8000
```

Open [http://localhost:8000/web/](http://localhost:8000/web/) in your browser. The playable front end is a virtual-credit demo and does not connect to Stake Engine, an RGS, or a wallet.

## Run the local math prototype

```bash
python games/clockwork_kingdom/run.py --spins 10000 --seed 20261116
python -m unittest discover -s tests -v
node --test tests/test_frontend.mjs
```

The simulation reports are in `games/clockwork_kingdom/reports/`. The **uncapped** theoretical RTP is calculated analytically from the reel strips, payline paytable, scatter awards, and non-retriggering free-spin expectation. The 5,000× round cap is applied in simulation; its extreme-tail RTP effect is not analytically bounded yet. Monte Carlo results are sample estimates and vary with seed and sample size.

## Stake Engine status

The repository contains a standalone math prototype and a playable HTML5 virtual-credit front end. It is **not yet a Stake Engine publication package or RGS-integrated game**. The official Math SDK's `create_books`, optimizer, generated configs, compressed book/lookup-table parity, and RGS format verification still need to be integrated and run. The browser demo generates local outcomes and must not be used for real-money play.

See the [official Math SDK](https://github.com/engineio/math-sdk) and [Stake Engine Math Quick Start](https://stake-engine.com/docs/math/quick-start).
