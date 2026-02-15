#!/usr/bin/env python3
"""Audit index/protocol baseline across Workbench and neighboring directories."""

from __future__ import annotations

import argparse
import configparser
import datetime as dt
import json
import re
import subprocess
from pathlib import Path
from typing import Any

DOC_PACK = ["README.md", "INDEX.md", "ONBOARDING.md", "ARCHITECTURE.md", "RUNBOOK.md"]
MODULE_FILES = ["aas-module.json", "aas-hive.json"]
PROTOCOL_REL = "protocols/AGENT_INTEROP_V1.md"
SEARCH_HYGIENE_FILES = [".rgignore", ".ignore"]
DOC_POINTERS = ["docs/README.md", "docs/GATE_GOVERNANCE_POINTER.md"]

FULL_BASELINE_FILES = DOC_PACK + MODULE_FILES + [PROTOCOL_REL] + SEARCH_HYGIENE_FILES + DOC_POINTERS
CONTEXT_BASELINE_FILES = DOC_PACK + [PROTOCOL_REL] + SEARCH_HYGIENE_FILES

REFERENCE_GLOBS = (
    "Tools/**/*.csproj",
    "Tools/**/*.props",
    "Tools/**/*.targets",
    "*.ps1",
    "scripts/**/*.ps1",
    "scripts/**/*.sh",
)
REFERENCE_TOKEN_RE = re.compile(r"""['"]([^'"]*(?:\.\./|\.\.\\\\)[^'"]+)['"]""")
REPO_NAME_HINTS = {
    "androidapp",
    "library",
    "maelstrom",
    "merlin",
    "myfortress",
    "workbench",
    "guild",
    "utilities",
    "toolsshared",
}

DEFAULT_TARGETS = ["ToolsShared", "Utilities", "Workbench"]

PROTOCOL_MARKERS = [
    "# Agent Interop Protocol V1",
    "## Core request fields",
    "## Core response fields",
    "## Status enum",
    "## Compatibility",
]

PROTOCOL_FIELDS = [
    "`protocol_version`",
    "`operation_id`",
    "`request_id`",
    "`source_repo`",
    "`target_repo`",
    "`initiator`",
    "`intent`",
    "`constraints`",
    "`expected_outputs`",
    "`timeout_sec`",
    "`created_at_utc`",
    "`ack`",
    "`status`",
    "`message`",
    "`artifacts`",
    "`updated_at_utc`",
]

PLUGIN_CLASS_RE = re.compile(r"(?m)^\s*class\s+Plugin(?:\s*[:(])")
REGISTER_FUNC_RE = re.compile(r"(?m)^\s*def\s+register\s*\(")


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _safe_read_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    return data


def _normalize(text: str) -> str:
    return text.rstrip() + "\n"


def _load_submodules(suite_root: Path) -> dict[str, dict[str, str]]:
    path = suite_root / ".gitmodules"
    if not path.exists():
        return {}

    parser = configparser.ConfigParser()
    parser.read(path, encoding="utf-8")

    rows: dict[str, dict[str, str]] = {}
    for section in parser.sections():
        if not section.startswith('submodule "'):
            continue
        name = section[len('submodule "') : -1]
        rows[name] = {
            "path": parser.get(section, "path", fallback="").strip(),
            "url": parser.get(section, "url", fallback="").strip(),
        }
    return rows


