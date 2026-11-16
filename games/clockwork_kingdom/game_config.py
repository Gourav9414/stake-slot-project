"""Clockwork Kingdom: Fortune Foundry math configuration.

Standalone deterministic math prototype. Reel strips and the paytable are
calibrated analytically to a 96.00% *uncapped* theoretical RTP target.
"""
from __future__ import annotations

import csv
from collections import Counter
from itertools import product
from pathlib import Path

GAME_ID = "clockwork_kingdom"
ROOT = Path(__file__).resolve().parent

# Multipliers are units of one line bet (total bet / 20).
BASE_PAYTABLE = {
    "W": {3: 5.0, 4: 20.0, 5: 100.0},
    "PHX": {3: 4.0, 4: 15.0, 5: 60.0},
    "GEAR": {3: 3.0, 4: 10.0, 5: 40.0},
    "KEY": {3: 2.0, 4: 8.0, 5: 30.0},
    "A": {3: 1.5, 4: 5.0, 5: 20.0},
    "K": {3: 1.0, 4: 4.0, 5: 15.0},
    "Q": {3: 0.8, 4: 3.0, 5: 10.0},
    "J": {3: 0.5, 4: 2.0, 5: 8.0},
}
SCATTER_PAYS = {3: 2.0, 4: 10.0, 5: 50.0}  # total-bet multipliers; 5+ pays 50x
FREE_SPINS = {3: 10, 4: 15, 5: 20}         # 5+ awards 20 spins; no retriggers

# Each tuple gives the visible row on reels 1..5.
PAYLINES = (
    (0,0,0,0,0), (1,1,1,1,1), (2,2,2,2,2),
    (0,1,2,1,0), (2,1,0,1,2), (0,0,1,2,2),
    (2,2,1,0,0), (1,0,1,2,1), (1,2,1,0,1),
    (0,1,1,1,2), (2,1,1,1,0), (0,1,0,1,2),
    (2,1,2,1,0), (1,1,0,1,1), (1,1,2,1,1),
    (0,2,1,0,2), (2,0,1,2,0), (0,0,2,0,0),
    (2,2,0,2,2), (1,0,0,0,1),
)

