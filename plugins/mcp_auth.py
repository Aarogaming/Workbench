#!/usr/bin/env python3
"""AAS-805: MCP auth token and API key configuration."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None


class MCPAuthErrorCode:
    INVALID_CREDENTIALS = "invalid_credentials"
    REQUESTS_MISSING = "requests_missing"
    SERVER_UNREACHABLE = "server_unreachable"
    AUTH_REJECTED = "auth_rejected"
    VERIFICATION_UNAVAILABLE = "verification_unavailable"
    VERIFICATION_INVALID = "verification_invalid"


@dataclass
class MCPAuthConfig:
    """MCP authentication configuration."""

    auth_token: str = ""
    api_key: str = ""
    server_url: str = ""
    timeout: int = 30
    require_verified: bool = True
    ping_paths: Tuple[str, ...] = ("/health", "/")
    verify_paths: Tuple[str, ...] = ("/auth/verify", "/v1/auth/verify")

    @classmethod
    def from_env(cls) -> "MCPAuthConfig":
        server_url = (
            os.getenv("carto_ai_MCP_SERVER_URL")
            or os.getenv("CARTO_AI_MCP_SERVER_URL")
            or os.getenv("MCP_SERVER_URL")
            or ""
        ).rstrip("/")
        require_verified = str(
            os.getenv("MCP_AUTH_REQUIRE_VERIFIED", "true")
        ).strip().lower() in {"1", "true", "yes", "on"}
        return cls(
            auth_token=os.getenv("MCP_AUTH_TOKEN")
            or os.getenv("CARTO_AI_MCP_TOKEN")
            or "",
            api_key=os.getenv("MCP_API_KEY") or os.getenv("CARTO_AI_MCP_API_KEY") or "",
            server_url=server_url,
            require_verified=require_verified,
        )


class MCPAuthManager:
    """Manages MCP authentication."""

    def __init__(self, config: MCPAuthConfig):
        self.config = config
        self.authenticated = False
        self.session_id: Optional[str] = None
        self.permissions: list[str] = []
        self.last_ping: Dict[str, Any] = {}
        self.last_auth_result: Dict[str, Any] = {}

    @classmethod
    def from_env(cls) -> "MCPAuthManager":
        return cls(MCPAuthConfig.from_env())

    def validate_credentials(self) -> Dict[str, Any]:
        issues = []

        if not (self.config.auth_token or self.config.api_key):
            issues.append("AUTH_TOKEN or API_KEY not set")
        elif self.config.auth_token and len(self.config.auth_token) < 20:
            issues.append("AUTH_TOKEN too short")
        elif self.config.api_key and len(self.config.api_key) < 16:
            issues.append("API_KEY too short")

        if not self.config.server_url:
            issues.append("SERVER_URL not set")

        return {"valid": len(issues) == 0, "issues": issues}

    def _auth_headers(self) -> Dict[str, str]:
        if self.config.auth_token:
            return {"Authorization": f"Bearer {self.config.auth_token}"}
        if self.config.api_key:
            return {"X-API-Key": self.config.api_key}
        return {}

    def _auth_mode(self) -> str:
        if self.config.auth_token:
            return "bearer"
        if self.config.api_key:
            return "api_key"
        return "none"

    def _build_url(self, path: str) -> str:
        if not path:
            return self.config.server_url
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.config.server_url}{path}"

    def _request_get(self, url: str) -> tuple[Optional[Any], float, str]:
        if requests is None:
            return None, 0.0, "requests missing"
        start = time.perf_counter()
        try:
            response = requests.get(
                url,
                timeout=self.config.timeout,
                headers=self._auth_headers(),
            )
            latency = (time.perf_counter() - start) * 1000.0
            return response, latency, ""
        except Exception as exc:
            latency = (time.perf_counter() - start) * 1000.0
            return None, latency, str(exc)

    def _response_json(self, response: Any) -> Dict[str, Any]:
        try:
            payload = response.json()
        except Exception:
            return {}
        return payload if isinstance(payload, dict) else {}

    def _extract_verification(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        token_valid = payload.get("token_valid")
        if token_valid is None:
            token_valid = payload.get("valid")
        if isinstance(token_valid, str):
            token_valid = token_valid.strip().lower() in {"1", "true", "yes", "on"}
        elif not isinstance(token_valid, bool):
            token_valid = None

        session_id = payload.get("session_id") or payload.get("session")
        if session_id is not None:
            session_id = str(session_id)

        raw_perms = payload.get("permissions")
        if raw_perms is None:
            raw_perms = payload.get("scopes")
        permissions: list[str] = []
        if isinstance(raw_perms, list):
            permissions = [str(item) for item in raw_perms]
        elif isinstance(raw_perms, str) and raw_perms.strip():
            permissions = [part.strip() for part in raw_perms.split(",") if part.strip()]

        expires_at = payload.get("expires_at")
        if expires_at is not None:
            expires_at = str(expires_at)

        return {
            "token_valid": token_valid,
            "session_id": session_id,
            "permissions": permissions,
            "expires_at": expires_at,
            "raw": payload,
        }

    def _error(self, code: str, message: str, **extra: Any) -> Dict[str, Any]:
        result = {"success": False, "error_code": code, "error": message}
        result.update(extra)
        return result

    def test_ping(self) -> Dict[str, Any]:
        """Test connectivity with measured latency."""
        credentials = self.validate_credentials()
        if not credentials["valid"]:
            return self._error(
                MCPAuthErrorCode.INVALID_CREDENTIALS,
                "Invalid credentials",
                ping="failed",
                issues=credentials["issues"],
            )
        if requests is None:
            return self._error(
                MCPAuthErrorCode.REQUESTS_MISSING,
                "requests missing",
                ping="failed",
            )

        last_error = "Unknown error"
        for path in self.config.ping_paths:
            url = self._build_url(path)
            response, latency_ms, error = self._request_get(url)
            if response is None:
                last_error = error or last_error
                continue
            if response.status_code < 400:
                result = {
                    "success": True,
                    "ping": "ok",
                    "server": url,
                    "http_status": int(response.status_code),
                    "latency_ms": round(float(latency_ms), 2),
                    "auth_mode": self._auth_mode(),
                }
                self.last_ping = result
                return result
            last_error = f"HTTP {response.status_code}"

        return self._error(
            MCPAuthErrorCode.SERVER_UNREACHABLE,
            last_error,
            ping="failed",
            server=self.config.server_url,
            auth_mode=self._auth_mode(),
        )

    def authenticate(self, require_verified: Optional[bool] = None) -> Dict[str, Any]:
        """Authenticate with MCP server using explicit verification contracts."""
        strict_verify = (
            self.config.require_verified if require_verified is None else bool(require_verified)
        )

        credentials = self.validate_credentials()
        if not credentials["valid"]:
            result = self._error(
                MCPAuthErrorCode.INVALID_CREDENTIALS,
                "Invalid credentials",
                issues=credentials["issues"],
                authenticated=False,
                verified=False,
            )
            self.last_auth_result = result
            return result
        if requests is None:
            result = self._error(
                MCPAuthErrorCode.REQUESTS_MISSING,
                "requests missing",
                authenticated=False,
                verified=False,
            )
            self.last_auth_result = result
            return result

        verification_errors: list[str] = []
        for path in self.config.verify_paths:
            url = self._build_url(path)
            response, latency_ms, error = self._request_get(url)
            if response is None:
                verification_errors.append(error or "request failed")
                continue

            status_code = int(response.status_code)
            if status_code in {401, 403}:
                result = self._error(
                    MCPAuthErrorCode.AUTH_REJECTED,
                    f"HTTP {status_code}",
                    authenticated=False,
                    verified=False,
                    server=url,
                    http_status=status_code,
                    latency_ms=round(float(latency_ms), 2),
                )
                self.last_auth_result = result
                self.authenticated = False
                self.session_id = None
                self.permissions = []
                return result

            if status_code >= 400:
                verification_errors.append(f"{url}: HTTP {status_code}")
                continue

            payload = self._response_json(response)
            parsed = self._extract_verification(payload)
            token_valid = parsed["token_valid"]
            if token_valid is False:
                result = self._error(
                    MCPAuthErrorCode.AUTH_REJECTED,
                    "Token rejected by verification endpoint",
                    authenticated=False,
                    verified=False,
                    server=url,
                    http_status=status_code,
                    latency_ms=round(float(latency_ms), 2),
                )
                self.last_auth_result = result
                self.authenticated = False
                self.session_id = None
                self.permissions = []
                return result

            if token_valid is True:
                self.authenticated = True
                self.session_id = parsed["session_id"]
                self.permissions = parsed["permissions"]
                result = {
                    "success": True,
                    "authenticated": True,
                    "verified": True,
                    "server": url,
                    "http_status": status_code,
                    "latency_ms": round(float(latency_ms), 2),
                    "session_id": self.session_id,
                    "permissions": list(self.permissions),
                    "expires_at": parsed["expires_at"],
                    "auth_mode": self._auth_mode(),
                }
                self.last_auth_result = result
                return result

            verification_errors.append(f"{url}: verification payload missing token_valid")

        ping_result = self.test_ping()
        if not ping_result.get("success"):
            result = self._error(
                MCPAuthErrorCode.SERVER_UNREACHABLE,
                "Ping failed after verification attempts",
                authenticated=False,
                verified=False,
                verification_errors=verification_errors,
                ping_result=ping_result,
            )
            self.last_auth_result = result
            self.authenticated = False
            self.session_id = None
            self.permissions = []
            return result

        if strict_verify:
            result = self._error(
                MCPAuthErrorCode.VERIFICATION_UNAVAILABLE,
                "Connectivity succeeded but verification contract is unavailable",
                authenticated=False,
                verified=False,
                verification_errors=verification_errors,
                ping_result=ping_result,
                auth_mode=self._auth_mode(),
            )
            self.last_auth_result = result
            self.authenticated = False
            self.session_id = None
            self.permissions = []
            return result

        self.authenticated = True
        self.session_id = None
        self.permissions = []
        result = {
            "success": True,
            "authenticated": True,
            "verified": False,
            "server": ping_result.get("server"),
            "http_status": ping_result.get("http_status"),
            "latency_ms": ping_result.get("latency_ms"),
            "session_id": None,
            "permissions": [],
            "auth_mode": self._auth_mode(),
            "verification_errors": verification_errors,
        }
        self.last_auth_result = result
        return result

    def get_status(self) -> Dict[str, Any]:
        return {
            "authenticated": self.authenticated,
            "session_id": self.session_id,
            "server_url": self.config.server_url,
            "timeout": self.config.timeout,
            "credentials_valid": self.validate_credentials()["valid"],
            "require_verified": self.config.require_verified,
            "permissions": list(self.permissions),
            "last_ping": dict(self.last_ping),
            "last_auth_result": dict(self.last_auth_result),
        }

    def logout(self) -> bool:
        self.authenticated = False
        self.session_id = None
        self.permissions = []
        return True
