#!/usr/bin/env python3
"""AAS-318: Integration Tests Framework"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Callable
from enum import Enum


class TestStatus(Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TestCase:
    """Single integration test case"""
    test_id: str
    name: str
    description: str
    setup: Optional[Callable] = None
    execute: Optional[Callable] = None
    teardown: Optional[Callable] = None
    expected_result: Any = None
    status: TestStatus = TestStatus.PENDING
    error: Optional[str] = None


class IntegrationTestSuite:
    """Suite of integration tests"""

    def __init__(self, suite_id: str):
        """Initialize test suite"""
        self.suite_id = suite_id
        self.tests: List[TestCase] = []
        self.passed = 0
        self.failed = 0
        self.skipped = 0

    def add_test(self, test: TestCase) -> None:
        """Add test to suite"""
        self.tests.append(test)

    def run(self) -> Dict[str, Any]:
        """Run all tests in suite"""
        results = {
            'suite_id': self.suite_id,
            'total': len(self.tests),
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'tests': []
        }

        for test in self.tests:
            test_result = self._run_test(test)
            results['tests'].append(test_result)

            if test.status == TestStatus.PASSED:
                results['passed'] += 1
                self.passed += 1
            elif test.status == TestStatus.FAILED:
                results['failed'] += 1
                self.failed += 1
            elif test.status == TestStatus.SKIPPED:
                results['skipped'] += 1
                self.skipped += 1

        return results

    def _run_test(self, test: TestCase) -> Dict[str, Any]:
        """Run single test"""
        test_result = {
            'test_id': test.test_id,
            'name': test.name,
            'status': 'unknown'
        }

        try:
            test.status = TestStatus.RUNNING

            if test.setup:
                test.setup()

            if test.execute:
                result = test.execute()
            else:
                result = None

            if test.teardown:
                test.teardown()

            test.status = TestStatus.PASSED
            test_result['status'] = 'passed'
            test_result['result'] = result

        except AssertionError as e:
            test.status = TestStatus.FAILED
            test.error = str(e)
            test_result['status'] = 'failed'
            test_result['error'] = str(e)

        except Exception as e:
            test.status = TestStatus.FAILED
            test.error = str(e)
            test_result['status'] = 'failed'
            test_result['error'] = str(e)

        return test_result

    def get_stats(self) -> Dict[str, Any]:
        """Get suite statistics"""
        total = len(self.tests)
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        return {
            'total': total,
            'passed': self.passed,
            'failed': self.failed,
            'skipped': self.skipped,
            'pass_rate': pass_rate
        }


class IntegrationTestManager:
    """Manages multiple test suites"""

    def __init__(self):
        """Initialize manager"""
        self.suites: Dict[str, IntegrationTestSuite] = {}
        self.results: List[Dict[str, Any]] = []

    def create_suite(self, suite_id: str) -> IntegrationTestSuite:
        """Create new test suite"""
        suite = IntegrationTestSuite(suite_id)
        self.suites[suite_id] = suite
        return suite

    def get_suite(self, suite_id: str) -> Optional[IntegrationTestSuite]:
        """Get suite by ID"""
        return self.suites.get(suite_id)

    def run_all(self) -> Dict[str, Any]:
        """Run all test suites"""
        overall = {
            'total_suites': len(self.suites),
            'total_tests': 0,
            'total_passed': 0,
            'total_failed': 0,
            'suite_results': []
        }

        for suite_id, suite in self.suites.items():
            result = suite.run()
            self.results.append(result)

            overall['total_tests'] += result['total']
            overall['total_passed'] += result['passed']
            overall['total_failed'] += result['failed']
            overall['suite_results'].append(result)

        return overall

    def get_summary(self) -> Dict[str, Any]:
        """Get test summary"""
        total_passed = sum(r['passed'] for r in self.results)
        total_tests = sum(r['total'] for r in self.results)
        pass_rate = (
            (total_passed / total_tests * 100)
            if total_tests > 0 else 0)

        return {
            'total_tests': total_tests,
            'total_passed': total_passed,
            'pass_rate': pass_rate,
            'suites_run': len(self.results)
        }
