#!/usr/bin/env python3
"""Compute exponential-backoff + jitter retry schedules for OpenAI loop calls."""

from __future__ import annotations

import argparse
import json
import random


def compute_backoff_schedule(
    attempts: int,
    *,
    base_delay: float,
    max_delay: float,
    jitter_ratio: float,
    seed: int | None = None,
) -> list[float]:
    if attempts <= 0:
        raise ValueError("attempts must be greater than 0")
    if base_delay <= 0:
        raise ValueError("base_delay must be greater than 0")
    if max_delay < base_delay:
        raise ValueError("max_delay must be greater than or equal to base_delay")
    if jitter_ratio < 0 or jitter_ratio > 1:
        raise ValueError("jitter_ratio must be in range [0, 1]")

    rng = random.Random(seed)
    schedule: list[float] = []
    for attempt in range(attempts):
        exponential = min(max_delay, base_delay * (2 ** attempt))
        jitter_delta = exponential * jitter_ratio
        low = max(0.0, exponential - jitter_delta)
        high = exponential + jitter_delta
        schedule.append(round(rng.uniform(low, high), 3))
    return schedule


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate retry schedule using exponential backoff + jitter."
    )
    parser.add_argument("--attempts", type=int, required=True)
    parser.add_argument("--base-delay", type=float, default=1.0)
    parser.add_argument("--max-delay", type=float, default=30.0)
    parser.add_argument("--jitter-ratio", type=float, default=0.2)
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional RNG seed for deterministic schedules.",
    )
    args = parser.parse_args()

    schedule = compute_backoff_schedule(
        args.attempts,
        base_delay=args.base_delay,
        max_delay=args.max_delay,
        jitter_ratio=args.jitter_ratio,
        seed=args.seed,
    )
    payload = {
        "attempts": args.attempts,
        "base_delay": args.base_delay,
        "max_delay": args.max_delay,
        "jitter_ratio": args.jitter_ratio,
        "schedule_seconds": schedule,
    }
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
