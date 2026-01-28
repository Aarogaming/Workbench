#!/usr/bin/env python3
"""AAS-306: Workflow Execution Engine"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import time


class ExecutionStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class WorkflowStep:
    """Single step in workflow"""
    step_id: str
    action: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    status: ExecutionStatus = ExecutionStatus.PENDING
    result: Optional[Any] = None


class WorkflowDefinition:
    """Definition of a workflow"""

    def __init__(self, workflow_id: str, name: str):
        """Initialize workflow definition"""
        self.workflow_id = workflow_id
        self.name = name
        self.steps: List[WorkflowStep] = []
        self.metadata: Dict[str, Any] = {}

    def add_step(self, step: WorkflowStep) -> None:
        """Add step to workflow"""
        self.steps.append(step)

    def get_steps(self) -> List[WorkflowStep]:
        """Get all steps"""
        return self.steps.copy()

    def validate(self) -> bool:
        """Validate workflow structure"""
        return len(self.steps) > 0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize workflow"""
        return {
            'id': self.workflow_id,
            'name': self.name,
            'steps': [
                {
                    'id': s.step_id,
                    'action': s.action,
                    'inputs': s.inputs
                }
                for s in self.steps
            ],
            'metadata': self.metadata
        }


class WorkflowExecutor:
    """Executes workflows"""

    def __init__(self):
        """Initialize executor"""
        self.handlers: Dict[str, Callable] = {}
        self.current_workflow: Optional[WorkflowDefinition] = None
        self.execution_status = ExecutionStatus.PENDING
        self.results: Dict[str, Any] = {}

    def register_handler(self, action: str,
                        handler: Callable) -> None:
        """Register action handler"""
        self.handlers[action] = handler

    def execute(self, workflow: WorkflowDefinition) -> Dict[str, Any]:
        """Execute workflow"""
        if not workflow.validate():
            return {
                'success': False,
                'error': 'Invalid workflow'
            }

        self.current_workflow = workflow
        self.execution_status = ExecutionStatus.RUNNING
        self.results.clear()

        try:
            for step in workflow.get_steps():
                if not self._execute_step(step):
                    self.execution_status = ExecutionStatus.FAILED
                    return {
                        'success': False,
                        'failed_step': step.step_id,
                        'error': 'Step execution failed'
                    }

            self.execution_status = ExecutionStatus.COMPLETED
            return {
                'success': True,
                'results': self.results
            }
        except Exception as e:
            self.execution_status = ExecutionStatus.FAILED
            return {
                'success': False,
                'error': str(e)
            }

    def _execute_step(self, step: WorkflowStep) -> bool:
        """Execute single step"""
        if step.action not in self.handlers:
            return False

        try:
            step.status = ExecutionStatus.RUNNING
            handler = self.handlers[step.action]
            step.result = handler(step.inputs, self.results)
            step.status = ExecutionStatus.COMPLETED
            self.results[step.step_id] = step.result
            return True
        except Exception:
            step.status = ExecutionStatus.FAILED
            return False

    def pause(self) -> None:
        """Pause workflow execution"""
        self.execution_status = ExecutionStatus.PAUSED

    def resume(self) -> Dict[str, Any]:
        """Resume workflow execution"""
        if self.current_workflow is None:
            return {'success': False}

        self.execution_status = ExecutionStatus.RUNNING
        return self.execute(self.current_workflow)

    def get_status(self) -> Dict[str, Any]:
        """Get execution status"""
        return {
            'status': self.execution_status.value,
            'workflow_id': (
                self.current_workflow.workflow_id
                if self.current_workflow else None),
            'results_count': len(self.results)
        }


class WorkflowScheduler:
    """Schedule workflows for execution"""

    def __init__(self):
        """Initialize scheduler"""
        self.scheduled: Dict[str, Dict[str, Any]] = {}
        self.executor = WorkflowExecutor()

    def schedule(self, workflow: WorkflowDefinition,
                 trigger: str, delay: float = 0.0) -> str:
        """Schedule workflow for execution"""
        schedule_id = f"sched_{len(self.scheduled)}"
        self.scheduled[schedule_id] = {
            'workflow': workflow,
            'trigger': trigger,
            'delay': delay,
            'created_at': time.time(),
            'executed': False
        }
        return schedule_id

    def run_scheduled(self, schedule_id: str) -> Dict[str, Any]:
        """Run scheduled workflow"""
        if schedule_id not in self.scheduled:
            return {'success': False}

        sched = self.scheduled[schedule_id]
        result = self.executor.execute(sched['workflow'])
        sched['executed'] = True
        sched['executed_at'] = time.time()
        return result

    def list_scheduled(self) -> List[Dict[str, Any]]:
        """List scheduled workflows"""
        return list(self.scheduled.values())

    def cancel_scheduled(self, schedule_id: str) -> bool:
        """Cancel scheduled workflow"""
        if schedule_id in self.scheduled:
            del self.scheduled[schedule_id]
            return True
        return False
