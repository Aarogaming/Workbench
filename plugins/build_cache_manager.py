#!/usr/bin/env python3
"""GitHub Actions Build Cache Manager for CI optimization.

This module provides comprehensive build artifact caching for GitHub Actions,
including compiled outputs, test results, coverage data, and build tools.
"""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class ArtifactType(Enum):
    """Build artifact type."""

    COMPILED = "compiled"
    TEST_RESULTS = "test_results"
    COVERAGE = "coverage"
    LINT = "lint"
    DOCUMENTATION = "documentation"
    DEPENDENCIES = "dependencies"
    TOOLS = "tools"


class CacheMode(Enum):
    """Cache operation mode."""

    READ_WRITE = "read_write"
    READ_ONLY = "read_only"
    WRITE_ONLY = "write_only"
    DISABLED = "disabled"


class CompressionLevel(Enum):
    """Cache compression level."""

    NONE = 0
    FAST = 1
    BALANCED = 6
    MAX = 9


class CacheAction(Enum):
    """Cache action type."""

    SAVE = "save"
    RESTORE = "restore"
    INVALIDATE = "invalidate"


@dataclass
class BuildArtifact:
    """Build artifact configuration."""

    name: str
    paths: List[str]
    artifact_type: ArtifactType
    size_mb: float = 0.0
    required: bool = True
    cache_on_failure: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "paths": self.paths,
            "artifact_type": self.artifact_type.value,
            "size_mb": self.size_mb,
            "required": self.required,
            "cache_on_failure": self.cache_on_failure,
        }


@dataclass
class CacheConfiguration:
    """Build cache configuration."""

    workflow_name: str
    runner_os: str
    cache_mode: CacheMode = CacheMode.READ_WRITE
    compression: CompressionLevel = CompressionLevel.BALANCED
    max_size_mb: int = 2048
    ttl_days: int = 7
    enable_parallel_upload: bool = True
    enable_incremental: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workflow_name": self.workflow_name,
            "runner_os": self.runner_os,
            "cache_mode": self.cache_mode.value,
            "compression": self.compression.value,
            "max_size_mb": self.max_size_mb,
            "ttl_days": self.ttl_days,
            "enable_parallel_upload": self.enable_parallel_upload,
            "enable_incremental": self.enable_incremental,
        }


@dataclass
class CacheKey:
    """Cache key specification."""

    primary: str
    restore_keys: List[str] = field(default_factory=list)
    hash_files: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "primary": self.primary,
            "restore_keys": self.restore_keys,
            "hash_files": self.hash_files,
        }


@dataclass
class CacheMetrics:
    """Cache performance metrics."""

    total_artifacts: int
    cached_size_mb: float
    cache_hits: int
    cache_misses: int
    avg_save_time_sec: float
    avg_restore_time_sec: float
    hit_rate: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class CacheEvent:
    """Cache operation event."""

    action: CacheAction
    artifact_name: str
    timestamp: str
    success: bool
    duration_sec: float = 0.0
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "action": self.action.value,
            "artifact_name": self.artifact_name,
            "timestamp": self.timestamp,
            "success": self.success,
            "duration_sec": self.duration_sec,
            "error_message": self.error_message,
        }


