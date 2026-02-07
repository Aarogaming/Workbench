#!/usr/bin/env python3
"""Gradle CI Cache Manager for dependency caching optimization.

This module provides comprehensive Gradle cache management for CI/CD pipelines,
including cache key generation, path management, validation, and statistics.
"""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class CacheStrategy(Enum):
    """Cache restoration strategy."""

    EXACT = "exact"
    PREFIX = "prefix"
    FALLBACK = "fallback"


class CacheProvider(Enum):
    """CI cache provider type."""

    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"
    JENKINS = "jenkins"
    CIRCLE_CI = "circle_ci"
    GENERIC = "generic"


class CacheStatus(Enum):
    """Cache validation status."""

    VALID = "valid"
    STALE = "stale"
    MISSING = "missing"
    CORRUPTED = "corrupted"


class CacheTier(Enum):
    """Cache priority tier."""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"


@dataclass
class CachePath:
    """Gradle cache path configuration."""

    path: str
    tier: CacheTier
    description: str
    required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "tier": self.tier.value,
            "description": self.description,
            "required": self.required,
        }


@dataclass
class CacheKey:
    """Cache key specification."""

    primary: str
    restore_keys: List[str] = field(default_factory=list)
    strategy: CacheStrategy = CacheStrategy.PREFIX
    provider: CacheProvider = CacheProvider.GITHUB_ACTIONS

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "primary": self.primary,
            "restore_keys": self.restore_keys,
            "strategy": self.strategy.value,
            "provider": self.provider.value,
        }


@dataclass
class CacheConfig:
    """Complete Gradle cache configuration."""

    runner_os: str
    gradle_version: str
    java_version: str
    dependency_files: List[str] = field(default_factory=list)
    enable_wrapper_cache: bool = True
    enable_dependency_cache: bool = True
    enable_build_cache: bool = True
    cache_ttl_days: int = 7

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class CacheValidation:
    """Cache validation result."""

    status: CacheStatus
    timestamp: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "timestamp": self.timestamp,
            "message": self.message,
            "details": self.details,
        }