def _parse_ls_tree_shas(raw: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        # 160000 commit <sha>\t<path>
        if "\t" not in line:
            continue
        left, path = line.split("\t", 1)
        parts = left.split()
        if len(parts) < 3:
            continue
        sha = parts[2]
        rows[path] = sha
    return rows


def _parse_ls_files_shas(raw: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        # 160000 <sha> 0\t<path>
        if "\t" not in line:
            continue
        left, path = line.split("\t", 1)
        parts = left.split()
        if len(parts) < 2:
            continue
        sha = parts[1]
        rows[path] = sha
    return rows


def _parse_submodule_status(raw: str) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for line in raw.splitlines():
        if not line.strip():
            continue
        prefix = line[0]
        body = line[1:].strip()
        parts = body.split()
        sha = parts[0] if parts else ""
        path = parts[1] if len(parts) > 1 else ""
        if not path:
            continue
        if prefix == " ":
            state = "clean"
        elif prefix == "+":
            state = "drifted"
        elif prefix == "-":
            state = "uninitialized"
        elif prefix == "U":
            state = "conflict"
        else:
            state = "unknown"
        rows[path] = {
            "path": path,
            "checkout_sha": sha,
            "state": state,
            "prefix": prefix,
            "raw": line,
        }
    return rows


def _extract_alignment_snapshot_shas(suite_root: Path) -> dict[str, str]:
    path = suite_root / "docs" / "AAS_CONTROL_PLANE_ALIGNMENT.md"
    if not path.exists():
        return {}
    body = _safe_read(path)
    rows: dict[str, str] = {}
    pattern = re.compile(r"^\|\s*`([^`]+)`\s*\|.*\|\s*`([0-9a-f]{40})`\s*\|\s*$")
    for line in body.splitlines():
        match = pattern.match(line)
        if not match:
            continue
        rows[match.group(1)] = match.group(2)
    return rows


def _load_protocol_template(
    suite_root: Path,
    template_path: Path,
) -> tuple[str | None, str | None]:
    """
    Load protocol template text.

    Preference order:
    1) Pinned content from superproject HEAD (stable against drifted submodule checkouts).
    2) Filesystem content from template_path.
    """
    template_text: str | None = None
    template_source: str | None = None

    # Try to resolve template from the submodule repo at the superproject-indexed SHA.
    try:
        rel = template_path.resolve().relative_to(suite_root.resolve()).as_posix()
    except Exception:
        rel = ""
    if rel:
        if rel.startswith("Library/"):
            library_repo = suite_root / "Library"
            sub_path = rel[len("Library/") :]
            try:
                ls_files = subprocess.check_output(
                    ["git", "-C", str(suite_root), "ls-files", "-s", "Library"],
                    text=True,
                    stderr=subprocess.STDOUT,
                )
                pin_rows = _parse_ls_files_shas(ls_files)
                library_pin = pin_rows.get("Library", "")
            except Exception:
                library_pin = ""
            if library_pin and library_repo.exists():
                try:
                    pinned = subprocess.check_output(
                        ["git", "-C", str(library_repo), "show", f"{library_pin}:{sub_path}"],
                        text=True,
                        stderr=subprocess.STDOUT,
                    )
                    if pinned:
                        template_text = pinned
                        template_source = f"pinned-submodule:Library@{library_pin}:{sub_path}"
                        return template_text, template_source
                except Exception:
                    pass

    # Fallback: resolve template from superproject HEAD path when possible.
    if rel:
        try:
            pinned = subprocess.check_output(
                ["git", "-C", str(suite_root), "show", f"HEAD:{rel}"],
                text=True,
                stderr=subprocess.STDOUT,
            )
            if pinned:
                template_text = pinned
                template_source = f"pinned:{rel}"
                return template_text, template_source
        except Exception:
            pass

    if template_path.exists():
        template_text = _safe_read(template_path)
        template_source = f"filesystem:{template_path}"
        return template_text, template_source

    return None, None


def _inspect_submodule_worktree(suite_root: Path, path: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "branch": "",
        "dirty_files": 0,
        "untracked_files": 0,
        "status_available": False,
        "status_error": "",
    }
    submodule_path = suite_root / path
    if not submodule_path.exists():
        result["status_error"] = "missing_submodule_path"
        return result
    try:
        raw = subprocess.check_output(
            ["git", "-C", str(submodule_path), "status", "--short", "--branch"],
            text=True,
            stderr=subprocess.STDOUT,
        )
    except Exception as exc:  # pragma: no cover - env dependent
        result["status_error"] = str(exc)
        return result

    lines = raw.splitlines()
    if lines:
        if lines[0].startswith("## "):
            result["branch"] = lines[0][3:].strip()
        for line in lines[1:]:
            if line.startswith("?? "):
                result["untracked_files"] += 1
            elif line.strip():
                result["dirty_files"] += 1
    result["status_available"] = True
    return result


def _parse_rev_list_count_output(raw: str) -> tuple[int, int] | None:
    text = raw.strip()
    if not text:
        return None
    parts = text.split()
    if len(parts) != 2:
        return None
    try:
        left = int(parts[0])
        right = int(parts[1])
    except ValueError:
        return None
    return left, right


def _compute_commit_distance(repo_path: Path, index_sha: str, checkout_sha: str) -> tuple[int, int] | None:
    if not index_sha or not checkout_sha:
        return None
    try:
        raw = subprocess.check_output(
            [
                "git",
                "-C",
                str(repo_path),
                "rev-list",
                "--left-right",
                "--count",
                f"{index_sha}...{checkout_sha}",
            ],
            text=True,
            stderr=subprocess.STDOUT,
        )
    except Exception:
        return None
    return _parse_rev_list_count_output(raw)


def _audit_cross_repo_references(workbench_root: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "scanned_files": 0,
        "total_references": 0,
        "missing_references": [],
        "warnings": [],
    }
    files: list[Path] = []
    seen: set[Path] = set()
    for pattern in REFERENCE_GLOBS:
        for path in workbench_root.glob(pattern):
            if not path.is_file():
                continue
            if path in seen:
                continue
            seen.add(path)
            files.append(path)

    result["scanned_files"] = len(files)
    for file_path in files:
        body = _safe_read(file_path)
        if not body:
            continue
        for match in REFERENCE_TOKEN_RE.finditer(body):
            token = match.group(1)
            raw = token
            token = token.replace("\\\\", "\\")
            normalized = token.replace("\\", "/")
            if not normalized.startswith("../"):
                continue
            lowered = normalized.lower()
            if not any(hint in lowered for hint in REPO_NAME_HINTS):
                continue
            result["total_references"] += 1
            resolved = (file_path.parent / normalized).resolve()
            if not resolved.exists():
                rel_file = file_path.relative_to(workbench_root).as_posix()
                result["missing_references"].append(
                    {
                        "file": rel_file,
                        "reference": raw,
                        "resolved": str(resolved),
                    }
                )
    if result["missing_references"]:
        result["warnings"].append("missing cross-repo path references detected")
    return result


def _load_target_policy(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None or not path.exists():
        return {}
    payload = _safe_read_json(path)
    if payload is None:
        return {}
    targets = payload.get("targets")
    if not isinstance(targets, list):
        return {}
    rows: dict[str, dict[str, Any]] = {}
    for item in targets:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if not isinstance(name, str) or not name.strip():
            continue
        rows[name] = item
    return rows


def _extend_targets_with_submodules(
    target_names: list[str],
    submodule_meta: dict[str, dict[str, str]],
) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for name in target_names:
        if not name or name in seen:
            continue
        seen.add(name)
        ordered.append(name)

    submodule_paths = sorted(
        {
            row.get("path", "").strip()
            for row in submodule_meta.values()
            if row.get("path", "").strip()
        },
        key=lambda text: text.lower(),
    )
    for path in submodule_paths:
        if path in seen:
            continue
        seen.add(path)
        ordered.append(path)
    return ordered


def _collect_submodule_status(
    suite_root: Path,
    submodule_meta: dict[str, dict[str, str]],
    include_dirty_warnings: bool = True,
    include_ahead_warnings: bool = True,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "available": False,
        "entries": [],
        "warnings": [],
        "error": None,
    }
    try:
        raw = subprocess.check_output(
            ["git", "-C", str(suite_root), "submodule", "status", "--recursive"],
            text=True,
            stderr=subprocess.STDOUT,
        )
    except Exception as exc:  # pragma: no cover - env dependent
        result["error"] = str(exc)
        return result

    paths = [row.get("path", "").strip() for row in submodule_meta.values()]
    paths = [path for path in paths if path]
    head_shas: dict[str, str] = {}
    index_shas: dict[str, str] = {}
    if paths:
        try:
            head_raw = subprocess.check_output(
                ["git", "-C", str(suite_root), "ls-tree", "HEAD", *paths],
                text=True,
                stderr=subprocess.STDOUT,
            )
            head_shas = _parse_ls_tree_shas(head_raw)
        except Exception:
            head_shas = {}
        try:
            index_raw = subprocess.check_output(
                ["git", "-C", str(suite_root), "ls-files", "-s", *paths],
                text=True,
                stderr=subprocess.STDOUT,
            )
            index_shas = _parse_ls_files_shas(index_raw)
        except Exception:
            index_shas = {}

    status_rows = _parse_submodule_status(raw)
    all_paths = sorted(set(paths) | set(status_rows))
    result["available"] = True
    for path in all_paths:
        status_row = status_rows.get(path, {})
        worktree = _inspect_submodule_worktree(suite_root, path)
        row = {
            "path": path,
            "state": status_row.get("state", "missing"),
            "prefix": status_row.get("prefix", "?"),
            "checkout_sha": status_row.get("checkout_sha", ""),
            "head_sha": head_shas.get(path, ""),
            "index_sha": index_shas.get(path, ""),
            "branch": worktree.get("branch", ""),
            "dirty_files": int(worktree.get("dirty_files", 0)),
            "untracked_files": int(worktree.get("untracked_files", 0)),
            "status_available": bool(worktree.get("status_available", False)),
            "status_error": worktree.get("status_error", ""),
            "checkout_behind_index": 0,
            "checkout_ahead_of_index": 0,
        }
        distance = _compute_commit_distance(
            suite_root / path, row["index_sha"], row["checkout_sha"]
        )
        if distance is not None:
            row["checkout_behind_index"] = distance[0]
            row["checkout_ahead_of_index"] = distance[1]
        result["entries"].append(row)
        ahead = int(row.get("checkout_ahead_of_index", 0))
        behind = int(row.get("checkout_behind_index", 0))
        mismatch = bool(row["index_sha"] and row["checkout_sha"] and row["index_sha"] != row["checkout_sha"])
        ahead_only_mismatch = mismatch and ahead > 0 and behind == 0

        if row["state"] != "clean" and not (ahead_only_mismatch and not include_ahead_warnings):
            result["warnings"].append(
                f"submodule `{path}` checkout state is `{row['state']}` ({row['checkout_sha']})"
            )
        if row["head_sha"] and row["index_sha"] and row["head_sha"] != row["index_sha"]:
            result["warnings"].append(
                f"submodule `{path}` has staged pointer change (HEAD {row['head_sha']} -> index {row['index_sha']})"
            )
        if mismatch and not (ahead_only_mismatch and not include_ahead_warnings):
            result["warnings"].append(
                f"submodule `{path}` checkout SHA differs from index pointer ({row['index_sha']} vs {row['checkout_sha']})"
            )
            if ahead > 0 and behind == 0:
                result["warnings"].append(
                    f"submodule `{path}` checkout is ahead of index by {ahead} commit(s)"
                )
            elif behind > 0 and ahead == 0:
                result["warnings"].append(
                    f"submodule `{path}` checkout is behind index by {behind} commit(s)"
                )
            elif ahead > 0 and behind > 0:
                result["warnings"].append(
                    f"submodule `{path}` checkout and index are diverged (ahead {ahead}, behind {behind})"
                )
        if row["status_available"] and include_dirty_warnings:
            if row["dirty_files"] > 0 or row["untracked_files"] > 0:
                result["warnings"].append(
                    f"submodule `{path}` has local worktree changes (dirty={row['dirty_files']} untracked={row['untracked_files']})"
                )
            if "ahead" in row["branch"] or "behind" in row["branch"]:
                result["warnings"].append(
                    f"submodule `{path}` branch divergence detected ({row['branch']})"
                )
        elif row["status_error"]:
            result["warnings"].append(
                f"submodule `{path}` status unavailable ({row['status_error']})"
            )
    return result


def _build_alignment_status(
    suite_root: Path,
    submodules: dict[str, Any],
) -> dict[str, Any]:
    snapshot_shas = _extract_alignment_snapshot_shas(suite_root)
    rows: list[dict[str, str]] = []
    warnings: list[str] = []

    if not snapshot_shas:
        return {
            "available": (suite_root / "docs" / "AAS_CONTROL_PLANE_ALIGNMENT.md").exists(),
            "entries": [],
            "warnings": [],
        }

    head_by_path = {row["path"]: row.get("head_sha", "") for row in submodules.get("entries", [])}
    for repo, snapshot_sha in sorted(snapshot_shas.items(), key=lambda kv: kv[0].lower()):
        # Snapshot uses repo names; .gitmodules path is also repo name in this workspace.
        head_sha = head_by_path.get(repo, "")
        if not head_sha:
            status = "unknown_repo"
            warnings.append(f"alignment snapshot includes `{repo}` but no submodule pin was found")
        elif head_sha == snapshot_sha:
            status = "match"
        else:
            status = "mismatch"
            warnings.append(
                f"alignment snapshot SHA mismatch for `{repo}` (docs {snapshot_sha} vs HEAD pin {head_sha})"
            )
        rows.append(
            {
                "repo": repo,
                "snapshot_sha": snapshot_sha,
                "head_sha": head_sha,
                "status": status,
            }
        )

    return {
        "available": True,
        "entries": rows,
        "warnings": warnings,
    }


def _extract_index_entries(index_body: str) -> list[str]:
    entries: list[str] = []
    for line in index_body.splitlines():
        match = re.match(r"^\s*-\s*`([^`]+)`", line)
        if not match:
            continue
        token = match.group(1).strip()
        if not token or "://" in token:
            continue
        token = token.replace("\\", "/")
        if token.startswith("./"):
            token = token[2:]
        if token.startswith("/"):
            continue
        entries.append(token)
    return entries


def _validate_protocol(repo_path: Path, repo_name: str, template_text: str | None) -> list[str]:
    warnings: list[str] = []
    protocol_path = repo_path / PROTOCOL_REL
    if not protocol_path.exists():
        return warnings

    body = _safe_read(protocol_path)
    for marker in PROTOCOL_MARKERS:
        if marker not in body:
            warnings.append(f"{PROTOCOL_REL}: missing marker '{marker}'")
    for field in PROTOCOL_FIELDS:
        if field not in body:
            warnings.append(f"{PROTOCOL_REL}: missing field token {field}")

    if template_text is not None:
        expected = _normalize(template_text.replace("{{REPO_NAME}}", repo_name))
        normalized_body = _normalize(body)
        # Allow additive repo-local notes only when canonical content stays intact as a full prefix.
        if normalized_body != expected and not normalized_body.startswith(expected):
            warnings.append(f"{PROTOCOL_REL}: differs from canonical template")

    return warnings


def _validate_hive_policy(repo_path: Path) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    policy = {
        "require_ack": None,
        "retries": None,
        "heartbeat_sec": None,
        "channels": [],
    }
    hive_path = repo_path / "aas-hive.json"
    if not hive_path.exists():
        return policy, warnings

    hive_cfg = _safe_read_json(hive_path)
    if hive_cfg is None:
        warnings.append("aas-hive.json: invalid JSON")
        return policy, warnings

    communication = hive_cfg.get("communication")
    if not isinstance(communication, dict):
        warnings.append("aas-hive.json: missing communication object")
        return policy, warnings

    require_ack = communication.get("require_ack")
    retries = communication.get("retries")
    heartbeat = communication.get("heartbeat_sec")
    channels = communication.get("channels")
    if not isinstance(channels, list):
        channels = []

    policy = {
        "require_ack": require_ack,
        "retries": retries,
        "heartbeat_sec": heartbeat,
        "channels": channels,
    }

    if require_ack is not True:
        warnings.append("aas-hive.json: communication.require_ack should be true")
    if not isinstance(retries, int) or retries < 1:
        warnings.append("aas-hive.json: communication.retries should be >= 1")
    if not isinstance(heartbeat, int) or heartbeat <= 0:
        warnings.append("aas-hive.json: communication.heartbeat_sec should be a positive integer")
    elif heartbeat > 45:
        warnings.append("aas-hive.json: communication.heartbeat_sec > 45 may delay stall detection")
    if "event_bus" not in channels:
        warnings.append("aas-hive.json: communication.channels should include event_bus")
    if "outbox" not in channels:
        warnings.append("aas-hive.json: communication.channels should include outbox")

    return policy, warnings


def _audit_target(
    repo_path: Path,
    target: str,
    submodule_meta: dict[str, dict[str, str]],
    template_text: str | None,
    enforce_baseline: bool,
    optional_absent: bool,
    policy_note: str,
) -> dict[str, Any]:
    rel_set = FULL_BASELINE_FILES if enforce_baseline else CONTEXT_BASELINE_FILES
    submodule = submodule_meta.get(target)

    row: dict[str, Any] = {
        "target": target,
        "path": str(repo_path),
        "baseline_enforced": enforce_baseline,
        "optional_absent": optional_absent,
        "policy_note": policy_note,
        "exists": repo_path.exists(),
        "is_git_repo": (repo_path / ".git").exists(),
        "submodule": submodule or {},
        "missing": [],
        "context_missing": [],
        "warnings": [],
        "notes": [],
        "index_missing_paths": [],
        "hive_policy": {
            "require_ack": None,
            "retries": None,
            "heartbeat_sec": None,
            "channels": [],
        },
        "ok": True,
    }

    if not repo_path.exists():
        if optional_absent:
            row["notes"].append("optional target path is absent")
            return row
        if enforce_baseline:
            row["missing"].append("target_path")
            row["ok"] = False
        else:
            row["warnings"].append("context target path is missing")
        return row

    for rel in rel_set:
        if not (repo_path / rel).exists():
            if enforce_baseline:
                row["missing"].append(rel)
            else:
                row["context_missing"].append(rel)

    index_path = repo_path / "INDEX.md"
    if index_path.exists():
        entries = _extract_index_entries(_safe_read(index_path))
        for rel in entries:
            if not (repo_path / rel).exists():
                row["index_missing_paths"].append(rel)
        if row["index_missing_paths"]:
            row["warnings"].append("INDEX.md references missing local paths")

    hive_policy, hive_warnings = _validate_hive_policy(repo_path)
    row["hive_policy"] = hive_policy
    row["warnings"].extend(hive_warnings)

    row["warnings"].extend(_validate_protocol(repo_path, target, template_text))

    if row["missing"]:
        row["ok"] = False
    return row


def _looks_like_legacy_plugin(body: str) -> bool:
    return bool(PLUGIN_CLASS_RE.search(body) or REGISTER_FUNC_RE.search(body))


def _audit_workbench_plugins(workbench_root: Path) -> dict[str, Any]:
    plugin_root = workbench_root / "plugins"
    result: dict[str, Any] = {
        "path": str(plugin_root),
        "exists": plugin_root.exists(),
        "manifest_dirs": [],
        "manifest_invalid": [],
        "manifest_missing_entry_file": [],
        "directory_plugins_without_manifest": [],
        "manifest_export_mismatch": [],
        "duplicate_capabilities": {},
        "flat_python_files": [],
        "flat_legacy_plugin_candidates": [],
        "flat_helper_modules": [],
        "warnings": [],
        "ok": True,
    }

    if not plugin_root.exists():
        result["warnings"].append("plugins directory is missing")
        result["ok"] = False
        return result

    capability_providers: dict[str, list[str]] = {}
    for child in sorted(plugin_root.iterdir(), key=lambda p: p.name.lower()):
        if child.name == "__pycache__":
            continue

        if child.is_dir():
            manifest_path = child / "manifest.json"
            plugin_path = child / "plugin.py"
            if manifest_path.exists():
                result["manifest_dirs"].append(child.name)
                manifest_data = _safe_read_json(manifest_path)
                if manifest_data is None:
                    result["manifest_invalid"].append(f"{child.name}/manifest.json")
                    continue
                if manifest_data.get("schemaName") != "PluginManifest":
                    result["warnings"].append(
                        f"{child.name}/manifest.json: schemaName should be PluginManifest"
                    )
                entry = manifest_data.get("entry")
                if not isinstance(entry, str) or not entry.strip():
                    result["warnings"].append(
                        f"{child.name}/manifest.json: missing or invalid entry field"
                    )
                else:
                    entry_path = child / entry
                    if not entry_path.exists():
                        result["manifest_missing_entry_file"].append(str(entry_path.relative_to(plugin_root)))

                capabilities = manifest_data.get("capabilities", [])
                capability_names: set[str] = set()
                if isinstance(capabilities, list):
                    for cap in capabilities:
                        if not isinstance(cap, dict):
                            continue
                        name = cap.get("name")
                        if isinstance(name, str) and name.strip():
                            capability_names.add(name.strip())
                            capability_providers.setdefault(name.strip(), []).append(child.name)

                exports: set[str] = set()
                extensions = manifest_data.get("extensions")
                if isinstance(extensions, dict):
                    aas_ext = extensions.get("aas")
                    if isinstance(aas_ext, dict):
                        raw_exports = aas_ext.get("exports", [])
                        if isinstance(raw_exports, list):
                            exports = {
                                item.strip()
                                for item in raw_exports
                                if isinstance(item, str) and item.strip()
                            }
                if capability_names and exports:
                    missing_exports = sorted(capability_names - exports)
                    if missing_exports:
                        result["manifest_export_mismatch"].append(
                            {
                                "plugin": child.name,
                                "kind": "missing_exports",
                                "capabilities": missing_exports,
                            }
                        )
                if exports and capability_names:
                    extra_exports = sorted(exports - capability_names)
                    if extra_exports:
                        result["manifest_export_mismatch"].append(
                            {
                                "plugin": child.name,
                                "kind": "exports_not_in_capabilities",
                                "capabilities": extra_exports,
                            }
                        )
            elif plugin_path.exists():
                result["directory_plugins_without_manifest"].append(child.name)
            continue

        if child.is_file() and child.suffix == ".py":
            if child.name == "__init__.py":
                continue
            result["flat_python_files"].append(child.name)
            body = _safe_read(child)
            if _looks_like_legacy_plugin(body):
                result["flat_legacy_plugin_candidates"].append(child.name)
            else:
                result["flat_helper_modules"].append(child.name)

    manifest_count = len(result["manifest_dirs"])
    legacy_count = len(result["flat_legacy_plugin_candidates"])
    if manifest_count > 0 and legacy_count > 0:
        result["warnings"].append(
            "mixed plugin layout detected: manifest plugin dirs and legacy flat plugin modules coexist"
        )
    if result["manifest_invalid"]:
        result["warnings"].append("invalid plugin manifest JSON detected")
    if result["manifest_missing_entry_file"]:
        result["warnings"].append("manifest entry points missing backing files")
    if result["directory_plugins_without_manifest"]:
        result["warnings"].append("plugin-like directories missing manifest.json")
    if result["manifest_export_mismatch"]:
        result["warnings"].append("manifest capability/export mismatch detected")

    duplicates = {
        capability: providers
        for capability, providers in capability_providers.items()
        if len(providers) > 1
    }
    if duplicates:
        result["duplicate_capabilities"] = duplicates
        result["warnings"].append("duplicate capability ownership detected across manifests")

    if result["warnings"] or result["manifest_invalid"] or result["manifest_missing_entry_file"]:
        result["ok"] = False
    return result


def _write_if_changed(path: Path, content: str) -> bool:
    if path.exists():
        try:
            if path.read_text(encoding="utf-8") == content:
                return False
        except OSError:
            pass
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def _build_issue_summary(
    targets: list[dict[str, Any]],
    plugins: dict[str, Any],
    references: dict[str, Any],
    submodules: dict[str, Any],
    alignment_snapshot: dict[str, Any],
    template_warning: str | None,
) -> dict[str, Any]:
    issues: list[dict[str, str]] = []

    def add_issue(severity: str, category: str, scope: str, message: str) -> None:
        issues.append(
            {
                "severity": severity,
                "category": category,
                "scope": scope,
                "message": message,
            }
        )

    for row in targets:
        target = str(row.get("target", ""))
        enforced = bool(row.get("baseline_enforced"))
        for rel in row.get("missing", []):
            add_issue(
                "error" if enforced else "warning",
                "baseline_missing",
                target,
                f"missing `{rel}`",
            )
        for rel in row.get("context_missing", []):
            add_issue("warning", "context_missing", target, f"missing `{rel}`")
        for rel in row.get("index_missing_paths", []):
            add_issue("warning", "index_broken_reference", target, f"INDEX points to `{rel}`")
        for warning in row.get("warnings", []):
            warning_text = str(warning)
            category = "target_warning"
            severity = "warning"
            if warning_text.startswith("protocols/AGENT_INTEROP_V1.md"):
                category = "protocol_drift"
                severity = "error" if enforced else "warning"
            elif warning_text.startswith("aas-hive.json:"):
                category = "hive_policy"
                severity = "error" if enforced else "warning"
            elif warning_text.startswith("INDEX.md references missing local paths"):
                category = "index_broken_reference"
            elif warning_text == "context target path is missing":
                category = "context_target_missing"
            add_issue(severity, category, target, warning_text)

    for warning in plugins.get("warnings", []):
        warning_text = str(warning)
        category = "plugin_warning"
        severity = "warning"
        if warning_text in {
            "invalid plugin manifest JSON detected",
            "manifest entry points missing backing files",
            "plugin-like directories missing manifest.json",
            "manifest capability/export mismatch detected",
            "duplicate capability ownership detected across manifests",
        }:
            category = "plugin_contract"
            severity = "error"
        elif warning_text.startswith("mixed plugin layout detected:"):
            category = "plugin_layout_migration"
        add_issue(severity, category, "Workbench/plugins", warning_text)

    for rel in plugins.get("manifest_invalid", []):
        add_issue("error", "plugin_manifest_invalid_json", rel, "invalid JSON")
    for rel in plugins.get("manifest_missing_entry_file", []):
        add_issue("error", "plugin_entry_missing_file", rel, "entry file missing")
    for rel in plugins.get("directory_plugins_without_manifest", []):
        add_issue("error", "plugin_missing_manifest", rel, "directory has plugin.py but no manifest")
    for row in plugins.get("manifest_export_mismatch", []):
        plugin = str(row.get("plugin", ""))
        kind = str(row.get("kind", ""))
        capabilities = row.get("capabilities", [])
        cap_text = ", ".join(capabilities) if isinstance(capabilities, list) else ""
        add_issue(
            "error",
            "plugin_capability_export_mismatch",
            plugin,
            f"{kind}: {cap_text}",
        )
    for capability, providers in plugins.get("duplicate_capabilities", {}).items():
        provider_text = ", ".join(sorted(providers)) if isinstance(providers, list) else ""
        add_issue(
            "error",
            "plugin_duplicate_capability",
            str(capability),
            f"provided by: {provider_text}",
        )

    for row in references.get("missing_references", []):
        file_name = str(row.get("file", ""))
        reference = str(row.get("reference", ""))
        resolved = str(row.get("resolved", ""))
        add_issue(
            "error",
            "cross_repo_reference_missing",
            file_name,
            f"`{reference}` -> `{resolved}`",
        )
    for warning in references.get("warnings", []):
        add_issue("warning", "cross_repo_reference_warning", "Workbench", str(warning))

    for warning in submodules.get("warnings", []):
        warning_text = str(warning)
        category = "submodule_warning"
        if "checkout state is" in warning_text:
            category = "submodule_checkout_state"
        elif "staged pointer change" in warning_text:
            category = "submodule_pointer_staged"
        elif "checkout SHA differs from index pointer" in warning_text:
            category = "submodule_pointer_mismatch"
        elif "ahead of index" in warning_text:
            category = "submodule_ahead"
        elif "behind index" in warning_text:
            category = "submodule_behind"
        elif "diverged" in warning_text:
            category = "submodule_diverged"
        elif "local worktree changes" in warning_text:
            category = "submodule_dirty_worktree"
        elif "branch divergence detected" in warning_text:
            category = "submodule_branch_divergence"
        add_issue("warning", category, "submodules", warning_text)

    for warning in alignment_snapshot.get("warnings", []):
        add_issue("warning", "alignment_snapshot", "AAS_CONTROL_PLANE_ALIGNMENT.md", str(warning))

    if template_warning:
        add_issue("warning", "protocol_template", "template", template_warning)

    by_severity = {"error": 0, "warning": 0, "info": 0}
    by_category: dict[str, int] = {}
    for item in issues:
        severity = item.get("severity", "warning")
        if severity not in by_severity:
            by_severity[severity] = 0
        by_severity[severity] += 1
        category = str(item.get("category", "unknown"))
        by_category[category] = by_category.get(category, 0) + 1

    return {
        "total": len(issues),
        "by_severity": by_severity,
        "by_category": dict(sorted(by_category.items(), key=lambda kv: kv[0])),
        "items": issues,
    }


def _build_submodule_reconciliation_plan(submodules: dict[str, Any]) -> list[dict[str, Any]]:
    if not submodules.get("available"):
        return []

    plan: list[dict[str, Any]] = []
    for row in submodules.get("entries", []):
        path = str(row.get("path", ""))
        state = str(row.get("state", "unknown"))
        ahead = int(row.get("checkout_ahead_of_index", 0))
        behind = int(row.get("checkout_behind_index", 0))
        dirty = int(row.get("dirty_files", 0))
        untracked = int(row.get("untracked_files", 0))

        if dirty > 0 or untracked > 0 or (ahead > 0 and behind > 0):
            risk = "high"
        elif state != "clean" or ahead > 0 or behind > 0:
            risk = "medium"
        else:
            risk = "low"

        status_cmd = f"git -C ../{path} status --short --branch"
        update_cmd = f"git -C .. submodule update --init --recursive {path}"
        if state == "clean" and ahead == 0 and behind == 0 and dirty == 0 and untracked == 0:
            action = "none"
            note = "checkout matches pinned pointer"
            command = ""
        elif dirty > 0 or untracked > 0:
            action = "preserve_local_work"
            note = "commit/stash before submodule sync"
            command = status_cmd
        elif behind > 0 and ahead == 0:
            action = "sync_to_pointer"
            note = "checkout is behind pinned pointer"
            command = update_cmd
        elif ahead > 0 and behind == 0:
            action = "choose_pointer_or_reset"
            note = "checkout ahead of pin; update pointer or reset checkout"
            command = f"{status_cmd} && {update_cmd}"
        elif ahead > 0 and behind > 0:
            action = "resolve_divergence"
            note = "checkout diverged from pin"
            command = status_cmd
        else:
            action = "inspect_state"
            note = "non-clean submodule state"
            command = status_cmd

        plan.append(
            {
                "path": path,
                "state": state,
                "ahead": ahead,
                "behind": behind,
                "dirty_files": dirty,
                "untracked_files": untracked,
                "risk": risk,
                "action": action,
                "note": note,
                "command": command,
            }
        )
    return plan


def _render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Workspace Index Audit")
    lines.append("")
    lines.append(f"- generated_utc: `{report['generated_utc']}`")
    lines.append(f"- suite_root: `{report['suite_root']}`")
    run_options = report.get("run_options", {})
    if run_options:
        lines.append("- run_options:")
        for key in [
            "targets_explicit",
            "include_all_submodule_targets",
            "strict",
            "strict_enforced_only",
            "ignore_cross_repo_warnings",
            "ignore_submodule_dirty",
            "ignore_submodule_ahead",
        ]:
            if key not in run_options:
                continue
            value = run_options[key]
            if isinstance(value, list):
                formatted = ", ".join(value) if value else "-"
                lines.append(f"  - {key}: `{formatted}`")
            else:
                lines.append(f"  - {key}: `{value}`")
    if report.get("template_source"):
        lines.append(f"- template_source: `{report['template_source']}`")

    issue_summary = report.get("issue_summary", {})
    if issue_summary:
        lines.append("")
        lines.append("## Issue Summary")
        lines.append("")
        lines.append(f"- total issues: `{issue_summary.get('total', 0)}`")
        severity = issue_summary.get("by_severity", {})
        lines.append(f"- errors: `{severity.get('error', 0)}`")
        lines.append(f"- warnings: `{severity.get('warning', 0)}`")
        lines.append(f"- info: `{severity.get('info', 0)}`")
        categories = issue_summary.get("by_category", {})
        if categories:
            lines.append("- categories:")
            for category, count in sorted(
                categories.items(),
                key=lambda kv: (-int(kv[1]), str(kv[0])),
            ):
                lines.append(f"  - `{category}`: `{count}`")
    lines.append("")
    lines.append("## Submodule Status")
    lines.append("")
    submodules = report["submodules"]
    if not submodules["available"]:
        lines.append("- submodule status unavailable")
        if submodules.get("error"):
            lines.append(f"- error: `{submodules['error']}`")
    else:
        lines.append("| Path | State | HEAD SHA | Index SHA | Checkout SHA | Ahead | Behind | Branch | Dirty | Untracked |")
        lines.append("|---|---|---|---|---|---:|---:|---|---:|---:|")
        for row in submodules["entries"]:
            lines.append(
                f"| `{row['path']}` | `{row['state']}` | `{row['head_sha']}` | `{row['index_sha']}` | `{row['checkout_sha']}` | {row.get('checkout_ahead_of_index', 0)} | {row.get('checkout_behind_index', 0)} | `{row.get('branch', '')}` | {row.get('dirty_files', 0)} | {row.get('untracked_files', 0)} |"
            )
        if submodules["warnings"]:
            lines.append("")
            lines.append("- warnings:")
            for warning in submodules["warnings"]:
                lines.append(f"  - {warning}")

    lines.append("")
    lines.append("## Submodule Reconciliation Plan")
    lines.append("")
    submodule_plan = report.get("submodule_reconciliation_plan", [])
    if not submodule_plan:
        lines.append("- no plan entries")
    else:
        lines.append("| Path | Risk | Ahead | Behind | Dirty | Untracked | Action | Command |")
        lines.append("|---|---|---:|---:|---:|---:|---|---|")
        for item in submodule_plan:
            command = str(item.get("command", ""))
            command_text = f"`{command}`" if command else "-"
            lines.append(
                f"| `{item.get('path', '')}` | `{item.get('risk', '')}` | {item.get('ahead', 0)} | {item.get('behind', 0)} | {item.get('dirty_files', 0)} | {item.get('untracked_files', 0)} | `{item.get('action', '')}` | {command_text} |"
            )
    lines.append("")
    lines.append("## Alignment Snapshot")
    lines.append("")
    alignment = report["alignment_snapshot"]
    if not alignment["available"]:
        lines.append("- alignment snapshot unavailable")
    elif not alignment["entries"]:
        lines.append("- alignment snapshot table not found or empty")
    else:
        lines.append("| Repo | Docs Snapshot SHA | HEAD Pin SHA | Status |")
        lines.append("|---|---|---|---|")
        for row in alignment["entries"]:
            lines.append(
                f"| `{row['repo']}` | `{row['snapshot_sha']}` | `{row['head_sha']}` | `{row['status']}` |"
            )
        if alignment["warnings"]:
            lines.append("")
            lines.append("- warnings:")
            for warning in alignment["warnings"]:
                lines.append(f"  - {warning}")
    lines.append("")
    lines.append("## Cross-Repo References")
    lines.append("")
    refs = report["cross_repo_references"]
    lines.append(f"- scanned files: `{refs['scanned_files']}`")
    lines.append(f"- total neighbor references: `{refs['total_references']}`")
    if refs["missing_references"]:
        lines.append("- missing references:")
        for row in refs["missing_references"]:
            lines.append(
                f"  - `{row['file']}` -> `{row['reference']}` (resolved: `{row['resolved']}`)"
            )
    else:
        lines.append("- missing references: none")
    lines.append("")
    lines.append("## Neighbor Targets")
    lines.append("")
    lines.append("| Target | Enforced | Exists | Submodule | Missing | Context Missing | Warnings |")
    lines.append("|---|---|---|---|---:|---:|---:|")
    for row in report["targets"]:
        submodule = "yes" if row.get("submodule") else "no"
        exists = "yes" if row.get("exists") else "no"
        enforced = "yes" if row.get("baseline_enforced") else "no"
        lines.append(
            f"| {row['target']} | {enforced} | {exists} | {submodule} | {len(row['missing'])} | {len(row['context_missing'])} | {len(row['warnings'])} |"
        )

    lines.append("")
    lines.append("## Workbench Plugins")
    lines.append("")
    plugins = report["plugins"]
    lines.append(f"- plugin path: `{plugins['path']}`")
    lines.append(f"- manifest plugin dirs: `{len(plugins['manifest_dirs'])}`")
    lines.append(f"- legacy flat plugin candidates: `{len(plugins['flat_legacy_plugin_candidates'])}`")
    lines.append(f"- flat helper modules: `{len(plugins['flat_helper_modules'])}`")
    lines.append(f"- manifest export mismatches: `{len(plugins['manifest_export_mismatch'])}`")
    lines.append(f"- duplicate capabilities: `{len(plugins['duplicate_capabilities'])}`")
    if plugins["warnings"]:
        lines.append("- warnings:")
        for warning in plugins["warnings"]:
            lines.append(f"  - {warning}")
    else:
        lines.append("- warnings: none")

    lines.append("")
    lines.append("## Detailed Findings")
    lines.append("")
    for row in report["targets"]:
        lines.append(f"### {row['target']}")
        lines.append("")
        lines.append(f"- path: `{row['path']}`")
        lines.append(f"- baseline_enforced: `{row['baseline_enforced']}`")
        lines.append(f"- optional_absent: `{row['optional_absent']}`")
        lines.append(f"- policy_note: `{row['policy_note']}`")
        lines.append(f"- exists: `{row['exists']}`")
        lines.append(f"- is_git_repo: `{row['is_git_repo']}`")
        if row.get("submodule"):
            lines.append(f"- submodule_path: `{row['submodule'].get('path', '-')}`")
            lines.append(f"- submodule_url: `{row['submodule'].get('url', '-')}`")
        else:
            lines.append("- submodule_path: `-`")
            lines.append("- submodule_url: `-`")

        if row["missing"]:
            lines.append("- missing:")
            for rel in row["missing"]:
                lines.append(f"  - `{rel}`")
        else:
            lines.append("- missing: none")

        if row["context_missing"]:
            lines.append("- context_missing:")
            for rel in row["context_missing"]:
                lines.append(f"  - `{rel}`")

        if row["index_missing_paths"]:
            lines.append("- index_missing_paths:")
            for rel in row["index_missing_paths"]:
                lines.append(f"  - `{rel}`")

        if row["warnings"]:
            lines.append("- warnings:")
            for warning in row["warnings"]:
                lines.append(f"  - {warning}")
        else:
            lines.append("- warnings: none")
        if row["notes"]:
            lines.append("- notes:")
            for note in row["notes"]:
                lines.append(f"  - {note}")
        lines.append("")

    lines.append("## Plugin File Lists")
    lines.append("")
    lines.append("- manifest_dirs:")
    for item in plugins["manifest_dirs"]:
        lines.append(f"  - `{item}`")
    lines.append("- flat_legacy_plugin_candidates:")
    for item in plugins["flat_legacy_plugin_candidates"]:
        lines.append(f"  - `{item}`")
    lines.append("- flat_helper_modules:")
    for item in plugins["flat_helper_modules"]:
        lines.append(f"  - `{item}`")
    lines.append("- manifest_export_mismatch:")
    for row in plugins["manifest_export_mismatch"]:
        caps = ", ".join(row["capabilities"])
        lines.append(f"  - `{row['plugin']}` `{row['kind']}`: {caps}")
    lines.append("- duplicate_capabilities:")
    for capability, providers in sorted(plugins["duplicate_capabilities"].items()):
        lines.append(f"  - `{capability}` -> {', '.join(sorted(providers))}")

    lines.append("")
    lines.append("## Recommended Actions")
    lines.append("")
    if report["recommended_actions"]:
        for action in report["recommended_actions"]:
            lines.append(f"- {action}")
    else:
        lines.append("- none")

    return "\n".join(lines).rstrip() + "\n"


def _build_recommendations(
    targets: list[dict[str, Any]],
    plugins: dict[str, Any],
    submodules: dict[str, Any],
    alignment_snapshot: dict[str, Any],
    references: dict[str, Any],
    template_warning: str | None,
) -> list[str]:
    actions: list[str] = []

    for row in targets:
        target = row["target"]
        if row["baseline_enforced"] and row["missing"]:
            actions.append(
                f"`{target}` missing enforced baseline files; add required docs/config/protocol pack."
            )
        if not row["baseline_enforced"] and not row["exists"] and not row["optional_absent"]:
            actions.append(
                f"`{target}` is listed as context but missing on disk; remove from target list if deprecated or add directory if still expected."
            )
        if row["context_missing"]:
            actions.append(
                f"`{target}` is context-only and missing context baseline files; scaffold with `python3 ../Library/scripts/bootstrap_peer_repo_baseline.py --parent-root .. --repos {target} --apply` or keep it excluded from target policy."
            )
        if row["index_missing_paths"]:
            actions.append(
                f"`{target}` has broken `INDEX.md` references; fix or remove missing index paths."
            )
    if submodules["warnings"]:
        entries = submodules.get("entries", [])
        drift_paths = sorted(
            {
                row["path"]
                for row in entries
                if (
                    row.get("state") != "clean"
                    or (
                        row.get("index_sha")
                        and row.get("checkout_sha")
                        and row.get("index_sha") != row.get("checkout_sha")
                    )
                )
            }
        )
        ahead_paths = sorted(
            {
                row["path"]
                for row in entries
                if int(row.get("checkout_ahead_of_index", 0)) > 0
                and int(row.get("checkout_behind_index", 0)) == 0
            }
        )
        behind_paths = sorted(
            {
                row["path"]
                for row in entries
                if int(row.get("checkout_behind_index", 0)) > 0
                and int(row.get("checkout_ahead_of_index", 0)) == 0
            }
        )
        diverged_paths = sorted(
            {
                row["path"]
                for row in entries
                if int(row.get("checkout_ahead_of_index", 0)) > 0
                and int(row.get("checkout_behind_index", 0)) > 0
            }
        )
        dirty_paths = sorted(
            {
                row["path"]
                for row in entries
                if (
                    int(row.get("dirty_files", 0)) > 0
                    or int(row.get("untracked_files", 0)) > 0
                    or "ahead" in str(row.get("branch", ""))
                    or "behind" in str(row.get("branch", ""))
                )
            }
        )
        dirty_drift_paths = sorted(
            {
                row["path"]
                for row in entries
                if row.get("path") in drift_paths
                and (int(row.get("dirty_files", 0)) > 0 or int(row.get("untracked_files", 0)) > 0)
            }
        )
        if drift_paths:
            drift_text = ", ".join(drift_paths)
            update_cmd = "git -C .. submodule update --init --recursive " + " ".join(drift_paths)
            actions.append(
                f"Submodule pointer/checkout drift detected ({drift_text}); inspect with `git -C .. submodule status --recursive`, then reconcile via `{update_cmd}` when ready."
            )
        if ahead_paths:
            actions.append(
                f"Submodule checkouts ahead of pinned pointer ({', '.join(ahead_paths)}); if intended, update superproject submodule pointer to include those commits."
            )
        if behind_paths:
            actions.append(
                f"Submodule checkouts behind pinned pointer ({', '.join(behind_paths)}); run submodule update to fast-forward checkout to pinned commits."
            )
        if diverged_paths:
            actions.append(
                f"Submodule checkouts diverged from pinned pointer ({', '.join(diverged_paths)}); resolve by choosing merge/rebase strategy before syncing pointer."
            )
        if dirty_drift_paths:
            actions.append(
                f"Drifted submodules have local edits ({', '.join(dirty_drift_paths)}); preserve work first (`git -C ../{dirty_drift_paths[0]} status --short --branch`) and commit/stash before running `{update_cmd}`."
            )
        if dirty_paths:
            actions.append(
                f"Multiple submodules have local worktree churn ({', '.join(dirty_paths)}); commit/stash/push as intended before treating workspace snapshots as a stable protocol baseline."
            )
    if alignment_snapshot["warnings"]:
        actions.append(
            "AAS alignment snapshot table is stale; refresh `docs/AAS_CONTROL_PLANE_ALIGNMENT.md` pinned SHAs."
        )
    if references["warnings"]:
        actions.append(
            "Fix missing cross-repo file references in Workbench tools/scripts or update neighbor repo layout assumptions."
        )

    if plugins["manifest_invalid"]:
        actions.append("Fix invalid `plugins/*/manifest.json` files.")
    if plugins["manifest_missing_entry_file"]:
        actions.append("Fix plugin manifest `entry` fields that do not resolve to real files.")
    if plugins["directory_plugins_without_manifest"]:
        actions.append(
            "Add `manifest.json` to plugin-like directories that have `plugin.py` but no manifest."
        )
    if plugins["manifest_export_mismatch"]:
        actions.append(
            "Fix plugin manifest capability/export mismatches so `extensions.aas.exports` matches declared capabilities."
        )
    if plugins["duplicate_capabilities"]:
        actions.append(
            "Resolve duplicate capability ownership across plugin manifests to avoid runtime routing ambiguity."
        )
    if plugins["warnings"] and not (
        plugins["manifest_invalid"]
        or plugins["manifest_missing_entry_file"]
        or plugins["directory_plugins_without_manifest"]
    ):
        actions.append("Review plugin layout warnings and decide if migration/cleanup is required.")
    if template_warning:
        actions.append("Restore protocol template path so drift checks can verify canonical protocol text.")

    # Preserve order but avoid duplicates.
    deduped: list[str] = []
    seen: set[str] = set()
    for action in actions:
        if action in seen:
            continue
        seen.add(action)
        deduped.append(action)
    return deduped


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit index/protocol baseline for Workbench neighbors and plugin layout."
    )
    parser.add_argument(
        "--suite-root",
        default="..",
        help="Path to suite root relative to Workbench root (default: ..).",
    )
    parser.add_argument(
        "--targets",
        nargs="+",
        default=None,
        help="Neighbor directories to inspect (default: policy targets or built-in defaults).",
    )
    parser.add_argument(
        "--target-policy",
        default="scripts/workspace_index_targets.json",
        help="Target policy JSON path relative to Workbench root.",
    )
    parser.add_argument(
        "--enforce-targets",
        nargs="*",
        default=None,
        help=(
            "Targets that must satisfy full module baseline. "
            "Default: submodule-backed, git-repo, or aas-module.json targets."
        ),
    )
    parser.add_argument(
        "--protocol-template",
        default="../Library/templates/protocols/AGENT_INTEROP_V1_TEMPLATE.md",
        help="Template path relative to Workbench root for drift checks.",
    )
    parser.add_argument(
        "--json-out",
        default="docs/reports/workspace_index_audit.json",
        help="JSON output path relative to Workbench root.",
    )
    parser.add_argument(
        "--md-out",
        default="docs/reports/workspace_index_audit.md",
        help="Markdown output path relative to Workbench root.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on warnings in addition to hard missing items.",
    )
    parser.add_argument(
        "--include-all-submodule-targets",
        action="store_true",
        help=(
            "Append all submodule paths from .gitmodules to the target audit list. "
            "Useful for full neighboring-repo sweeps."
        ),
    )
    parser.add_argument(
        "--strict-enforced-only",
        action="store_true",
        help=(
            "Fail on warnings only for enforced targets (plus plugin/template warnings), "
            "ignoring context-target warnings."
        ),
    )
    parser.add_argument(
        "--ignore-cross-repo-warnings",
        action="store_true",
        help=(
            "Ignore cross-repo reference warnings in strict modes. "
            "Useful for standalone checkouts that do not include neighbor repositories."
        ),
    )
    parser.add_argument(
        "--ignore-submodule-dirty",
        action="store_true",
        help=(
            "Ignore submodule worktree dirty/divergence warnings. "
            "Pointer mismatch and checkout drift warnings are still enforced."
        ),
    )
    parser.add_argument(
        "--ignore-submodule-ahead",
        action="store_true",
        help=(
            "Ignore ahead-only submodule checkout drift warnings. "
            "Behind/diverged/conflict/pointer-change warnings remain enforced."
        ),
    )
    args = parser.parse_args()

    workbench_root = Path(__file__).resolve().parents[1]
    suite_root = (workbench_root / args.suite_root).resolve()

    template_path = (workbench_root / args.protocol_template).resolve()
    template_text: str | None = None
    template_source: str | None = None
    template_warning: str | None = None
    template_text, template_source = _load_protocol_template(suite_root, template_path)
    template_required = (suite_root / ".gitmodules").exists() or (suite_root / "Library").exists()
    if template_text is None and template_required:
        template_warning = f"protocol template not found: {template_path}"

    submodule_meta = _load_submodules(suite_root)
    submodule_state = _collect_submodule_status(
        suite_root,
        submodule_meta,
        include_dirty_warnings=not args.ignore_submodule_dirty,
        include_ahead_warnings=not args.ignore_submodule_ahead,
    )
    alignment_snapshot = _build_alignment_status(suite_root, submodule_state)
    policy_path = (workbench_root / args.target_policy).resolve() if args.target_policy else None
    target_policy = _load_target_policy(policy_path)
    has_gitmodules = (suite_root / ".gitmodules").exists()
    if args.targets:
        target_names = args.targets
    elif not has_gitmodules:
        # Standalone Workbench checkout: avoid assuming sibling repos exist.
        target_names = ["Workbench"]
    else:
        target_names = list(target_policy) or DEFAULT_TARGETS
    if args.include_all_submodule_targets and has_gitmodules:
        target_names = _extend_targets_with_submodules(target_names, submodule_meta)
    explicit_enforce = set(args.enforce_targets or [])
    has_explicit_enforce = args.enforce_targets is not None

    def _resolve_target_path(target: str) -> Path:
        direct = suite_root / target
        if direct.exists():
            return direct
        if target.lower() == "workbench" and workbench_root.name.lower() == "workbench":
            return workbench_root
        return direct

    def _should_enforce(target: str, path: Path) -> bool:
        if has_explicit_enforce:
            return target in explicit_enforce
        policy = target_policy.get(target, {})
        policy_enforce = policy.get("enforce_baseline")
        if isinstance(policy_enforce, bool):
            return policy_enforce
        if target in submodule_meta:
            return True
        if (path / ".git").exists():
            return True
        if (path / "aas-module.json").exists():
            return True
        return False

    def _is_optional_absent(target: str) -> bool:
        policy = target_policy.get(target, {})
        flag = policy.get("optional_absent")
        return bool(flag) if isinstance(flag, bool) else False

    def _policy_note(target: str) -> str:
        policy = target_policy.get(target, {})
        note = policy.get("note")
        return note if isinstance(note, str) else ""

    targets: list[dict[str, Any]] = []
    for target in target_names:
        repo_path = _resolve_target_path(target)
        targets.append(
            _audit_target(
                repo_path=repo_path,
                target=target,
                submodule_meta=submodule_meta,
                template_text=template_text,
                enforce_baseline=_should_enforce(target, repo_path),
                optional_absent=_is_optional_absent(target),
                policy_note=_policy_note(target),
            )
        )
    plugins = _audit_workbench_plugins(workbench_root)
    references = _audit_cross_repo_references(workbench_root)
    recommendations = _build_recommendations(
        targets,
        plugins,
        submodule_state,
        alignment_snapshot,
        references,
        template_warning,
    )
    issue_summary = _build_issue_summary(
        targets=targets,
        plugins=plugins,
        references=references,
        submodules=submodule_state,
        alignment_snapshot=alignment_snapshot,
        template_warning=template_warning,
    )
    submodule_reconciliation_plan = _build_submodule_reconciliation_plan(submodule_state)

    report: dict[str, Any] = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "suite_root": str(suite_root),
        "policy_path": str(policy_path) if policy_path else "",
        "targets": targets,
        "plugins": plugins,
        "cross_repo_references": references,
        "submodules": submodule_state,
        "alignment_snapshot": alignment_snapshot,
        "recommended_actions": recommendations,
        "issue_summary": issue_summary,
        "submodule_reconciliation_plan": submodule_reconciliation_plan,
        "template_path": str(template_path),
        "template_source": template_source or "",
        "run_options": {
            "targets_explicit": args.targets or [],
            "include_all_submodule_targets": bool(args.include_all_submodule_targets),
            "strict": bool(args.strict),
            "strict_enforced_only": bool(args.strict_enforced_only),
            "ignore_cross_repo_warnings": bool(args.ignore_cross_repo_warnings),
            "ignore_submodule_dirty": bool(args.ignore_submodule_dirty),
            "ignore_submodule_ahead": bool(args.ignore_submodule_ahead),
        },
    }
    if template_warning:
        report["template_warning"] = template_warning

    json_text = json.dumps(report, indent=2, sort_keys=False) + "\n"
    md_text = _render_markdown(report)

    json_out_path = (workbench_root / args.json_out).resolve()
    md_out_path = (workbench_root / args.md_out).resolve()
    json_changed = _write_if_changed(json_out_path, json_text)
    md_changed = _write_if_changed(md_out_path, md_text)

    missing_count = sum(len(row["missing"]) for row in targets)
    context_missing_count = sum(len(row["context_missing"]) for row in targets)
    enforced_warning_count = sum(
        len(row["warnings"]) for row in targets if row.get("baseline_enforced")
    )
    context_warning_count = sum(
        len(row["warnings"]) for row in targets if not row.get("baseline_enforced")
    )
    plugin_warning_count = len(plugins["warnings"])
    reference_warning_count = len(references["warnings"])
    effective_reference_warning_count = (
        0 if args.ignore_cross_repo_warnings else reference_warning_count
    )
    submodule_warning_count = len(submodule_state["warnings"])
    alignment_warning_count = len(alignment_snapshot["warnings"])
    template_warning_count = 1 if template_warning else 0
    warning_count = (
        enforced_warning_count
        + context_warning_count
        + plugin_warning_count
        + effective_reference_warning_count
        + submodule_warning_count
        + alignment_warning_count
        + template_warning_count
    )

    print(f"Suite root: {suite_root}")
    print(f"Targets checked: {len(targets)}")
    print(f"Total missing items: {missing_count}")
    print(f"Total context-missing items: {context_missing_count}")
    print(f"Total warnings: {warning_count}")
    print(f"  enforced-target warnings: {enforced_warning_count}")
    print(f"  context-target warnings: {context_warning_count}")
    print(f"  plugin warnings: {plugin_warning_count}")
    print(f"  cross-repo reference warnings: {reference_warning_count}")
    if args.ignore_cross_repo_warnings and reference_warning_count:
        print("  cross-repo reference warnings (ignored in exit status)")
    print(f"  submodule warnings: {submodule_warning_count}")
    print(f"  alignment warnings: {alignment_warning_count}")
    print(f"  template warnings: {template_warning_count}")
    print(f"Wrote JSON report: {json_out_path} ({'updated' if json_changed else 'unchanged'})")
    print(f"Wrote Markdown report: {md_out_path} ({'updated' if md_changed else 'unchanged'})")
    if template_warning:
        print(f"Warning: {template_warning}")

    has_missing = any(row["missing"] for row in targets)
    has_warnings = warning_count > 0
    enforced_warning_total = (
        enforced_warning_count
        + plugin_warning_count
        + effective_reference_warning_count
        + submodule_warning_count
        + alignment_warning_count
        + template_warning_count
    )
    if has_missing:
        return 1
    if args.strict_enforced_only and enforced_warning_total > 0:
        return 1
    if args.strict and has_warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
