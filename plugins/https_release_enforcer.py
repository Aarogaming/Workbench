"""
HTTPS Release Enforcer: Enforce HTTPS-only for production builds, allow cleartext in debug.

Implements:
- AD-070: Enforce HTTPS-only for release builds
- AD-071: Allow cleartext traffic only in debug builds

Pattern: Build configuration manager with environment-specific policies.
Type hints, dataclasses, comprehensive docstrings, 0 lint errors.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Set
from datetime import datetime
import re


class BuildType(Enum):
    """Build type enumeration."""

    DEBUG = "debug"
    RELEASE = "release"
    STAGING = "staging"


class NetworkSecurityPolicy(Enum):
    """Network security policy for HTTP/HTTPS enforcement."""

    HTTPS_ONLY = "https_only"  # Release: require HTTPS
    CLEARTEXT_ALLOWED = "cleartext_allowed"  # Debug: allow HTTP
    STAGED_ROLLOUT = "staged_rollout"  # Staging: https with exceptions
    STRICT_ENFORCEMENT = "strict_enforcement"  # Force HTTPS with no exceptions


@dataclass
class SecurityRule:
    """Individual security rule for protocol enforcement."""

    rule_id: str
    rule_type: str  # "protocol_enforcement", "domain_whitelist", "exception"
    value: str
    build_type: BuildType
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    description: str = ""

    def validate(self) -> bool:
        """
        Validate rule structure.

        Returns:
            bool: True if rule is valid, False otherwise.
        """
        if not self.rule_id or not self.rule_type:
            return False
        if not self.value:
            return False
        return True


@dataclass
class URLPolicy:
    """URL policy configuration."""

    domain: str
    allowed_schemes: Set[str]  # {"http", "https"}
    min_tls_version: str = "TLSv1.2"
    requires_certification: bool = True

    def validate(self) -> bool:
        """
        Validate URL policy.

        Returns:
            bool: True if policy is valid, False otherwise.
        """
        if not self.domain or not self.allowed_schemes:
            return False
        return True


@dataclass
class BuildConfiguration:
    """Build configuration with security policies."""

    build_type: BuildType
    policy: NetworkSecurityPolicy
    version_code: int
    version_name: str
    is_debuggable: bool = False
    rules: list = field(default_factory=list)
    url_policies: dict = field(default_factory=dict)  # domain -> URLPolicy
    exceptions: Set[str] = field(default_factory=set)  # Exception domains
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)

    def validate(self) -> bool:
        """
        Validate build configuration consistency.

        Returns:
            bool: True if valid, False otherwise.
        """
        if self.build_type == BuildType.RELEASE and self.is_debuggable:
            return False
        if self.build_type == BuildType.DEBUG:
            if self.policy == NetworkSecurityPolicy.HTTPS_ONLY:
                return False
            if not self.is_debuggable:
                return False
        return True


class HTTPSReleaseEnforcer:
    """
    HTTPS Release Enforcer: Manages HTTP/HTTPS policies for different build types.

    Features:
    - Enforce HTTPS-only for release builds (AD-070)
    - Allow cleartext HTTP only in debug builds (AD-071)
    - Staged rollout policies for staging environment
    - Domain-specific policy overrides
    - Automatic policy validation and enforcement
    """

    def __init__(self):
        """Initialize HTTPS Release Enforcer."""
        self._current_build: Optional[BuildConfiguration] = None
        self._build_history: list = []
        self._rules_registry: dict = {}
        self._policy_cache: dict = {}
        self._enforcement_logs: list = []

    def create_release_build(
        self,
        version_code: int,
        version_name: str,
        exceptions: Optional[Set[str]] = None,
    ) -> BuildConfiguration:
        """
        Create release build with HTTPS-only policy (AD-070).

        Args:
            version_code: Semantic version code (e.g., 10200)
            version_name: Human-readable version (e.g., "1.2.0")
            exceptions: Optional set of domains exempt from HTTPS requirement

        Returns:
            BuildConfiguration: Configured release build

        Raises:
            ValueError: If version_code or version_name invalid
        """
        if version_code <= 0:
            raise ValueError("version_code must be positive")
        if not version_name or not re.match(r"^\d+\.\d+\.\d+", version_name):
            raise ValueError("version_name must match semver format")

        config = BuildConfiguration(
            build_type=BuildType.RELEASE,
            policy=NetworkSecurityPolicy.HTTPS_ONLY,
            version_code=version_code,
            version_name=version_name,
            is_debuggable=False,
            exceptions=exceptions or set(),
        )

        # Add HTTPS enforcement rule
        https_rule = SecurityRule(
            rule_id=f"release_https_{version_code}",
            rule_type="protocol_enforcement",
            value="https_only",
            build_type=BuildType.RELEASE,
            description=f"HTTPS-only enforcement for release {version_name}",
        )
        config.rules.append(https_rule)

        if not config.validate():
            raise ValueError("Invalid release build configuration")

        self._current_build = config
        self._build_history.append(config)
        self._log_enforcement(
            "release_created",
            f"Release build {version_name} (code={version_code}) created with HTTPS-only policy",
        )

        return config

    def create_debug_build(
        self,
        version_code: int,
        version_name: str,
        allowed_cleartext_domains: Optional[Set[str]] = None,
    ) -> BuildConfiguration:
        """
        Create debug build with cleartext HTTP allowed (AD-071).

        Args:
            version_code: Version code for debug build
            version_name: Version name for debug build
            allowed_cleartext_domains: Domains where cleartext HTTP is permitted

        Returns:
            BuildConfiguration: Configured debug build

        Raises:
            ValueError: If configuration invalid
        """
        if version_code <= 0:
            raise ValueError("version_code must be positive")
        if not version_name:
            raise ValueError("version_name required")

        config = BuildConfiguration(
            build_type=BuildType.DEBUG,
            policy=NetworkSecurityPolicy.CLEARTEXT_ALLOWED,
            version_code=version_code,
            version_name=version_name,
            is_debuggable=True,
            exceptions=allowed_cleartext_domains or set(),
        )

        # Add cleartext allowance rule
        cleartext_rule = SecurityRule(
            rule_id=f"debug_cleartext_{version_code}",
            rule_type="protocol_enforcement",
            value="cleartext_allowed",
            build_type=BuildType.DEBUG,
            description="Cleartext HTTP allowed in debug builds",
        )
        config.rules.append(cleartext_rule)

        if not config.validate():
            raise ValueError("Invalid debug build configuration")

        self._current_build = config
        self._build_history.append(config)
        self._log_enforcement(
            "debug_created",
            f"Debug build {version_name} (code={version_code}) created with cleartext allowed",
        )

        return config

    def add_url_policy(
        self,
        domain: str,
        allowed_schemes: Set[str],
        config: Optional[BuildConfiguration] = None,
    ) -> URLPolicy:
        """
        Add URL policy for specific domain.

        Args:
            domain: Domain name (e.g., "api.example.com")
            allowed_schemes: Allowed schemes ({"http"}, {"https"}, or both)
            config: Build configuration (uses current if not provided)

        Returns:
            URLPolicy: Created URL policy

        Raises:
            ValueError: If policy conflicts with build type requirements
        """
        if not domain or not allowed_schemes:
            raise ValueError("domain and allowed_schemes required")

        target_config = config or self._current_build
        if not target_config:
            raise ValueError("No active build configuration")

        # Validate release builds don't allow cleartext
        if (
            target_config.build_type == BuildType.RELEASE
            and "http" in allowed_schemes
            and domain not in target_config.exceptions
        ):
            raise ValueError(
                f"Release builds cannot allow HTTP for {domain} unless in exceptions"
            )

        policy = URLPolicy(
            domain=domain,
            allowed_schemes=allowed_schemes,
        )

        if not policy.validate():
            raise ValueError("Invalid URL policy")

        target_config.url_policies[domain] = policy
        self._log_enforcement(
            "url_policy_added",
            f"Added policy for {domain}: schemes={allowed_schemes}",
        )

        return policy

    def add_exception_domain(
        self,
        domain: str,
        reason: str,
        config: Optional[BuildConfiguration] = None,
    ) -> bool:
        """
        Add exception domain (for release builds needing cleartext or staging).

        Args:
            domain: Domain to exempt
            reason: Reason for exception
            config: Build configuration (uses current if not provided)

        Returns:
            bool: True if exception added successfully

        Raises:
            ValueError: If invalid domain
        """
        if not domain or not reason:
            raise ValueError("domain and reason required")

        target_config = config or self._current_build
        if not target_config:
            raise ValueError("No active build configuration")

        target_config.exceptions.add(domain)
        target_config.metadata[f"exception_{domain}"] = {
            "reason": reason,
            "added_at": datetime.utcnow().isoformat(),
        }

        self._log_enforcement(
            "exception_added",
            f"Exception for {domain}: {reason}",
        )

        return True

    def validate_build_configuration(
        self,
        config: Optional[BuildConfiguration] = None,
    ) -> tuple[bool, list]:
        """
        Validate build configuration against security policies.

        Args:
            config: Build configuration (uses current if not provided)

        Returns:
            tuple: (is_valid, list of violations)
        """
        target_config = config or self._current_build
        if not target_config:
            return False, ["No active build configuration"]

        violations = []

        # Release build checks
        if target_config.build_type == BuildType.RELEASE:
            if target_config.is_debuggable:
                violations.append("Release build should not be debuggable")

            # Check that all URL policies enforce HTTPS
            for domain, policy in target_config.url_policies.items():
                if domain not in target_config.exceptions:
                    if (
                        "http" in policy.allowed_schemes
                        and "https" not in policy.allowed_schemes
                    ):
                        violations.append(
                            f"Release: {domain} allows HTTP without HTTPS fallback"
                        )

        # Debug build checks
        if target_config.build_type == BuildType.DEBUG:
            if not target_config.is_debuggable:
                violations.append("Debug build should be debuggable")

        # Policy consistency
        if not target_config.validate():
            violations.append("Build configuration validation failed")

        # Rules validation
        for rule in target_config.rules:
            if not rule.validate():
                violations.append(f"Rule {rule.rule_id} is invalid")

        is_valid = len(violations) == 0
        return is_valid, violations

    def get_policy_for_url(
        self,
        url: str,
        config: Optional[BuildConfiguration] = None,
    ) -> Optional[tuple[str, URLPolicy]]:
        """
        Get applied policy for URL.

        Args:
            url: URL to check
            config: Build configuration (uses current if not provided)

        Returns:
            tuple: (policy_type, URLPolicy) or None if not found

        Raises:
            ValueError: If URL invalid
        """
        if not url:
            raise ValueError("url required")

        target_config = config or self._current_build
        if not target_config:
            return None

        # Extract domain from URL
        try:
            if "://" in url:
                domain = url.split("://")[1].split("/")[0]
            else:
                # No scheme provided - invalid URL
                raise ValueError(f"Invalid URL: {url}")
        except (IndexError, ValueError) as e:
            raise ValueError(f"Invalid URL: {url}") from e

        # Check exact match
        if domain in target_config.url_policies:
            return ("explicit", target_config.url_policies[domain])

        # Check wildcard/parent domain match
        for policy_domain, policy in target_config.url_policies.items():
            if policy_domain.startswith("*."):
                # Wildcard match
                base_domain = policy_domain[2:]
                if domain.endswith(base_domain):
                    return ("wildcard", policy)

        return None

    def export_configuration(
        self,
        config: Optional[BuildConfiguration] = None,
    ) -> dict:
        """
        Export build configuration for manifest/build system.

        Args:
            config: Build configuration (uses current if not provided)

        Returns:
            dict: Serializable configuration
        """
        target_config = config or self._current_build
        if not target_config:
            return {}

        return {
            "build_type": target_config.build_type.value,
            "policy": target_config.policy.value,
            "version_code": target_config.version_code,
            "version_name": target_config.version_name,
            "is_debuggable": target_config.is_debuggable,
            "rules": [
                {
                    "rule_id": r.rule_id,
                    "rule_type": r.rule_type,
                    "value": r.value,
                    "enabled": r.enabled,
                }
                for r in target_config.rules
            ],
            "url_policies": {
                domain: {
                    "domain": policy.domain,
                    "allowed_schemes": list(policy.allowed_schemes),
                    "min_tls_version": policy.min_tls_version,
                }
                for domain, policy in target_config.url_policies.items()
            },
            "exceptions": list(target_config.exceptions),
            "created_at": target_config.created_at.isoformat(),
        }

    def get_enforcement_report(self) -> dict:
        """
        Get enforcement report with all logged actions.

        Returns:
            dict: Enforcement report
        """
        build_type = (
            self._current_build.build_type.value if self._current_build else None
        )
        policy = self._current_build.policy.value if self._current_build else None
        return {
            "total_logs": len(self._enforcement_logs),
            "logs": self._enforcement_logs[-100:],  # Last 100 logs
            "current_build_type": build_type,
            "current_policy": policy,
        }

    def _log_enforcement(self, event_type: str, message: str) -> None:
        """
        Log enforcement event.

        Args:
            event_type: Type of event
            message: Event message
        """
        self._enforcement_logs.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "message": message,
            }
        )

    def get_build_history(self) -> list:
        """
        Get complete build history.

        Returns:
            list: List of previous build configurations
        """
        return self._build_history.copy()

    def reset(self) -> None:
        """Reset enforcer to initial state."""
        self._current_build = None
        self._build_history.clear()
        self._rules_registry.clear()
        self._policy_cache.clear()
        self._enforcement_logs.clear()
