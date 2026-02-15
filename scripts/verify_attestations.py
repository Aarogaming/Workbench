#!/usr/bin/env python3
"""Verify GitHub artifact attestations for one or more local subjects."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


RunFn = Callable[..., subprocess.CompletedProcess[str]]
SleepFn = Callable[[float], None]


@dataclass
class VerificationResult:
    subject: str
    passed: bool
    attempts: int
    return_code: int
    stdout: str
    stderr: str


def _parse_dotenv(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[key] = value
    return values


def _discover_github_token(root: Path, env_file: str | None = None) -> tuple[str | None, str]:
    for key in ("GH_TOKEN", "GITHUB_TOKEN", "GITHUB_PAT"):
        value = os.getenv(key, "").strip()
        if value:
            return value, f"process_env:{key}"

    candidates: list[Path] = []
    if env_file:
        candidate = Path(env_file)
        if not candidate.is_absolute():
            candidate = (root / candidate).resolve()
        candidates.append(candidate)
    else:
        candidates.extend(
            [
                (root / ".env").resolve(),
                (root.parent / ".env").resolve(),
                (root.parent.parent / ".env").resolve(),
            ]
        )

    seen: set[str] = set()
    for candidate in candidates:
        candidate_str = str(candidate)
        if candidate_str in seen:
            continue
        seen.add(candidate_str)
        values = _parse_dotenv(candidate)
        for key in ("GH_TOKEN", "GITHUB_TOKEN", "GITHUB_PAT"):
            value = values.get(key, "").strip()
            if value:
                return value, f"dotenv:{candidate}:{key}"

    return None, "not_found"


def _build_command(subject: str, repository: str) -> list[str]:
    return [
        "gh",
        "attestation",
        "verify",
        subject,
        "-R",
        repository,
        "--format",
        "json",
    ]


def _verify_subject(
    subject: str,
    repository: str,
    retries: int,
    retry_delay: float,
    run_fn: RunFn = subprocess.run,
    sleep_fn: SleepFn = time.sleep,
) -> VerificationResult:
    attempts = max(1, retries)
    cmd = _build_command(subject, repository)
    last = subprocess.CompletedProcess(cmd, returncode=1, stdout="", stderr="not run")
    for idx in range(1, attempts + 1):
        try:
            result = run_fn(
                cmd,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            result = subprocess.CompletedProcess(
                cmd,
                returncode=127,
                stdout="",
                stderr=str(exc),
            )
        last = result
        if result.returncode == 0:
            return VerificationResult(
                subject=subject,
                passed=True,
                attempts=idx,
                return_code=result.returncode,
                stdout=result.stdout or "",
                stderr=result.stderr or "",
            )
        if idx < attempts:
            sleep_fn(max(0.0, retry_delay))

    return VerificationResult(
        subject=subject,
        passed=False,
        attempts=attempts,
        return_code=last.returncode,
        stdout=last.stdout or "",
        stderr=last.stderr or "",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify GitHub artifact attestations for local artifacts."
    )
    parser.add_argument(
        "--repo",
        default=os.getenv("GITHUB_REPOSITORY"),
        help="Repository slug owner/name (default: $GITHUB_REPOSITORY).",
    )
    parser.add_argument(
        "--subject",
        action="append",
        default=[],
        help="Path to local artifact subject to verify. May be provided multiple times.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=4,
        help="Attempts per subject (default: 4).",
    )
    parser.add_argument(
        "--retry-delay",
        type=float,
        default=15.0,
        help="Delay between retries in seconds (default: 15).",
    )
    parser.add_argument(
        "--json-out",
        default="docs/reports/attestation_verify_report.json",
        help="JSON report output path relative to repo root.",
    )
    parser.add_argument(
        "--env-file",
        default=None,
        help="Optional dotenv file path for token discovery.",
    )
    args = parser.parse_args()

    if not args.repo:
        print("Missing repository slug; pass --repo owner/name or set GITHUB_REPOSITORY.")
        return 1
    if not args.subject:
        print("At least one --subject is required.")
        return 1

    root = Path(__file__).resolve().parents[1]
    out_path = (root / args.json_out).resolve()
    repository = args.repo.strip()
    token, auth_source = _discover_github_token(root, env_file=args.env_file)
    if token:
        # gh uses GH_TOKEN; keep auth source in report and avoid printing token values.
        os.environ["GH_TOKEN"] = token

    subjects = [
        str((root / subject).resolve()) if not Path(subject).is_absolute() else subject
        for subject in args.subject
    ]
    results = [
        _verify_subject(
            subject=subject,
            repository=repository,
            retries=args.retries,
            retry_delay=args.retry_delay,
        )
        for subject in subjects
    ]

    failed = [row for row in results if not row.passed]
    report: dict[str, Any] = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repository": repository,
        "auth": {
            "token_detected": bool(token),
            "source": auth_source,
        },
        "summary": {
            "total": len(results),
            "passed": len(results) - len(failed),
            "failed": len(failed),
        },
        "results": [
            {
                "subject": row.subject,
                "passed": row.passed,
                "attempts": row.attempts,
                "return_code": row.return_code,
                "stdout": row.stdout,
                "stderr": row.stderr,
            }
            for row in results
        ],
        "gate": {
            "pass": len(failed) == 0,
            "reasons": [
                f"verification failed for {row.subject} (exit {row.return_code})"
                for row in failed
            ],
        },
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Repository: {repository}")
    print(f"Auth token detected: {bool(token)} (source: {auth_source})")
    for row in results:
        print(
            f"- subject={row.subject} passed={row.passed} attempts={row.attempts} exit={row.return_code}"
        )
    print(f"JSON report: {out_path}")
    if failed:
        for reason in report["gate"]["reasons"]:
            print(f"- {reason}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
