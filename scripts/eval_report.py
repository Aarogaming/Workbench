#!/usr/bin/env python3
"""Run deterministic Workbench eval scenarios and emit score reports."""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass
class EvalResult:
    eval_id: str
    passed: bool
    score: float
    max_score: float
    details: str


def _load_module(module_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get(module_name)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = original


def _eval_workflow_pause_resume(root: Path) -> EvalResult:
    module = _load_module(root / "plugins" / "workflow_engine.py", "eval_workflow_engine")
    workflow = module.WorkflowDefinition("wf-eval", "pause resume eval")
    workflow.add_step(module.WorkflowStep(step_id="s1", action="first"))
    workflow.add_step(module.WorkflowStep(step_id="s2", action="second"))
    executor = module.WorkflowExecutor()
    calls = {"first": 0, "second": 0}

    def first_handler(_inputs, _results):
        calls["first"] += 1
        executor.pause()
        return "first"

    def second_handler(_inputs, _results):
        calls["second"] += 1
        return "second"

    executor.register_handler("first", first_handler)
    executor.register_handler("second", second_handler)
    paused = executor.execute(workflow)
    resumed = executor.resume()

    passed = (
        paused.get("status") == "paused"
        and resumed.get("success") is True
        and calls["first"] == 1
        and calls["second"] == 1
        and resumed.get("results", {}).get("s2") == "second"
    )
    details = f"paused={paused.get('status')} first={calls['first']} second={calls['second']}"
    return EvalResult(
        eval_id="workflow_pause_resume",
        passed=passed,
        score=1.0 if passed else 0.0,
        max_score=1.0,
        details=details,
    )


def _eval_workflow_delay_contract(root: Path) -> EvalResult:
    module = _load_module(root / "plugins" / "workflow_engine.py", "eval_workflow_delay")
    workflow = module.WorkflowDefinition("wf-delay", "delay contract")
    workflow.add_step(module.WorkflowStep(step_id="s1", action="noop"))
    scheduler = module.WorkflowScheduler()
    scheduler.executor.register_handler("noop", lambda _inputs, _results: "ok")
    schedule_id = scheduler.schedule(workflow, trigger="delayed", delay=5.0)
    created_at = scheduler.scheduled[schedule_id]["created_at"]
    early = scheduler.run_scheduled(schedule_id, now=created_at + 1.0)
    ready = scheduler.run_scheduled(schedule_id, now=created_at + 5.1)
    passed = (
        early.get("success") is False
        and early.get("error_code") == "schedule_not_ready"
        and ready.get("success") is True
    )
    details = f"early={early.get('error_code')} ready={ready.get('success')}"
    return EvalResult(
        eval_id="workflow_delay_contract",
        passed=passed,
        score=1.0 if passed else 0.0,
        max_score=1.0,
        details=details,
    )


def _eval_mcp_auth_invalid_credentials(root: Path) -> EvalResult:
    module = _load_module(root / "plugins" / "mcp_auth.py", "eval_mcp_auth_invalid")
    manager = module.MCPAuthManager(module.MCPAuthConfig(auth_token="", api_key="", server_url=""))
    result = manager.authenticate()
    passed = result.get("success") is False and result.get("error_code") == "invalid_credentials"
    details = f"error_code={result.get('error_code')}"
    return EvalResult(
        eval_id="mcp_auth_invalid_credentials",
        passed=passed,
        score=1.0 if passed else 0.0,
        max_score=1.0,
        details=details,
    )


def _eval_mcp_auth_verified_contract(root: Path) -> EvalResult:
    module = _load_module(root / "plugins" / "mcp_auth.py", "eval_mcp_auth_verified")

    class Response:
        def __init__(self, status_code: int, payload: dict[str, Any] | None = None):
            self.status_code = status_code
            self._payload = payload or {}

        def json(self):
            return self._payload

    class Requests:
        def get(self, url, timeout, headers):
            _ = timeout, headers
            if str(url).endswith("/auth/verify"):
                return Response(
                    200,
                    payload={
                        "token_valid": True,
                        "session_id": "eval-session",
                        "permissions": ["read"],
                    },
                )
            return Response(200, payload={})

    module.requests = Requests()
    manager = module.MCPAuthManager(
        module.MCPAuthConfig(
            auth_token="x" * 24,
            api_key="",
            server_url="https://example.com",
            timeout=5,
            require_verified=True,
        )
    )
    result = manager.authenticate()
    passed = (
        result.get("success") is True
        and result.get("verified") is True
        and result.get("session_id") == "eval-session"
        and manager.authenticated is True
    )
    details = f"success={result.get('success')} verified={result.get('verified')}"
    return EvalResult(
        eval_id="mcp_auth_verified_contract",
        passed=passed,
        score=1.0 if passed else 0.0,
        max_score=1.0,
        details=details,
    )


def _eval_plugin_contract_audit(root: Path) -> EvalResult:
    cmd = [sys.executable, "scripts/check_plugin_contracts.py"]
    proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    passed = proc.returncode == 0
    details = f"exit_code={proc.returncode}"
    return EvalResult(
        eval_id="plugin_contract_audit",
        passed=passed,
        score=1.0 if passed else 0.0,
        max_score=1.0,
        details=details,
    )


def _eval_workflow_pinning(root: Path) -> EvalResult:
    cmd = [sys.executable, "scripts/check_workflow_pinning.py"]
    proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    passed = proc.returncode == 0
    details = f"exit_code={proc.returncode}"
    return EvalResult(
        eval_id="workflow_pinning_audit",
        passed=passed,
        score=1.0 if passed else 0.0,
        max_score=1.0,
        details=details,
    )


def _eval_workflow_pinning_exceptions(root: Path) -> EvalResult:
    cmd = [sys.executable, "scripts/check_workflow_pinning_exceptions.py"]
    proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    passed = proc.returncode == 0
    details = f"exit_code={proc.returncode}"
    return EvalResult(
        eval_id="workflow_pinning_exceptions_review",
        passed=passed,
        score=1.0 if passed else 0.0,
        max_score=1.0,
        details=details,
    )


EVALUATORS: dict[str, Callable[[Path], EvalResult]] = {
    "workflow_pause_resume": _eval_workflow_pause_resume,
    "workflow_delay_contract": _eval_workflow_delay_contract,
    "mcp_auth_invalid_credentials": _eval_mcp_auth_invalid_credentials,
    "mcp_auth_verified_contract": _eval_mcp_auth_verified_contract,
    "plugin_contract_audit": _eval_plugin_contract_audit,
    "workflow_pinning_audit": _eval_workflow_pinning,
    "workflow_pinning_exceptions_review": _eval_workflow_pinning_exceptions,
}


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _load_scenarios(path: Path) -> list[dict[str, Any]]:
    payload = _load_json(path)
    if payload is None:
        return [{"id": key, "enabled": True} for key in sorted(EVALUATORS)]
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list):
        return [{"id": key, "enabled": True} for key in sorted(EVALUATORS)]
    rows: list[dict[str, Any]] = []
    for row in scenarios:
        if isinstance(row, dict):
            eval_id = row.get("id")
            if isinstance(eval_id, str) and eval_id.strip():
                rows.append(
                    {"id": eval_id.strip(), "enabled": bool(row.get("enabled", True))}
                )
    return rows


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Eval Report",
        "",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- total: `{report['summary']['total']}`",
        f"- passed: `{report['summary']['passed']}`",
        f"- failed: `{report['summary']['failed']}`",
        f"- pass_rate: `{report['summary']['pass_rate']:.3f}`",
        "",
        "| Eval ID | Passed | Score | Details |",
        "|---|---|---:|---|",
    ]
    for row in report["results"]:
        lines.append(
            f"| `{row['eval_id']}` | `{row['passed']}` | {row['score']:.2f}/{row['max_score']:.2f} | {row['details']} |"
        )
    gate = report.get("gate", {})
    if gate:
        lines.append("")
        lines.append("## Gate")
        lines.append("")
        lines.append(f"- pass: `{gate.get('pass')}`")
        if gate.get("reasons"):
            lines.append("- reasons:")
            for reason in gate["reasons"]:
                lines.append(f"  - {reason}")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic Workbench eval scenarios.")
    parser.add_argument(
        "--scenarios",
        default="evals/scenarios/main.json",
        help="Scenario definition JSON path.",
    )
    parser.add_argument(
        "--baseline",
        default="evals/baselines/main.json",
        help="Baseline JSON path.",
    )
    parser.add_argument(
        "--json-out",
        default="docs/reports/eval_report.json",
        help="JSON report output path.",
    )
    parser.add_argument(
        "--md-out",
        default="docs/reports/eval_report.md",
        help="Markdown report output path.",
    )
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Update baseline using current run summary.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    scenario_path = (root / args.scenarios).resolve()
    baseline_path = (root / args.baseline).resolve()
    json_out = (root / args.json_out).resolve()
    md_out = (root / args.md_out).resolve()

    scenarios = _load_scenarios(scenario_path)
    results: list[EvalResult] = []
    for row in scenarios:
        eval_id = row["id"]
        if not row["enabled"]:
            continue
        evaluator = EVALUATORS.get(eval_id)
        if evaluator is None:
            results.append(
                EvalResult(
                    eval_id=eval_id,
                    passed=False,
                    score=0.0,
                    max_score=1.0,
                    details="unknown evaluator id",
                )
            )
            continue
        try:
            results.append(evaluator(root))
        except Exception as exc:
            results.append(
                EvalResult(
                    eval_id=eval_id,
                    passed=False,
                    score=0.0,
                    max_score=1.0,
                    details=f"exception: {exc}",
                )
            )

    total = len(results)
    passed_count = len([row for row in results if row.passed])
    failed_count = total - passed_count
    score_total = sum(row.score for row in results)
    max_total = sum(row.max_score for row in results) or 1.0
    pass_rate = score_total / max_total

    gate = {"pass": True, "reasons": []}
    baseline = _load_json(baseline_path)
    if baseline is None:
        gate["pass"] = False
        gate["reasons"].append(f"baseline missing or invalid: {baseline_path}")
    else:
        min_pass_rate = float(baseline.get("min_pass_rate", 1.0))
        required_pass = baseline.get("required_pass", [])
        if pass_rate < min_pass_rate:
            gate["pass"] = False
            gate["reasons"].append(
                f"pass_rate {pass_rate:.3f} is below min_pass_rate {min_pass_rate:.3f}"
            )
        if isinstance(required_pass, list):
            by_id = {row.eval_id: row for row in results}
            for eval_id in required_pass:
                if not isinstance(eval_id, str):
                    continue
                row = by_id.get(eval_id)
                if row is None or not row.passed:
                    gate["pass"] = False
                    gate["reasons"].append(f"required eval failed: {eval_id}")

    report = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scenario_path": str(scenario_path),
        "baseline_path": str(baseline_path),
        "summary": {
            "total": total,
            "passed": passed_count,
            "failed": failed_count,
            "pass_rate": pass_rate,
        },
        "results": [
            {
                "eval_id": row.eval_id,
                "passed": row.passed,
                "score": row.score,
                "max_score": row.max_score,
                "details": row.details,
            }
            for row in results
        ],
        "gate": gate,
    }

    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.write_text(_render_markdown(report), encoding="utf-8")

    if args.update_baseline:
        updated = {
            "min_pass_rate": round(pass_rate, 3),
            "required_pass": [row.eval_id for row in results if row.passed],
        }
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        baseline_path.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
        print(f"Updated baseline: {baseline_path}")

    print(f"Scenarios: {scenario_path}")
    print(f"Baseline: {baseline_path}")
    print(f"Pass rate: {pass_rate:.3f} ({passed_count}/{total})")
    print(f"JSON report: {json_out}")
    print(f"Markdown report: {md_out}")
    if gate["reasons"]:
        print("Gate reasons:")
        for reason in gate["reasons"]:
            print(f"- {reason}")
    return 0 if gate["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