class BuildCacheManager:
    """Manage GitHub Actions build artifact caching."""

    def __init__(self, config: CacheConfiguration):
        """Initialize build cache manager."""
        self._config = config
        self._artifacts: List[BuildArtifact] = []
        self._keys: List[CacheKey] = []
        self._events: List[CacheEvent] = []
        self._metrics: Optional[CacheMetrics] = None
        self._callbacks: Dict[str, List[Callable]] = {
            "artifact_added": [],
            "cache_saved": [],
            "cache_restored": [],
            "metrics_updated": [],
        }

    def add_artifact(self, artifact: BuildArtifact) -> None:
        """Add build artifact for caching."""
        self._artifacts.append(artifact)
        self._trigger_callbacks("artifact_added", artifact)

    def add_compiled_output(
        self, paths: List[str], name: str = "compiled-output"
    ) -> BuildArtifact:
        """Add compiled output artifact."""
        artifact = BuildArtifact(
            name=name,
            paths=paths,
            artifact_type=ArtifactType.COMPILED,
            required=True,
        )
        self.add_artifact(artifact)
        return artifact

    def add_test_results(
        self,
        paths: List[str],
        name: str = "test-results",
        cache_on_failure: bool = True,
    ) -> BuildArtifact:
        """Add test results artifact."""
        artifact = BuildArtifact(
            name=name,
            paths=paths,
            artifact_type=ArtifactType.TEST_RESULTS,
            required=False,
            cache_on_failure=cache_on_failure,
        )
        self.add_artifact(artifact)
        return artifact

    def add_coverage_data(
        self, paths: List[str], name: str = "coverage"
    ) -> BuildArtifact:
        """Add coverage data artifact."""
        artifact = BuildArtifact(
            name=name,
            paths=paths,
            artifact_type=ArtifactType.COVERAGE,
            required=False,
        )
        self.add_artifact(artifact)
        return artifact

    def generate_cache_key(
        self,
        artifact: BuildArtifact,
        include_commit_sha: bool = False,
        commit_sha: Optional[str] = None,
    ) -> CacheKey:
        """Generate cache key for artifact."""
        # Build primary key components
        key_parts = [
            self._config.runner_os,
            self._config.workflow_name,
            artifact.name,
        ]

        if include_commit_sha and commit_sha:
            key_parts.append(commit_sha[:8])

        # Add file hash if incremental caching enabled
        if self._config.enable_incremental:
            file_hash = self._hash_artifact_paths(artifact.paths)
            key_parts.append(file_hash)

        primary_key = "-".join(key_parts)

        # Build restore keys (fallback chain)
        restore_keys = []

        # Level 1: Same OS, workflow, artifact (any commit)
        restore_keys.append(
            "-".join(
                [
                    self._config.runner_os,
                    self._config.workflow_name,
                    artifact.name,
                ]
            )
        )

        # Level 2: Same OS, workflow (any artifact)
        restore_keys.append(
            "-".join([self._config.runner_os, self._config.workflow_name])
        )

        cache_key = CacheKey(
            primary=primary_key,
            restore_keys=restore_keys,
            hash_files=artifact.paths if self._config.enable_incremental else [],
        )

        self._keys.append(cache_key)
        return cache_key

    def _hash_artifact_paths(self, paths: List[str]) -> str:
        """Generate hash from artifact paths."""
        hasher = hashlib.sha256()
        for path in sorted(paths):
            hasher.update(path.encode())
        return hasher.hexdigest()[:12]

    def generate_github_actions_yaml(self) -> str:
        """Generate GitHub Actions cache steps YAML."""
        if not self._artifacts:
            return "# No artifacts configured"

        yaml_lines = []

        for artifact in self._artifacts:
            cache_key = self.generate_cache_key(artifact)

            yaml_lines.extend(
                [
                    f"- name: Cache {artifact.name}",
                    "  uses: actions/cache@v4",
                    "  with:",
                    "    path: |",
                ]
            )

            for path in artifact.paths:
                yaml_lines.append(f"      {path}")

            yaml_lines.extend(
                [
                    f"    key: {cache_key.primary}",
                    "    restore-keys: |",
                ]
            )

            for restore_key in cache_key.restore_keys:
                yaml_lines.append(f"      {restore_key}")

            # Add conditional for failures if needed
            if artifact.cache_on_failure:
                yaml_lines.append("    save-always: true")

            yaml_lines.append("")  # Blank line between artifacts

        return "\n".join(yaml_lines)

    def record_cache_event(
        self,
        action: CacheAction,
        artifact_name: str,
        success: bool,
        duration_sec: float = 0.0,
        error_message: Optional[str] = None,
    ) -> CacheEvent:
        """Record cache operation event."""
        event = CacheEvent(
            action=action,
            artifact_name=artifact_name,
            timestamp=datetime.now(timezone.utc).isoformat(),
            success=success,
            duration_sec=duration_sec,
            error_message=error_message,
        )

        self._events.append(event)

        if action == CacheAction.SAVE:
            self._trigger_callbacks("cache_saved", event)
        elif action == CacheAction.RESTORE:
            self._trigger_callbacks("cache_restored", event)

        return event

    def calculate_metrics(self) -> CacheMetrics:
        """Calculate cache performance metrics."""
        if not self._events:
            return CacheMetrics(
                total_artifacts=len(self._artifacts),
                cached_size_mb=0.0,
                cache_hits=0,
                cache_misses=0,
                avg_save_time_sec=0.0,
                avg_restore_time_sec=0.0,
                hit_rate=0.0,
            )

        # Count hits and misses from restore events
        restore_events = [e for e in self._events if e.action == CacheAction.RESTORE]
        cache_hits = sum(1 for e in restore_events if e.success)
        cache_misses = sum(1 for e in restore_events if not e.success)

        # Calculate average times
        save_events = [e for e in self._events if e.action == CacheAction.SAVE]
        avg_save_time = (
            sum(e.duration_sec for e in save_events) / len(save_events)
            if save_events
            else 0.0
        )

        avg_restore_time = (
            sum(e.duration_sec for e in restore_events) / len(restore_events)
            if restore_events
            else 0.0
        )

        # Calculate total size
        total_size = sum(a.size_mb for a in self._artifacts)

        # Calculate hit rate
        total_requests = cache_hits + cache_misses
        hit_rate = (cache_hits / total_requests * 100) if total_requests > 0 else 0.0

        metrics = CacheMetrics(
            total_artifacts=len(self._artifacts),
            cached_size_mb=total_size,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            avg_save_time_sec=avg_save_time,
            avg_restore_time_sec=avg_restore_time,
            hit_rate=hit_rate,
        )

        self._metrics = metrics
        self._trigger_callbacks("metrics_updated", metrics)
        return metrics

    def get_artifacts_by_type(self, artifact_type: ArtifactType) -> List[BuildArtifact]:
        """Get artifacts filtered by type."""
        return [a for a in self._artifacts if a.artifact_type == artifact_type]

    def get_required_artifacts(self) -> List[BuildArtifact]:
        """Get required artifacts only."""
        return [a for a in self._artifacts if a.required]

    def update_config(self, **kwargs: Any) -> None:
        """Update cache configuration."""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)

    def validate_cache_size(self) -> Dict[str, Any]:
        """Validate total cache size against limit."""
        total_size = sum(a.size_mb for a in self._artifacts)
        is_valid = total_size <= self._config.max_size_mb
        percentage = (
            (total_size / self._config.max_size_mb * 100)
            if self._config.max_size_mb > 0
            else 0.0
        )

        return {
            "valid": is_valid,
            "total_size_mb": total_size,
            "max_size_mb": self._config.max_size_mb,
            "usage_percentage": percentage,
            "exceeds_limit": total_size > self._config.max_size_mb,
        }

    def get_event_history(
        self, action: Optional[CacheAction] = None
    ) -> List[CacheEvent]:
        """Get event history, optionally filtered by action."""
        if action is None:
            return self._events.copy()
        return [e for e in self._events if e.action == action]

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
            "artifacts": [a.to_dict() for a in self._artifacts],
            "keys": [k.to_dict() for k in self._keys],
            "events": [e.to_dict() for e in self._events],
            "metrics": self._metrics.to_dict() if self._metrics else None,
            "validation": self.validate_cache_size(),
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "total_artifacts": len(self._artifacts),
                "total_events": len(self._events),
            },
        }


