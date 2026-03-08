#!/usr/bin/env python3
"""Evaluate baseline JetStream consumer profile by workload class."""

from __future__ import annotations

import argparse
import json


PROFILE_BASELINES: dict[str, dict[str, object]] = {
    "interactive": {
        "max_ack_pending": 64,
        "ack_wait_seconds": 30,
        "max_deliver": 3,
        "backoff_seconds": [5, 15, 30],
    },
    "batch": {
        "max_ack_pending": 256,
        "ack_wait_seconds": 120,
        "max_deliver": 5,
        "backoff_seconds": [30, 120, 300],
    },
    "critical": {
        "max_ack_pending": 32,
        "ack_wait_seconds": 300,
        "max_deliver": 8,
        "backoff_seconds": [60, 300, 900, 1800],
    },
}


def evaluate_consumer_profile(workload: str, max_ack_pending_override: int | None = None) -> dict[str, object]:
    if workload not in PROFILE_BASELINES:
        raise ValueError(f"workload must be one of {tuple(PROFILE_BASELINES)}")
    baseline = dict(PROFILE_BASELINES[workload])

    max_ack_pending = int(baseline["max_ack_pending"])
    override_applied = False
    if max_ack_pending_override is not None:
        if max_ack_pending_override <= 0:
            raise ValueError("max_ack_pending_override must be greater than 0")
        max_ack_pending = max_ack_pending_override
        override_applied = True

    return {
        "workload": workload,
        "max_ack_pending": max_ack_pending,
        "ack_wait_seconds": baseline["ack_wait_seconds"],
        "max_deliver": baseline["max_deliver"],
        "backoff_seconds": baseline["backoff_seconds"],
        "dlq_on_max_deliver": True,
        "override_applied": override_applied,
        "recommended_action": "review_override" if override_applied else "use_baseline",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate baseline JetStream consumer profile and redelivery backoff settings."
    )
    parser.add_argument(
        "--workload",
        required=True,
        choices=tuple(PROFILE_BASELINES),
        help="Workload class (`interactive`, `batch`, `critical`).",
    )
    parser.add_argument(
        "--max-ack-pending-override",
        type=int,
        default=None,
        help="Optional MaxAckPending override for review.",
    )
    args = parser.parse_args()

    payload = evaluate_consumer_profile(
        workload=args.workload,
        max_ack_pending_override=args.max_ack_pending_override,
    )
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
