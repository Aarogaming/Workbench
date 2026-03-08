#!/usr/bin/env python3
"""Evaluate Argus Watchtower and Janus Gate promotion readiness."""

from __future__ import annotations

import argparse
import json


HEALTH_CHOICES = ("healthy", "degraded", "critical")


def evaluate_promotion_readiness(
    ci_pass: bool,
    provenance_pass: bool,
    advisory_health: str,
    review_approved: bool,
    runtime_health: str,
) -> dict[str, object]:
    if advisory_health not in HEALTH_CHOICES:
        raise ValueError(f"advisory_health must be one of {HEALTH_CHOICES}")
    if runtime_health not in HEALTH_CHOICES:
        raise ValueError(f"runtime_health must be one of {HEALTH_CHOICES}")

    argus_watchtower_pass = ci_pass and provenance_pass and advisory_health == "healthy"
    janus_stage1_review_pass = review_approved
    janus_stage2_runtime_pass = runtime_health == "healthy"
    janus_gate_pass = janus_stage1_review_pass and janus_stage2_runtime_pass
    promotion_allowed = argus_watchtower_pass and janus_gate_pass

    blocked_reasons: list[str] = []
    if not ci_pass:
        blocked_reasons.append("ci_failed")
    if not provenance_pass:
        blocked_reasons.append("provenance_failed")
    if advisory_health != "healthy":
        blocked_reasons.append("advisory_unhealthy")
    if not review_approved:
        blocked_reasons.append("review_gate_unapproved")
    if runtime_health != "healthy":
        blocked_reasons.append("runtime_unhealthy")

    return {
        "ci_pass": ci_pass,
        "provenance_pass": provenance_pass,
        "advisory_health": advisory_health,
        "review_approved": review_approved,
        "runtime_health": runtime_health,
        "argus_watchtower_pass": argus_watchtower_pass,
        "janus_stage1_review_pass": janus_stage1_review_pass,
        "janus_stage2_runtime_pass": janus_stage2_runtime_pass,
        "janus_gate_pass": janus_gate_pass,
        "promotion_allowed": promotion_allowed,
        "recommended_action": "promote" if promotion_allowed else "hold",
        "blocked_reasons": blocked_reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate promotion gate readiness for Argus Watchtower and Janus Gate."
    )
    parser.add_argument("--ci-pass", choices=("true", "false"), required=True)
    parser.add_argument("--provenance-pass", choices=("true", "false"), required=True)
    parser.add_argument("--advisory-health", choices=HEALTH_CHOICES, required=True)
    parser.add_argument("--review-approved", choices=("true", "false"), required=True)
    parser.add_argument("--runtime-health", choices=HEALTH_CHOICES, required=True)
    args = parser.parse_args()

    payload = evaluate_promotion_readiness(
        ci_pass=(args.ci_pass == "true"),
        provenance_pass=(args.provenance_pass == "true"),
        advisory_health=args.advisory_health,
        review_approved=(args.review_approved == "true"),
        runtime_health=args.runtime_health,
    )
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
