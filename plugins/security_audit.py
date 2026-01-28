#!/usr/bin/env python3
"""AAS-333: Security Audit Framework"""

from dataclasses import dataclass
from typing import Dict, List, Any, Callable, Optional
from enum import Enum


class SeverityLevel(Enum):
    """Security issue severity"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class SecurityIssue:
    """Security issue found during audit"""
    issue_id: str
    title: str
    severity: SeverityLevel
    description: str
    affected_component: str
    recommendation: str


class SecurityAudit:
    """Security audit execution"""

    def __init__(self, audit_id: str):
        """Initialize security audit"""
        self.audit_id = audit_id
        self.checks: Dict[str, Callable] = {}
        self.issues: List[SecurityIssue] = []

    def register_check(self, check_id: str,
                       check_func: Callable) -> None:
        """Register security check"""
        self.checks[check_id] = check_func

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all security checks"""
        results = {
            'audit_id': self.audit_id,
            'total_checks': len(self.checks),
            'check_results': [],
            'issues_found': 0
        }

        for check_id, check_func in self.checks.items():
            try:
                result = check_func()
                if result.get('passed'):
                    status = 'passed'
                else:
                    status = 'failed'
                    if result.get('issue'):
                        self.issues.append(result['issue'])
                        results['issues_found'] += 1

                results['check_results'].append({
                    'check_id': check_id,
                    'status': status,
                    'message': result.get('message', '')
                })

            except Exception as e:
                results['check_results'].append({
                    'check_id': check_id,
                    'status': 'error',
                    'message': str(e)
                })

        return results

    def get_issues_by_severity(
            self,
            severity: SeverityLevel) -> List[SecurityIssue]:
        """Get issues by severity level"""
        return [
            issue for issue in self.issues
            if issue.severity == severity
        ]

    def generate_report(self) -> Dict[str, Any]:
        """Generate security audit report"""
        critical_count = len(
            self.get_issues_by_severity(SeverityLevel.CRITICAL))
        high_count = len(
            self.get_issues_by_severity(SeverityLevel.HIGH))
        medium_count = len(
            self.get_issues_by_severity(SeverityLevel.MEDIUM))
        low_count = len(
            self.get_issues_by_severity(SeverityLevel.LOW))

        severity_score = (
            critical_count * 100 +
            high_count * 50 +
            medium_count * 25 +
            low_count * 10
        )

        return {
            'audit_id': self.audit_id,
            'total_issues': len(self.issues),
            'critical': critical_count,
            'high': high_count,
            'medium': medium_count,
            'low': low_count,
            'severity_score': severity_score,
            'risk_level': self._calculate_risk_level(
                severity_score),
            'issues': [
                {
                    'title': issue.title,
                    'severity': issue.severity.value,
                    'component': issue.affected_component,
                    'recommendation': issue.recommendation
                }
                for issue in self.issues
            ]
        }

    def _calculate_risk_level(self, score: int) -> str:
        """Calculate overall risk level"""
        if score >= 300:
            return 'critical'
        elif score >= 150:
            return 'high'
        elif score >= 50:
            return 'medium'
        else:
            return 'low'


class SecurityAuditManager:
    """Manages security audits"""

    def __init__(self):
        """Initialize audit manager"""
        self.audits: Dict[str, SecurityAudit] = {}
        self.audit_history: List[Dict[str, Any]] = []

    def create_audit(self, audit_id: str) -> SecurityAudit:
        """Create new security audit"""
        audit = SecurityAudit(audit_id)
        self.audits[audit_id] = audit
        return audit

    def run_audit(self, audit_id: str) -> Optional[Dict[str, Any]]:
        """Run security audit"""
        audit = self.audits.get(audit_id)
        if not audit:
            return None

        audit.run_all_checks()
        report = audit.generate_report()
        self.audit_history.append(report)

        return report

    def compare_audits(self, audit_id1: str,
                       audit_id2: str) -> Dict[str, Any]:
        """Compare two audit results"""
        audit1 = self.audits.get(audit_id1)
        audit2 = self.audits.get(audit_id2)

        if not audit1 or not audit2:
            return {'error': 'Audit not found'}

        report1 = audit1.generate_report()
        report2 = audit2.generate_report()

        return {
            'audit1': audit_id1,
            'audit2': audit_id2,
            'issues_change': (
                report2['total_issues'] -
                report1['total_issues']),
            'severity_score_change': (
                report2['severity_score'] -
                report1['severity_score']),
            'improved': (
                report2['total_issues'] <
                report1['total_issues'])
        }

    def get_latest_report(self) -> Optional[Dict[str, Any]]:
        """Get latest audit report"""
        if self.audit_history:
            return self.audit_history[-1]
        return None

    def get_trend(self) -> Dict[str, Any]:
        """Get security trend"""
        if len(self.audit_history) < 2:
            return {'trend': 'insufficient data'}

        latest = self.audit_history[-1]
        previous = self.audit_history[-2]

        trend = 'improving' if (
            latest['total_issues'] <
            previous['total_issues']
        ) else 'degrading'

        return {
            'trend': trend,
            'latest_issues': latest['total_issues'],
            'previous_issues': previous['total_issues']
        }
