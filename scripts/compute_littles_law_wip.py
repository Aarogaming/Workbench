#!/usr/bin/env python3
"""Compute lane WIP target using Little's Law."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def compute_recommended_wip(
    throughput_per_day: float,
    lead_time_days: float,
    buffer: float = 1.15,
) -> dict[str, float | int]:
    if throughput_per_day <= 0:
        raise ValueError("throughput_per_day must be > 0")
    if lead_time_days <= 0:
        raise ValueError("lead_time_days must be > 0")
    if buffer <= 0:
        raise ValueError("buffer must be > 0")

    base_wip = throughput_per_day * lead_time_days
    buffered_wip = base_wip * buffer
    recommended_wip = max(1, int(round(buffered_wip)))
    return {
        "formula": "WIP = throughput * lead_time",
        "throughput_per_day": throughput_per_day,
        "lead_time_days": lead_time_days,
        "buffer": buffer,
        "base_wip": base_wip,
        "buffered_wip": buffered_wip,
        "recommended_wip": recommended_wip,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compute recommended lane WIP using Little's Law."
    )
    parser.add_argument("--throughput-per-day", type=float, required=True)
    parser.add_argument("--lead-time-days", type=float, required=True)
    parser.add_argument(
        "--buffer",
        type=float,
        default=1.15,
        help="Multiplicative stability buffer (default: 1.15).",
    )
    parser.add_argument(
        "--json-out",
        default=None,
        help="Optional output path for JSON result.",
    )
    args = parser.parse_args()

    try:
        result = compute_recommended_wip(
            throughput_per_day=args.throughput_per_day,
            lead_time_days=args.lead_time_days,
            buffer=args.buffer,
        )
    except ValueError as exc:
        print(f"[fail] {exc}")
        return 1

    if args.json_out:
        target = Path(args.json_out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("[ok] little's law wip computed")
    print(f"  - throughput_per_day: {result['throughput_per_day']}")
    print(f"  - lead_time_days: {result['lead_time_days']}")
    print(f"  - buffer: {result['buffer']}")
    print(f"  - recommended_wip: {result['recommended_wip']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
