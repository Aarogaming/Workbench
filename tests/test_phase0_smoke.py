from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path


def _load_module(
    relative_path: str,
    module_name: str,
    stubs: dict[str, object] | None = None,
):
    root = Path(__file__).resolve().parents[1]
    module_path = root / relative_path
    assert module_path.exists(), f"Missing module path: {module_path}"

    original_modules: list[tuple[str, object | None]] = []
    if stubs:
        for name, stub in stubs.items():
            original_modules.append((name, sys.modules.get(name)))
            sys.modules[name] = stub

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    original_module = sys.modules.get(module_name)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original_module is None:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = original_module
        for name, original in original_modules:
            if original is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = original


def _repo_size_guard_stubs() -> dict[str, object]:
    core_module = types.ModuleType("core")
    plugin_manifest_module = types.ModuleType("core.plugin_manifest")

    def get_hive_metadata(manifest):
        extensions = manifest.get("extensions", {}) if isinstance(manifest, dict) else {}
        return extensions.get("aas", {}) if isinstance(extensions, dict) else {}

    plugin_manifest_module.get_hive_metadata = get_hive_metadata
    core_module.plugin_manifest = plugin_manifest_module

    loguru_module = types.ModuleType("loguru")

    class _Logger:
        def warning(self, *_args, **_kwargs):
            return None

    loguru_module.logger = _Logger()
    return {
        "core": core_module,
        "core.plugin_manifest": plugin_manifest_module,
        "loguru": loguru_module,
    }


def test_workflow_engine_executes_registered_steps():
    module = _load_module("plugins/workflow_engine.py", "phase0_workflow_engine")
    workflow = module.WorkflowDefinition("wf-smoke", "workflow smoke")
    workflow.add_step(module.WorkflowStep(step_id="s1", action="inc", inputs={"value": 1}))
    workflow.add_step(module.WorkflowStep(step_id="s2", action="inc", inputs={"value": 2}))

    executor = module.WorkflowExecutor()

    def _handler(inputs, results):
        return int(inputs.get("value", 0)) + len(results)

    executor.register_handler("inc", _handler)
    result = executor.execute(workflow)

    assert result["success"] is True
    assert result["results"]["s1"] == 1
    assert result["results"]["s2"] == 3
    assert executor.get_status()["status"] == "completed"


def test_workflow_scheduler_runs_scheduled_entry():
    module = _load_module("plugins/workflow_engine.py", "phase0_workflow_engine_sched")
    workflow = module.WorkflowDefinition("wf-sched", "scheduler smoke")
    workflow.add_step(module.WorkflowStep(step_id="s1", action="echo", inputs={"text": "ok"}))

    scheduler = module.WorkflowScheduler()
    scheduler.executor.register_handler("echo", lambda inputs, _results: inputs["text"])
    schedule_id = scheduler.schedule(workflow, trigger="manual", delay=0.0)
    result = scheduler.run_scheduled(schedule_id)

    assert result["success"] is True
    assert result["result"]["results"]["s1"] == "ok"
    assert scheduler.scheduled[schedule_id]["executed"] is True


def test_workflow_resume_continues_from_cursor_without_replaying_steps():
    module = _load_module("plugins/workflow_engine.py", "phase1_workflow_resume")
    workflow = module.WorkflowDefinition("wf-resume", "resume behavior")
    workflow.add_step(module.WorkflowStep(step_id="s1", action="first"))
    workflow.add_step(module.WorkflowStep(step_id="s2", action="second"))

    calls = {"first": 0, "second": 0}
    executor = module.WorkflowExecutor()

    def first_handler(_inputs, _results):
        calls["first"] += 1
        executor.pause()
        return "first-ok"

    def second_handler(_inputs, _results):
        calls["second"] += 1
        return "second-ok"

    executor.register_handler("first", first_handler)
    executor.register_handler("second", second_handler)

    paused = executor.execute(workflow)
    assert paused["success"] is False
    assert paused["status"] == "paused"
    assert executor.get_status()["current_step_index"] == 1
    assert calls["first"] == 1
    assert calls["second"] == 0

    resumed = executor.resume()
    assert resumed["success"] is True
    assert resumed["status"] == "completed"
    assert resumed["results"]["s1"] == "first-ok"
    assert resumed["results"]["s2"] == "second-ok"
    assert calls["first"] == 1
    assert calls["second"] == 1


