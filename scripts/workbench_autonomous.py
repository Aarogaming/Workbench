#!/usr/bin/env python3
"""
Workbench Autonomous Runner

Runs Workbench maintenance tasks continuously with resource-aware throttling.
"""
import sys
from pathlib import Path

# Import shared framework from AAS core
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "core"))
from autonomous_runner import (
    TaskSpec,
    build_parser,
    execute_autonomous_loop,
)


def build_tasks(args) -> list[TaskSpec]:
    """Define Workbench maintenance tasks."""
    workbench_root = Path(__file__).resolve().parents[1]
    py = "python"
    scripts = workbench_root / "scripts"
    
    skip_scorecard = getattr(args, "skip_scorecard", False)
    
    tasks = [
        TaskSpec(
            name="Check secret hygiene",
            command=[py, str(scripts / "check_secret_hygiene.py")],
            heavy=False,
        ),
        TaskSpec(
            name="Check workflow pinning",
            command=[py, str(scripts / "check_workflow_pinning.py")],
            heavy=False,
        ),
        TaskSpec(
            name="Check workflow permissions policy",
            command=[py, str(scripts / "check_workflow_permissions_policy.py")],
            heavy=False,
        ),
        TaskSpec(
            name="Check plugin contracts",
            command=[py, str(scripts / "check_plugin_contracts.py")],
            heavy=False,
        ),
        TaskSpec(
            name="Validate workspace index",
            command=[py, str(scripts / "validate_workspace_index.py")],
            heavy=False,
        ),
        TaskSpec(
            name="Update scorecard history",
            command=[py, str(scripts / "update_scorecard_history.py")],
            heavy=True,
            enabled=not skip_scorecard,
        ),
        TaskSpec(
            name="Check DORA reliability scoreboard",
            command=[py, str(scripts / "check_dora_reliability_scoreboard.py")],
            heavy=False,
        ),
    ]
    
    return [t for t in tasks if t.enabled]


def main():
    parser = build_parser("Workbench")
    parser.add_argument("--skip-scorecard", action="store_true", help="Skip scorecard history update.")
    args = parser.parse_args()
    workbench_root = Path(__file__).resolve().parents[1]
    execute_autonomous_loop("Workbench", workbench_root, build_tasks, args)


if __name__ == "__main__":
    main()
