"""Deterministic single-round game state and event generation."""
from __future__ import annotations

import random
from typing import Any

from game_config import GameConfig, PAYLINES

class GameState:
    def __init__(self, config: GameConfig):
        self.config = config

    def _draw_board(self, rng: random.Random) -> list[list[str]]:
        # Board is row-major: board[row][reel]. Each reel stop is independently drawn.
        columns = []
        for reel in self.config.reels:
            stop = rng.randrange(len(reel))
            columns.append([reel[(stop + row) % len(reel)] for row in range(3)])
        return [[columns[reel][row] for reel in range(5)] for row in range(3)]

    def _line_wins(self, board: list[list[str]], bet: float) -> tuple[list[dict[str, Any]], float]:
        line_bet = bet / self.config.num_paylines
        wins = []
        total = 0.0
        for line_number, pattern in enumerate(PAYLINES, start=1):
            symbols = tuple(board[row][reel] for reel, row in enumerate(pattern))
            best_symbol = None
            best_count = 0
            best_multiplier = 0.0
            for target, payouts in self.config.paytable.items():
                run = 0
                for symbol in symbols:
                    if symbol == target or (symbol == "W" and target != "W"):
                        run += 1
                    else:
                        break
                multiplier = payouts.get(run, 0.0)
                if multiplier > best_multiplier:
                    best_symbol, best_count, best_multiplier = target, run, multiplier
            if best_multiplier > 0:
                amount = best_multiplier * line_bet
                wins.append({
                    "line": line_number, "symbol": best_symbol, "count": best_count,
                    "multiplier": best_multiplier, "amount": amount,
                })
                total += amount
        return wins, total

    def _resolve_spin(self, rng: random.Random, bet: float, is_free_spin: bool) -> dict[str, Any]:
        board = self._draw_board(rng)
        line_wins, line_amount = self._line_wins(board, bet)
        scatter_count = sum(symbol == "S" for row in board for symbol in row)
        scatter_amount = self.config.scatter_payout(scatter_count) * bet
        fs_award = 0 if is_free_spin else self.config.free_spin_award(scatter_count)
        return {
            "board": board,
            "line_wins": line_wins,
            "line_payout": line_amount,
            "scatter_count": scatter_count,
            "scatter_payout": scatter_amount,
            "free_spins_awarded": fs_award,
            "payout": line_amount + scatter_amount,
        }

    def run_spin(self, rng: random.Random, bet: float = 1.0, round_id: int | None = None) -> dict[str, Any]:
        if bet <= 0:
            raise ValueError("Bet must be greater than zero.")
        base = self._resolve_spin(rng, bet, is_free_spin=False)
        free_spins = [
            self._resolve_spin(rng, bet, is_free_spin=True)
            for _ in range(base["free_spins_awarded"])
        ]
        uncapped_total = base["payout"] + sum(spin["payout"] for spin in free_spins)
        cap = self.config.max_win * bet
        total = min(uncapped_total, cap)
        events = [
            {"type": "reveal", "board": base["board"]},
            {"type": "line_wins", "wins": base["line_wins"], "amount": base["line_payout"]},
            {"type": "scatter", "count": base["scatter_count"], "amount": base["scatter_payout"]},
        ]
        if free_spins:
            events.append({"type": "free_spins_trigger", "count": len(free_spins)})
            for index, spin in enumerate(free_spins, start=1):
                events.append({
                    "type": "free_spin", "index": index, "board": spin["board"],
                    "line_wins": spin["line_wins"], "scatter_count": spin["scatter_count"],
                    "payout": spin["payout"],
                })
        if uncapped_total > cap:
            events.append({"type": "win_cap", "cap": cap})
        events.append({"type": "round_total", "payout": total})
        return {
            "id": round_id,
            "bet": bet,
            "base": base,
            "free_spins": free_spins,
            "free_spins_played": len(free_spins),
            "uncapped_payout": uncapped_total,
            "payout": total,
            "payout_multiplier": total / bet,
            "hit": total > 0,
            "events": events,
        }