def test_workflow_scheduler_rejects_early_execution_by_delay():
    module = _load_module("plugins/workflow_engine.py", "phase1_workflow_sched_delay")
    workflow = module.WorkflowDefinition("wf-delay", "delay behavior")
    workflow.add_step(module.WorkflowStep(step_id="s1", action="noop"))

    scheduler = module.WorkflowScheduler()
    scheduler.executor.register_handler("noop", lambda _inputs, _results: "ok")
    schedule_id = scheduler.schedule(workflow, trigger="delayed", delay=10.0)
    created_at = scheduler.scheduled[schedule_id]["created_at"]

    early = scheduler.run_scheduled(schedule_id, now=created_at + 5.0)
    assert early["success"] is False
    assert early["error_code"] == "schedule_not_ready"

    ready = scheduler.run_scheduled(schedule_id, now=created_at + 10.1)
    assert ready["success"] is True
    assert ready["result"]["results"]["s1"] == "ok"


def test_mcp_auth_validate_credentials_reports_missing_fields():
    module = _load_module("plugins/mcp_auth.py", "phase0_mcp_auth_validate")
    config = module.MCPAuthConfig(auth_token="", api_key="", server_url="")
    manager = module.MCPAuthManager(config)

    result = manager.validate_credentials()
    assert result["valid"] is False
    assert "AUTH_TOKEN or API_KEY not set" in result["issues"]
    assert "SERVER_URL not set" in result["issues"]


def test_mcp_auth_ping_success_sets_authenticated_state():
    module = _load_module("plugins/mcp_auth.py", "phase0_mcp_auth_ping")

    class _Response:
        def __init__(self, status_code, payload=None):
            self.status_code = status_code
            self._payload = payload or {}

        def json(self):
            return self._payload

    class _Requests:
        def __init__(self):
            self.calls = []

        def get(self, url, timeout, headers):
            self.calls.append({"url": url, "timeout": timeout, "headers": headers})
            if url.endswith("/auth/verify"):
                return _Response(
                    200,
                    payload={
                        "token_valid": True,
                        "session_id": "sess-123",
                        "permissions": ["read", "execute"],
                    },
                )
            return _Response(200)

    fake_requests = _Requests()
    module.requests = fake_requests

    config = module.MCPAuthConfig(
        auth_token="x" * 24,
        api_key="",
        server_url="https://example.com",
        timeout=5,
    )
    manager = module.MCPAuthManager(config)
    result = manager.test_ping()

    assert result["success"] is True
    assert result["http_status"] == 200
    assert manager.authenticated is False
    assert fake_requests.calls
    assert fake_requests.calls[0]["url"] == "https://example.com/health"
    assert "Authorization" in fake_requests.calls[0]["headers"]

    auth_result = manager.authenticate()
    assert auth_result["success"] is True
    assert auth_result["verified"] is True
    assert auth_result["session_id"] == "sess-123"
    assert manager.authenticated is True
    assert manager.permissions == ["read", "execute"]


def test_mcp_auth_ping_fails_when_requests_unavailable():
    module = _load_module("plugins/mcp_auth.py", "phase0_mcp_auth_no_requests")
    module.requests = None

    config = module.MCPAuthConfig(
        auth_token="x" * 24,
        api_key="",
        server_url="https://example.com",
        timeout=5,
    )
    manager = module.MCPAuthManager(config)
    result = manager.test_ping()

    assert result["success"] is False
    assert result["error_code"] == "requests_missing"


def test_mcp_auth_strict_mode_requires_verification_contract():
    module = _load_module("plugins/mcp_auth.py", "phase1_mcp_auth_strict")

    class _Response:
        def __init__(self, status_code):
            self.status_code = status_code

        def json(self):
            return {}

    class _Requests:
        def get(self, _url, timeout, headers):
            _ = timeout, headers
            return _Response(200)

    module.requests = _Requests()
    config = module.MCPAuthConfig(
        auth_token="x" * 24,
        api_key="",
        server_url="https://example.com",
        timeout=5,
        require_verified=True,
    )
    manager = module.MCPAuthManager(config)
    result = manager.authenticate()

    assert result["success"] is False
    assert result["error_code"] == "verification_unavailable"
    assert manager.authenticated is False


def test_repo_size_guard_detects_oversized_file(tmp_path: Path):
    module = _load_module(
        "plugins/repo_size_guard/plugin.py",
        "phase0_repo_size_guard",
        stubs=_repo_size_guard_stubs(),
    )
    plugin = module.Plugin(manifest={})

    (tmp_path / "small.txt").write_text("ok", encoding="utf-8")
    (tmp_path / "big.bin").write_bytes(b"x" * (2 * 1024 * 1024))

    result = plugin.check_repo_size(root=str(tmp_path), max_mb=1)
    assert result["ok"] is False
    assert result["oversized_count"] == 1
    assert result["oversized"][0]["path"] == "big.bin"


def test_repo_size_guard_exposes_expected_command():
    module = _load_module(
        "plugins/repo_size_guard/plugin.py",
        "phase0_repo_size_guard_commands",
        stubs=_repo_size_guard_stubs(),
    )
    plugin = module.Plugin(manifest={})
    commands = plugin.commands()

    assert "workbench.repo.check_size" in commands
    assert callable(commands["workbench.repo.check_size"])