@dataclass
class CacheStats:
    """Cache usage statistics."""

    total_size_mb: float
    cache_hits: int
    cache_misses: int
    last_updated: str
    paths_cached: int
    hit_rate: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class GradleCacheManager:
    """Manage Gradle dependency caching for CI/CD."""

    DEFAULT_PATHS = [
        CachePath(
            "~/.gradle/caches",
            CacheTier.PRIMARY,
            "Gradle dependency cache",
        ),
        CachePath(
            "~/.gradle/wrapper",
            CacheTier.PRIMARY,
            "Gradle wrapper distribution",
        ),
        CachePath(
            ".gradle/build-cache",
            CacheTier.SECONDARY,
            "Gradle build cache",
        ),
        CachePath(
            "~/.gradle/daemon",
            CacheTier.TERTIARY,
            "Gradle daemon state",
            required=False,
        ),
    ]

    def __init__(self, config: CacheConfig):
        """Initialize cache manager."""
        self._config = config
        self._paths: List[CachePath] = []
        self._keys: List[CacheKey] = []
        self._validations: List[CacheValidation] = []
        self._stats: Optional[CacheStats] = None
        self._callbacks: Dict[str, List[Callable]] = {
            "key_generated": [],
            "cache_validated": [],
            "config_updated": [],
        }

        self._initialize_paths()

    def _initialize_paths(self) -> None:
        """Initialize default cache paths."""
        self._paths = [
            path for path in self.DEFAULT_PATHS if self._should_include_path(path)
        ]

    def _should_include_path(self, path: CachePath) -> bool:
        """Check if path should be included based on config."""
        if "wrapper" in path.path and not self._config.enable_wrapper_cache:
            return False
        if "build-cache" in path.path and not self._config.enable_build_cache:
            return False
        if "caches" in path.path and not self._config.enable_dependency_cache:
            return False
        return True

    def generate_cache_key(
        self,
        provider: CacheProvider = CacheProvider.GITHUB_ACTIONS,
        include_java_version: bool = True,
    ) -> CacheKey:
        """Generate cache key for current configuration."""
        # Calculate hash of dependency files
        dep_hash = self._hash_dependency_files()

        # Build primary key
        key_parts = [
            self._config.runner_os,
            "gradle",
            self._config.gradle_version,
        ]

        if include_java_version:
            key_parts.append(f"java{self._config.java_version}")

        key_parts.append(dep_hash)

        primary_key = "-".join(key_parts)

        # Build restore keys (fallback chain)
        restore_keys = []

        # Level 1: Same OS, Gradle, Java (any deps)
        if include_java_version:
            restore_keys.append(
                "-".join(
                    [
                        self._config.runner_os,
                        "gradle",
                        self._config.gradle_version,
                        f"java{self._config.java_version}",
                    ]
                )
            )

        # Level 2: Same OS, Gradle (any Java, any deps)
        restore_keys.append(
            "-".join(
                [
                    self._config.runner_os,
                    "gradle",
                    self._config.gradle_version,
                ]
            )
        )

        # Level 3: Same OS (any Gradle, any Java, any deps)
        restore_keys.append(f"{self._config.runner_os}-gradle")

        cache_key = CacheKey(
            primary=primary_key,
            restore_keys=restore_keys,
            strategy=CacheStrategy.PREFIX,
            provider=provider,
        )

        self._keys.append(cache_key)
        self._trigger_callbacks("key_generated", cache_key)

        return cache_key

    def _hash_dependency_files(self) -> str:
        """Generate hash from dependency file contents."""
        if not self._config.dependency_files:
            return "no-deps"

        hasher = hashlib.sha256()

        for file_pattern in self._config.dependency_files:
            # Simulate file hashing (in real CI, would read actual files)
            hasher.update(file_pattern.encode())

        return hasher.hexdigest()[:12]

    def get_cache_paths(self, tier: Optional[CacheTier] = None) -> List[CachePath]:
        """Get cache paths, optionally filtered by tier."""
        if tier is None:
            return self._paths.copy()
        return [p for p in self._paths if p.tier == tier]

    def add_custom_path(self, path: CachePath) -> None:
        """Add custom cache path."""
        self._paths.append(path)

    def validate_cache(self, cache_age_hours: Optional[int] = None) -> CacheValidation:
        """Validate cache configuration and status."""
        timestamp = datetime.now(timezone.utc).isoformat()

        # Check for required paths
        missing_paths = [p.path for p in self._paths if p.required and not p.path]

        if missing_paths:
            validation = CacheValidation(
                status=CacheStatus.MISSING,
                timestamp=timestamp,
                message=f"Missing required paths: {', '.join(missing_paths)}",
                details={"missing_paths": missing_paths},
            )
        elif cache_age_hours and cache_age_hours > self._config.cache_ttl_days * 24:
            validation = CacheValidation(
                status=CacheStatus.STALE,
                timestamp=timestamp,
                message=f"Cache older than TTL ({self._config.cache_ttl_days}d)",
                details={"age_hours": cache_age_hours},
            )
        else:
            validation = CacheValidation(
                status=CacheStatus.VALID,
                timestamp=timestamp,
                message="Cache configuration valid",
                details={
                    "paths_count": len(self._paths),
                    "ttl_days": self._config.cache_ttl_days,
                },
            )

        self._validations.append(validation)
        self._trigger_callbacks("cache_validated", validation)

        return validation

    def update_config(self, **kwargs: Any) -> None:
        """Update cache configuration."""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)

        self._initialize_paths()
        self._trigger_callbacks("config_updated", self._config)

    def generate_github_actions_yaml(self) -> str:
        """Generate GitHub Actions cache step YAML."""
        cache_key = self.generate_cache_key(CacheProvider.GITHUB_ACTIONS)
        paths = [p.path for p in self._paths]

        yaml_lines = [
            "- name: Cache Gradle dependencies",
            "  uses: actions/cache@v4",
            "  with:",
            f"    path: |",
        ]

        for path in paths:
            yaml_lines.append(f"      {path}")

        yaml_lines.extend(
            [
                f"    key: {cache_key.primary}",
                "    restore-keys: |",
            ]
        )

        for restore_key in cache_key.restore_keys:
            yaml_lines.append(f"      {restore_key}")

        return "\n".join(yaml_lines)

    def calculate_statistics(
        self, cache_hits: int, cache_misses: int, total_size_mb: float
    ) -> CacheStats:
        """Calculate cache usage statistics."""
        total_requests = cache_hits + cache_misses
        hit_rate = (cache_hits / total_requests * 100) if total_requests > 0 else 0.0

        stats = CacheStats(
            total_size_mb=total_size_mb,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            last_updated=datetime.now(timezone.utc).isoformat(),
            paths_cached=len(self._paths),
            hit_rate=hit_rate,
        )

        self._stats = stats
        return stats

    def get_configuration(self) -> CacheConfig:
        """Get current cache configuration."""
        return self._config

    def get_validation_history(self) -> List[CacheValidation]:
        """Get validation history."""
        return self._validations.copy()

    def get_key_history(self) -> List[CacheKey]:
        """Get generated key history."""
        return self._keys.copy()

    def register_callback(self, event_type: str, callback: Callable) -> None:
        """Register callback for events."""
        if event_type in self._callbacks:
            self._callbacks[event_type].append(callback)

    def _trigger_callbacks(self, event_type: str, data: Any) -> None:
        """Trigger registered callbacks."""
        for callback in self._callbacks.get(event_type, []):
            try:
                callback(data)
            except Exception:
                pass  # Suppress callback errors

    def export_report(self) -> Dict[str, Any]:
        """Export comprehensive cache report."""
        return {
            "config": self._config.to_dict(),
            "paths": [p.to_dict() for p in self._paths],
            "keys": [k.to_dict() for k in self._keys],
            "validations": [v.to_dict() for v in self._validations],
            "stats": self._stats.to_dict() if self._stats else None,
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "total_keys": len(self._keys),
                "total_validations": len(self._validations),
            },
        }


def create_default_config(
    runner_os: str = "Linux",
    gradle_version: str = "8.5",
    java_version: str = "17",
) -> CacheConfig:
    """Create default cache configuration."""
    return CacheConfig(
        runner_os=runner_os,
        gradle_version=gradle_version,
        java_version=java_version,
        dependency_files=[
            "build.gradle",
            "build.gradle.kts",
            "settings.gradle",
            "settings.gradle.kts",
            "gradle.properties",
        ],
    )


if __name__ == "__main__":
    # Demo usage
    config = create_default_config()
    manager = GradleCacheManager(config)

    print("=== Gradle Cache Manager ===")
    print(f"Paths: {len(manager.get_cache_paths())}")

    key = manager.generate_cache_key()
    print(f"\nPrimary Key: {key.primary}")
    print(f"Restore Keys: {len(key.restore_keys)}")

    validation = manager.validate_cache()
    print(f"\nValidation: {validation.status.value}")

    yaml = manager.generate_github_actions_yaml()
    print(f"\nGenerated YAML:\n{yaml}")
