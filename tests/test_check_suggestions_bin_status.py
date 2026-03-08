from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_suggestions_bin_status.py"
    spec = importlib.util.spec_from_file_location(
        "check_suggestions_bin_status_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_suggestions_bin_status_script")
    sys.modules["check_suggestions_bin_status_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_suggestions_bin_status_script", None)
        else:
            sys.modules["check_suggestions_bin_status_script"] = original


def _write_report(module, root: Path, items: list[dict[str, str]], schema: str | None = None) -> None:
    report = root / module.SUGGESTIONS_BIN_REPORT
    report.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": schema or module.REPORT_SCHEMA,
        "items": items,
    }
    report.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def test_check_suggestions_bin_passes_with_valid_status_lines():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        path = root / module.SUGGESTIONS_BIN_DOC
        path.parent.mkdir(parents=True, exist_ok=True)
        (root / "docs" / "example.md").parent.mkdir(parents=True, exist_ok=True)
        (root / "docs" / "example.md").write_text("evidence\n", encoding="utf-8")
        (root / "scripts" / "example.py").parent.mkdir(parents=True, exist_ok=True)
        (root / "scripts" / "example.py").write_text("print('ok')\n", encoding="utf-8")
        path.write_text(
            "\n".join(
                (
                    "## Batch",
                    "- `WB-SUG-001` Example",
                    "  - status: `implemented` (`docs/example.md` + `scripts/example.py`)",
                    "- `WB-SUG-002` Example 2",
                    "  - status: `approved`",
                )
            )
            + "\n",
            encoding="utf-8",
        )
        _write_report(
            module,
            root,
            [
                {"id": "WB-SUG-001", "status": "implemented"},
                {"id": "WB-SUG-002", "status": "approved"},
            ],
        )
        issues = module.check_suggestions_bin(root)
        assert issues == []


def test_check_suggestions_bin_fails_when_status_missing():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        path = root / module.SUGGESTIONS_BIN_DOC
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "\n".join(
                (
                    "## Batch",
                    "- `WB-SUG-010` Missing status",
                )
            )
            + "\n",
            encoding="utf-8",
        )
        _write_report(module, root, [])
        issues = module.check_suggestions_bin(root)
        assert any("missing status line" in issue for issue in issues)


def test_check_suggestions_bin_fails_for_invalid_status():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        path = root / module.SUGGESTIONS_BIN_DOC
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
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
        _write_report(module, root, [])
        issues = module.check_suggestions_bin(root)
        assert any("invalid status" in issue for issue in issues)


def test_check_suggestions_bin_fails_implemented_without_evidence():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        path = root / module.SUGGESTIONS_BIN_DOC
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "\n".join(
                (
                    "## Batch",
                    "- `WB-SUG-012` Missing evidence",
                    "  - status: `implemented`",
                )
            )
            + "\n",
            encoding="utf-8",
        )
        _write_report(module, root, [{"id": "WB-SUG-012", "status": "implemented"}])
        issues = module.check_suggestions_bin(root)
        assert any("implemented status missing evidence references" in issue for issue in issues)


def test_check_suggestions_bin_fails_when_report_schema_invalid():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        path = root / module.SUGGESTIONS_BIN_DOC
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "\n".join(
                (
                    "## Batch",
                    "- `WB-SUG-020` Example",
                    "  - status: `approved`",
                )
            )
            + "\n",
            encoding="utf-8",
        )
        _write_report(module, root, [{"id": "WB-SUG-020", "status": "approved"}], schema="legacy.v0")
        issues = module.check_suggestions_bin(root)
        assert any("invalid or unsupported report schema" in issue for issue in issues)


def test_check_suggestions_bin_fails_when_report_status_mismatch():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        path = root / module.SUGGESTIONS_BIN_DOC
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "\n".join(
                (
                    "## Batch",
                    "- `WB-SUG-021` Example",
                    "  - status: `approved`",
                )
            )
            + "\n",
            encoding="utf-8",
        )
        _write_report(module, root, [{"id": "WB-SUG-021", "status": "implemented"}])
        issues = module.check_suggestions_bin(root)
        assert any("status mismatch" in issue for issue in issues)


def test_check_suggestions_bin_fails_when_suggestion_count_exceeds_cap():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        path = root / module.SUGGESTIONS_BIN_DOC
        path.parent.mkdir(parents=True, exist_ok=True)

        lines = ["## Batch"]
        report_items = []
        for number in range(1, module.MAX_SUGGESTIONS + 2):
            suggestion_id = f"WB-SUG-{number:03d}"
            lines.append(f"- `{suggestion_id}` Example {number}")
            lines.append("  - status: `approved`")
            report_items.append({"id": suggestion_id, "status": "approved"})
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        _write_report(module, root, report_items)

        issues = module.check_suggestions_bin(root)
        assert any("exceeds cap" in issue for issue in issues)
