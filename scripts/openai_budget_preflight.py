#!/usr/bin/env python3
"""Evaluate OpenAI project budget alarm/cap preflight state."""

from __future__ import annotations

import argparse
import json


def evaluate_budget_preflight(
    project_tier: str,
    current_spend: float,
    cap: float,
    alarm_threshold: float,
) -> tuple[dict[str, object], int]:
    if project_tier not in {"staging", "production"}:
        raise ValueError("project_tier must be staging or production")
    if cap <= 0:
        raise ValueError("cap must be greater than 0")
    if current_spend < 0:
        raise ValueError("current_spend must be greater than or equal to 0")
    if alarm_threshold <= 0 or alarm_threshold >= 1:
        raise ValueError("alarm_threshold must be between 0 and 1")

    usage_ratio = current_spend / cap
    alarm = usage_ratio >= alarm_threshold
    hard_block = current_spend > cap

    payload = {
        "project_tier": project_tier,
        "current_spend": round(current_spend, 2),
        "cap": round(cap, 2),
        "usage_ratio": round(usage_ratio, 4),
        "alarm_threshold": round(alarm_threshold, 4),
        "alarm": alarm,
        "hard_block": hard_block,
        "status": "block" if hard_block else "allow",
    }
    return payload, (1 if hard_block else 0)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate OpenAI project budget preflight gate state."
    )
    parser.add_argument("--project-tier", required=True, choices=("staging", "production"))
    parser.add_argument("--current-spend", type=float, required=True)
    parser.add_argument("--cap", type=float, required=True)
    parser.add_argument("--alarm-threshold", type=float, default=0.9)
    args = parser.parse_args()

    payload, code = evaluate_budget_preflight(
        project_tier=args.project_tier,
        current_spend=args.current_spend,
        cap=args.cap,
        alarm_threshold=args.alarm_threshold,
    )
    print(json.dumps(payload, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
