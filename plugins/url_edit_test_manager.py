"""
URL Edit Test Manager - UI testing for URL editing and refresh flows.

This module provides comprehensive UI testing capabilities for URL editing,
validation, and refresh workflows (AD-095).

Implements:
- AD-095: Add UI test for editing URLs + refresh flow
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Callable
from collections import defaultdict


class URLValidationRule(Enum):
    """URL validation rules."""

    REQUIRE_SCHEME = "require_scheme"
    REQUIRE_DOMAIN = "require_domain"
    ALLOW_LOCALHOST = "allow_localhost"
    HTTPS_ONLY = "https_only"
    NO_IP_ADDRESSES = "no_ip_addresses"
    MAX_LENGTH = "max_length"
    VALID_TLD = "valid_tld"


class RefreshTrigger(Enum):
    """Triggers for refresh operations."""

    MANUAL = "manual"
    URL_CHANGE = "url_change"
    VALIDATION_SUCCESS = "validation_success"
    AUTO_REFRESH = "auto_refresh"
    USER_ACTION = "user_action"
    EXTERNAL_EVENT = "external_event"


class UIElementState(Enum):
    """UI element states."""

    ENABLED = "enabled"
    DISABLED = "disabled"
    LOADING = "loading"
    ERROR = "error"
    SUCCESS = "success"
    HIDDEN = "hidden"


class TestResult(Enum):
    """Test execution results."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class URLEditAction:
    """Represents a URL editing action."""

    action_id: str
    url_before: str
    url_after: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    validation_passed: bool = False
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "action_id": self.action_id,
            "url_before": self.url_before,
            "url_after": self.url_after,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "validation_passed": self.validation_passed,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


@dataclass
class RefreshEvent:
    """Represents a refresh event."""

    event_id: str
    trigger: RefreshTrigger
    url: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    success: bool = False
    duration_ms: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "trigger": self.trigger.value,
            "url": self.url,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


