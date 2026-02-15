#!/usr/bin/env python3
"""Validate plugin manifest contracts for Workbench plugins."""

from __future__ import annotations

import argparse
import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Finding:
    severity: str
    plugin: str
    message: str


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _validate_entry_contract(plugin_dir: Path, entry: str) -> list[Finding]:
    findings: list[Finding] = []
    plugin_name = plugin_dir.name
    entry_path = plugin_dir / entry
    if not entry_path.exists():
        findings.append(Finding("error", plugin_name, f"entry file missing: {entry}"))
        return findings

    try:
        tree = ast.parse(entry_path.read_text(encoding="utf-8"), filename=str(entry_path))
    except SyntaxError as exc:
        findings.append(Finding("error", plugin_name, f"entry has syntax error: {exc}"))
        return findings

    has_plugin_class = False
    has_commands_method = False
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        if node.name != "Plugin":
            continue
        has_plugin_class = True
        for member in node.body:
            if isinstance(member, ast.FunctionDef) and member.name == "commands":
                has_commands_method = True
                break

    if not has_plugin_class:
        findings.append(Finding("error", plugin_name, "entry missing `Plugin` class"))
    if has_plugin_class and not has_commands_method:
        findings.append(Finding("error", plugin_name, "`Plugin` missing `commands()` method"))
    return findings


def _validate_manifest(plugin_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    plugin_name = plugin_dir.name
    manifest_path = plugin_dir / "manifest.json"
    if not manifest_path.exists():
        findings.append(Finding("error", plugin_name, "missing manifest.json"))
        return findings

    payload = _read_json(manifest_path)
    if payload is None:
        findings.append(Finding("error", plugin_name, "manifest.json is invalid JSON"))
        return findings

    if payload.get("schemaName") != "PluginManifest":
        findings.append(Finding("error", plugin_name, "schemaName must be PluginManifest"))

    entry = payload.get("entry")
    if not isinstance(entry, str) or not entry.strip():
        findings.append(Finding("error", plugin_name, "entry must be a non-empty string"))
        return findings

    findings.extend(_validate_entry_contract(plugin_dir, entry.strip()))

    capabilities = payload.get("capabilities", [])
    cap_names: set[str] = set()
    if isinstance(capabilities, list):
        for item in capabilities:
            if isinstance(item, dict):
                name = item.get("name")
                if isinstance(name, str) and name.strip():
                    cap_names.add(name.strip())

    exports: set[str] = set()
    extensions = payload.get("extensions")
    if isinstance(extensions, dict):
        aas_ext = extensions.get("aas")
        if isinstance(aas_ext, dict):
            raw = aas_ext.get("exports", [])
            if isinstance(raw, list):
                exports = {str(item).strip() for item in raw if str(item).strip()}

    missing_exports = sorted(cap_names - exports)
    extra_exports = sorted(exports - cap_names)
    if missing_exports:
        findings.append(
            Finding("error", plugin_name, f"capabilities missing from exports: {', '.join(missing_exports)}")
        )
    if extra_exports:
        findings.append(
            Finding("error", plugin_name, f"exports missing from capabilities: {', '.join(extra_exports)}")
        )

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Workbench plugin contracts.")
    parser.add_argument(
        "--plugin-root",
        default="plugins",
        help="Plugin root path relative to repository root.",
    )
    parser.add_argument(
        "--json-out",
        default="docs/reports/plugin_contract_audit.json",
        help="JSON report output path.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    plugin_root = (root / args.plugin_root).resolve()

    findings: list[Finding] = []
    if not plugin_root.exists():
        findings.append(Finding("error", "plugins", f"missing plugin root: {plugin_root}"))
    else:
        for child in sorted(plugin_root.iterdir(), key=lambda p: p.name.lower()):
            if not child.is_dir():
                continue
            if child.name == "__pycache__":
                continue
            findings.extend(_validate_manifest(child))

    report = {
        "plugin_root": str(plugin_root),
        "total_findings": len(findings),
        "errors": len([f for f in findings if f.severity == "error"]),
        "items": [
            {"severity": item.severity, "plugin": item.plugin, "message": item.message}
            for item in findings
        ],
    }
    out_path = (root / args.json_out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Plugin root: {plugin_root}")
    print(f"Total findings: {report['total_findings']}")
    print(f"Errors: {report['errors']}")
    print(f"JSON report: {out_path}")
    for item in findings:
        print(f"- [{item.severity}] {item.plugin}: {item.message}")

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
