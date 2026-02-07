"""AD-111: Versioning strategy for release builds.

Provides comprehensive version management, release naming, and build metadata
for Android release builds with support for semantic versioning, build numbers,
and reproducible builds.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class VersionBumpType(Enum):
    """Semantic version bump types."""

    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    BUILD = "build"


class ReleaseChannel(Enum):
    """Release channel types."""

    DEV = "dev"
    STAGE = "stage"
    PROD = "prod"
    BETA = "beta"


@dataclass
class SemanticVersion:
    """Semantic version representation (major.minor.patch)."""

    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        """Return version string."""
        return f"{self.major}.{self.minor}.{self.patch}"

    def bump(self, bump_type: VersionBumpType) -> "SemanticVersion":
        """Return new version after bump."""
        if bump_type == VersionBumpType.MAJOR:
            return SemanticVersion(self.major + 1, 0, 0)
        if bump_type == VersionBumpType.MINOR:
            return SemanticVersion(self.major, self.minor + 1, 0)
        if bump_type == VersionBumpType.PATCH:
            return SemanticVersion(self.major, self.minor, self.patch + 1)
        return self


@dataclass
class BuildMetadata:
    """Build metadata for a release."""

    build_number: int
    build_timestamp: str
    git_commit: str
    channel: ReleaseChannel
    flavor: str  # dev/stage/prod
    signing_config: Optional[str] = None
    reproducible: bool = True

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "build_number": self.build_number,
            "build_timestamp": self.build_timestamp,
            "git_commit": self.git_commit,
            "channel": self.channel.value,
            "flavor": self.flavor,
            "signing_config": self.signing_config,
            "reproducible": self.reproducible,
        }


@dataclass
class ReleaseInfo:
    """Release information."""

    version: SemanticVersion
    build_metadata: BuildMetadata
    apk_name: str
    release_notes: str = ""
    signed: bool = False
    checksums: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "version": str(self.version),
            "channel": self.build_metadata.channel.value,
            "build_metadata": self.build_metadata.to_dict(),
            "apk_name": self.apk_name,
            "release_notes": self.release_notes,
            "signed": self.signed,
            "checksums": self.checksums,
        }


class VersioningStrategy:
    """Manages versioning and release build strategy."""

    def __init__(self, initial_version: str = "1.0.0"):
        """Initialize versioning strategy."""
        parts = initial_version.split(".")
        self.current_version = SemanticVersion(
            int(parts[0]), int(parts[1]), int(parts[2])
        )
        self.build_counter = 0
        self.release_history: List[ReleaseInfo] = []
        self.version_history: List[Tuple[str, datetime]] = []

    def bump_version(self, bump_type: VersionBumpType) -> str:
        """Bump version and return new version string."""
        if bump_type != VersionBumpType.BUILD:
            self.current_version = self.current_version.bump(bump_type)
        else:
            self.build_counter += 1
        timestamp = datetime.now()
        self.version_history.append((str(self.current_version), timestamp))
        return str(self.current_version)

    def get_build_number(self) -> int:
        """Get next build number."""
        self.build_counter += 1
        return self.build_counter

    def generate_apk_name(
        self,
        app_name: str,
        channel: ReleaseChannel,
        flavor: str,
    ) -> str:
        """Generate APK output name based on versioning strategy."""
        version_str = str(self.current_version)
        build_num = self.build_counter + 1  # Preview next build
        timestamp = datetime.now().strftime("%Y%m%d")
        return (
            f"{app_name}-{channel.value}-{flavor}-"
            f"v{version_str}-b{build_num}-{timestamp}.apk"
        )

    def create_release(
        self,
        channel: ReleaseChannel,
        flavor: str,
        git_commit: str,
        release_notes: str = "",
    ) -> ReleaseInfo:
        """Create release information."""
        build_num = self.get_build_number()
        build_meta = BuildMetadata(
            build_number=build_num,
            build_timestamp=datetime.now().isoformat(),
            git_commit=git_commit,
            channel=channel,
            flavor=flavor,
        )
        apk_name = self.generate_apk_name("app", channel, flavor)
        release = ReleaseInfo(
            version=self.current_version,
            build_metadata=build_meta,
            apk_name=apk_name,
            release_notes=release_notes,
        )
        self.release_history.append(release)
        return release

    def get_release_history(
        self, channel: Optional[ReleaseChannel] = None
    ) -> List[ReleaseInfo]:
        """Get release history, optionally filtered by channel."""
        if channel is None:
            return self.release_history
        return [r for r in self.release_history if r.build_metadata.channel == channel]

    def get_version_history(self) -> List[str]:
        """Get version history."""
        return [v[0] for v in self.version_history]

    def get_current_version(self) -> str:
        """Get current version."""
        return str(self.current_version)

    def get_status(self) -> Dict:
        """Get versioning strategy status."""
        return {
            "current_version": str(self.current_version),
            "build_counter": self.build_counter,
            "release_count": len(self.release_history),
            "version_history_count": len(self.version_history),
        }


class ReleaseSigningConfig:
    """Manages release signing configuration."""

    def __init__(self, keystore_path: str, alias: str, password: str):
        """Initialize signing config."""
        self.keystore_path = keystore_path
        self.alias = alias
        self.password = password
        self.enabled = False

    def enable(self) -> Dict:
        """Enable signing."""
        self.enabled = True
        return {
            "status": "signing_enabled",
            "keystore": self.keystore_path,
            "alias": self.alias,
        }

    def disable(self) -> Dict:
        """Disable signing."""
        self.enabled = False
        return {"status": "signing_disabled"}

    def get_signing_command(self, apk_path: str) -> str:
        """Generate signing command."""
        return (
            f"jarsigner -verbose -sigalg SHA256withRSA "
            f"-digestalg SHA256 -keystore {self.keystore_path} "
            f"-storepass {self.password} {apk_path} {self.alias}"
        )


class BuildChecklist:
    """Pre-release build checklist."""

    def __init__(self):
        """Initialize checklist."""
        self.items = {
            "lint_passed": False,
            "tests_passed": False,
            "proguard_rules_updated": False,
            "release_notes_written": False,
            "version_bumped": False,
            "signing_configured": False,
            "reproducible_build": False,
        }
        self.completed_at: Optional[str] = None

    def mark_complete(self, item: str) -> Dict:
        """Mark checklist item complete."""
        if item in self.items:
            self.items[item] = True
        return {"item": item, "status": "completed"}

    def is_ready(self) -> bool:
        """Check if all checklist items complete."""
        return all(self.items.values())

    def get_status(self) -> Dict:
        """Get checklist status."""
        return {
            "items": self.items,
            "ready": self.is_ready(),
            "completion": (f"{sum(self.items.values())}/{len(self.items)}"),
        }


class ReproducibleBuildConfig:
    """Configuration for reproducible builds."""

    def __init__(self):
        """Initialize reproducible build config."""
        self.source_date_epoch: Optional[str] = None
        self.build_props: Dict[str, str] = {}
        self.enabled = True

    def set_source_date(self, timestamp: str) -> Dict:
        """Set SOURCE_DATE_EPOCH for reproducibility."""
        self.source_date_epoch = timestamp
        return {
            "status": "source_date_set",
            "timestamp": timestamp,
        }

    def add_build_property(self, key: str, value: str) -> Dict:
        """Add build property for reproducibility."""
        self.build_props[key] = value
        return {
            "status": "property_added",
            "key": key,
            "value": value,
        }

    def get_config(self) -> Dict:
        """Get reproducible build configuration."""
        return {
            "enabled": self.enabled,
            "source_date_epoch": self.source_date_epoch,
            "build_properties": self.build_props,
        }
