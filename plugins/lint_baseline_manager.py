"""
Lint Baseline Manager - Lint baseline creation and enforcement.

This module provides comprehensive lint management capabilities including
baseline creation, enforcement, and violation tracking (AD-099).

Implements:
- AD-099: Add lint baseline and enforce lint
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Set
from collections import defaultdict
import hashlib


class LintSeverity(Enum):
    """Lint issue severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


class LintRuleCategory(Enum):
    """Categories of lint rules."""

    CORRECTNESS = "correctness"
    PERFORMANCE = "performance"
    SECURITY = "security"
    STYLE = "style"
    BEST_PRACTICE = "best_practice"
    ACCESSIBILITY = "accessibility"


class EnforcementLevel(Enum):
    """Lint enforcement levels."""

    STRICT = "strict"
    BASELINE = "baseline"
    WARN_ONLY = "warn_only"
    DISABLED = "disabled"


class BaselineAction(Enum):
    """Actions for baseline violations."""

    IGNORE = "ignore"
    WARN = "warn"
    ERROR = "error"
    FIX = "fix"


@dataclass
class LintIssue:
    """Represents a single lint issue."""

    rule_id: str
    file_path: str
    line: int
    column: int
    message: str
    severity: LintSeverity
    category: LintRuleCategory
    timestamp: datetime = field(default_factory=datetime.utcnow)
    is_new: bool = True
    auto_fixable: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_hash(self) -> str:
        """Get unique hash for this issue."""
        key = f"{self.rule_id}:{self.file_path}:{self.line}:{self.column}"
        return hashlib.md5(key.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "file_path": self.file_path,
            "line": self.line,
            "column": self.column,
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "timestamp": self.timestamp.isoformat(),
            "is_new": self.is_new,
            "auto_fixable": self.auto_fixable,
            "metadata": self.metadata,
        }


@dataclass
class LintBaseline:
    """Represents a lint baseline snapshot."""

    baseline_id: str
    created_at: datetime
    issues: List[LintIssue] = field(default_factory=list)
    issue_hashes: Set[str] = field(default_factory=set)
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Build issue hash set."""
        if self.issues:
            self.issue_hashes = {issue.get_hash() for issue in self.issues}

    def contains_issue(self, issue: LintIssue) -> bool:
        """Check if baseline contains issue."""
        return issue.get_hash() in self.issue_hashes

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "baseline_id": self.baseline_id,
            "created_at": self.created_at.isoformat(),
            "issue_count": len(self.issues),
            "issues": [i.to_dict() for i in self.issues],
            "description": self.description,
            "metadata": self.metadata,
        }


@dataclass
class LintRuleConfig:
    """Configuration for a lint rule."""

    rule_id: str
    enabled: bool = True
    severity: LintSeverity = LintSeverity.WARNING
    category: LintRuleCategory = LintRuleCategory.STYLE
    baseline_action: BaselineAction = BaselineAction.WARN
    custom_config: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate rule configuration."""
        if not self.rule_id:
            raise ValueError("rule_id required")


@dataclass
class LintRunResult:
    """Result of a lint run."""

    run_id: str
    timestamp: datetime
    files_scanned: int
    issues_found: int
    new_issues: int
    baseline_issues: int
    errors: int
    warnings: int
    duration_ms: float
    passed: bool
    enforcement_level: EnforcementLevel
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp.isoformat(),
            "files_scanned": self.files_scanned,
            "issues_found": self.issues_found,
            "new_issues": self.new_issues,
            "baseline_issues": self.baseline_issues,
            "errors": self.errors,
            "warnings": self.warnings,
            "duration_ms": self.duration_ms,
            "passed": self.passed,
            "enforcement_level": self.enforcement_level.value,
            "metadata": self.metadata,
        }