class GameConfig:
    game_id = GAME_ID
    num_reels = 5
    num_rows = 3
    num_paylines = 20
    target_rtp = 0.96
    max_win = 5000.0
    line_bet_fraction = 1.0 / num_paylines

    def __init__(self) -> None:
        self.reels = self._load_reels(ROOT / "reels" / "BR0.csv")
        self._validate_reels()
        self.scatter_distribution = self._scatter_count_distribution()
        self.expected_scatter_return = sum(
            probability * self.scatter_payout(count)
            for count, probability in self.scatter_distribution.items()
        )
        self.expected_free_spins = sum(
            probability * self.free_spin_award(count)
            for count, probability in self.scatter_distribution.items()
        )
        self.expected_line_return_unscaled = self._expected_line_return_unscaled()
        numerator = self.target_rtp / (1.0 + self.expected_free_spins) - self.expected_scatter_return
        if self.expected_line_return_unscaled <= 0 or numerator <= 0:
            raise ValueError("Reel strips cannot support the requested RTP with this paytable.")
        self.paytable_scale = numerator / self.expected_line_return_unscaled
        self.paytable = {
            symbol: {count: value * self.paytable_scale for count, value in pays.items()}
            for symbol, pays in BASE_PAYTABLE.items()
        }
        # This is the uncapped analytical target. The effect of the 5,000x
        # round cap on the extreme tail is not analytically bounded in this prototype.
        self.theoretical_rtp_uncapped = (
            self.expected_line_return_unscaled * self.paytable_scale
            + self.expected_scatter_return
        ) * (1.0 + self.expected_free_spins)

    @staticmethod
    def _load_reels(path: Path) -> list[list[str]]:
        with path.open(newline="", encoding="utf-8") as file:
            rows = [row for row in csv.reader(file) if row]
        if not rows or any(len(row) != 5 for row in rows):
            raise ValueError("BR0.csv must contain 5 columns (one per reel).")
        return [[row[column].strip() for row in rows] for column in range(5)]

    def _validate_reels(self) -> None:
        valid = set(BASE_PAYTABLE) | {"S"}
        if len(self.reels) != 5 or any(len(reel) < 5 for reel in self.reels):
            raise ValueError("Expected five reel strips, each with at least five stops.")
        for index, reel in enumerate(self.reels, start=1):
            unknown = set(reel) - valid
            if unknown:
                raise ValueError(f"Unknown symbols on reel {index}: {sorted(unknown)}")
            if "S" not in reel:
                raise ValueError(f"Reel {index} must contain Scatter symbols.")

    @staticmethod
    def scatter_payout(count: int) -> float:
        return SCATTER_PAYS.get(min(count, 5), 0.0)

    @staticmethod
    def free_spin_award(count: int) -> int:
        return FREE_SPINS.get(min(count, 5), 0)

    @staticmethod
    def line_payout_unscaled(symbols: tuple[str, ...]) -> float:
        """Evaluate one left-to-right line; W substitutes, but never for Scatter."""
        best = 0.0
        for target, payouts in BASE_PAYTABLE.items():
            run = 0
            for symbol in symbols:
                if symbol == target or (symbol == "W" and target != "W"):
                    run += 1
                else:
                    break
            if run >= 3:
                best = max(best, payouts[run])
        return best

    def _expected_line_return_unscaled(self) -> float:
        probabilities = []
        for reel in self.reels:
            counts = Counter(reel)
            probabilities.append({symbol: count / len(reel) for symbol, count in counts.items()})
        symbols = tuple(sorted(set().union(*(set(p) for p in probabilities))))
        expected = 0.0
        for outcome in product(symbols, repeat=5):
            probability = 1.0
            for reel_index, symbol in enumerate(outcome):
                probability *= probabilities[reel_index].get(symbol, 0.0)
            if probability:
                expected += probability * self.line_payout_unscaled(outcome)
        return expected

    def _scatter_count_distribution(self) -> dict[int, float]:
        # Count scatters across each reel's three consecutive visible positions,
        # then convolve the five independent reel-stop distributions.
        distribution = {0: 1.0}
        for reel in self.reels:
            strip_length = len(reel)
            per_reel = Counter()
            for stop in range(strip_length):
                count = sum(reel[(stop + row) % strip_length] == "S" for row in range(3))
                per_reel[count] += 1.0 / strip_length
            combined = Counter()
            for previous_count, previous_probability in distribution.items():
                for reel_count, reel_probability in per_reel.items():
                    combined[previous_count + reel_count] += previous_probability * reel_probability
            distribution = dict(combined)
        return distribution

    def summary(self) -> dict:
        line_rtp = self.expected_line_return_unscaled * self.paytable_scale * (1 + self.expected_free_spins)
        scatter_rtp = self.expected_scatter_return * (1 + self.expected_free_spins)
        return {
            "game_id": self.game_id,
            "target_rtp": self.target_rtp,
            "theoretical_rtp_uncapped": self.theoretical_rtp_uncapped,
            "win_cap_rtp_effect": "not analytically bounded; cap not hit in supplied simulations",
            "paytable_scale": self.paytable_scale,
            "line_rtp_contribution_uncapped": line_rtp,
            "scatter_rtp_contribution_uncapped": scatter_rtp,
            "expected_free_spins_per_paid_round": self.expected_free_spins,
            "scatter_trigger_probability": sum(p for count, p in self.scatter_distribution.items() if count >= 3),
            "scatter_count_distribution": {str(k): v for k, v in sorted(self.scatter_distribution.items())},
            "max_win_cap": self.max_win,
            "paytable": self.paytable,
        }