def create_default_python_config(
    workflow_name: str = "Python CI", runner_os: str = "Linux"
) -> CacheConfiguration:
    """Create default Python build cache configuration."""
    return CacheConfiguration(
        workflow_name=workflow_name,
        runner_os=runner_os,
        cache_mode=CacheMode.READ_WRITE,
        max_size_mb=2048,
        ttl_days=7,
    )


def create_default_android_config(
    workflow_name: str = "Android CI", runner_os: str = "Linux"
) -> CacheConfiguration:
    """Create default Android build cache configuration."""
    return CacheConfiguration(
        workflow_name=workflow_name,
        runner_os=runner_os,
        cache_mode=CacheMode.READ_WRITE,
        max_size_mb=4096,  # Android builds larger
        ttl_days=14,  # Longer TTL for stable deps
    )


if __name__ == "__main__":
    # Demo usage
    config = create_default_python_config()
    manager = BuildCacheManager(config)

    # Add artifacts
    manager.add_compiled_output([".pytest_cache", "__pycache__"])
    manager.add_test_results(["test-results/**/*.xml"])
    manager.add_coverage_data([".coverage", "htmlcov/"])

    print("=== Build Cache Manager ===")
    print(f"Artifacts: {len(manager._artifacts)}")

    yaml = manager.generate_github_actions_yaml()
    print(f"\nGenerated YAML:\n{yaml}")

    # Record some events
    manager.record_cache_event(CacheAction.RESTORE, "compiled-output", True, 2.5)
    manager.record_cache_event(CacheAction.SAVE, "test-results", True, 1.2)

    metrics = manager.calculate_metrics()
    print(f"\nMetrics - Hit Rate: {metrics.hit_rate:.1f}%")
