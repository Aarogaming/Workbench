from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_dora_reliability_scoreboard.py"
    spec = importlib.util.spec_from_file_location(
        "check_dora_reliability_scoreboard_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_dora_reliability_scoreboard_script")
    sys.modules["check_dora_reliability_scoreboard_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_dora_reliability_scoreboard_script", None)
        else:
            sys.modules["check_dora_reliability_scoreboard_script"] = original


def _valid_payload() -> dict[str, object]:
    return {
        "schema_version": "workbench.dora_reliability.v1",
        "measurement_mode": "pilot",
        "generated_at": "2026-02-17T08:10:00Z",
        "window": {
            "cadence": "weekly",
            "start_date": "2026-02-10",
            "end_date": "2026-02-16",
        },
        "metrics": {
            "dora": {
                "deployment_frequency_per_week": {
                    "value": 3.0,
                    "target_min": 1.0,
                    "status": "green",
                    "source": "sample",
                },
                "lead_time_for_changes_median_hours": {
                    "value": 18.0,
                    "target_max": 24.0,
                    "status": "green",
                    "source": "sample",
                },
                "change_failure_rate_pct": {
                    "value": 0.0,
                    "target_max": 15.0,
                    "status": "green",
                    "source": "sample",
                },
                "time_to_restore_service_median_hours": {
                    "value": 0.0,
                    "target_max": 24.0,
                    "status": "green",
                    "source": "sample",
                },
            },
            "reliability": {
                "quality_gate_pass_rate_pct": {
                    "value": 100.0,
                    "target_min": 95.0,
                    "status": "green",
                    "source": "sample",
                },
                "hard_block_rate_pct": {
                    "value": 0.0,
                    "target_max": 10.0,
                    "status": "green",
                    "source": "sample",
                },
                "cp4b_sla_breach_count": {
                    "value": 0,
                    "target_max": 0,
                    "status": "green",
                    "source": "sample",
                },
                "incident_handoff_completeness_pct": {
                    "value": 100.0,
                    "target_min": 100.0,
                    "status": "green",
                    "source": "sample",
                },
            },
        },
        "overall_status": "green",
        "notes": ["sample"],
    }


def _valid_markdown() -> str:
    return (
        "# DORA + Reliability Weekly Scoreboard\n\n"
        "## DORA Metrics\n\n"
        "## Reliability Metrics\n\n"
        "## Sources\n"
    )


def _write_files(module, root: Path, payload: dict[str, object], markdown: str) -> None:
    json_path = root / module.SCOREBOARD_JSON
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    md_path = root / module.SCOREBOARD_MD
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(markdown, encoding="utf-8")


def test_check_scoreboard_passes_for_valid_contract():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_files(module, root, _valid_payload(), _valid_markdown())
        issues = module.check_scoreboard(root)
        assert issues == []


def test_check_scoreboard_fails_when_required_metric_missing():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        payload = _valid_payload()
        assert isinstance(payload["metrics"], dict)
        assert isinstance(payload["metrics"]["dora"], dict)
        payload["metrics"]["dora"].pop("deployment_frequency_per_week")
        _write_files(module, root, payload, _valid_markdown())
        issues = module.check_scoreboard(root)
        assert any("deployment_frequency_per_week" in issue for issue in issues)


def test_check_scoreboard_fails_when_percentage_out_of_range():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        payload = _valid_payload()
        assert isinstance(payload["metrics"], dict)
        assert isinstance(payload["metrics"]["reliability"], dict)
        metric = payload["metrics"]["reliability"]["quality_gate_pass_rate_pct"]
        assert isinstance(metric, dict)
        metric["value"] = 140.0
        _write_files(module, root, payload, _valid_markdown())
        issues = module.check_scoreboard(root)
        assert any("must be between 0 and 100" in issue for issue in issues)


def test_check_scoreboard_fails_when_markdown_heading_missing():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        markdown = "# DORA + Reliability Weekly Scoreboard\n\n## DORA Metrics\n"
        _write_files(module, root, _valid_payload(), markdown)
        issues = module.check_scoreboard(root)
        assert any("missing heading" in issue for issue in issues)
