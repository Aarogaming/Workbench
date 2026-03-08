from __future__ import annotations

import http.client
import importlib.util
import json
import threading
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "merlin_mock_capabilities_server.py"
    spec = importlib.util.spec_from_file_location("merlin_mock_capabilities_server", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_capabilities_payload_contains_required_operations() -> None:
    module = _load_module()
    payload = module.build_capabilities_payload()
    operations = {entry["name"] for entry in payload["capabilities"]}

    assert payload["schema_name"] == "AAS.RepoCapabilityManifest"
    assert payload["endpoint"] == "/merlin/operations"
    assert "merlin.research.manager.session.create" in operations
    assert "merlin.research.manager.session.get" in operations
    assert "merlin.research.manager.brief.get" in operations


def test_handler_enforces_api_key_and_returns_manifest() -> None:
    module = _load_module()
    payload = module.build_capabilities_payload()
    server = module.HTTPServer(
        ("127.0.0.1", 0),
        module.make_handler(payload, api_key="merlin-secret-key"),
    )
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        denied = http.client.HTTPConnection(host, port, timeout=3)
        denied.request(
            "GET",
            "/merlin/operations/capabilities",
            headers={"X-Merlin-Key": "wrong-key"},
        )
        denied_resp = denied.getresponse()
        denied_resp.read()
        denied.close()

        allowed = http.client.HTTPConnection(host, port, timeout=3)
        allowed.request(
            "GET",
            "/merlin/operations/capabilities",
            headers={"X-Merlin-Key": "merlin-secret-key"},
        )
        allowed_resp = allowed.getresponse()
        body = allowed_resp.read()
        allowed.close()
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()

    assert denied_resp.status == 403
    assert allowed_resp.status == 200
    decoded = json.loads(body.decode("utf-8"))
    assert decoded["schema_version"] == "1.0.0"
    assert decoded["service"] == "merlin_api_server_mock"
