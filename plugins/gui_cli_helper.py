#!/usr/bin/env python3
"""GUI-001: GUI CLI Task Helper"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class CLITask:
    """CLI task definition"""

    name: str
    description: str
    command: str
    category: str
    help_text: str


class GUICLIHelper:
    """GUI CLI task helper"""

    def __init__(self):
        """Initialize CLI helper"""
        self.tasks: Dict[str, CLITask] = {}
        self.categories: Dict[str, List[str]] = {}

    def register_task(self, task: CLITask) -> None:
        """Register CLI task"""
        self.tasks[task.name] = task

        if task.category not in self.categories:
            self.categories[task.category] = []
        self.categories[task.category].append(task.name)

    def get_task(self, name: str) -> Optional[CLITask]:
        """Get task by name"""
        return self.tasks.get(name)

    def list_tasks(self) -> List[Dict[str, Any]]:
        """List all tasks"""
        return [
            {
                "name": task.name,
                "description": task.description,
                "category": task.category,
            }
            for task in self.tasks.values()
        ]

    def list_by_category(self, category: str) -> List[str]:
        """List tasks by category"""
        return self.categories.get(category, [])

    def get_help(self, task_name: str) -> str:
        """Get help for task"""
        task = self.tasks.get(task_name)
        if task:
            return task.help_text
        return "Task not found"

    def execute(
        self, task_name: str, args: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Execute CLI task"""
        task = self.tasks.get(task_name)
        if not task:
            return {"success": False, "error": "Task not found"}

        return {
            "success": True,
            "task": task.name,
            "command": task.command,
            "args": args or [],
            "status": "executed",
        }

    def get_documentation(self) -> Dict[str, Any]:
        """Get full documentation"""
        docs = {"total_tasks": len(self.tasks), "categories": {}}

        for category, tasks in self.categories.items():
            docs["categories"][category] = [
                {"name": name, "description": self.tasks[name].description}
                for name in tasks
            ]

        return docs