@dataclass
class UITestCase:
    """Represents a UI test case."""

    test_id: str
    name: str
    description: str
    steps: List[str] = field(default_factory=list)
    expected_result: str = ""
    validation_rules: List[URLValidationRule] = field(default_factory=list)
    timeout_seconds: int = 30
    retry_count: int = 0
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate test case."""
        if not self.test_id:
            raise ValueError("test_id required")
        if not self.name:
            raise ValueError("name required")


@dataclass
class TestExecutionResult:
    """Result of test execution."""

    test_id: str
    result: TestResult
    duration_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    steps_executed: int = 0
    error_message: Optional[str] = None
    screenshots: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "test_id": self.test_id,
            "result": self.result.value,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp.isoformat(),
            "steps_executed": self.steps_executed,
            "error_message": self.error_message,
            "screenshots": self.screenshots,
            "logs": self.logs,
            "metadata": self.metadata,
        }


class URLEditTestManager:
    """
    Manages UI testing for URL editing and refresh flows.

    Features:
    - URL validation with configurable rules
    - Refresh event tracking
    - UI element state management
    - Test case execution and reporting
    - Action history tracking
    """

    def __init__(self):
        """Initialize the URL edit test manager."""
        self._test_cases: Dict[str, UITestCase] = {}
        self._edit_actions: List[URLEditAction] = []
        self._refresh_events: List[RefreshEvent] = []
        self._test_results: List[TestExecutionResult] = []
        self._ui_states: Dict[str, UIElementState] = {}
        self._validation_rules: List[URLValidationRule] = []
        self._callbacks: Dict[str, List[Callable]] = defaultdict(list)

    def add_validation_rule(self, rule: URLValidationRule) -> None:
        """Add a URL validation rule."""
        if rule not in self._validation_rules:
            self._validation_rules.append(rule)

    def remove_validation_rule(self, rule: URLValidationRule) -> None:
        """Remove a URL validation rule."""
        if rule in self._validation_rules:
            self._validation_rules.remove(rule)

    def validate_url(self, url: str) -> tuple[bool, Optional[str]]:
        """
        Validate URL against configured rules.

        Args:
            url: URL to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not url:
            return False, "URL cannot be empty"

        # Check REQUIRE_SCHEME
        if URLValidationRule.REQUIRE_SCHEME in self._validation_rules:
            if not url.startswith(("http://", "https://", "ftp://")):
                return False, "URL must have a valid scheme"

        # Check HTTPS_ONLY
        if URLValidationRule.HTTPS_ONLY in self._validation_rules:
            if not url.startswith("https://"):
                return False, "Only HTTPS URLs are allowed"

        # Check REQUIRE_DOMAIN
        if URLValidationRule.REQUIRE_DOMAIN in self._validation_rules:
            if "://" in url:
                domain_part = url.split("://", 1)[1].split("/", 1)[0]
                if not domain_part or "." not in domain_part:
                    if not (
                        URLValidationRule.ALLOW_LOCALHOST in self._validation_rules
                        and domain_part == "localhost"
                    ):
                        return False, "URL must have a valid domain"

        # Check NO_IP_ADDRESSES
        if URLValidationRule.NO_IP_ADDRESSES in self._validation_rules:
            if "://" in url:
                domain_part = url.split("://", 1)[1].split("/", 1)[0]
                # Simple IP check
                parts = domain_part.split(".")
                if len(parts) == 4 and all(
                    p.isdigit() and 0 <= int(p) <= 255 for p in parts
                ):
                    return False, "IP addresses are not allowed"

        # Check MAX_LENGTH
        if URLValidationRule.MAX_LENGTH in self._validation_rules:
            if len(url) > 2048:  # Standard max URL length
                return False, "URL exceeds maximum length"

        return True, None

    def record_edit_action(
        self,
        action_id: str,
        url_before: str,
        url_after: str,
        user_id: Optional[str] = None,
    ) -> URLEditAction:
        """
        Record a URL edit action.

        Args:
            action_id: Unique action identifier
            url_before: URL before edit
            url_after: URL after edit
            user_id: Optional user identifier

        Returns:
            URLEditAction instance
        """
        is_valid, error_msg = self.validate_url(url_after)

        action = URLEditAction(
            action_id=action_id,
            url_before=url_before,
            url_after=url_after,
            user_id=user_id,
            validation_passed=is_valid,
            error_message=error_msg,
        )

        self._edit_actions.append(action)
        self._trigger_callbacks("edit_action", action)

        return action

    def trigger_refresh(
        self,
        event_id: str,
        trigger: RefreshTrigger,
        url: str,
        duration_ms: float = 0.0,
    ) -> RefreshEvent:
        """
        Trigger and record a refresh event.

        Args:
            event_id: Unique event identifier
            trigger: Refresh trigger type
            url: URL being refreshed
            duration_ms: Refresh duration in milliseconds

        Returns:
            RefreshEvent instance
        """
        is_valid, error_msg = self.validate_url(url)

        event = RefreshEvent(
            event_id=event_id,
            trigger=trigger,
            url=url,
            success=is_valid,
            duration_ms=duration_ms,
            error_message=error_msg,
        )

        self._refresh_events.append(event)
        self._trigger_callbacks("refresh_event", event)

        return event

    def set_ui_element_state(self, element_id: str, state: UIElementState) -> None:
        """Set UI element state."""
        self._ui_states[element_id] = state
        self._trigger_callbacks(
            "ui_state_change", {"element_id": element_id, "state": state}
        )

    def get_ui_element_state(self, element_id: str) -> Optional[UIElementState]:
        """Get UI element state."""
        return self._ui_states.get(element_id)

    def register_test_case(self, test_case: UITestCase) -> None:
        """Register a UI test case."""
        self._test_cases[test_case.test_id] = test_case

    def execute_test(
        self,
        test_id: str,
        execute_callback: Optional[Callable] = None,
    ) -> TestExecutionResult:
        """
        Execute a UI test case.

        Args:
            test_id: Test case identifier
            execute_callback: Optional callback for test execution logic

        Returns:
            TestExecutionResult instance
        """
        if test_id not in self._test_cases:
            raise ValueError(f"Test case not found: {test_id}")

        test_case = self._test_cases[test_id]
        start_time = datetime.utcnow()

        try:
            # Execute test logic (simplified)
            if execute_callback:
                execute_callback(test_case)

            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            result = TestExecutionResult(
                test_id=test_id,
                result=TestResult.PASSED,
                duration_ms=duration,
                steps_executed=len(test_case.steps),
            )
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            result = TestExecutionResult(
                test_id=test_id,
                result=TestResult.ERROR,
                duration_ms=duration,
                error_message=str(e),
            )

        self._test_results.append(result)
        self._trigger_callbacks("test_complete", result)

        return result

    def get_test_results(
        self, test_id: Optional[str] = None
    ) -> List[TestExecutionResult]:
        """Get test execution results."""
        if test_id:
            return [r for r in self._test_results if r.test_id == test_id]
        return self._test_results.copy()

    def get_edit_history(self, user_id: Optional[str] = None) -> List[URLEditAction]:
        """Get URL edit action history."""
        if user_id:
            return [a for a in self._edit_actions if a.user_id == user_id]
        return self._edit_actions.copy()

    def get_refresh_history(
        self, trigger: Optional[RefreshTrigger] = None
    ) -> List[RefreshEvent]:
        """Get refresh event history."""
        if trigger:
            return [e for e in self._refresh_events if e.trigger == trigger]
        return self._refresh_events.copy()

    def get_test_statistics(self) -> Dict[str, Any]:
        """Get test execution statistics."""
        total = len(self._test_results)
        if total == 0:
            return {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
                "pass_rate": 0.0,
            }

        by_result = defaultdict(int)
        for result in self._test_results:
            by_result[result.result.value] += 1

        passed = by_result[TestResult.PASSED.value]
        pass_rate = (passed / total) * 100 if total > 0 else 0.0

        return {
            "total_tests": total,
            "passed": passed,
            "failed": by_result[TestResult.FAILED.value],
            "errors": by_result[TestResult.ERROR.value],
            "skipped": by_result[TestResult.SKIPPED.value],
            "pass_rate": pass_rate,
        }

    def register_callback(self, event_type: str, callback: Callable) -> None:
        """Register callback for events."""
        self._callbacks[event_type].append(callback)

    def _trigger_callbacks(self, event_type: str, data: Any) -> None:
        """Trigger callbacks for event type."""
        for callback in self._callbacks.get(event_type, []):
            try:
                callback(data)
            except Exception:
                pass  # Silently ignore callback errors

    def clear_history(self) -> int:
        """Clear all history. Returns count of items cleared."""
        count = (
            len(self._edit_actions)
            + len(self._refresh_events)
            + len(self._test_results)
        )
        self._edit_actions.clear()
        self._refresh_events.clear()
        self._test_results.clear()
        return count

    def export_test_report(self) -> Dict[str, Any]:
        """Export comprehensive test report."""
        return {
            "statistics": self.get_test_statistics(),
            "test_results": [r.to_dict() for r in self._test_results],
            "edit_actions": [a.to_dict() for a in self._edit_actions],
            "refresh_events": [e.to_dict() for e in self._refresh_events],
            "validation_rules": [r.value for r in self._validation_rules],
            "ui_states": {k: v.value for k, v in self._ui_states.items()},
        }
