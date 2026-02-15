#!/usr/bin/env python3
"""Append scorecard audit snapshots into a local historical trend report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _load_history(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payload = _load_json(path)
    rows = payload.get("entries", [])
    if not isinstance(rows, list):
        return []
    cleaned: list[dict[str, Any]] = []
    for row in rows:
        if isinstance(row, dict):
            cleaned.append(row)
    return cleaned


def _entry_from_audit(audit: dict[str, Any]) -> dict[str, Any]:
    generated = str(audit.get("generated_utc", ""))
    project = str(audit.get("project", ""))
    available = bool(audit.get("available", False))
    gate = audit.get("gate", {}) if isinstance(audit.get("gate"), dict) else {}
    gate_pass = bool(gate.get("pass", False))
    score = None
    checks: dict[str, float] = {}
    if available:
        scorecard = audit.get("scorecard", {})
        if isinstance(scorecard, dict):
            raw_score = scorecard.get("score")
            if isinstance(raw_score, (int, float)):
                score = float(raw_score)
            raw_checks = scorecard.get("check_scores", {})
            if isinstance(raw_checks, dict):
                for name, value in raw_checks.items():
                    if isinstance(name, str) and isinstance(value, (int, float)):
                        checks[name] = float(value)
    return {
        "generated_utc": generated,
        "project": project,
        "available": available,
        "gate_pass": gate_pass,
        "score": score,
        "check_scores": checks,
    }


def _dedupe_and_sort(entries: list[dict[str, Any]], max_entries: int) -> list[dict[str, Any]]:
    unique: dict[tuple[str, str], dict[str, Any]] = {}
    for row in entries:
        key = (str(row.get("generated_utc", "")), str(row.get("project", "")))
        unique[key] = row
    ordered = sorted(unique.values(), key=lambda row: str(row.get("generated_utc", "")))
    if max_entries > 0:
        ordered = ordered[-max_entries:]
    return ordered


def _render_markdown(entries: list[dict[str, Any]]) -> str:
    lines = [
        "# Scorecard History",
        "",
        f"- entries: `{len(entries)}`",
        "",
        "| generated_utc | project | available | gate_pass | score | score_delta |",
        "|---|---|---:|---:|---:|---:|",
    ]
    prev_score: float | None = None
    for row in entries:
        score = row.get("score")
        score_value = f"{float(score):.2f}" if isinstance(score, (int, float)) else "-"
        if isinstance(score, (int, float)) and prev_score is not None:
            delta = float(score) - prev_score
            delta_value = f"{delta:+.2f}"
        else:
            delta_value = "-"
        lines.append(
            "| "
            + f"{row.get('generated_utc', '')} | "
            + f"{row.get('project', '')} | "
            + f"{row.get('available', False)} | "
            + f"{row.get('gate_pass', False)} | "
            + f"{score_value} | "
            + f"{delta_value} |"
        )
        if isinstance(score, (int, float)):
            prev_score = float(score)
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Update scorecard history/trend reports.")
    parser.add_argument(
        "--audit-json",
        default="docs/reports/scorecard_threshold_audit.json",
        help="Current scorecard audit JSON path relative to repo root.",
    )
    parser.add_argument(
        "--history-json",
        default="docs/reports/scorecard_history.json",
        help="History JSON output path relative to repo root.",
    )
    parser.add_argument(
        "--history-md",
        default="docs/reports/scorecard_history.md",
        help="History markdown output path relative to repo root.",
    )
    parser.add_argument(
        "--max-entries",
        type=int,
        default=180,
        help="Maximum history entries to keep.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    audit_path = (root / args.audit_json).resolve()
    history_json_path = (root / args.history_json).resolve()
    history_md_path = (root / args.history_md).resolve()

    audit = _load_json(audit_path)
    history = _load_history(history_json_path)
    history.append(_entry_from_audit(audit))
    ordered = _dedupe_and_sort(history, max_entries=max(1, args.max_entries))

    payload = {"entries": ordered}
    history_json_path.parent.mkdir(parents=True, exist_ok=True)
    history_json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    history_md_path.parent.mkdir(parents=True, exist_ok=True)
    history_md_path.write_text(_render_markdown(ordered), encoding="utf-8")

    print(f"Audit JSON: {audit_path}")
    print(f"History entries: {len(ordered)}")
    print(f"History JSON: {history_json_path}")
    print(f"History Markdown: {history_md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
