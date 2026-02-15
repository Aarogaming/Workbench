#!/usr/bin/env python3
"""Check OpenSSF Scorecard API results against repository policy thresholds."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ScorecardPolicy:
    min_score: float
    min_checks: dict[str, float]


@dataclass
class Evaluation:
    passed: bool
    reasons: list[str]
    overall_score: float
    check_scores: dict[str, float]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _load_policy(path: Path) -> ScorecardPolicy:
    payload = _load_json(path)
    raw_min_score = payload.get("min_score", 0.0)
    if not isinstance(raw_min_score, (int, float)):
        raise ValueError("min_score must be numeric")
    min_score = float(raw_min_score)

    raw_checks = payload.get("min_checks", {})
    if not isinstance(raw_checks, dict):
        raise ValueError("min_checks must be an object")

    min_checks: dict[str, float] = {}
    for name, value in raw_checks.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("min_checks keys must be non-empty strings")
        if not isinstance(value, (int, float)):
            raise ValueError(f"min_checks[{name!r}] must be numeric")
        min_checks[name.strip()] = float(value)

    return ScorecardPolicy(min_score=min_score, min_checks=min_checks)


def _build_project(repo_slug: str | None, project: str | None) -> str:
    if project:
        value = project.strip()
        if value:
            return value
    if repo_slug:
        value = repo_slug.strip()
        if value:
            return f"github.com/{value}"
    raise ValueError("missing repository; pass --repo owner/name or --project github.com/owner/name")


def _build_api_url(api_base: str, project: str) -> str:
    base = api_base.rstrip("/")
    encoded = urllib.parse.quote(project, safe="/.")
    return f"{base}/{encoded}"


def _fetch_payload(url: str, timeout: float) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("Scorecard API response is not a JSON object")
    return payload


def _extract_check_scores(payload: dict[str, Any]) -> dict[str, float]:
    rows = payload.get("checks", [])
    if not isinstance(rows, list):
        raise ValueError("Scorecard payload `checks` is not a list")
    scores: dict[str, float] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = row.get("name")
        score = row.get("score")
        if isinstance(name, str) and name and isinstance(score, (int, float)):
            scores[name] = float(score)
    return scores


def _evaluate_payload(payload: dict[str, Any], policy: ScorecardPolicy) -> Evaluation:
    raw_score = payload.get("score")
    if not isinstance(raw_score, (int, float)):
        raise ValueError("Scorecard payload missing numeric `score`")
    overall_score = float(raw_score)
    reasons: list[str] = []

    if overall_score < policy.min_score:
        reasons.append(
            f"overall score {overall_score:.2f} is below policy min_score {policy.min_score:.2f}"
        )

    check_scores = _extract_check_scores(payload)
    for check_name, min_required in sorted(policy.min_checks.items()):
        actual = check_scores.get(check_name)
        if actual is None:
            reasons.append(f"required check missing in payload: {check_name}")
            continue
        if actual < min_required:
            reasons.append(
                f"check {check_name} score {actual:.2f} is below minimum {min_required:.2f}"
            )

    return Evaluation(
        passed=(len(reasons) == 0),
        reasons=reasons,
        overall_score=overall_score,
        check_scores=check_scores,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enforce Scorecard score/check thresholds from policy."
    )
    parser.add_argument(
        "--repo",
        default=os.getenv("GITHUB_REPOSITORY"),
        help="Repository slug owner/name (default: $GITHUB_REPOSITORY).",
    )
    parser.add_argument(
        "--project",
        default=None,
        help="Full Scorecard project name (example: github.com/owner/name).",
    )
    parser.add_argument(
        "--policy-file",
        default=".github/scorecard-policy.json",
        help="Scorecard threshold policy JSON path relative to repo root.",
    )
    parser.add_argument(
        "--json-out",
        default="docs/reports/scorecard_threshold_audit.json",
        help="Output report path relative to repo root.",
    )
    parser.add_argument(
        "--api-base",
        default="https://api.scorecard.dev/projects",
        help="Scorecard API base URL.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="HTTP timeout seconds.",
    )
    parser.add_argument(
        "--allow-unavailable",
        action="store_true",
        help="Pass when scorecard data is unavailable (records warning in report).",
    )
    parser.add_argument(
        "--input-json",
        default=None,
        help="Optional local JSON payload path (skips network fetch).",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    policy_path = (root / args.policy_file).resolve()
    out_path = (root / args.json_out).resolve()

    try:
        policy = _load_policy(policy_path)
    except Exception as exc:
        print(f"Policy load error: {exc}")
        return 1

    try:
        project = _build_project(args.repo, args.project)
    except Exception as exc:
        print(f"Project error: {exc}")
        return 1

    report: dict[str, Any] = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project": project,
        "policy_file": str(policy_path),
        "policy": {
            "min_score": policy.min_score,
            "min_checks": policy.min_checks,
        },
    }

    payload: dict[str, Any] | None = None
    source = ""
    fetch_error = ""
    if args.input_json:
        source = str((Path(args.input_json)).resolve())
        try:
            payload = _load_json(Path(args.input_json).resolve())
        except Exception as exc:
            fetch_error = f"input payload error: {exc}"
    else:
        source = _build_api_url(args.api_base, project)
        try:
            payload = _fetch_payload(source, timeout=args.timeout)
        except urllib.error.HTTPError as exc:
            fetch_error = f"http error {exc.code}: {exc.reason}"
        except Exception as exc:
            fetch_error = str(exc)

    if payload is None:
        reasons = [f"scorecard data unavailable: {fetch_error}"]
        passed = bool(args.allow_unavailable)
        report.update(
            {
                "available": False,
                "source": source,
                "fetch_error": fetch_error,
                "gate": {"pass": passed, "reasons": reasons},
            }
        )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Project: {project}")
        print(f"Source: {source}")
        print("Available: false")
        print(f"Pass: {passed}")
        for reason in reasons:
            print(f"- {reason}")
        print(f"JSON report: {out_path}")
        return 0 if passed else 1

    try:
        evaluation = _evaluate_payload(payload, policy)
    except Exception as exc:
        print(f"Evaluation error: {exc}")
        return 1

    report.update(
        {
            "available": True,
            "source": source,
            "scorecard": {
                "score": evaluation.overall_score,
                "check_scores": evaluation.check_scores,
            },
            "gate": {
                "pass": evaluation.passed,
                "reasons": evaluation.reasons,
            },
        }
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Project: {project}")
    print(f"Source: {source}")
    print(f"Score: {evaluation.overall_score:.2f}")
    print(f"Pass: {evaluation.passed}")
    for reason in evaluation.reasons:
        print(f"- {reason}")
    print(f"JSON report: {out_path}")
    return 0 if evaluation.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
