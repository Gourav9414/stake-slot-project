# Clockwork Kingdom — Local Windows Run Guide

This guide starts the **local virtual-credit browser game**. No paid API, cookies, API key, wallet, RGS account, or hosting account is required.

## What this version does (and does not do)

- Playable 5-reel × 3-row slot prototype with 20 fixed paylines, wilds, scatters, and non-retriggering free spins.
- Browser outcomes are generated locally in JavaScript from the checked-in reel strips.
- Python runs the standalone math simulator and writes a JSON simulation report.
- **Important:** the Python simulator creates simulation reports, not official Stake Engine SDK math books. Official SDK book/LUT generation and certification are not claimed or verified.
- Virtual credits only. There is no real-money play, wallet, login, RGS, or remote API.

## 1. Install the free tools (once)

Install Git for Windows and Python 3.12 (64-bit). Node.js 22 LTS is optional and is only needed for the frontend automated test. During Python setup, enable **Add Python to PATH** if offered.

## 2. Download the project

Open **Windows PowerShell** and paste:

```powershell
git clone https://github.com/Gourav9414/stake-slot-project.git
Set-Location stake-slot-project
```

If you already downloaded the project, update it instead:

```powershell
Set-Location "$HOME\stake-slot-project"
git pull origin main
```

## 3. Run the Python math simulation

From the repository folder, paste:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe games/clockwork_kingdom/run.py --spins 100000 --seed 20261116
```

The standalone simulator uses only Python's standard library; no paid service or API is used. The JSON report is saved under:

`games/clockwork_kingdom/reports/simulation_100000.json`

For a quicker 10,000-round run:

```powershell
.\.venv\Scripts\python.exe games/clockwork_kingdom/run.py --spins 10000 --seed 20261116
```

The report includes sample RTP and the uncapped analytical target. Monte Carlo RTP is an estimate; the 96% figure is not a certified or post-win-cap RTP guarantee.

## 4. Start the local browser game

Keep PowerShell in the **repository root** (the folder containing `web` and `games`). Run:

```powershell
py -3.12 -m http.server 8000
```

Leave that window open. Open Chrome or Edge and visit:

**http://localhost:8000/web/**

Choose a virtual bet and press **SPIN**. The game starts with 1,000 demo credits. Stop the server with `Ctrl+C`.

Do not double-click `web/index.html`: the browser needs the local HTTP server to load the reel CSV and JavaScript modules correctly.

## 5. Optional automated tests

Open a **second** PowerShell window:

```powershell
Set-Location "$HOME\stake-slot-project"
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
node --test tests/test_frontend.mjs
```

The Node.js test command requires Node.js 22 LTS. The game itself runs in the browser and does not require Node.js or npm.

## Troubleshooting

- **'py' is not recognized:** reinstall Python 3.12 and enable PATH, or use `python` instead of `py -3.12`.
- **Port 8000 is busy:** run `py -3.12 -m http.server 8001` and open `http://localhost:8001/web/`.
- **Reels do not load:** stop the server with `Ctrl+C`, make sure PowerShell is in the repository root, then start it again.
- **Spin is disabled:** wait for the status message to say the reels are ready, and choose a bet no larger than the remaining virtual balance.
