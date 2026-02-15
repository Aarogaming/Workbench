from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "check_secret_hygiene.py"
    spec = importlib.util.spec_from_file_location("check_secret_hygiene_script", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get("check_secret_hygiene_script")
    sys.modules["check_secret_hygiene_script"] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop("check_secret_hygiene_script", None)
        else:
            sys.modules["check_secret_hygiene_script"] = original


def test_strict_mode_fails_closed_on_git_error(monkeypatch):
    module = _load_module()
    monkeypatch.setattr(module, "_candidate_paths", lambda include_all: (_ for _ in ()).throw(RuntimeError("git unavailable")))
    monkeypatch.setattr(sys, "argv", ["check_secret_hygiene.py", "--all", "--strict"])
    assert module.main() == 2


def test_non_strict_mode_allows_git_error(monkeypatch):
    module = _load_module()
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.delenv("SECRET_HYGIENE_STRICT", raising=False)
    monkeypatch.setattr(module, "_candidate_paths", lambda include_all: (_ for _ in ()).throw(RuntimeError("git unavailable")))
    monkeypatch.setattr(sys, "argv", ["check_secret_hygiene.py", "--all"])
    assert module.main() == 0


def test_detects_blocked_file(monkeypatch):
    module = _load_module()
    monkeypatch.setattr(module, "_candidate_paths", lambda include_all: ["secrets/id_rsa", "safe/file.txt"])
    monkeypatch.setattr(sys, "argv", ["check_secret_hygiene.py", "--all"])
    assert module.main() == 2
