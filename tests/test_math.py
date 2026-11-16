import random
import sys
import unittest
from pathlib import Path

GAME_DIR = Path(__file__).resolve().parents[1] / "games" / "clockwork_kingdom"
sys.path.insert(0, str(GAME_DIR))
from game_config import GameConfig, PAYLINES
from gamestate import GameState


class MathEngineTests(unittest.TestCase):
    def setUp(self):
        self.config = GameConfig()
        self.state = GameState(self.config)

    def test_configuration_shape(self):
        self.assertEqual(len(self.config.reels), 5)
        self.assertEqual({len(reel) for reel in self.config.reels}, {50})
        self.assertEqual(len(PAYLINES), 20)
        self.assertEqual(len(set(PAYLINES)), 20)

    def test_theoretical_rtp_is_exact_uncapped_target(self):
        self.assertAlmostEqual(self.config.theoretical_rtp_uncapped, 0.96, places=12)

    def test_payline_requires_three_leftmost_adjacent_symbols(self):
        self.assertGreater(self.config.line_payout_unscaled(("PHX", "W", "PHX", "A", "A")), 0)
        self.assertEqual(self.config.line_payout_unscaled(("A", "A", "J", "A", "A")), 0)

    def test_wild_does_not_substitute_for_scatter(self):
        self.assertEqual(self.config.line_payout_unscaled(("S", "W", "W", "W", "W")), 0)

    def test_board_dimensions(self):
        board = self.state._draw_board(random.Random(2026))
        self.assertEqual(len(board), 3)
        self.assertTrue(all(len(row) == 5 for row in board))

    def test_free_spins_do_not_retrigger(self):
        rng = random.Random(4)
        for _ in range(100):
            result = self.state._resolve_spin(rng, 1.0, is_free_spin=True)
            self.assertEqual(result["free_spins_awarded"], 0)

    def test_round_is_reproducible(self):
        first = self.state.run_spin(random.Random(12345), round_id=1)
        second = self.state.run_spin(random.Random(12345), round_id=1)
        self.assertEqual(first, second)

    def test_win_cap_is_enforced(self):
        for seed in range(500):
            result = self.state.run_spin(random.Random(seed), bet=2.0)
            self.assertLessEqual(result["payout"], self.config.max_win * 2.0)

    def test_non_positive_bet_is_rejected(self):
        with self.assertRaises(ValueError):
            self.state.run_spin(random.Random(1), bet=0)


if __name__ == "__main__":
    unittest.main()
