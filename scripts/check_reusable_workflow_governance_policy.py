#!/usr/bin/env python3
"""Validate reusable workflow governance policy contract."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


POLICY_DOC = Path("docs/research/REUSABLE_WORKFLOW_GOVERNANCE_POLICY.md")
RUNBOOK_DOC = Path("docs/research/CP_RUNBOOK_COMMANDS.md")
CHECKLIST_TEMPLATE = Path("docs/research/templates/PRIVATE_WORKFLOW_SHARING_WARNING_CHECKLIST.md")
INVENTORY_SCRIPT = Path("scripts/generate_reusable_workflow_inventory.py")

WORKFLOW_ROOT = Path(".github/workflows")
LOCAL_REUSABLE_RE = re.compile(r"^\s*uses:\s*['\"]?(\./\.github/workflows/[^'\"#\s]+\.yml)")

REQUIRED_HEADINGS: tuple[str, ...] = (
    "## Reusable Workflow Nesting Depth Cap (WB-SUG-101)",
    "## Monthly Reusable Workflow Consumer Inventory (WB-SUG-102)",
    "## Private Workflow Sharing Warning Checklist (WB-SUG-103)",
    "## Self-Hosted Runner Group + Labels Selector Policy (WB-SUG-104)",
    "## Required Local Artifacts",
    "## Verification Commands and Outcomes",
)

REQUIRED_POLICY_SNIPPETS: tuple[str, ...] = (
    "<=3",
    "monthly inventory",
    "log visibility",
    "token scope",
    "runs-on: self-hosted",
    "group + labels",
)

REQUIRED_FILES: tuple[Path, ...] = (
    Path("scripts/check_reusable_workflow_governance_policy.py"),
    Path("scripts/generate_reusable_workflow_inventory.py"),
    Path("docs/research/templates/PRIVATE_WORKFLOW_SHARING_WARNING_CHECKLIST.md"),
)

INVENTORY_SCRIPT_TOKENS: tuple[str, ...] = (
    "collect_reusable_workflow_consumers",
    "workbench.reusable_workflow_inventory.v1",
    "reusable_workflow_inventory.json",
    "reusable_workflow_inventory.md",
)

CHECKLIST_TOKENS: tuple[str, ...] = (
    "Log visibility",
    "Token scope",
    "Repository allowlist",
    "Rollback path",
)

WORKFLOW_TOKENS: dict[Path, tuple[str, ...]] = {
    Path(".github/workflows/ci.yml"): (
        "python3 scripts/check_reusable_workflow_governance_policy.py",
    ),
    Path(".github/workflows/size-check.yml"): (
        "python3 scripts/check_reusable_workflow_governance_policy.py",
    ),
}

REQUIRED_RUNBOOK_TOKENS: tuple[str, ...] = (
    "## Reusable Workflow Governance",
    "python3 scripts/check_reusable_workflow_governance_policy.py",
    "python3 scripts/generate_reusable_workflow_inventory.py --output-dir docs/reports",
    "cat docs/research/REUSABLE_WORKFLOW_GOVERNANCE_POLICY.md",
    "cat docs/research/templates/PRIVATE_WORKFLOW_SHARING_WARNING_CHECKLIST.md",
)


def _check_file_tokens(path: Path, tokens: tuple[str, ...], issue_prefix: str) -> list[str]:
    if not path.exists():
        return [f"missing required file: {path.as_posix()}"]
    content = path.read_text(encoding="utf-8")
    issues: list[str] = []
    for token in tokens:
        if token not in content:
            issues.append(f"{issue_prefix}: missing token '{token}'")
    return issues


def _collect_reusable_graph(root: Path) -> dict[str, set[str]]:
    workflow_dir = root / WORKFLOW_ROOT
    graph: dict[str, set[str]] = {}
    if not workflow_dir.exists():
        return graph

    for workflow in sorted(workflow_dir.glob("*.yml")):
        consumer = workflow.relative_to(root).as_posix()
        graph.setdefault(consumer, set())
        for raw in workflow.read_text(encoding="utf-8").splitlines():
            match = LOCAL_REUSABLE_RE.match(raw)
            if not match:
                continue
            target = match.group(1)
            if target.startswith("./"):
                target = target[2:]
            graph[consumer].add(target)
    return graph


def _check_reusable_depth_cap(root: Path, max_depth: int) -> list[str]:
    graph = _collect_reusable_graph(root)
    issues: list[str] = []

    visiting: set[str] = set()
    memo: dict[str, int] = {}

    def depth(node: str) -> int:
        if node in memo:
            return memo[node]
        if node in visiting:
            issues.append(f"reusable workflow call cycle detected: {node}")
            return 0
        visiting.add(node)
        best = 0
        for child in graph.get(node, set()):
            best = max(best, 1 + depth(child))
        visiting.remove(node)
        memo[node] = best
        return best

    for node in graph:
        chain_depth = depth(node)
        if chain_depth > max_depth:
            issues.append(
                f"{node}: reusable workflow call depth={chain_depth} exceeds cap={max_depth}"
            )
    return issues


def _check_self_hosted_selector_policy(root: Path) -> list[str]:
    issues: list[str] = []
    workflow_dir = root / WORKFLOW_ROOT
    if not workflow_dir.exists():
        return issues

    for workflow in sorted(workflow_dir.glob("*.yml")):
        lines = workflow.read_text(encoding="utf-8").splitlines()
        for idx, raw in enumerate(lines):
            stripped = raw.strip()
            if stripped.startswith("runs-on:"):
                value = stripped.split(":", 1)[1].strip()
                if value in {"self-hosted", "[self-hosted]", "['self-hosted']", '["self-hosted"]'}:
                    issues.append(
                        f"{workflow.as_posix()}:{idx + 1}: broad self-hosted selector forbidden"
                    )
            if stripped == "runs-on:":
                indent = len(raw) - len(raw.lstrip(" "))
                items: list[str] = []
                cursor = idx + 1
                while cursor < len(lines):
                    candidate = lines[cursor]
                    candidate_stripped = candidate.strip()
                    candidate_indent = len(candidate) - len(candidate.lstrip(" "))
                    if candidate_stripped and candidate_indent <= indent:
                        break
                    if candidate_stripped.startswith("- "):
                        items.append(candidate_stripped[2:].strip().strip("'\""))
                    cursor += 1
                if items == ["self-hosted"]:
                    issues.append(
                        f"{workflow.as_posix()}:{idx + 1}: self-hosted list requires group+labels selector"
                    )
    return issues


def check_policy(root: Path) -> list[str]:
    issues: list[str] = []

    policy_path = root / POLICY_DOC
    if not policy_path.exists():
        return [f"missing policy doc: {POLICY_DOC.as_posix()}"]

    content = policy_path.read_text(encoding="utf-8")
    for heading in REQUIRED_HEADINGS:
        if heading not in content:
            issues.append(f"missing policy heading in {POLICY_DOC.as_posix()}: {heading}")
    for snippet in REQUIRED_POLICY_SNIPPETS:
        if snippet not in content:
            issues.append(f"missing policy snippet in {POLICY_DOC.as_posix()}: {snippet}")

    for relative in REQUIRED_FILES:
        if not (root / relative).exists():
            issues.append(f"missing required file: {relative.as_posix()}")

    issues.extend(
        _check_file_tokens(
            root / INVENTORY_SCRIPT,
            INVENTORY_SCRIPT_TOKENS,
            INVENTORY_SCRIPT.as_posix(),
        )
    )
    issues.extend(
        _check_file_tokens(
            root / CHECKLIST_TEMPLATE,
            CHECKLIST_TOKENS,
            CHECKLIST_TEMPLATE.as_posix(),
        )
    )
    for workflow_path, tokens in WORKFLOW_TOKENS.items():
        issues.extend(
            _check_file_tokens(
                root / workflow_path,
                tokens,
                workflow_path.as_posix(),
            )
        )
    issues.extend(
        _check_file_tokens(
            root / RUNBOOK_DOC,
            REQUIRED_RUNBOOK_TOKENS,
            RUNBOOK_DOC.as_posix(),
        )
    )
    issues.extend(_check_reusable_depth_cap(root, max_depth=3))
    issues.extend(_check_self_hosted_selector_policy(root))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate reusable workflow governance policy contract."
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Optional repo root override (default: script parent repo root).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    issues = check_policy(root)
    if issues:
        print("[fail] reusable workflow governance policy check")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("[ok] reusable workflow governance policy check")
    print(f"  - {POLICY_DOC.as_posix()}")
    print(f"  - {INVENTORY_SCRIPT.as_posix()}")
    print(f"  - {CHECKLIST_TEMPLATE.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
