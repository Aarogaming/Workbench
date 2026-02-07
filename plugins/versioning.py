"""
AAS-268: Plugin Versioning System

Provides semantic versioning and version management for plugins.
Supports version constraints, compatibility checking, and updates.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import re


@dataclass
class Version:
    """Semantic version representation (major.minor.patch)"""

    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None

    def __str__(self) -> str:
        version_str = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version_str += f"-{self.prerelease}"
        return version_str

    @staticmethod
    def parse(version_str: str) -> "Version":
        """Parse semantic version string"""
        pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.]+))?$"
        match = re.match(pattern, version_str)
        if not match:
            raise ValueError(f"Invalid version: {version_str}")

        major, minor, patch, prerelease = match.groups()
        return Version(int(major), int(minor), int(patch), prerelease)

    def is_compatible(self, required: "Version") -> bool:
        """Check compatibility with required version using semver rules"""
        if self.major != required.major:
            return False
        if self.minor < required.minor:
            return False
        if self.minor == required.minor and self.patch < required.patch:
            return False
        return True

    def __lt__(self, other: "Version") -> bool:
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        return self.patch < other.patch

    def __le__(self, other: "Version") -> bool:
        return self < other or self == other

    def __eq__(self, other: "Version") -> bool:
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.prerelease == other.prerelease
        )


class VersionConstraint:
    """Version constraint specification"""

    def __init__(self, constraint_str: str):
        self.constraint_str = constraint_str
        self.parsed = self._parse_constraint(constraint_str)

    def _parse_constraint(self, constraint_str: str) -> Tuple[str, Version]:
        """Parse constraint like >=1.0.0, ~1.2.0, ^1.0.0"""
        operators = [">=", "<=", "==", "~", "^", ">", "<"]
        for op in operators:
            if constraint_str.startswith(op):
                version_str = constraint_str[len(op) :].strip()
                return op, Version.parse(version_str)
        raise ValueError(f"Invalid constraint: {constraint_str}")

    def satisfies(self, version: Version) -> bool:
        """Check if version satisfies constraint"""
        op, constraint_ver = self.parsed

        if op == ">=":
            return version >= constraint_ver
        elif op == "<=":
            return version <= constraint_ver
        elif op == "==":
            return version == constraint_ver
        elif op == ">":
            return version > constraint_ver
        elif op == "<":
            return version < constraint_ver
        elif op == "~":  # Tilde: compatible patch versions
            return (
                version.major == constraint_ver.major
                and version.minor == constraint_ver.minor
                and version >= constraint_ver
            )
        elif op == "^":  # Caret: compatible minor versions
            return version.major == constraint_ver.major and version >= constraint_ver

        return False


class PluginVersionManager:
    """Manages plugin versions and compatibility"""

    def __init__(self):
        self.registry: dict[str, Version] = {}

    def register_version(self, plugin_id: str, version: Version):
        """Register a plugin version"""
        self.registry[plugin_id] = version

    def check_compatibility(
        self, plugin_id: str, required_version: VersionConstraint
    ) -> bool:
        """Check if installed version satisfies requirement"""
        if plugin_id not in self.registry:
            return False
        return required_version.satisfies(self.registry[plugin_id])

    def get_latest_compatible(
        self, plugin_id: str, versions: List[Version]
    ) -> Optional[Version]:
        """Get latest version that's compatible"""
        compatible = [
            v
            for v in versions
            if v.is_compatible(self.registry.get(plugin_id, Version(0, 0, 0)))
        ]
        return max(compatible) if compatible else None


# Export public API
__all__ = ["Version", "VersionConstraint", "PluginVersionManager"]
