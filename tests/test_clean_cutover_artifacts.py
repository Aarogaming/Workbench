from __future__ import annotations

import os
import subprocess
import tempfile
import time
from pathlib import Path


def test_clean_cutover_artifacts_dry_run_and_delete():
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as tmp:
        cutover_root = Path(tmp) / "cutover"
        old_dir = cutover_root / "INCIDENT-OLD" / "111-a1"
        new_dir = cutover_root / "INCIDENT-NEW" / "222-a1"
        old_dir.mkdir(parents=True, exist_ok=True)
        new_dir.mkdir(parents=True, exist_ok=True)
        (old_dir / "file.txt").write_text("x\n", encoding="utf-8")
        (new_dir / "file.txt").write_text("y\n", encoding="utf-8")

        now = time.time()
        ten_days = 10 * 86400
        one_day = 1 * 86400
        os.utime(old_dir, (now - ten_days, now - ten_days))
        os.utime(new_dir, (now - one_day, now - one_day))

        dry_run = subprocess.run(
            [
                "python3",
                "scripts/clean_cutover_artifacts.py",
                "--root",
                str(cutover_root),
                "--retention-class",
                "short",
                "--short-days",
                "3",
                "--dry-run",
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        assert dry_run.returncode == 0, dry_run.stdout + dry_run.stderr
        assert "[dry-run-delete]" in dry_run.stdout
        assert old_dir.exists()
        assert new_dir.exists()

        apply_run = subprocess.run(
            [
                "python3",
                "scripts/clean_cutover_artifacts.py",
                "--root",
                str(cutover_root),
                "--retention-class",
                "short",
                "--short-days",
                "3",
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        assert apply_run.returncode == 0, apply_run.stdout + apply_run.stderr
        assert not old_dir.exists()
        assert new_dir.exists()
