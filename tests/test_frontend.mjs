import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { parseReelCsv, drawBoard, linePayout, resolvePaidRound, PAYLINES, PAYTABLE_SCALE } from '../web/engine.js';

const csv = await readFile(new URL('../games/clockwork_kingdom/reels/BR0.csv', import.meta.url), 'utf8');
const reels = parseReelCsv(csv);

test('loads five 50-stop reels and 20 unique paylines', () => {
  assert.equal(reels.length, 5);
  assert.deepEqual(reels.map(reel => reel.length), [50,50,50,50,50]);
  assert.equal(PAYLINES.length, 20);
  assert.equal(new Set(PAYLINES.map(line => line.join(','))).size, 20);
});

test('draws a 3 by 5 board from deterministic reel stops', () => {
  const board = drawBoard(reels, () => 0);
  assert.equal(board.length, 3);
  assert.ok(board.every(row => row.length === 5));
});

test('wild substitutes for regular symbols but not scatter', () => {
  assert.ok(linePayout(['PHX','W','PHX','A','A']).multiplier > 0);
  assert.equal(linePayout(['S','W','W','W','W']).multiplier, 0);
});

test('a completed round is reproducible with the same random stream', () => {
  const a = resolvePaidRound(reels, 1, () => 0.12345);
  const b = resolvePaidRound(reels, 1, () => 0.12345);
  assert.deepEqual(a, b);
});

test('paytable scale is positive and the paid round respects the max win cap', () => {
  assert.ok(PAYTABLE_SCALE > 0);
  const result = resolvePaidRound(reels, 1, () => 0.5);
  assert.ok(result.payout <= 5000);
});

test('three visible Scatters award ten non-retriggering free spins', () => {
  const stops = reels.map(reel => {
    const trigger = reel.findIndex((symbol, index) => [0,1,2].some(row => reel[(index + row) % reel.length] === 'S'));
    const safe = reel.findIndex((symbol, index) => [0,1,2].every(row => reel[(index + row) % reel.length] !== 'S'));
    return { trigger, safe };
  });
  const selected = [stops[0].trigger, stops[1].trigger, stops[2].trigger, stops[3].safe, stops[4].safe];
  const sequence = selected.map(stop => (stop + 0.25) / 50);
  const rng = () => sequence.length ? sequence.shift() : 0;
  const result = resolvePaidRound(reels, 1, rng);
  assert.equal(result.base.scatterCount, 3);
  assert.equal(result.base.freeSpinsAwarded, 10);
  assert.equal(result.freeSpins.length, 10);
  assert.ok(result.freeSpins.every(spin => spin.freeSpinsAwarded === 0));
});
