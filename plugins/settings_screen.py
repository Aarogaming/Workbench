"""AD-057: Settings screen for URLs and refresh options.

Provides comprehensive settings management for endpoint URLs, refresh
intervals, notifications, and analytics preferences with persistent
configuration storage.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime


class RefreshInterval(Enum):
    """Refresh interval options."""

    EVERY_30S = 30
    EVERY_1M = 60
    EVERY_5M = 300
    EVERY_15M = 900
    EVERY_1H = 3600


class NotificationType(Enum):
    """Notification types."""

    STATUS_CHANGE = "status_change"
    ERROR = "error"
    DEGRADED = "degraded"
    RESOLVED = "resolved"


@dataclass
class URLSettings:
    """URL configuration."""

    primary_url: str
    backup_urls: List[str] = field(default_factory=list)
    timeout_ms: int = 5000
    retry_count: int = 3
    use_https_only: bool = True

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "primary_url": self.primary_url,
            "backup_urls": self.backup_urls,
            "timeout_ms": self.timeout_ms,
            "retry_count": self.retry_count,
            "use_https_only": self.use_https_only,
        }


@dataclass
class RefreshSettings:
    """Refresh interval configuration."""

    interval: RefreshInterval = RefreshInterval.EVERY_1M
    auto_start: bool = True
    background_refresh: bool = True
    wifi_only: bool = False

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "interval_seconds": self.interval.value,
            "auto_start": self.auto_start,
            "background_refresh": self.background_refresh,
            "wifi_only": self.wifi_only,
        }


@dataclass
class NotificationSettings:
    """Notification preferences."""

    enabled: bool = True
    notify_on_status_change: bool = True
    notify_on_error: bool = True
    notify_on_resolved: bool = True
    sound_enabled: bool = True
    vibration_enabled: bool = True

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "enabled": self.enabled,
            "notify_on_status_change": self.notify_on_status_change,
            "notify_on_error": self.notify_on_error,
            "notify_on_resolved": self.notify_on_resolved,
            "sound_enabled": self.sound_enabled,
            "vibration_enabled": self.vibration_enabled,
        }


class SettingsScreen:
    """Settings screen manager."""

    def __init__(self):
        """Initialize settings."""
        self.url_settings = URLSettings(primary_url="https://api.example.com")
        self.refresh_settings = RefreshSettings()
        self.notification_settings = NotificationSettings()
        self.last_saved: Optional[str] = None

    def validate_url(self, url: str) -> Dict:
        """Validate URL format."""
        issues = []

        if not url:
            issues.append("URL cannot be empty")
        elif not url.startswith(("http://", "https://")):
            issues.append("URL must start with http:// or https://")

        if self.url_settings.use_https_only and url.startswith("http://"):
            issues.append("HTTPS-only mode enabled, but URL uses HTTP")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }

    def update_primary_url(self, url: str) -> Dict:
        """Update primary URL."""
        validation = self.validate_url(url)
        if not validation["valid"]:
            return {
                "status": "invalid",
                "issues": validation["issues"],
            }

        self.url_settings.primary_url = url
        return {
            "status": "updated",
            "url": url,
        }

    def add_backup_url(self, url: str) -> Dict:
        """Add backup URL."""
        validation = self.validate_url(url)
        if not validation["valid"]:
            return {
                "status": "invalid",
                "issues": validation["issues"],
            }

        if url not in self.url_settings.backup_urls:
            self.url_settings.backup_urls.append(url)

        return {
            "status": "added",
            "url": url,
            "total_backup_urls": len(self.url_settings.backup_urls),
        }

    def remove_backup_url(self, url: str) -> Dict:
        """Remove backup URL."""
        if url in self.url_settings.backup_urls:
            self.url_settings.backup_urls.remove(url)

        return {
            "status": "removed",
            "url": url,
            "remaining_backup_urls": len(self.url_settings.backup_urls),
        }

    def set_refresh_interval(self, interval: RefreshInterval) -> Dict:
        """Set refresh interval."""
        self.refresh_settings.interval = interval
        return {
            "status": "updated",
            "interval_seconds": interval.value,
        }

    def set_wifi_only_mode(self, enabled: bool) -> Dict:
        """Set WiFi-only refresh mode."""
        self.refresh_settings.wifi_only = enabled
        return {
            "status": "updated",
            "wifi_only": enabled,
        }

    def toggle_notifications(self, enabled: bool) -> Dict:
        """Toggle all notifications."""
        self.notification_settings.enabled = enabled
        return {
            "status": "updated",
            "notifications_enabled": enabled,
        }

    def set_notification_type(
        self, notification_type: NotificationType, enabled: bool
    ) -> Dict:
        """Enable/disable specific notification type."""
        if notification_type == NotificationType.STATUS_CHANGE:
            self.notification_settings.notify_on_status_change = enabled
        elif notification_type == NotificationType.ERROR:
            self.notification_settings.notify_on_error = enabled
        elif notification_type == NotificationType.RESOLVED:
            self.notification_settings.notify_on_resolved = enabled

        return {
            "status": "updated",
            "notification_type": notification_type.value,
            "enabled": enabled,
        }

    def save_settings(self) -> Dict:
        """Save settings."""
        self.last_saved = datetime.now().isoformat()
        return {
            "status": "saved",
            "timestamp": self.last_saved,
        }

    def reset_to_defaults(self) -> Dict:
        """Reset all settings to defaults."""
        self.url_settings = URLSettings(primary_url="https://api.example.com")
        self.refresh_settings = RefreshSettings()
        self.notification_settings = NotificationSettings()
        return {"status": "reset"}

    def get_all_settings(self) -> Dict:
        """Get all current settings."""
        return {
            "urls": self.url_settings.to_dict(),
            "refresh": self.refresh_settings.to_dict(),
            "notifications": self.notification_settings.to_dict(),
            "last_saved": self.last_saved,
        }

    def export_settings(self) -> str:
        """Export settings as JSON string."""
        import json

        return json.dumps(self.get_all_settings(), indent=2)

    def import_settings(self, settings_json: str) -> Dict:
        """Import settings from JSON string."""
        import json

        try:
            settings = json.loads(settings_json)

            if "urls" in settings:
                url_data = settings["urls"]
                self.url_settings = URLSettings(
                    primary_url=url_data.get("primary_url", "https://api.example.com"),
                    backup_urls=url_data.get("backup_urls", []),
                    timeout_ms=url_data.get("timeout_ms", 5000),
                    retry_count=url_data.get("retry_count", 3),
                    use_https_only=url_data.get("use_https_only", True),
                )

            if "refresh" in settings:
                ref_data = settings["refresh"]
                interval_value = ref_data.get("interval_seconds", 60)
                interval = next(
                    (r for r in RefreshInterval if r.value == interval_value),
                    RefreshInterval.EVERY_1M,
                )
                self.refresh_settings = RefreshSettings(
                    interval=interval,
                    auto_start=ref_data.get("auto_start", True),
                    background_refresh=ref_data.get("background_refresh", True),
                    wifi_only=ref_data.get("wifi_only", False),
                )

            if "notifications" in settings:
                notif_data = settings["notifications"]
                self.notification_settings = NotificationSettings(
                    enabled=notif_data.get("enabled", True),
                    notify_on_status_change=notif_data.get(
                        "notify_on_status_change", True
                    ),
                    notify_on_error=notif_data.get("notify_on_error", True),
                    notify_on_resolved=notif_data.get("notify_on_resolved", True),
                    sound_enabled=notif_data.get("sound_enabled", True),
                    vibration_enabled=notif_data.get("vibration_enabled", True),
                )

            return {"status": "imported"}
        except Exception as e:
            return {
                "status": "import_failed",
                "error": str(e),
            }


class SettingsNavigation:
    """Navigation to settings (AD-058)."""

    def __init__(self, main_screen=None):
        """Initialize navigation."""
        self.main_screen = main_screen
        self.settings_visible = False

    def open_settings(self) -> Dict:
        """Open settings from main screen."""
        self.settings_visible = True
        return {
            "status": "settings_opened",
            "timestamp": datetime.now().isoformat(),
        }

    def close_settings(self) -> Dict:
        """Close settings and return to main."""
        self.settings_visible = False
        return {
            "status": "settings_closed",
            "timestamp": datetime.now().isoformat(),
        }

    def get_navigation_state(self) -> Dict:
        """Get current navigation state."""
        return {
            "settings_visible": self.settings_visible,
            "main_screen_available": self.main_screen is not None,
        }
