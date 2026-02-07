#!/usr/bin/env python3
"""GUI CLI Wrapper for command-line interface to GUI system (GUI-005).

This module provides a comprehensive CLI wrapper for the GUI system,
including command execution, task management, output formatting, and
context handling.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class CommandType(Enum):
    """CLI command type."""

    ACTION = "action"
    QUERY = "query"
    CONFIG = "config"
    ADMIN = "admin"


class OutputFormat(Enum):
    """Output format type."""

    TEXT = "text"
    JSON = "json"
    YAML = "yaml"
    TABLE = "table"


class ExitCode(Enum):
    """CLI exit codes."""

    SUCCESS = 0
    ERROR = 1
    INVALID_ARGS = 2
    NOT_FOUND = 3
    TIMEOUT = 4


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class CLICommand:
    """CLI command definition."""

    name: str
    category: str
    description: str
    command_type: CommandType
    help_text: str
    aliases: List[str] = field(default_factory=list)
    required_args: List[str] = field(default_factory=list)
    optional_args: List[str] = field(default_factory=list)
    returns_data: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "command_type": self.command_type.value,
            "aliases": self.aliases,
            "required_args": self.required_args,
            "optional_args": self.optional_args,
        }


@dataclass
class CommandContext:
    """Command execution context."""

    command_name: str
    args: List[str] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    output_format: OutputFormat = OutputFormat.TEXT
    verbose: bool = False
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "command_name": self.command_name,
            "args": self.args,
            "kwargs": self.kwargs,
            "output_format": self.output_format.value,
            "verbose": self.verbose,
            "timestamp": self.timestamp,
        }


@dataclass
class CommandResult:
    """Command execution result."""

    command_name: str
    status: TaskStatus
    exit_code: ExitCode
    output: Any = None
    error_message: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "command_name": self.command_name,
            "status": self.status.value,
            "exit_code": self.exit_code.value,
            "output": self.output,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
        }


@dataclass
class CLITask:
    """Task wrapper for CLI execution."""

    task_id: str
    command_name: str
    status: TaskStatus
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[CommandResult] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "command_name": self.command_name,
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result.to_dict() if self.result else None,
        }


class GUICLIWrapper:
    """Wrap GUI system with CLI interface."""

    def __init__(self, app_name: str = "GUI CLI"):
        """Initialize GUI CLI wrapper."""
        self._app_name = app_name
        self._commands: Dict[str, CLICommand] = {}
        self._command_handlers: Dict[str, Callable] = {}
        self._tasks: Dict[str, CLITask] = {}
        self._task_counter = 0
        self._callbacks: Dict[str, List[Callable]] = {
            "command_registered": [],
            "command_executed": [],
            "task_created": [],
            "task_completed": [],
        }
        self._history: List[CommandResult] = []

    def register_command(
        self,
        command: CLICommand,
        handler: Callable,
    ) -> None:
        """Register CLI command with handler."""
        self._commands[command.name] = command

        # Register aliases
        for alias in command.aliases:
            self._commands[alias] = command

        self._command_handlers[command.name] = handler
        self._trigger_callbacks("command_registered", command)

    def get_command(self, name: str) -> Optional[CLICommand]:
        """Get command by name or alias."""
        return self._commands.get(name)

    def list_commands(self, category: Optional[str] = None) -> List[CLICommand]:
        """List all commands, optionally filtered by category."""
        commands = list(self._commands.values())

        if category:
            commands = [c for c in commands if c.category == category]

        # Remove duplicates (aliases)
        seen = set()
        unique_commands = []
        for cmd in commands:
            if cmd.name not in seen:
                seen.add(cmd.name)
                unique_commands.append(cmd)

        return unique_commands

    def execute_command(
        self,
        context: CommandContext,
    ) -> CommandResult:
        """Execute CLI command."""
        start_time = datetime.now(timezone.utc)

        # Find command
        command = self.get_command(context.command_name)
        if not command:
            result = CommandResult(
                command_name=context.command_name,
                status=TaskStatus.FAILED,
                exit_code=ExitCode.NOT_FOUND,
                error_message=f"Command not found: {context.command_name}",
            )
            self._history.append(result)
            return result

        # Get handler
        handler = self._command_handlers.get(command.name)
        if not handler:
            result = CommandResult(
                command_name=context.command_name,
                status=TaskStatus.FAILED,
                exit_code=ExitCode.ERROR,
                error_message=f"No handler for: {context.command_name}",
            )
            self._history.append(result)
            return result

        # Validate arguments
        validation = self._validate_arguments(command, context)
        if validation["valid"] is False:
            result = CommandResult(
                command_name=context.command_name,
                status=TaskStatus.FAILED,
                exit_code=ExitCode.INVALID_ARGS,
                error_message=validation["message"],
            )
            self._history.append(result)
            return result

        # Execute handler
        try:
            output = handler(context)

            duration_ms = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds() * 1000

            result = CommandResult(
                command_name=context.command_name,
                status=TaskStatus.SUCCESS,
                exit_code=ExitCode.SUCCESS,
                output=output,
                duration_ms=duration_ms,
            )
        except Exception as e:
            duration_ms = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds() * 1000

            result = CommandResult(
                command_name=context.command_name,
                status=TaskStatus.FAILED,
                exit_code=ExitCode.ERROR,
                error_message=str(e),
                duration_ms=duration_ms,
            )

        self._history.append(result)
        self._trigger_callbacks("command_executed", result)
        return result

    def _validate_arguments(
        self, command: CLICommand, context: CommandContext
    ) -> Dict[str, Any]:
        """Validate command arguments."""
        # Check required arguments
        for required_arg in command.required_args:
            if required_arg not in context.kwargs:
                return {
                    "valid": False,
                    "message": f"Missing required argument: {required_arg}",
                }

        return {"valid": True}

    def create_task(self, context: CommandContext) -> CLITask:
        """Create CLI task for deferred execution."""
        self._task_counter += 1
        task_id = f"task-{self._task_counter}"

        task = CLITask(
            task_id=task_id,
            command_name=context.command_name,
            status=TaskStatus.PENDING,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        self._tasks[task_id] = task
        self._trigger_callbacks("task_created", task)
        return task

    def execute_task(self, task_id: str) -> Optional[CommandResult]:
        """Execute a pending task."""
        task = self._tasks.get(task_id)
        if not task:
            return None

        if task.status != TaskStatus.PENDING:
            return None

        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now(timezone.utc).isoformat()

        context = CommandContext(command_name=task.command_name)
        result = self.execute_command(context)

        task.status = result.status
        task.completed_at = datetime.now(timezone.utc).isoformat()
        task.result = result

        self._trigger_callbacks("task_completed", task)
        return result

    def format_output(self, data: Any, format_type: OutputFormat) -> str:
        """Format output for display."""
        if format_type == OutputFormat.JSON:
            return json.dumps(data, indent=2, default=str)

        elif format_type == OutputFormat.TABLE:
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], dict):
                    keys = data[0].keys()
                    lines = []
                    header = " | ".join(str(k) for k in keys)
                    lines.append(header)
                    lines.append("-" * len(header))
                    for row in data:
                        lines.append(" | ".join(str(row.get(k, "")) for k in keys))
                    return "\n".join(lines)

            return str(data)

        elif format_type == OutputFormat.YAML:
            # Simple YAML-like formatting
            lines = []
            if isinstance(data, dict):
                for key, value in data.items():
                    lines.append(f"{key}: {value}")
            else:
                lines.append(str(data))
            return "\n".join(lines)

        else:  # TEXT
            return str(data)

    def get_command_history(
        self, status: Optional[TaskStatus] = None
    ) -> List[CommandResult]:
        """Get command execution history."""
        if status is None:
            return self._history.copy()
        return [r for r in self._history if r.status == status]

    def get_task(self, task_id: str) -> Optional[CLITask]:
        """Get task by ID."""
        return self._tasks.get(task_id)

    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[CLITask]:
        """List all tasks, optionally filtered by status."""
        tasks = list(self._tasks.values())

        if status:
            tasks = [t for t in tasks if t.status == status]

        return tasks

    def cancel_task(self, task_id: str) -> bool:
        """Cancel pending task."""
        task = self._tasks.get(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            return True
        return False

    def register_callback(self, event_type: str, callback: Callable) -> None:
        """Register callback for events."""
        if event_type in self._callbacks:
            self._callbacks[event_type].append(callback)

    def _trigger_callbacks(self, event_type: str, data: Any) -> None:
        """Trigger registered callbacks."""
        for callback in self._callbacks.get(event_type, []):
            try:
                callback(data)
            except Exception:
                pass  # Suppress callback errors

    def get_statistics(self) -> Dict[str, Any]:
        """Get CLI statistics."""
        completed = [r for r in self._history if r.status == TaskStatus.SUCCESS]
        failed = [r for r in self._history if r.status == TaskStatus.FAILED]

        return {
            "total_commands": len(self._history),
            "total_tasks": len(self._tasks),
            "successful_commands": len(completed),
            "failed_commands": len(failed),
            "success_rate": (
                len(completed) / len(self._history) * 100 if self._history else 0.0
            ),
            "avg_duration_ms": (
                sum(r.duration_ms for r in self._history) / len(self._history)
                if self._history
                else 0.0
            ),
            "unique_commands": len(set(r.command_name for r in self._history)),
        }

    def export_report(self) -> Dict[str, Any]:
        """Export comprehensive CLI report."""
        return {
            "app_name": self._app_name,
            "commands": [c.to_dict() for c in self.list_commands()],
            "history": [r.to_dict() for r in self._history],
            "tasks": [t.to_dict() for t in self._tasks.values()],
            "statistics": self.get_statistics(),
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "total_commands_registered": len(
                    set(c.name for c in self._commands.values())
                ),
                "total_history_entries": len(self._history),
            },
        }


def create_gui_cli() -> GUICLIWrapper:
    """Create and initialize GUI CLI wrapper."""
    cli = GUICLIWrapper("GUI")

    # Register core commands
    help_cmd = CLICommand(
        name="help",
        category="system",
        description="Show help information",
        command_type=CommandType.QUERY,
        help_text="Display help for commands",
        aliases=["h", "-h", "--help"],
        returns_data=True,
    )
    cli.register_command(
        help_cmd,
        lambda ctx: f"Help: {ctx.command_name}",
    )

    version_cmd = CLICommand(
        name="version",
        category="system",
        description="Show version information",
        command_type=CommandType.QUERY,
        help_text="Display version",
        returns_data=True,
    )
    cli.register_command(
        version_cmd,
        lambda ctx: {"version": "1.0.0", "build": "20260128"},
    )

    return cli


if __name__ == "__main__":
    cli = create_gui_cli()
    print("GUI CLI Wrapper initialized")
    print(f"Commands: {len(cli.list_commands())}")
