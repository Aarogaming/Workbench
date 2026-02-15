#!/usr/bin/env python3
"""Smoke test MCP connectivity/auth configuration."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def _load_mcp_auth_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "plugins" / "mcp_auth.py"
    module_name = "workbench_mcp_auth"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module spec: {path}")
    module = importlib.util.module_from_spec(spec)
    original = sys.modules.get(module_name)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
        return module
    finally:
        if original is None:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = original


def main() -> int:
    parser = argparse.ArgumentParser(description="Run MCP smoke checks from env configuration.")
    parser.add_argument(
        "--allow-unverified",
        action="store_true",
        help="Allow connectivity-only auth pass when verification endpoint is unavailable.",
    )
    parser.add_argument(
        "--require-configured",
        action="store_true",
        help="Fail if MCP_SERVER_URL/auth credentials are not configured.",
    )
    args = parser.parse_args()

    module = _load_mcp_auth_module()
    manager = module.MCPAuthManager.from_env()
    cfg = manager.config

    configured = bool(cfg.server_url and (cfg.auth_token or cfg.api_key))
    if not configured and not args.require_configured:
        print(
            json.dumps(
                {
                    "skipped": True,
                    "reason": "MCP auth/server env vars are not configured",
                    "required_env": [
                        "MCP_SERVER_URL",
                        "MCP_AUTH_TOKEN or MCP_API_KEY",
                    ],
                },
                indent=2,
            )
        )
        return 0

    ping = manager.test_ping()
    auth = manager.authenticate(require_verified=not args.allow_unverified)
    payload = {
        "configured": configured,
        "allow_unverified": bool(args.allow_unverified),
        "ping": ping,
        "auth": auth,
        "status": manager.get_status(),
    }
    print(json.dumps(payload, indent=2))
    return 0 if auth.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
