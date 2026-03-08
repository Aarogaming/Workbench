from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_ssdf_quality_gate_mapping.py"
    spec = importlib.util.spec_from_file_location(
        "check_ssdf_quality_gate_mapping_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_ssdf_quality_gate_mapping_script")
    sys.modules["check_ssdf_quality_gate_mapping_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_ssdf_quality_gate_mapping_script", None)
        else:
            sys.modules["check_ssdf_quality_gate_mapping_script"] = original


def _write_gate_source(root: Path, gates: list[str]) -> None:
    source = root / "scripts" / "run_quality_gates.py"
    source.parent.mkdir(parents=True, exist_ok=True)
    lines = ["gates = ["]
    for gate in gates:
        lines.append(f'    Gate(name="{gate}", cmd=["echo", "{gate}"]),')
    lines.append("]")
    source.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_mapping_doc(module, root: Path, gate_rows: list[str]) -> None:
    mapping = root / module.MAPPING_DOC
    mapping.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(
        [
            "# SSDF Mapping",
            "",
            module.REQUIRED_SECTION_HEADERS[0],
            "",
            "| Gate | Command | SSDF Practices |",
            "| --- | --- | --- |",
            *gate_rows,
            "",
            module.REQUIRED_SECTION_HEADERS[1],
            "",
            "| Workflow | Enforced checks | SSDF Practices |",
            "| --- | --- | --- |",
            "| `.github/workflows/ci.yml` | `check` | `PO.3.1` |",
            "| `.github/workflows/size-check.yml` | `check` | `RV.1.1` |",
            "",
        ]
    )
    mapping.write_text(body, encoding="utf-8")


def test_check_mapping_passes_with_gate_and_workflow_coverage():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_gate_source(root, ["secret-hygiene", "fetch-index"])
        _write_mapping_doc(
            module,
            root,
            [
                "| `secret-hygiene` | `python3 scripts/check_secret_hygiene.py` | `PW.6.2` |",
                "| `fetch-index` | `python3 scripts/validate_fetch_index.py` | `RV.1.2` |",
            ],
        )
        issues = module.check_mapping(root)
        assert issues == []


def test_check_mapping_fails_when_gate_row_missing():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_gate_source(root, ["secret-hygiene", "fetch-index"])
        _write_mapping_doc(
            module,
            root,
            [
                "| `secret-hygiene` | `python3 scripts/check_secret_hygiene.py` | `PW.6.2` |",
            ],
        )
        issues = module.check_mapping(root)
        assert any("missing gate mapping row" in issue for issue in issues)


def test_check_mapping_fails_when_ssdf_token_missing():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write_gate_source(root, ["secret-hygiene"])
        _write_mapping_doc(
            module,
            root,
            [
                "| `secret-hygiene` | `python3 scripts/check_secret_hygiene.py` | `none` |",
            ],
        )
        issues = module.check_mapping(root)
        assert any("missing SSDF token" in issue for issue in issues)
