from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_scan_reports_missing_and_can_fail_if_missing():
    root = Path(__file__).resolve().parents[1]

    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        _write(
            repo / "core" / "a.py",
            """
from abc import ABC

class AManager(LifecycleStateMixin):
    pass

class BManager:
    pass

class CCoordinator(ABC):
    pass
""",
        )

        cmd = [
            "python3",
            "scripts/maintain_health_protocol_coverage.py",
            "--repo-root",
            str(repo),
        ]
        result = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr

        payload = json.loads(result.stdout)
        assert payload["summary"]["concrete_classes"] == 2
        assert payload["summary"]["adopted_classes"] == 1
        assert payload["summary"]["missing_classes"] == 1
        assert payload["missing"][0]["name"] == "BManager"

        fail_cmd = cmd + ["--fail-if-missing"]
        fail_result = subprocess.run(fail_cmd, cwd=root, capture_output=True, text=True)
        assert fail_result.returncode == 2


def test_update_docs_rewrites_counts():
    root = Path(__file__).resolve().parents[1]

    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"

        _write(
            repo / "core" / "x.py",
            """
class XManager(LifecycleStateMixin):
    pass

class YCoordinator(LifecycleStateMixin):
    pass
""",
        )

        _write(
            repo / "WAVE2_COMPLETION_REPORT_2026_03_10.md",
            """
- **Total Managers/Coordinators in core/:** 49 concrete classes
- **Migrated to health protocol:** 49/49 (100%)
""",
        )

        _write(
            repo / "DUPLICATION_AUDIT_WAVE2_2026_03_09.md",
            """
**Final count:** 53 managers migrated total, 8/8 bridges, 240+ tests passing
""",
        )

        cmd = [
            "python3",
            "scripts/maintain_health_protocol_coverage.py",
            "--repo-root",
            str(repo),
            "--update-docs",
        ]
        result = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr

        report = (repo / "WAVE2_COMPLETION_REPORT_2026_03_10.md").read_text(encoding="utf-8")
        audit = (repo / "DUPLICATION_AUDIT_WAVE2_2026_03_09.md").read_text(encoding="utf-8")

        assert "**Total Managers/Coordinators in core/:** 2 concrete classes" in report
        assert "**Migrated to health protocol:** 2/2 (100%)" in report
        assert "**Final count:** 2 managers migrated total" in audit
