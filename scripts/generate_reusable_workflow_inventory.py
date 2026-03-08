#!/usr/bin/env python3
"""Generate reusable workflow consumer inventory artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path


USES_RE = re.compile(r"^\s*uses:\s*(.+?)\s*(?:#.*)?$")


def _normalize_uses(value: str) -> str:
    return value.strip().strip("'").strip('"')


def _classify_reusable_use(uses: str) -> tuple[str, str, str] | None:
    if uses.startswith("./.github/workflows/"):
        return ("local", uses, "local")
    if "/.github/workflows/" in uses and "@" in uses:
        target, ref = uses.rsplit("@", 1)
        return ("remote", target, ref)
    return None


def collect_reusable_workflow_consumers(root: Path) -> list[dict[str, str | int]]:
    workflow_dir = root / ".github" / "workflows"
    entries: list[dict[str, str | int]] = []
    if not workflow_dir.exists():
        return entries

    for workflow_path in sorted(workflow_dir.glob("*.yml")):
        relative = workflow_path.relative_to(root).as_posix()
        lines = workflow_path.read_text(encoding="utf-8").splitlines()
        for line_no, raw in enumerate(lines, start=1):
            match = USES_RE.match(raw)
            if not match:
                continue
            normalized = _normalize_uses(match.group(1))
            classified = _classify_reusable_use(normalized)
            if classified is None:
                continue
            scope, target_workflow, ref = classified
            entries.append(
                {
                    "consumer_workflow": relative,
                    "line": line_no,
                    "scope": scope,
                    "target_workflow": target_workflow,
                    "ref": ref,
                }
            )
    return entries


def _write_json(path: Path, entries: list[dict[str, str | int]]) -> None:
    payload = {
        "schema": "workbench.reusable_workflow_inventory.v1",
        "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_count": len(entries),
        "entries": entries,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_markdown(path: Path, entries: list[dict[str, str | int]]) -> None:
    lines = [
        "# Reusable Workflow Consumer Inventory",
        "",
        f"Generated at (UTC): {dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        "| Consumer workflow | Line | Scope | Target workflow | Ref |",
        "| --- | --- | --- | --- | --- |",
    ]
    for entry in entries:
        lines.append(
            "| `{consumer_workflow}` | `{line}` | `{scope}` | `{target_workflow}` | `{ref}` |".format(
                **entry
            )
        )
    if not entries:
        lines.append("| `-` | `-` | `-` | `-` | `-` |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate reusable workflow consumer inventory reports."
    )
    parser.add_argument(
        "--output-dir",
        default="docs/reports",
        help="Directory for generated inventory reports.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    out_dir = (root / args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    entries = collect_reusable_workflow_consumers(root)
    json_out = out_dir / "reusable_workflow_inventory.json"
    md_out = out_dir / "reusable_workflow_inventory.md"

    _write_json(json_out, entries)
    _write_markdown(md_out, entries)

    print("[ok] reusable workflow inventory generated")
    print(f"  - entries={len(entries)}")
    print(f"  - {json_out}")
    print(f"  - {md_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
