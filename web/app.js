import { parseReelCsv, resolvePaidRound, SYMBOLS, BASE_PAYTABLE, PAYTABLE_SCALE, PAYLINES } from "./engine.js";

const $ = id => document.getElementById(id);
const balanceEl = $("balance");
const betEl = $("bet");
const spinButton = $("spin");
const lastWinEl = $("last-win");
const statusEl = $("status");
const summaryEl = $("round-summary");
const reelsEl = $("reels");
let reels = null;
let balance = 1000;
let busy = false;

const money = value => Number(value).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

function makePaytable() {
  const rows = [`<div class="pay-row header"><span>SYMBOL</span><span>3</span><span>4</span><span>5</span></div>`];
  for (const [symbol, pays] of Object.entries(BASE_PAYTABLE)) {
    const glyph = SYMBOLS[symbol].glyph;
    rows.push(`<div class="pay-row"><span class="pay-symbol">${glyph} ${symbol}</span><span>${(pays[3] * PAYTABLE_SCALE).toFixed(1)}×</span><span>${(pays[4] * PAYTABLE_SCALE).toFixed(1)}×</span><span>${(pays[5] * PAYTABLE_SCALE).toFixed(1)}×</span></div>`);
  }
  $("paytable").innerHTML = rows.join("");
}

function renderBoard(board, lineWins = [], scatterPositions = []) {
  const winning = new Set();
  for (const win of lineWins) for (const pos of win.positions) winning.add(`${pos.row}:${pos.reel}`);
  const scatters = new Set(scatterPositions.map(pos => `${pos.row}:${pos.reel}`));
  reelsEl.innerHTML = Array.from({ length: 5 }, (_, reel) => {
    const cells = Array.from({ length: 3 }, (_, row) => {
      const symbol = board[row][reel];
      const classes = ["cell"];
      if (winning.has(`${row}:${reel}`)) classes.push("win-cell");
      else if (scatters.has(`${row}:${reel}`)) classes.push("scatter-cell");
      if (["PHX", "GEAR", "KEY"].includes(symbol)) classes.push("symbol-small");
      return `<div class="${classes.join(" ")}" title="${SYMBOLS[symbol].name}">${SYMBOLS[symbol].glyph}</div>`;
    }).join("");
    return `<div class="reel">${cells}</div>`;
  }).join("");
}

function updateWallet() {
  balanceEl.textContent = money(balance);
  spinButton.disabled = busy || !reels || balance < Number(betEl.value);
}

function formatWinSummary(result) {
  const baseLines = result.base.lineWins.length;
  const scatterCount = result.base.scatterCount;
  const pieces = [];
  if (baseLines) pieces.push(`${baseLines} winning line${baseLines === 1 ? "" : "s"}`);
  if (scatterCount >= 3) pieces.push(`${scatterCount} Scatters · ${result.base.freeSpinsAwarded} free spins`);
  if (result.freeSpins.length) {
    const featureTotal = result.freeSpins.reduce((sum, spin) => sum + spin.payout, 0);
    pieces.push(`Time Rift paid ${money(featureTotal)} across ${result.freeSpins.length} free spins`);
  }
  if (result.capped) pieces.push("5,000× round cap reached");
  return pieces.length ? pieces.join(" · ") : `No win this round. ${PAYLINES.length} paylines were evaluated.`;
}

async function spin() {
  if (busy || !reels) return;
  const bet = Number(betEl.value);
  if (bet <= 0 || balance < bet) return;
  busy = true;
  balance -= bet;
  updateWallet();
  statusEl.textContent = "The foundry is turning…";
  summaryEl.textContent = "Reels in motion…";
  lastWinEl.textContent = "—";
  reelsEl.classList.add("spinning");
  await delay(620);
  try {
    const result = resolvePaidRound(reels, bet);
    reelsEl.classList.remove("spinning");
    renderBoard(result.base.board, result.base.lineWins, result.base.scatterPositions);
    balance += result.payout;
    lastWinEl.textContent = money(result.payout);
    statusEl.textContent = result.payout > 0
      ? `ROUND WIN · ${result.payoutMultiplier.toFixed(2)}× BET · ${money(result.payout)} CREDITS`
      : "NO WIN · THE KINGDOM KEEPS ITS SECRETS";
    summaryEl.textContent = formatWinSummary(result);
  } catch (error) {
    balance += bet;
    statusEl.textContent = `Spin error: ${error.message}`;
    statusEl.classList.add("loading-error");
  } finally {
    reelsEl.classList.remove("spinning");
    busy = false;
    updateWallet();
  }
}

async function init() {
  makePaytable();
  betEl.addEventListener("change", updateWallet);
  spinButton.addEventListener("click", spin);
  try {
    const response = await fetch("../games/clockwork_kingdom/reels/BR0.csv");
    if (!response.ok) throw new Error(`Could not load reel strips (${response.status}).`);
    reels = parseReelCsv(await response.text());
    renderBoard([["GEAR","J","KEY","J","GEAR"],["J","J","K","A","K"],["KEY","KEY","J","J","KEY"]]);
    statusEl.textContent = "Reels ready. Choose a virtual bet and spin.";
    updateWallet();
  } catch (error) {
    statusEl.textContent = `${error.message} Start the local web server from the repository root.`;
    statusEl.classList.add("loading-error");
    updateWallet();
  }
}

init();
