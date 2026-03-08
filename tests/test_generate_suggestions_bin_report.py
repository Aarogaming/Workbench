from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "generate_suggestions_bin_report.py"
    spec = importlib.util.spec_from_file_location(
        "generate_suggestions_bin_report_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("generate_suggestions_bin_report_script")
    sys.modules["generate_suggestions_bin_report_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("generate_suggestions_bin_report_script", None)
        else:
            sys.modules["generate_suggestions_bin_report_script"] = original


def test_generate_report_collects_status_rows():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / module.SUGGESTIONS_BIN_DOC
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(
            "\n".join(
                (
                    "## Batch",
                    "- `WB-SUG-001` Suggestion one",
                    "  - status: `implemented` (`docs/example.md`)",
                    "- `WB-SUG-002` Suggestion two",
                    "  - status: `approved`",
                )
            )
            + "\n",
            encoding="utf-8",
        )

        report, issues = module.generate_report(root)
        assert issues == []
        assert report is not None
        assert report["schema_version"] == module.SCHEMA_VERSION
        assert report["summary"]["total"] == 2
        assert report["summary"]["implemented"] == 1
        assert report["items"][0]["id"] == "WB-SUG-001"
        assert report["items"][0]["status"] == "implemented"
        assert report["items"][1]["status"] == "approved"


def test_generate_report_fails_when_status_missing():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / module.SUGGESTIONS_BIN_DOC
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(
            "\n".join(
                (
                    "## Batch",
                    "- `WB-SUG-010` Missing status",
                )
            )
            + "\n",
            encoding="utf-8",
        )

        report, issues = module.generate_report(root)
        assert report is None
        assert any("missing status line" in issue for issue in issues)


def test_generate_report_fails_for_invalid_status():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / module.SUGGESTIONS_BIN_DOC
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(
            "\n".join(
                (
                    "## Batch",
                    "- `WB-SUG-011` Invalid status",
                    "  - status: `done`",
                )
            )
            + "\n",
            encoding="utf-8",
        )

        report, issues = module.generate_report(root)
        assert report is None
        assert any("invalid status" in issue for issue in issues)


def test_check_report_sync_passes_when_report_matches():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / module.SUGGESTIONS_BIN_DOC
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(
            "\n".join(
                (
                    "## Batch",
                    "- `WB-SUG-001` Suggestion one",
                    "  - status: `implemented` (`docs/example.md`)",
                )
            )
            + "\n",
            encoding="utf-8",
        )
        report, issues = module.generate_report(root)
        assert issues == []
        assert report is not None
        out = root / module.DEFAULT_OUTPUT
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

        checked, sync_issues = module.check_report_sync(root)
        assert checked is not None
        assert sync_issues == []


def test_check_report_sync_fails_when_report_missing():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / module.SUGGESTIONS_BIN_DOC
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(
            "\n".join(
                (
                    "## Batch",
                    "- `WB-SUG-002` Suggestion two",
                    "  - status: `approved`",
                )
            )
            + "\n",
            encoding="utf-8",
        )
        _, sync_issues = module.check_report_sync(root)
        assert any("missing report file" in issue for issue in sync_issues)


def test_check_report_sync_fails_when_report_out_of_sync():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / module.SUGGESTIONS_BIN_DOC
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(
            "\n".join(
                (
                    "## Batch",
                    "- `WB-SUG-003` Suggestion three",
                    "  - status: `approved`",
                )
            )
            + "\n",
            encoding="utf-8",
        )
        out = root / module.DEFAULT_OUTPUT
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(
                {
                    "schema_version": module.SCHEMA_VERSION,
                    "generated_utc": "2026-02-15T00:00:00Z",
                    "source_doc": module.SUGGESTIONS_BIN_DOC.as_posix(),
                    "status_values": list(module.ALLOWED_STATUSES),
                    "summary": {
                        "total": 1,
                        "implemented": 1,
                        "status_counts": {
                            "new": 0,
                            "reviewing": 0,
                            "approved": 0,
                            "scheduled": 0,
                            "implemented": 1,
                            "rejected": 0,
                        },
                    },
                    "items": [
                        {
                            "id": "WB-SUG-003",
                            "title": "Suggestion three",
                            "status": "implemented",
                        }
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        _, sync_issues = module.check_report_sync(root)
        assert any("report out of sync" in issue for issue in sync_issues)
