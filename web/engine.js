export const BASE_PAYTABLE = {
  W: { 3: 5, 4: 20, 5: 100 },
  PHX: { 3: 4, 4: 15, 5: 60 },
  GEAR: { 3: 3, 4: 10, 5: 40 },
  KEY: { 3: 2, 4: 8, 5: 30 },
  A: { 3: 1.5, 4: 5, 5: 20 },
  K: { 3: 1, 4: 4, 5: 15 },
  Q: { 3: 0.8, 4: 3, 5: 10 },
  J: { 3: 0.5, 4: 2, 5: 8 },
};

// Calibrated against games/clockwork_kingdom/reels/BR0.csv in the math prototype.
export const PAYTABLE_SCALE = 11.16089551766943;
export const TARGET_RTP = 0.96;
export const MAX_WIN = 5000;
export const PAYLINES = [
  [0,0,0,0,0], [1,1,1,1,1], [2,2,2,2,2],
  [0,1,2,1,0], [2,1,0,1,2], [0,0,1,2,2],
  [2,2,1,0,0], [1,0,1,2,1], [1,2,1,0,1],
  [0,1,1,1,2], [2,1,1,1,0], [0,1,0,1,2],
  [2,1,2,1,0], [1,1,0,1,1], [1,1,2,1,1],
  [0,2,1,0,2], [2,0,1,2,0], [0,0,2,0,0],
  [2,2,0,2,2], [1,0,0,0,1],
];
export const SCATTER_PAYS = { 3: 2, 4: 10, 5: 50 };
export const FREE_SPINS = { 3: 10, 4: 15, 5: 20 };
export const SYMBOLS = {
  W: { glyph: "👑", name: "Royal Crown" },
  PHX: { glyph: "🔥", name: "Phoenix" },
  GEAR: { glyph: "⚙️", name: "Gear" },
  KEY: { glyph: "🗝️", name: "Key" },
  A: { glyph: "A", name: "Ace" },
  K: { glyph: "K", name: "King" },
  Q: { glyph: "Q", name: "Queen" },
  J: { glyph: "J", name: "Jack" },
  S: { glyph: "⌛", name: "Timepiece Scatter" },
};

export function parseReelCsv(csvText) {
  const rows = csvText.trim().split(/\r?\n/).map(line => line.split(",").map(s => s.trim()));
  if (rows.length !== 50 || rows.some(row => row.length !== 5)) {
    throw new Error("Reel data must contain exactly 50 rows and 5 columns.");
  }
  const reels = Array.from({ length: 5 }, (_, column) => rows.map(row => row[column]));
  for (const reel of reels) {
    if (reel.some(symbol => !SYMBOLS[symbol])) throw new Error("Reel contains an unknown symbol.");
  }
  return reels;
}

export function drawBoard(reels, rng = Math.random) {
  if (!Array.isArray(reels) || reels.length !== 5 || reels.some(reel => reel.length !== 50)) {
    throw new Error("Expected five 50-stop reels.");
  }
  const columns = reels.map(reel => {
    const stop = Math.min(reel.length - 1, Math.floor(rng() * reel.length));
    return [0, 1, 2].map(row => reel[(stop + row) % reel.length]);
  });
  return [0, 1, 2].map(row => [0, 1, 2, 3, 4].map(reel => columns[reel][row]));
}

export function linePayout(symbols) {
  let best = { symbol: null, count: 0, multiplier: 0 };
  for (const [target, payouts] of Object.entries(BASE_PAYTABLE)) {
    let count = 0;
    for (const symbol of symbols) {
      if (symbol === target || (symbol === "W" && target !== "W")) count++;
      else break;
    }
    const multiplier = payouts[count] ? payouts[count] * PAYTABLE_SCALE : 0;
    if (multiplier > best.multiplier) best = { symbol: target, count, multiplier };
  }
  return best;
}

export function resolveSingleSpin(reels, bet, rng = Math.random, isFreeSpin = false) {
  const board = drawBoard(reels, rng);
  const lineWins = [];
  let linePayoutTotal = 0;
  PAYLINES.forEach((pattern, index) => {
    const symbols = pattern.map((row, reel) => board[row][reel]);
    const win = linePayout(symbols);
    if (win.multiplier > 0) {
      const amount = win.multiplier * (bet / PAYLINES.length);
      const positions = pattern.slice(0, win.count).map((row, reel) => ({ row, reel }));
      lineWins.push({ line: index + 1, symbol: win.symbol, count: win.count, multiplier: win.multiplier, amount, positions });
      linePayoutTotal += amount;
    }
  });
  const scatterPositions = [];
  board.forEach((row, rowIndex) => row.forEach((symbol, reelIndex) => {
    if (symbol === "S") scatterPositions.push({ row: rowIndex, reel: reelIndex });
  }));
  const scatterCount = scatterPositions.length;
  const scatterMultiplier = SCATTER_PAYS[Math.min(scatterCount, 5)] || 0;
  const scatterPayout = scatterMultiplier * bet;
  const freeSpinsAwarded = isFreeSpin ? 0 : (FREE_SPINS[Math.min(scatterCount, 5)] || 0);
  return {
    board, lineWins, linePayout: linePayoutTotal, scatterPositions, scatterCount,
    scatterMultiplier, scatterPayout, freeSpinsAwarded,
    payout: linePayoutTotal + scatterPayout,
  };
}

export function resolvePaidRound(reels, bet, rng = Math.random) {
  if (!Number.isFinite(bet) || bet <= 0) throw new Error("Bet must be positive.");
  const base = resolveSingleSpin(reels, bet, rng, false);
  const freeSpins = [];
  for (let i = 0; i < base.freeSpinsAwarded; i++) {
    freeSpins.push(resolveSingleSpin(reels, bet, rng, true));
  }
  const uncappedPayout = base.payout + freeSpins.reduce((sum, spin) => sum + spin.payout, 0);
  const payout = Math.min(uncappedPayout, MAX_WIN * bet);
  return {
    base, freeSpins, uncappedPayout, payout, payoutMultiplier: payout / bet,
    hit: payout > 0, capped: uncappedPayout > payout,
  };
}
