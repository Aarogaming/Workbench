#!/usr/bin/env python3
"""Local mock server for Merlin capabilities endpoint used in CP6 verification."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any


MOCK_OPERATIONS = (
    "merlin.research.manager.session.create",
    "merlin.research.manager.session.get",
    "merlin.research.manager.session.signal.add",
    "merlin.research.manager.sessions.list",
    "merlin.research.manager.brief.get",
)


def build_capabilities_payload() -> dict[str, Any]:
    return {
        "schema_name": "AAS.RepoCapabilityManifest",
        "schema_version": "1.0.0",
        "repo": "AaroneousAutomationSuite/Merlin",
        "service": "merlin_api_server_mock",
        "endpoint": "/merlin/operations",
        "capabilities": [
            {
                "name": operation,
                "version": "1.0.0",
                "stability": "stable",
            }
            for operation in MOCK_OPERATIONS
        ],
    }


def make_handler(payload: dict[str, Any], api_key: str) -> type[BaseHTTPRequestHandler]:
    payload_bytes = json.dumps(payload).encode("utf-8")

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path != "/merlin/operations/capabilities":
                self.send_response(404)
                self.end_headers()
                return
            if self.headers.get("X-Merlin-Key") != api_key:
                self.send_response(403)
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload_bytes)))
            self.end_headers()
            self.wfile.write(payload_bytes)

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            return

    return Handler


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Serve local Merlin capabilities for Workbench CP6 verification."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--api-key", default="merlin-secret-key")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Handle exactly one request then exit.",
    )
    args = parser.parse_args()

    server = HTTPServer(
        (args.host, args.port),
        make_handler(build_capabilities_payload(), args.api_key),
    )
    print(
        f"mock_merlin_capabilities_server: listening on {args.host}:{args.port}",
        flush=True,
    )
    try:
        if args.once:
            server.handle_request()
        else:
            server.serve_forever()
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
