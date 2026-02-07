#!/usr/bin/env python3
"""AAS-320: Load Testing Suite"""

from dataclasses import dataclass
from typing import Dict, List, Any, Callable, Optional
from enum import Enum


class LoadPattern(Enum):
    """Load testing patterns"""

    RAMP = "ramp"
    SPIKE = "spike"
    CONSTANT = "constant"
    WAVE = "wave"


@dataclass
class LoadConfig:
    """Load test configuration"""

    pattern: LoadPattern = LoadPattern.CONSTANT
    initial_load: int = 10
    peak_load: int = 100
    duration_seconds: int = 60
    ramp_time_seconds: int = 30


class LoadTest:
    """Single load test execution"""

    def __init__(self, test_id: str, test_func: Callable, config: LoadConfig):
        """Initialize load test"""
        self.test_id = test_id
        self.test_func = test_func
        self.config = config
        self.results: List[Dict[str, Any]] = []
        self.errors = 0
        self.successes = 0

    def run(self) -> Dict[str, Any]:
        """Run load test"""
        results = {
            "test_id": self.test_id,
            "pattern": self.config.pattern.value,
            "total_requests": 0,
            "successful": 0,
            "failed": 0,
            "response_times": [],
        }

        for i in range(self.config.initial_load):
            try:
                response_time = self.test_func()
                results["response_times"].append(response_time)
                results["successful"] += 1
                self.successes += 1
            except Exception:
                results["failed"] += 1
                self.errors += 1

        results["total_requests"] = results["successful"] + results["failed"]

        if results["response_times"]:
            results["avg_response_time"] = sum(results["response_times"]) / len(
                results["response_times"]
            )
            results["min_response_time"] = min(results["response_times"])
            results["max_response_time"] = max(results["response_times"])

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get test statistics"""
        total = self.successes + self.errors
        success_rate = (self.successes / total * 100) if total > 0 else 0

        return {
            "successes": self.successes,
            "errors": self.errors,
            "total": total,
            "success_rate": success_rate,
        }


class LoadTestSuite:
    """Suite of load tests"""

    def __init__(self, suite_id: str):
        """Initialize load test suite"""
        self.suite_id = suite_id
        self.tests: List[LoadTest] = []
        self.results: List[Dict[str, Any]] = []

    def add_test(self, test: LoadTest) -> None:
        """Add test to suite"""
        self.tests.append(test)

    def run_all(self) -> Dict[str, Any]:
        """Run all load tests"""
        overall = {
            "suite_id": self.suite_id,
            "total_tests": len(self.tests),
            "test_results": [],
        }

        total_requests = 0
        total_successful = 0
        total_failed = 0

        for test in self.tests:
            result = test.run()
            self.results.append(result)
            overall["test_results"].append(result)

            total_requests += result.get("total_requests", 0)
            total_successful += result.get("successful", 0)
            total_failed += result.get("failed", 0)

        overall["total_requests"] = total_requests
        overall["total_successful"] = total_successful
        overall["total_failed"] = total_failed

        if total_requests > 0:
            overall["success_rate"] = total_successful / total_requests * 100

        return overall

    def get_performance_baseline(self) -> Dict[str, Any]:
        """Get performance baseline from results"""
        if not self.results:
            return {"baseline": "no data"}

        all_response_times = []
        for result in self.results:
            all_response_times.extend(result.get("response_times", []))

        if not all_response_times:
            return {"baseline": "no response times"}

        return {
            "avg_response_time": (sum(all_response_times) / len(all_response_times)),
            "min_response_time": min(all_response_times),
            "max_response_time": max(all_response_times),
            "total_samples": len(all_response_times),
        }


class LoadTestManager:
    """Manages load testing"""

    def __init__(self):
        """Initialize manager"""
        self.suites: Dict[str, LoadTestSuite] = {}

    def create_suite(self, suite_id: str) -> LoadTestSuite:
        """Create new load test suite"""
        suite = LoadTestSuite(suite_id)
        self.suites[suite_id] = suite
        return suite

    def run_suite(self, suite_id: str) -> Optional[Dict[str, Any]]:
        """Run specific suite"""
        suite = self.suites.get(suite_id)
        if suite:
            return suite.run_all()
        return None

    def run_all_suites(self) -> Dict[str, Any]:
        """Run all suites"""
        results = {"total_suites": len(self.suites), "suite_results": []}

        for suite_id, suite in self.suites.items():
            result = suite.run_all()
            results["suite_results"].append(result)

        return results
