from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from core.plugin_manifest import get_hive_metadata
from loguru import logger

DEFAULT_IGNORE_DIRS = {
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


def _should_ignore_dir(name: str, ignore_dirs: set[str]) -> bool:
    return name in ignore_dirs or name.startswith(".")


def _format_mb(size: int) -> float:
    return round(size / (1024 * 1024), 2)


class Plugin:
    def __init__(self, hub: Any = None, manifest: Dict[str, Any] | None = None):
        self.hub = hub
        self.manifest = manifest or {}
        hive_meta = get_hive_metadata(self.manifest)
        self.hive = str(hive_meta.get("hive") or "workbench").lower()

    def commands(self) -> Dict[str, Any]:
        return {
            "workbench.repo.check_size": self.check_repo_size,
        }

    def check_repo_size(
        self,
        root: str = "",
        max_mb: int = 100,
        ignore_dirs: Optional[Iterable[str]] = None,
        limit: int = 0,
    ) -> Dict[str, Any]:
        repo_root = Path(root) if root else Path(__file__).resolve().parents[3]
        if not repo_root.exists():
            return {"ok": False, "error": f"Root not found: {repo_root}"}

        ignore_set = set(ignore_dirs) if ignore_dirs else set(DEFAULT_IGNORE_DIRS)
        max_bytes = int(max_mb) * 1024 * 1024
        issues: List[Dict[str, Any]] = []

        for dirpath, dirnames, filenames in os.walk(repo_root):
            dirnames[:] = [d for d in dirnames if not _should_ignore_dir(d, ignore_set)]
            for filename in filenames:
                path = Path(dirpath) / filename
                try:
                    size = path.stat().st_size
                except OSError:
                    continue
                if size > max_bytes:
                    issues.append(
                        {
                            "path": str(path.relative_to(repo_root)),
                            "size_bytes": size,
                            "size_mb": _format_mb(size),
                        }
                    )

        issues.sort(key=lambda item: item["size_bytes"], reverse=True)
        if limit and limit > 0:
            issues = issues[:limit]

        ok = len(issues) == 0
        if not ok:
            logger.warning(
                f"Repo size guard found {len(issues)} files over {max_mb}MB"
            )

        return {
            "ok": ok,
            "root": str(repo_root),
            "max_mb": int(max_mb),
            "oversized_count": len(issues),
            "oversized": issues,
        }
