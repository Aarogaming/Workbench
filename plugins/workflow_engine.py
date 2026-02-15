#!/usr/bin/env python3
"""AAS-306: Workflow Execution Engine"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import time
from typing import Any, Callable, Dict, List, Optional


class ExecutionStatus(Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class WorkflowStep:
    """Single step in workflow."""

    step_id: str
    action: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    status: ExecutionStatus = ExecutionStatus.PENDING
    result: Optional[Any] = None


class WorkflowDefinition:
    """Definition of a workflow."""

    def __init__(self, workflow_id: str, name: str):
        self.workflow_id = workflow_id
        self.name = name
        self.steps: List[WorkflowStep] = []
        self.metadata: Dict[str, Any] = {}

    def add_step(self, step: WorkflowStep) -> None:
        self.steps.append(step)

    def get_steps(self) -> List[WorkflowStep]:
        return self.steps.copy()

    def validate(self) -> bool:
        return len(self.steps) > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.workflow_id,
            "name": self.name,
            "steps": [
                {"id": step.step_id, "action": step.action, "inputs": step.inputs}
                for step in self.steps
            ],
            "metadata": self.metadata,
        }


class WorkflowExecutor:
    """Executes workflows with pause/resume cursor semantics."""

    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        self.current_workflow: Optional[WorkflowDefinition] = None
        self.execution_status = ExecutionStatus.PENDING
        self.results: Dict[str, Any] = {}
        self.current_step_index = 0
        self.pause_requested = False
        self.last_error = ""
        self.run_started_at = 0.0
        self.last_run_started_at = 0.0
        self.last_run_completed_at = 0.0
        self.metrics: Dict[str, Any] = {
            "runs_started": 0,
            "runs_completed": 0,
            "runs_failed": 0,
            "runs_paused": 0,
            "steps_succeeded": 0,
            "steps_failed": 0,
            "total_runtime_sec": 0.0,
        }

    def register_handler(self, action: str, handler: Callable) -> None:
        self.handlers[action] = handler

    def _reset_workflow_state(self, workflow: WorkflowDefinition) -> None:
        self.current_workflow = workflow
        self.execution_status = ExecutionStatus.PENDING
        self.results.clear()
        self.current_step_index = 0
        self.pause_requested = False
        self.last_error = ""
        for step in workflow.get_steps():
            step.status = ExecutionStatus.PENDING
            step.result = None

    def execute(
        self,
        workflow: WorkflowDefinition,
        continue_from_current: bool = False,
    ) -> Dict[str, Any]:
        """Execute workflow from start or from the current cursor."""
        if not workflow.validate():
            return {"success": False, "error": "Invalid workflow", "error_code": "invalid_workflow"}

        if (
            not continue_from_current
            or self.current_workflow is not workflow
            or self.execution_status == ExecutionStatus.COMPLETED
        ):
            self._reset_workflow_state(workflow)
        elif self.current_workflow is None:
            self._reset_workflow_state(workflow)

        self.pause_requested = False
        self.execution_status = ExecutionStatus.RUNNING
        self.run_started_at = time.time()
        self.last_run_started_at = self.run_started_at
        self.metrics["runs_started"] = int(self.metrics["runs_started"]) + 1

        start = time.perf_counter()
        steps = workflow.get_steps()
        try:
            while self.current_step_index < len(steps):
                step = steps[self.current_step_index]
                if step.status == ExecutionStatus.COMPLETED:
                    self.current_step_index += 1
                    continue

                if not self._execute_step(step):
                    self.execution_status = ExecutionStatus.FAILED
                    self.last_error = f"Step execution failed: {step.step_id}"
                    self.metrics["runs_failed"] = int(self.metrics["runs_failed"]) + 1
                    return {
                        "success": False,
                        "status": self.execution_status.value,
                        "failed_step": step.step_id,
                        "step_index": self.current_step_index,
                        "error": self.last_error,
                        "error_code": "step_execution_failed",
                        "results": dict(self.results),
                    }

                self.current_step_index += 1
                if self.pause_requested:
                    self.execution_status = ExecutionStatus.PAUSED
                    self.metrics["runs_paused"] = int(self.metrics["runs_paused"]) + 1
                    return {
                        "success": False,
                        "status": self.execution_status.value,
                        "next_step_index": self.current_step_index,
                        "results": dict(self.results),
                    }

            self.execution_status = ExecutionStatus.COMPLETED
            self.metrics["runs_completed"] = int(self.metrics["runs_completed"]) + 1
            return {
                "success": True,
                "status": self.execution_status.value,
                "results": dict(self.results),
            }
        except Exception as exc:
            self.execution_status = ExecutionStatus.FAILED
            self.last_error = str(exc)
            self.metrics["runs_failed"] = int(self.metrics["runs_failed"]) + 1
            return {
                "success": False,
                "status": self.execution_status.value,
                "error": str(exc),
                "error_code": "execution_exception",
                "results": dict(self.results),
            }
        finally:
            duration = time.perf_counter() - start
            self.metrics["total_runtime_sec"] = float(self.metrics["total_runtime_sec"]) + duration
            self.last_run_completed_at = time.time()
            if self.execution_status != ExecutionStatus.RUNNING:
                self.run_started_at = 0.0

    def _execute_step(self, step: WorkflowStep) -> bool:
        if step.action not in self.handlers:
            step.status = ExecutionStatus.FAILED
            self.last_error = f"No handler for action: {step.action}"
            self.metrics["steps_failed"] = int(self.metrics["steps_failed"]) + 1
            return False

        try:
            step.status = ExecutionStatus.RUNNING
            handler = self.handlers[step.action]
            step.result = handler(step.inputs, self.results)
            step.status = ExecutionStatus.COMPLETED
            self.results[step.step_id] = step.result
            self.metrics["steps_succeeded"] = int(self.metrics["steps_succeeded"]) + 1
            return True
        except Exception as exc:
            step.status = ExecutionStatus.FAILED
            self.last_error = str(exc)
            self.metrics["steps_failed"] = int(self.metrics["steps_failed"]) + 1
            return False

    def pause(self) -> bool:
        """Request pause; execution pauses after current step completes."""
        if self.current_workflow is None:
            return False
        self.pause_requested = True
        if self.execution_status in {ExecutionStatus.PENDING, ExecutionStatus.PAUSED}:
            self.execution_status = ExecutionStatus.PAUSED
        return True

    def resume(self) -> Dict[str, Any]:
        """Resume from current cursor instead of restarting the workflow."""
        if self.current_workflow is None:
            return {
                "success": False,
                "error": "No workflow to resume",
                "error_code": "no_workflow",
            }
        if self.execution_status == ExecutionStatus.COMPLETED:
            return {
                "success": True,
                "status": self.execution_status.value,
                "results": dict(self.results),
            }
        self.pause_requested = False
        return self.execute(self.current_workflow, continue_from_current=True)

    def get_status(self) -> Dict[str, Any]:
        total_steps = len(self.current_workflow.get_steps()) if self.current_workflow else 0
        return {
            "status": self.execution_status.value,
            "workflow_id": self.current_workflow.workflow_id if self.current_workflow else None,
            "current_step_index": self.current_step_index,
            "total_steps": total_steps,
            "results_count": len(self.results),
            "pause_requested": self.pause_requested,
            "last_error": self.last_error,
            "last_run_started_at": self.last_run_started_at or None,
            "last_run_completed_at": self.last_run_completed_at or None,
            "metrics": dict(self.metrics),
        }


class WorkflowScheduler:
    """Schedules workflows and enforces trigger/delay semantics."""

    ALLOWED_TRIGGERS = {"manual", "delayed", "immediate", "interval"}

    def __init__(self):
        self.scheduled: Dict[str, Dict[str, Any]] = {}
        self.executor = WorkflowExecutor()
        self.metrics: Dict[str, int] = {
            "scheduled_total": 0,
            "run_requests": 0,
            "run_successes": 0,
            "run_failures": 0,
            "not_ready_rejections": 0,
        }

    def schedule(
        self,
        workflow: WorkflowDefinition,
        trigger: str,
        delay: float = 0.0,
        interval: float = 0.0,
    ) -> str:
        normalized_trigger = str(trigger or "manual").strip().lower()
        if normalized_trigger not in self.ALLOWED_TRIGGERS:
            normalized_trigger = "manual"

        safe_delay = max(0.0, float(delay))
        safe_interval = max(0.0, float(interval))
        created_at = time.time()
        schedule_id = f"sched_{len(self.scheduled)}"
        next_run_at = created_at if normalized_trigger == "immediate" else created_at + safe_delay
        recurring = normalized_trigger == "interval" and safe_interval > 0.0

        self.scheduled[schedule_id] = {
            "schedule_id": schedule_id,
            "workflow": workflow,
            "trigger": normalized_trigger,
            "delay": safe_delay,
            "interval": safe_interval,
            "recurring": recurring,
            "created_at": created_at,
            "next_run_at": next_run_at,
            "last_run_at": None,
            "executed": False,
            "executed_count": 0,
            "last_result": None,
        }
        self.metrics["scheduled_total"] = int(self.metrics["scheduled_total"]) + 1
        return schedule_id

    def run_scheduled(
        self,
        schedule_id: str,
        force: bool = False,
        now: Optional[float] = None,
    ) -> Dict[str, Any]:
        if schedule_id not in self.scheduled:
            return {
                "success": False,
                "error": "Schedule not found",
                "error_code": "schedule_not_found",
            }

        self.metrics["run_requests"] = int(self.metrics["run_requests"]) + 1
        sched = self.scheduled[schedule_id]
        now_ts = float(now) if now is not None else time.time()
        next_run_at = float(sched["next_run_at"])
        trigger = str(sched["trigger"])
        recurring = bool(sched["recurring"])
        already_executed = int(sched["executed_count"]) > 0

        if not recurring and already_executed:
            return {
                "success": False,
                "error": "Schedule already executed",
                "error_code": "already_executed",
                "schedule_id": schedule_id,
            }

        if not force and now_ts < next_run_at:
            self.metrics["not_ready_rejections"] = int(self.metrics["not_ready_rejections"]) + 1
            return {
                "success": False,
                "error": "Schedule is not ready to run",
                "error_code": "schedule_not_ready",
                "schedule_id": schedule_id,
                "retry_after_sec": round(next_run_at - now_ts, 3),
                "next_run_at": next_run_at,
                "trigger": trigger,
            }

        result = self.executor.execute(sched["workflow"])
        sched["executed"] = bool(result.get("success"))
        sched["executed_count"] = int(sched["executed_count"]) + 1
        sched["last_result"] = result
        sched["last_run_at"] = now_ts
        if recurring:
            sched["next_run_at"] = now_ts + float(sched["interval"])
        else:
            sched["next_run_at"] = float("inf")

        if result.get("success"):
            self.metrics["run_successes"] = int(self.metrics["run_successes"]) + 1
        else:
            self.metrics["run_failures"] = int(self.metrics["run_failures"]) + 1

        return {
            "success": bool(result.get("success")),
            "schedule_id": schedule_id,
            "trigger": trigger,
            "executed_count": int(sched["executed_count"]),
            "next_run_at": sched["next_run_at"],
            "result": result,
        }

    def run_due(
        self,
        now: Optional[float] = None,
        limit: int = 0,
    ) -> Dict[str, Any]:
        now_ts = float(now) if now is not None else time.time()
        due: List[str] = []
        for schedule_id, sched in self.scheduled.items():
            trigger = str(sched["trigger"])
            if trigger == "manual":
                continue
            if int(sched["executed_count"]) > 0 and not bool(sched["recurring"]):
                continue
            if float(sched["next_run_at"]) <= now_ts:
                due.append(schedule_id)

        due.sort()
        if limit > 0:
            due = due[:limit]

        results = [self.run_scheduled(schedule_id, force=True, now=now_ts) for schedule_id in due]
        return {"success": True, "now": now_ts, "count": len(results), "results": results}

    def list_scheduled(self) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for schedule_id, sched in self.scheduled.items():
            rows.append(
                {
                    "schedule_id": schedule_id,
                    "trigger": sched["trigger"],
                    "delay": sched["delay"],
                    "interval": sched["interval"],
                    "recurring": sched["recurring"],
                    "created_at": sched["created_at"],
                    "next_run_at": sched["next_run_at"],
                    "last_run_at": sched["last_run_at"],
                    "executed": sched["executed"],
                    "executed_count": sched["executed_count"],
                    "workflow_id": sched["workflow"].workflow_id,
                }
            )
        return rows

    def get_metrics(self) -> Dict[str, int]:
        return dict(self.metrics)

    def cancel_scheduled(self, schedule_id: str) -> bool:
        if schedule_id in self.scheduled:
            del self.scheduled[schedule_id]
            return True
        return False
