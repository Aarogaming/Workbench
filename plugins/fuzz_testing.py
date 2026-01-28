#!/usr/bin/env python3
"""AAS-321: Fuzz Testing Framework"""

from typing import Dict, List, Any, Callable, Optional
from enum import Enum
import random
import string


class FuzzStrategy(Enum):
    """Fuzzing strategies"""
    RANDOM_BYTES = "random_bytes"
    BOUNDARY_VALUES = "boundary_values"
    MUTATION = "mutation"
    GRAMMAR_BASED = "grammar_based"


class FuzzTest:
    """Fuzz test execution"""

    def __init__(self, test_id: str, target_func: Callable,
                 strategy: FuzzStrategy):
        """Initialize fuzz test"""
        self.test_id = test_id
        self.target_func = target_func
        self.strategy = strategy
        self.test_cases: List[Any] = []
        self.crashes = 0
        self.errors = 0
        self.successes = 0

    def _generate_random_input(self) -> str:
        """Generate random input"""
        length = random.randint(1, 100)
        return ''.join(
            random.choices(
                string.ascii_letters + string.digits, k=length))

    def _generate_boundary_input(self) -> Any:
        """Generate boundary value input"""
        return random.choice([
            "",
            None,
            0,
            -1,
            2147483647,
            float('inf'),
            float('-inf'),
            "x" * 10000
        ])

    def _mutate_input(self, input_data: str) -> str:
        """Mutate existing input"""
        if not input_data:
            return self._generate_random_input()

        data_list = list(input_data)
        mutations = random.randint(1, 3)

        for _ in range(mutations):
            idx = random.randint(0, len(data_list) - 1)
            data_list[idx] = random.choice(string.ascii_letters)

        return ''.join(data_list)

    def run(self, iterations: int = 100) -> Dict[str, Any]:
        """Run fuzz test"""
        results = {
            'test_id': self.test_id,
            'strategy': self.strategy.value,
            'iterations': iterations,
            'successes': 0,
            'errors': 0,
            'crashes': 0,
            'crash_inputs': []
        }

        for _ in range(iterations):
            try:
                if self.strategy == FuzzStrategy.RANDOM_BYTES:
                    input_data = self._generate_random_input()
                elif self.strategy == FuzzStrategy.BOUNDARY_VALUES:
                    input_data = self._generate_boundary_input()
                elif self.strategy == FuzzStrategy.MUTATION:
                    input_data = self._mutate_input(
                        self.test_cases[-1]
                        if self.test_cases else "")
                else:
                    input_data = self._generate_random_input()

                self.test_cases.append(input_data)
                self.target_func(input_data)
                results['successes'] += 1
                self.successes += 1

            except Exception as e:
                error_type = type(e).__name__
                if error_type == 'SegmentationFault':
                    results['crashes'] += 1
                    results['crash_inputs'].append(input_data)
                    self.crashes += 1
                else:
                    results['errors'] += 1
                    self.errors += 1

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get fuzz test statistics"""
        total = self.successes + self.errors + self.crashes

        return {
            'total_inputs': total,
            'successes': self.successes,
            'errors': self.errors,
            'crashes': self.crashes,
            'crash_rate': (
                (self.crashes / total * 100) if total > 0 else 0),
            'unique_inputs': len(set(self.test_cases))
        }


class FuzzTestSuite:
    """Suite of fuzz tests"""

    def __init__(self, suite_id: str):
        """Initialize fuzz test suite"""
        self.suite_id = suite_id
        self.tests: List[FuzzTest] = []
        self.results: List[Dict[str, Any]] = []

    def add_test(self, test: FuzzTest) -> None:
        """Add fuzz test"""
        self.tests.append(test)

    def run_all(self, iterations: int = 100) -> Dict[str, Any]:
        """Run all fuzz tests"""
        overall = {
            'suite_id': self.suite_id,
            'total_tests': len(self.tests),
            'iterations_per_test': iterations,
            'test_results': [],
            'total_crashes': 0,
            'total_errors': 0
        }

        for test in self.tests:
            result = test.run(iterations)
            self.results.append(result)
            overall['test_results'].append(result)

            overall['total_crashes'] += result.get('crashes', 0)
            overall['total_errors'] += result.get('errors', 0)

        return overall

    def get_vulnerability_report(self) -> Dict[str, Any]:
        """Get vulnerability report from fuzz results"""
        crashes = []
        for result in self.results:
            if result.get('crash_inputs'):
                crashes.append({
                    'test_id': result['test_id'],
                    'crash_inputs': result['crash_inputs']
                })

        return {
            'vulnerabilities_found': len(crashes),
            'crash_details': crashes,
            'severity': 'high' if crashes else 'low'
        }


class FuzzTestManager:
    """Manages fuzz testing"""

    def __init__(self):
        """Initialize manager"""
        self.suites: Dict[str, FuzzTestSuite] = {}

    def create_suite(self, suite_id: str) -> FuzzTestSuite:
        """Create new fuzz test suite"""
        suite = FuzzTestSuite(suite_id)
        self.suites[suite_id] = suite
        return suite

    def run_suite(self, suite_id: str,
                  iterations: int = 100) -> Optional[Dict[str, Any]]:
        """Run specific suite"""
        suite = self.suites.get(suite_id)
        if suite:
            return suite.run_all(iterations)
        return None

    def get_all_vulnerabilities(self) -> Dict[str, Any]:
        """Get all found vulnerabilities"""
        all_crashes = []
        for suite in self.suites.values():
            report = suite.get_vulnerability_report()
            all_crashes.extend(report.get('crash_details', []))

        return {
            'total_vulnerabilities': len(all_crashes),
            'crash_reports': all_crashes
        }
