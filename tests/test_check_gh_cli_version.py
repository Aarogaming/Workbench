from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_gh_cli_version.py"
    spec = importlib.util.spec_from_file_location("check_gh_cli_version_script", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_gh_cli_version_script")
    sys.modules["check_gh_cli_version_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_gh_cli_version_script", None)
        else:
            sys.modules["check_gh_cli_version_script"] = original


def test_parse_semver_accepts_standard_version():
    module = _load_module()
    assert module._parse_semver("gh version 2.86.0 (2026-01-21)") == (2, 86, 0)


def test_check_gh_cli_version_passes_for_newer_version():
    module = _load_module()

    def fake_run(cmd, capture_output, text):
        _ = capture_output, text
        return subprocess.CompletedProcess(
            cmd,
            returncode=0,
            stdout="gh version 2.86.0 (2026-01-21)\n",
            stderr="",
        )

    result = module.check_gh_cli_version("2.50.0", run_fn=fake_run)
    assert result.ok is True
    assert result.detected_version == "2.86.0"


def test_check_gh_cli_version_fails_for_older_version():
    module = _load_module()

    def fake_run(cmd, capture_output, text):
        _ = capture_output, text
        return subprocess.CompletedProcess(
            cmd,
            returncode=0,
            stdout="gh version 2.49.0 (2025-01-21)\n",
            stderr="",
        )

    result = module.check_gh_cli_version("2.50.0", run_fn=fake_run)
    assert result.ok is False
    assert "below required minimum" in result.message


def test_check_gh_cli_version_fails_when_cli_missing():
    module = _load_module()

    def fake_run(cmd, capture_output, text):
        _ = cmd, capture_output, text
        raise FileNotFoundError("gh not found")

    result = module.check_gh_cli_version("2.50.0", run_fn=fake_run)
    assert result.ok is False
    assert result.message == "gh CLI not found in PATH"


def test_check_gh_cli_version_fails_for_invalid_minimum():
    module = _load_module()

    def fake_run(cmd, capture_output, text):
        _ = cmd, capture_output, text
        return subprocess.CompletedProcess(cmd, returncode=0, stdout="", stderr="")

    result = module.check_gh_cli_version("invalid", run_fn=fake_run)
    assert result.ok is False
    assert "invalid --min-version" in result.message
