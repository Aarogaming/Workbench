from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "record_campaign_outcome.py"
    spec = importlib.util.spec_from_file_location(
        "record_campaign_outcome_script",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("record_campaign_outcome_script")
    sys.modules["record_campaign_outcome_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("record_campaign_outcome_script", None)
        else:
            sys.modules["record_campaign_outcome_script"] = original


def test_record_campaign_outcome_writes_json_and_markdown():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        argv = [
            "record_campaign_outcome.py",
            "--campaign-id",
            "WB-CAMPAIGN-001",
            "--owner-lane",
            "A0",
            "--terminal-outcome",
            "complete",
            "--summary",
            "all checks passed",
            "--json-out",
            "outcome.json",
            "--md-out",
            "outcome.md",
        ]

        old_cwd = Path.cwd()
        old_argv = sys.argv[:]
        try:
            os.chdir(root)
            sys.argv = argv
            rc = module.main()
            assert rc == 0
        finally:
            sys.argv = old_argv
            os.chdir(old_cwd)

        payload = json.loads((root / "outcome.json").read_text(encoding="utf-8"))
        assert payload["terminal_outcome"] == "complete"
        assert payload["campaign"]["id"] == "WB-CAMPAIGN-001"
        assert (root / "outcome.md").exists()


def test_record_campaign_outcome_requires_unblock_inputs_for_hard_block():
    module = _load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        argv = [
            "record_campaign_outcome.py",
            "--campaign-id",
            "WB-CAMPAIGN-002",
            "--owner-lane",
            "A0",
            "--terminal-outcome",
            "hard_block",
            "--summary",
            "blocked",
            "--json-out",
            "outcome.json",
            "--md-out",
            "outcome.md",
        ]

        old_cwd = Path.cwd()
        old_argv = sys.argv[:]
        try:
            os.chdir(root)
            sys.argv = argv
            try:
                module.main()
                assert False, "expected SystemExit"
            except SystemExit as exc:
                assert "requires at least one" in str(exc)
        finally:
            sys.argv = old_argv
            os.chdir(old_cwd)
