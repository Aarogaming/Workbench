#!/usr/bin/env python3
"""Run Workbench CP6 Merlin local verification commands with deterministic reporting."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def build_required_commands() -> list[str]:
    return [
        "python3 -m pytest -q tests/test_merlin_research_manager_consumer.py",
        "python3 -m pytest -q tests/test_merlin_research_manager_consumer.py -k test_envelope_builders_emit_create_signal_brief_operations",
        'python3 -m pytest -q tests/test_merlin_research_manager_consumer.py -k "test_read_only_error_selects_non_mutating_fallback or test_validation_error_maps_to_expected_fallback"',
        """python3 - <<'PY'
import json, requests
from pathlib import Path
p=Path('artifacts/diagnostics/merlin_capabilities_live_2026-02-18.json'); p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(requests.get('http://localhost:8001/merlin/operations/capabilities', headers={'X-Merlin-Key':'merlin-secret-key'}, timeout=20).json(), indent=2)+'\\n', encoding='utf-8')
print(p.as_posix())
PY""",
        "python3 scripts/merlin_research_manager_consumer.py --capabilities-json artifacts/diagnostics/merlin_capabilities_live_2026-02-18.json",
    ]


def _start_one_shot_mock_server() -> subprocess.Popen[str]:
    process = subprocess.Popen(
        [
            "python3",
            "scripts/merlin_mock_capabilities_server.py",
            "--once",
            "--host",
            "127.0.0.1",
            "--port",
            "8001",
            "--api-key",
            "merlin-secret-key",
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if process.stdout is not None:
        process.stdout.readline()
    return process


def _run_shell(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-lc", command],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def _summarize_output(completed: subprocess.CompletedProcess[str], max_chars: int) -> str:
    merged = (completed.stdout or "") + (completed.stderr or "")
    merged = merged.strip()
    if len(merged) <= max_chars:
        return merged
    return merged[: max_chars - 3] + "..."


def run_checks(*, max_output_chars: int) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    commands = build_required_commands()

    for index, command in enumerate(commands, start=1):
        server_process: subprocess.Popen[str] | None = None
        server_status = ""
        if index == 4:
            server_process = _start_one_shot_mock_server()
            time.sleep(0.05)

        completed = _run_shell(command)
        status = "PASS" if completed.returncode == 0 else "FAIL"

        if server_process is not None:
            try:
                wait_code = server_process.wait(timeout=5)
                server_status = f"mock_server_exit_code={wait_code}"
            except subprocess.TimeoutExpired:
                server_process.kill()
                server_status = "mock_server_exit_code=timeout_killed"

        entry = {
            "index": index,
            "command": command,
            "status": status,
            "returncode": completed.returncode,
            "output_summary": _summarize_output(completed, max_output_chars),
        }
        if server_status:
            entry["mock_server_status"] = server_status
        results.append(entry)

    overall = "PASS" if all(item["status"] == "PASS" for item in results) else "FAIL"
    return {
        "overall_status": overall,
        "checks": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run CP6 Merlin local checks and emit machine-readable summary."
    )
    parser.add_argument(
        "--output-json",
        default="artifacts/diagnostics/merlin_cp6_local_checks_2026-02-19.json",
    )
    parser.add_argument("--max-output-chars", type=int, default=2400)
    args = parser.parse_args()

    summary = run_checks(max_output_chars=args.max_output_chars)

    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(output_path.as_posix())
    print(summary["overall_status"])
    return 0 if summary["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
