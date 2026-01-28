#!/usr/bin/env python3
import os
import sys
from pathlib import Path

MAX_MB = 100
MAX_BYTES = MAX_MB * 1024 * 1024
IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    "build",
    "dist",
    "target",
    "bin",
    "obj",
}


def should_ignore_dir(name: str) -> bool:
    return name in IGNORE_DIRS or name.startswith(".")


def format_mb(size: int) -> str:
    return f"{size / (1024 * 1024):.2f}MB"


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    issues = []

    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if not should_ignore_dir(d)]
        for filename in files:
            path = Path(root) / filename
            try:
                size = path.stat().st_size
            except OSError:
                continue
            if size > MAX_BYTES:
                issues.append((path, size))

    print(f"Git file size limit: {MAX_MB}MB")
    if not issues:
        print("No oversized files found.")
        return 0

    print(f"Found {len(issues)} oversized files:")
    for path, size in sorted(issues, key=lambda x: x[1], reverse=True):
        rel_path = path.relative_to(repo_root)
        print(f"  - {rel_path}: {format_mb(size)}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
