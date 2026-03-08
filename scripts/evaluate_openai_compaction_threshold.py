#!/usr/bin/env python3
"""Evaluate whether an OpenAI loop should trigger /responses/compact."""

from __future__ import annotations

import argparse
import json


def evaluate_compaction(current_ratio: float, threshold: float) -> dict[str, object]:
    if threshold <= 0 or threshold >= 1:
        raise ValueError("threshold must be between 0 and 1")
    if current_ratio < 0:
        raise ValueError("current_ratio must be greater than or equal to 0")

    compact = current_ratio >= threshold
    return {
        "current_ratio": round(current_ratio, 4),
        "threshold": round(threshold, 4),
        "compact": compact,
        "recommended_action": "/responses/compact" if compact else "continue",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate compaction threshold trigger for OpenAI loops."
    )
    parser.add_argument("--current-ratio", type=float, required=True)
    parser.add_argument("--threshold", type=float, default=0.8)
    args = parser.parse_args()

    payload = evaluate_compaction(args.current_ratio, args.threshold)
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
