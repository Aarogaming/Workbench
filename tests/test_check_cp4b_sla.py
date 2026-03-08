from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


def _tracker_content(status: str, sla_utc: str) -> str:
    return (
        "# Tracker\n\n"
        "## Owner + SLA Tracker\n\n"
        "| Action ID | Action | Owner | SLA (UTC) | Status | Closure Evidence |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        f"| `CP4B-001` | Item | `lane-a` | `{sla_utc}` | `{status}` | `evidence` |\n"
    )


def test_check_cp4b_sla_fails_on_overdue_non_implemented():
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "cp4b.md"
        path.write_text(_tracker_content("in_progress", "2026-02-10T00:00:00Z"), encoding="utf-8")

        result = subprocess.run(
            [
                "python3",
                "scripts/check_cp4b_sla.py",
                "--path",
                str(path),
                "--now-utc",
                "2026-02-17T00:00:00Z",
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "[fail] overdue CP4-B items" in result.stdout


def test_check_cp4b_sla_passes_for_implemented_overdue_item():
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "cp4b.md"
        path.write_text(_tracker_content("implemented", "2026-02-10T00:00:00Z"), encoding="utf-8")

        result = subprocess.run(
            [
                "python3",
                "scripts/check_cp4b_sla.py",
                "--path",
                str(path),
                "--now-utc",
                "2026-02-17T00:00:00Z",
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert "[ok] CP4-B SLA check" in result.stdout


def test_check_cp4b_sla_fails_for_invalid_status():
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "cp4b.md"
        path.write_text(_tracker_content("unknown", "2026-02-20T00:00:00Z"), encoding="utf-8")

        result = subprocess.run(
            [
                "python3",
                "scripts/check_cp4b_sla.py",
                "--path",
                str(path),
                "--now-utc",
                "2026-02-17T00:00:00Z",
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "invalid status" in result.stdout


def test_check_cp4b_sla_fails_for_missing_closure_evidence():
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "cp4b.md"
        content = (
            "# Tracker\n\n"
            "## Owner + SLA Tracker\n\n"
            "| Action ID | Action | Owner | SLA (UTC) | Status | Closure Evidence |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            "| `CP4B-001` | Item | `lane-a` | `2026-02-20T00:00:00Z` | `implemented` | `` |\n"
        )
        path.write_text(content, encoding="utf-8")

        result = subprocess.run(
            [
                "python3",
                "scripts/check_cp4b_sla.py",
                "--path",
                str(path),
                "--now-utc",
                "2026-02-17T00:00:00Z",
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "implemented status requires closure evidence" in result.stdout
