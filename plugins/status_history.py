"""AD-076: Status history log (last 20 checks).

Provides comprehensive status history tracking with persistent storage,
notifications on changes, and shareable status snapshots for debugging
and monitoring.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime


class StatusType(Enum):
    """Status types."""

    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class HistoryPeriod(Enum):
    """History query periods."""

    LAST_HOUR = "last_hour"
    LAST_DAY = "last_day"
    LAST_WEEK = "last_week"
    ALL = "all"


@dataclass
class StatusCheckResult:
    """Result of a single status check."""

    timestamp: str
    status: StatusType
    response_time_ms: float
    error_message: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "status": self.status.value,
            "response_time_ms": self.response_time_ms,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


@dataclass
class StatusTransition:
    """Status transition for notifications."""

    from_status: StatusType
    to_status: StatusType
    timestamp: str
    check_count_since_last_transition: int = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "from": self.from_status.value,
            "to": self.to_status.value,
            "timestamp": self.timestamp,
            "checks_since_transition": self.check_count_since_last_transition,
        }


class StatusHistoryLog:
    """Maintains last 20 status checks."""

    MAX_ENTRIES = 20

    def __init__(self):
        """Initialize history log."""
        self.checks: List[StatusCheckResult] = []
        self.transitions: List[StatusTransition] = []

    def add_check(self, result: StatusCheckResult) -> Dict:
        """Add status check result."""
        # Detect transitions
        prev_status = None
        transition = None

        if self.checks:
            prev_status = self.checks[-1].status
            if prev_status != result.status:
                transition = StatusTransition(
                    from_status=prev_status,
                    to_status=result.status,
                    timestamp=result.timestamp,
                    check_count_since_last_transition=len(self.checks),
                )
                self.transitions.append(transition)

        self.checks.append(result)

        # Maintain max 20 entries
        if len(self.checks) > self.MAX_ENTRIES:
            self.checks.pop(0)

        return {
            "status": "added",
            "total_checks": len(self.checks),
            "transition": transition.to_dict() if transition else None,
        }

    def get_recent(self, count: int = 10) -> List[Dict]:
        """Get most recent checks."""
        return [c.to_dict() for c in self.checks[-count:]]

    def get_by_period(self, period: HistoryPeriod) -> List[Dict]:
        """Get checks for a time period."""
        if period == HistoryPeriod.ALL:
            return [c.to_dict() for c in self.checks]

        now = datetime.now()
        filtered = []

        for check in self.checks:
            check_time = datetime.fromisoformat(check.timestamp)
            delta = now - check_time

            include = False
            if period == HistoryPeriod.LAST_HOUR:
                include = delta.total_seconds() <= 3600
            elif period == HistoryPeriod.LAST_DAY:
                include = delta.total_seconds() <= 86400
            elif period == HistoryPeriod.LAST_WEEK:
                include = delta.total_seconds() <= 604800

            if include:
                filtered.append(check.to_dict())

        return filtered

    def get_current_status(self) -> Optional[Dict]:
        """Get current status."""
        if not self.checks:
            return None
        return self.checks[-1].to_dict()

    def get_status_counts(self) -> Dict:
        """Get count of each status type."""
        counts = {s.value: 0 for s in StatusType}
        for check in self.checks:
            counts[check.status.value] += 1
        return counts

    def get_transitions(self) -> List[Dict]:
        """Get all transitions."""
        return [t.to_dict() for t in self.transitions]

    def get_uptime_percentage(self) -> float:
        """Calculate uptime percentage (online/total)."""
        if not self.checks:
            return 0.0
        online_count = sum(1 for c in self.checks if c.status == StatusType.ONLINE)
        return (online_count / len(self.checks)) * 100

    def get_status(self) -> Dict:
        """Get history status."""
        return {
            "total_checks": len(self.checks),
            "max_entries": self.MAX_ENTRIES,
            "current_status": self.get_current_status(),
            "status_counts": self.get_status_counts(),
            "uptime_percentage": self.get_uptime_percentage(),
            "transitions_count": len(self.transitions),
        }

    def clear(self) -> Dict:
        """Clear all history."""
        self.checks.clear()
        self.transitions.clear()
        return {"status": "cleared", "remaining_checks": 0}


class StatusPersistence:
    """Persistent storage for status history (AD-077)."""

    def __init__(self):
        """Initialize persistence layer."""
        self.storage: Dict[str, List[Dict]] = {}
        self.enabled = False

    def enable(self) -> Dict:
        """Enable persistence."""
        self.enabled = True
        return {"status": "persistence_enabled"}

    def save_check(self, endpoint_id: str, check: StatusCheckResult) -> Dict:
        """Save check to persistent storage."""
        if not self.enabled:
            return {"status": "persistence_disabled"}

        if endpoint_id not in self.storage:
            self.storage[endpoint_id] = []

        self.storage[endpoint_id].append(check.to_dict())

        # Limit stored items per endpoint
        if len(self.storage[endpoint_id]) > 100:
            self.storage[endpoint_id].pop(0)

        return {
            "status": "saved",
            "endpoint_id": endpoint_id,
            "stored_count": len(self.storage[endpoint_id]),
        }

    def load_checks(self, endpoint_id: str) -> List[Dict]:
        """Load checks from persistent storage."""
        return self.storage.get(endpoint_id, [])

    def get_status(self) -> Dict:
        """Get persistence status."""
        return {
            "enabled": self.enabled,
            "endpoints_stored": len(self.storage),
            "total_checks_stored": sum(len(checks) for checks in self.storage.values()),
        }


class StatusNotificationManager:
    """Manages notifications for status changes (AD-086)."""

    def __init__(self):
        """Initialize notification manager."""
        self.notifications: List[Dict] = []
        self.enabled = True
        self.subscribers: List[str] = []

    def register_subscriber(self, subscriber_id: str) -> Dict:
        """Register for notifications."""
        if subscriber_id not in self.subscribers:
            self.subscribers.append(subscriber_id)
        return {
            "status": "subscribed",
            "subscriber_id": subscriber_id,
            "total_subscribers": len(self.subscribers),
        }

    def unregister_subscriber(self, subscriber_id: str) -> Dict:
        """Unregister from notifications."""
        if subscriber_id in self.subscribers:
            self.subscribers.remove(subscriber_id)
        return {
            "status": "unsubscribed",
            "subscriber_id": subscriber_id,
            "total_subscribers": len(self.subscribers),
        }

    def notify_transition(self, transition: StatusTransition) -> Dict:
        """Notify subscribers of status transition."""
        if not self.enabled:
            return {"status": "notifications_disabled"}

        notification = {
            "type": "status_transition",
            "transition": transition.to_dict(),
            "timestamp": datetime.now().isoformat(),
            "recipients": len(self.subscribers),
        }
        self.notifications.append(notification)

        return {
            "status": "notified",
            "notification_id": len(self.notifications),
            "recipients": len(self.subscribers),
        }

    def get_notifications(self, limit: int = 10) -> List[Dict]:
        """Get recent notifications."""
        return self.notifications[-limit:]

    def get_status(self) -> Dict:
        """Get notification status."""
        return {
            "enabled": self.enabled,
            "subscribers": len(self.subscribers),
            "total_notifications": len(self.notifications),
        }


class StatusSnapshot:
    """Shareable status snapshot (AD-089)."""

    def __init__(self, history: StatusHistoryLog):
        """Initialize snapshot."""
        self.history = history
        self.created_at = datetime.now().isoformat()
        self.snapshot_id = None

    def generate(self) -> Dict:
        """Generate shareable snapshot."""
        self.snapshot_id = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return {
            "snapshot_id": self.snapshot_id,
            "created_at": self.created_at,
            "current_status": self.history.get_current_status(),
            "recent_checks": self.history.get_recent(10),
            "status_counts": self.history.get_status_counts(),
            "uptime": self.history.get_uptime_percentage(),
            "transitions": self.history.get_transitions(),
        }

    def to_share_url(self, base_url: str = "status.local") -> str:
        """Generate shareable URL."""
        if not self.snapshot_id:
            self.generate()
        return f"{base_url}/snapshots/{self.snapshot_id}"

    def to_markdown(self) -> str:
        """Export snapshot as markdown."""
        snapshot = self.generate()
        current = snapshot.get("current_status", {})
        status = current.get("status", "unknown")

        md = "# Status Snapshot\n\n"
        md += f"**Generated:** {snapshot['created_at']}\n"
        md += f"**ID:** {snapshot['snapshot_id']}\n\n"
        md += f"## Current Status: {status}\n\n"
        md += f"**Uptime:** {snapshot['uptime']:.1f}%\n\n"
        md += "## Status Distribution\n\n"

        counts = snapshot.get("status_counts", {})
        for status_type, count in counts.items():
            md += f"- {status_type}: {count}\n"

        md += "\n## Share\n\n"
        md += f"URL: {self.to_share_url()}\n"

        return md

    def get_status(self) -> Dict:
        """Get snapshot status."""
        return {
            "snapshot_id": self.snapshot_id,
            "created_at": self.created_at,
        }
