"""Run the deterministic Clockwork Kingdom math prototype.

Usage: python games/clockwork_kingdom/run.py --spins 10000 --seed 20261116
This standalone runner is a calibration harness, not the official Math SDK
book-generation or RGS publication pipeline.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from game_config import GameConfig
from gamestate import GameState


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spins", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20261116)
    parser.add_argument("--bet", type=float, default=1.0)
    args = parser.parse_args()
    if args.spins < 1:
        parser.error("--spins must be at least 1")
    if args.bet <= 0:
        parser.error("--bet must be greater than zero")

    config = GameConfig()
    state = GameState(config)
    rng = random.Random(args.seed)
    total_bet = total_payout = 0.0
    hits = feature_rounds = free_spins_awarded = 0
    max_observed = 0.0
    payout_buckets = Counter()
    mean_payout = m2_payout = 0.0

    for spin_number in range(1, args.spins + 1):
        result = state.run_spin(rng, args.bet, spin_number)
        total_bet += args.bet
        total_payout += result["payout"]
        delta = result["payout"] - mean_payout
        mean_payout += delta / spin_number
        m2_payout += delta * (result["payout"] - mean_payout)
        hits += int(result["hit"])
        feature_rounds += int(result["free_spins_played"] > 0)
        free_spins_awarded += result["free_spins_played"]
        max_observed = max(max_observed, result["payout_multiplier"])
        payout_buckets["zero" if result["payout"] == 0 else "win"] += 1

    empirical_rtp = total_payout / total_bet
    sample_variance = m2_payout / (args.spins - 1) if args.spins > 1 else 0.0
    standard_error_rtp = (sample_variance / args.spins) ** 0.5 / args.bet
    report = {
        "game_id": config.game_id,
        "simulations": args.spins,
        "seed": args.seed,
        "bet_per_paid_round": args.bet,
        "total_bet": total_bet,
        "total_payout": total_payout,
        "empirical_rtp": empirical_rtp,
        "sample_standard_deviation_per_round": sample_variance ** 0.5,
        "rtp_standard_error": standard_error_rtp,
        "rtp_95pct_normal_interval": [
            max(0.0, empirical_rtp - 1.96 * standard_error_rtp),
            empirical_rtp + 1.96 * standard_error_rtp,
        ],
        "theoretical_rtp_uncapped": config.theoretical_rtp_uncapped,
        "target_rtp": config.target_rtp,
        "hit_rate": hits / args.spins,
        "feature_trigger_rate": feature_rounds / args.spins,
        "average_free_spins_per_paid_round": free_spins_awarded / args.spins,
        "max_observed_win_multiplier": max_observed,
        "payout_buckets": dict(payout_buckets),
        "math": config.summary(),
        "note": (
            "Empirical RTP is a Monte Carlo estimate. The 96.00% analytical RTP is before "
            "the 5,000x round cap; the cap effect on the extreme tail is not analytically "
            "bounded here. This prototype is not an SDK validation or certification result."
        ),
    }
    report_dir = HERE / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"simulation_{args.spins}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "simulations", "seed", "empirical_rtp", "theoretical_rtp_uncapped", "target_rtp",
        "hit_rate", "feature_trigger_rate", "average_free_spins_per_paid_round",
        "max_observed_win_multiplier", "rtp_standard_error", "rtp_95pct_normal_interval",
        "total_bet", "total_payout",
    )}, indent=2))
    print(f"Report written: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
