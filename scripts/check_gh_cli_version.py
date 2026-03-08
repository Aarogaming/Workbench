#!/usr/bin/env python3
"""Validate GitHub CLI availability and minimum version."""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from typing import Callable


RunFn = Callable[..., subprocess.CompletedProcess[str]]
SEMVER_RE = re.compile(r"\b(\d+)\.(\d+)\.(\d+)\b")


@dataclass
class VersionCheckResult:
    ok: bool
    detected_version: str | None
    message: str


def _parse_semver(text: str) -> tuple[int, int, int] | None:
    match = SEMVER_RE.search(text)
    if not match:
        return None
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


def _format_semver(value: tuple[int, int, int]) -> str:
    return f"{value[0]}.{value[1]}.{value[2]}"


def check_gh_cli_version(min_version: str, run_fn: RunFn = subprocess.run) -> VersionCheckResult:
    required = _parse_semver(min_version)
    if required is None:
        return VersionCheckResult(
            ok=False,
            detected_version=None,
            message=f"invalid --min-version '{min_version}'; expected semantic version x.y.z",
        )

    cmd = ["gh", "--version"]
    try:
        result = run_fn(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        return VersionCheckResult(
            ok=False,
            detected_version=None,
            message="gh CLI not found in PATH",
        )

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        return VersionCheckResult(
            ok=False,
            detected_version=None,
            message=f"gh --version failed with exit {result.returncode}: {stderr or 'no stderr'}",
        )

    output = "\n".join([(result.stdout or "").strip(), (result.stderr or "").strip()]).strip()
    detected = _parse_semver(output)
    if detected is None:
        return VersionCheckResult(
            ok=False,
            detected_version=None,
            message="unable to parse gh semantic version from output",
        )

    if detected < required:
        return VersionCheckResult(
            ok=False,
            detected_version=_format_semver(detected),
            message=(
                f"gh version {_format_semver(detected)} is below required minimum "
                f"{_format_semver(required)}"
            ),
        )

    return VersionCheckResult(
        ok=True,
        detected_version=_format_semver(detected),
        message=f"gh version {_format_semver(detected)} satisfies minimum {_format_semver(required)}",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check GitHub CLI minimum version.")
    parser.add_argument(
        "--min-version",
        default="2.50.0",
        help="Minimum required gh semantic version (default: 2.50.0).",
    )
    args = parser.parse_args()

    result = check_gh_cli_version(args.min_version)
    if result.ok:
        print(f"[ok] {result.message}")
        return 0

    print(f"[fail] {result.message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
