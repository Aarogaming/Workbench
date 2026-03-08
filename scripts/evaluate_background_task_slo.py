#!/usr/bin/env python3
"""Evaluate async background-task timeout/cancellation SLO posture."""

from __future__ import annotations

import argparse
import json


def evaluate_background_task_slo(
    duration_seconds: int,
    timeout_seconds: int,
    cancelled: bool,
) -> dict[str, object]:
    if duration_seconds < 0:
        raise ValueError("duration_seconds must be non-negative")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be greater than 0")

    timeout_breach = duration_seconds > timeout_seconds
    violation = timeout_breach and not cancelled
    return {
        "duration_seconds": duration_seconds,
        "timeout_seconds": timeout_seconds,
        "cancelled": cancelled,
        "timeout_breach": timeout_breach,
        "slo_violation": violation,
        "recommended_action": "cancel_and_escalate" if violation else "within_slo",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate background-task timeout/cancellation SLO status."
    )
    parser.add_argument("--duration-seconds", type=int, required=True)
    parser.add_argument("--timeout-seconds", type=int, required=True)
    parser.add_argument(
        "--cancelled",
        type=str,
        default="false",
        choices=("true", "false"),
        help="Whether task was cancelled prior to timeout breach.",
    )
    args = parser.parse_args()

    payload = evaluate_background_task_slo(
        duration_seconds=args.duration_seconds,
        timeout_seconds=args.timeout_seconds,
        cancelled=(args.cancelled == "true"),
    )
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
