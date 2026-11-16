# Clockwork Kingdom — Fortune Foundry

A local 5-reel × 3-row, 20-fixed-payline slot prototype with virtual credits.

## Play locally

Follow [RUN_INSTRUCTIONS.md](RUN_INSTRUCTIONS.md). From the repository root:

```powershell
py -3.12 -m http.server 8000
```

Open http://localhost:8000/web/ in your browser.

## Project layout

- `web/`: standalone HTML, CSS and JavaScript game client.
- `games/clockwork_kingdom/`: Python math model, reel strips and simulation runner.
- `tests/`: Python and JavaScript tests.

## Scope and math status

This is a local demonstration only. It uses virtual credits and does not connect to Stake Engine, an RGS, a wallet, or a remote API. The Python runner produces Monte Carlo simulation reports; it does **not** currently generate official Stake Engine math books or lookup tables. The 96% value is an uncapped analytical target, not a certified/post-cap RTP guarantee.