class LintBaselineManager:
    """
    Manages lint baselines and enforcement.

    Features:
    - Baseline creation and management
    - Issue tracking and comparison
    - Enforcement level configuration
    - Rule management
    - Auto-fix support
    - Violation reporting
    """

    def __init__(self):
        """Initialize the lint baseline manager."""
        self._baselines: Dict[str, LintBaseline] = {}
        self._active_baseline: Optional[str] = None
        self._rules: Dict[str, LintRuleConfig] = {}
        self._issues: List[LintIssue] = []
        self._run_history: List[LintRunResult] = []
        self._enforcement_level = EnforcementLevel.BASELINE

    def create_baseline(
        self,
        baseline_id: str,
        issues: List[LintIssue],
        description: str = "",
    ) -> LintBaseline:
        """
        Create a new lint baseline.

        Args:
            baseline_id: Unique baseline identifier
            issues: List of lint issues to baseline
            description: Optional baseline description

        Returns:
            LintBaseline instance
        """
        baseline = LintBaseline(
            baseline_id=baseline_id,
            created_at=datetime.utcnow(),
            issues=issues.copy(),
            description=description,
        )

        self._baselines[baseline_id] = baseline
        return baseline

    def set_active_baseline(self, baseline_id: str) -> None:
        """Set the active baseline."""
        if baseline_id not in self._baselines:
            raise ValueError(f"Baseline not found: {baseline_id}")
        self._active_baseline = baseline_id

    def get_active_baseline(self) -> Optional[LintBaseline]:
        """Get the active baseline."""
        if self._active_baseline:
            return self._baselines.get(self._active_baseline)
        return None

    def add_rule(self, rule_config: LintRuleConfig) -> None:
        """Add or update a lint rule configuration."""
        self._rules[rule_config.rule_id] = rule_config

    def remove_rule(self, rule_id: str) -> None:
        """Remove a lint rule configuration."""
        self._rules.pop(rule_id, None)

    def get_rule(self, rule_id: str) -> Optional[LintRuleConfig]:
        """Get lint rule configuration."""
        return self._rules.get(rule_id)

    def set_enforcement_level(self, level: EnforcementLevel) -> None:
        """Set global enforcement level."""
        self._enforcement_level = level

    def check_issues(
        self,
        issues: List[LintIssue],
        enforce: bool = True,
    ) -> tuple[List[LintIssue], List[LintIssue]]:
        """
        Check issues against active baseline.

        Args:
            issues: List of issues to check
            enforce: Whether to enforce baseline

        Returns:
            Tuple of (new_issues, baseline_issues)
        """
        baseline = self.get_active_baseline()

        if not baseline or not enforce:
            return issues, []

        new_issues = []
        baseline_issues = []

        for issue in issues:
            if baseline.contains_issue(issue):
                issue.is_new = False
                baseline_issues.append(issue)
            else:
                issue.is_new = True
                new_issues.append(issue)

        return new_issues, baseline_issues

    def run_lint_check(
        self,
        run_id: str,
        issues: List[LintIssue],
        files_scanned: int,
        duration_ms: float,
    ) -> LintRunResult:
        """
        Execute a lint check and record results.

        Args:
            run_id: Unique run identifier
            issues: Issues found during lint
            files_scanned: Number of files scanned
            duration_ms: Duration in milliseconds

        Returns:
            LintRunResult instance
        """
        new_issues, baseline_issues = self.check_issues(issues)

        # Count by severity
        errors = sum(1 for i in new_issues if i.severity == LintSeverity.ERROR)
        warnings = sum(1 for i in new_issues if i.severity == LintSeverity.WARNING)

        # Determine pass/fail based on enforcement level
        passed = True
        if self._enforcement_level == EnforcementLevel.STRICT:
            passed = len(new_issues) == 0
        elif self._enforcement_level == EnforcementLevel.BASELINE:
            passed = errors == 0
        # WARN_ONLY and DISABLED always pass

        result = LintRunResult(
            run_id=run_id,
            timestamp=datetime.utcnow(),
            files_scanned=files_scanned,
            issues_found=len(issues),
            new_issues=len(new_issues),
            baseline_issues=len(baseline_issues),
            errors=errors,
            warnings=warnings,
            duration_ms=duration_ms,
            passed=passed,
            enforcement_level=self._enforcement_level,
        )

        self._run_history.append(result)
        self._issues.extend(issues)

        return result

    def get_fixable_issues(self) -> List[LintIssue]:
        """Get all auto-fixable issues."""
        return [i for i in self._issues if i.auto_fixable]

    def get_issues_by_severity(self, severity: LintSeverity) -> List[LintIssue]:
        """Get issues by severity level."""
        return [i for i in self._issues if i.severity == severity]

    def get_issues_by_category(self, category: LintRuleCategory) -> List[LintIssue]:
        """Get issues by category."""
        return [i for i in self._issues if i.category == category]

    def get_issues_by_file(self, file_path: str) -> List[LintIssue]:
        """Get issues for a specific file."""
        return [i for i in self._issues if i.file_path == file_path]

    def get_run_history(self, limit: Optional[int] = None) -> List[LintRunResult]:
        """Get lint run history."""
        if limit:
            return self._run_history[-limit:]
        return self._run_history.copy()

    def get_statistics(self) -> Dict[str, Any]:
        """Get lint statistics."""
        if not self._issues:
            return {
                "total_issues": 0,
                "new_issues": 0,
                "baseline_issues": 0,
                "by_severity": {},
                "by_category": {},
                "fixable_count": 0,
            }

        by_severity = defaultdict(int)
        by_category = defaultdict(int)

        for issue in self._issues:
            by_severity[issue.severity.value] += 1
            by_category[issue.category.value] += 1

        new_count = sum(1 for i in self._issues if i.is_new)
        baseline_count = len(self._issues) - new_count
        fixable_count = sum(1 for i in self._issues if i.auto_fixable)

        return {
            "total_issues": len(self._issues),
            "new_issues": new_count,
            "baseline_issues": baseline_count,
            "by_severity": dict(by_severity),
            "by_category": dict(by_category),
            "fixable_count": fixable_count,
        }

    def export_baseline(self, baseline_id: str) -> Dict[str, Any]:
        """Export baseline to dictionary."""
        if baseline_id not in self._baselines:
            raise ValueError(f"Baseline not found: {baseline_id}")

        return self._baselines[baseline_id].to_dict()

    def import_baseline(self, baseline_data: Dict[str, Any]) -> LintBaseline:
        """Import baseline from dictionary."""
        issues = []
        for issue_data in baseline_data.get("issues", []):
            issue = LintIssue(
                rule_id=issue_data["rule_id"],
                file_path=issue_data["file_path"],
                line=issue_data["line"],
                column=issue_data["column"],
                message=issue_data["message"],
                severity=LintSeverity(issue_data["severity"]),
                category=LintRuleCategory(issue_data["category"]),
                is_new=issue_data.get("is_new", True),
                auto_fixable=issue_data.get("auto_fixable", False),
                metadata=issue_data.get("metadata", {}),
            )
            issues.append(issue)

        baseline = LintBaseline(
            baseline_id=baseline_data["baseline_id"],
            created_at=datetime.fromisoformat(baseline_data["created_at"]),
            issues=issues,
            description=baseline_data.get("description", ""),
            metadata=baseline_data.get("metadata", {}),
        )

        self._baselines[baseline.baseline_id] = baseline
        return baseline

    def clear_issues(self) -> int:
        """Clear all tracked issues. Returns count cleared."""
        count = len(self._issues)
        self._issues.clear()
        return count

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive lint report."""
        active_baseline = self.get_active_baseline()

        return {
            "enforcement_level": self._enforcement_level.value,
            "active_baseline": (
                active_baseline.baseline_id if active_baseline else None
            ),
            "statistics": self.get_statistics(),
            "recent_runs": [r.to_dict() for r in self.get_run_history(limit=10)],
            "rules": {
                rule_id: {
                    "enabled": rule.enabled,
                    "severity": rule.severity.value,
                    "category": rule.category.value,
                }
                for rule_id, rule in self._rules.items()
            },
        }
