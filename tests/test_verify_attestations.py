from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "verify_attestations.py"
    spec = importlib.util.spec_from_file_location("verify_attestations_script", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("verify_attestations_script")
    sys.modules["verify_attestations_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("verify_attestations_script", None)
        else:
            sys.modules["verify_attestations_script"] = original


def test_build_command_contains_expected_flags():
    module = _load_module()
    cmd = module._build_command(
        "/tmp/file.bin",
        "owner/repo",
        "owner/repo/.github/workflows/build.yml",
        "https://slsa.dev/provenance/v1",
    )
    assert cmd[:4] == ["gh", "attestation", "verify", "/tmp/file.bin"]
    assert "-R" in cmd
    assert "--signer-workflow" in cmd
    assert "--predicate-type" in cmd
    assert "--format" in cmd


def test_build_command_includes_bundle_when_provided():
    module = _load_module()
    cmd = module._build_command(
        "/tmp/file.bin",
        "owner/repo",
        "owner/repo/.github/workflows/build.yml",
        "https://slsa.dev/provenance/v1",
        "/tmp/bundle.jsonl",
    )
    assert "--bundle" in cmd
    assert "/tmp/bundle.jsonl" in cmd


def test_parse_dotenv_reads_key_values(tmp_path):
    module = _load_module()
    env_path = tmp_path / ".env"
    env_path.write_text(
        "A=1\n"
        "GH_TOKEN='abc123'\n"
        "export GITHUB_TOKEN=xyz\n",
        encoding="utf-8",
    )
    values = module._parse_dotenv(env_path)
    assert values["A"] == "1"
    assert values["GH_TOKEN"] == "abc123"
    assert values["GITHUB_TOKEN"] == "xyz"


def test_discover_github_token_prefers_process_env(tmp_path):
    module = _load_module()
    root = Path(__file__).resolve().parents[1]
    old = os.environ.get("GH_TOKEN")
    os.environ["GH_TOKEN"] = "process-token"
    try:
        token, source = module._discover_github_token(root, env_file=str(tmp_path / ".env"))
    finally:
        if old is None:
            os.environ.pop("GH_TOKEN", None)
        else:
            os.environ["GH_TOKEN"] = old
    assert token == "process-token"
    assert source == "process_env:GH_TOKEN"


def test_discover_github_token_from_dotenv(tmp_path):
    module = _load_module()
    env_path = tmp_path / ".env"
    env_path.write_text("GITHUB_PAT=pat-token\n", encoding="utf-8")
    token, source = module._discover_github_token(Path("/"), env_file=str(env_path))
    assert token == "pat-token"
    assert "dotenv:" in source


def test_verify_subject_retries_then_passes():
    module = _load_module()
    calls = {"count": 0}

    def fake_run(cmd, capture_output, text):
        _ = capture_output, text
        calls["count"] += 1
        if calls["count"] == 1:
            return subprocess.CompletedProcess(cmd, returncode=1, stdout="", stderr="retry")
        return subprocess.CompletedProcess(cmd, returncode=0, stdout='[{"ok":true}]', stderr="")

    result = module._verify_subject(
        subject="/tmp/file.bin",
        repository="owner/repo",
        signer_workflow="owner/repo/.github/workflows/build.yml",
        predicate_type="https://slsa.dev/provenance/v1",
        bundle_path=None,
        retries=3,
        retry_delay=0.0,
        run_fn=fake_run,
        sleep_fn=lambda _seconds: None,
    )

    assert result.passed is True
    assert result.attempts == 2
    assert calls["count"] == 2


def test_verify_subject_fails_after_max_attempts():
    module = _load_module()

    def fake_run(cmd, capture_output, text):
        _ = capture_output, text
        return subprocess.CompletedProcess(cmd, returncode=2, stdout="", stderr="no attest")

    result = module._verify_subject(
        subject="/tmp/file.bin",
        repository="owner/repo",
        signer_workflow="owner/repo/.github/workflows/build.yml",
        predicate_type="https://slsa.dev/provenance/v1",
        bundle_path=None,
        retries=2,
        retry_delay=0.0,
        run_fn=fake_run,
        sleep_fn=lambda _seconds: None,
    )

    assert result.passed is False
    assert result.attempts == 2
    assert result.return_code == 2
