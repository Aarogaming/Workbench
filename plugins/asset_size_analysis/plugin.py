from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

from core.plugin_manifest import get_hive_metadata
from loguru import logger

DEFAULT_ROOT = Path(__file__).resolve().parents[2]


def _format_size(size: float) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"


def _resolve_root_dir(root_dir: str) -> Path:
    candidate = (root_dir or ".").strip()
    if candidate in {"", "."}:
        return DEFAULT_ROOT
    return Path(candidate).resolve()


class Plugin:
    def __init__(self, hub: Any = None, manifest: Dict[str, Any] | None = None):
        self.hub = hub
        self.manifest = manifest or {}
        hive_meta = get_hive_metadata(self.manifest)
        self.hive = str(hive_meta.get("hive") or "workbench").lower()

    def commands(self) -> Dict[str, Any]:
        return {"workbench.asset.size_analysis": self.analyze_size}

    def analyze_size(self, root_dir: str = ".") -> Dict[str, Any]:
        root = _resolve_root_dir(root_dir)
        if not root.exists():
            return {"ok": False, "error": f"Root not found: {root}"}

        stats: Dict[str, int] = {}
        total_size = 0

        try:
            for root_dir_path, dirs, files in os.walk(root):
                dirs[:] = [d for d in dirs if d.casefold() not in {"tools", ".git"}]
                for file in files:
                    path = Path(root_dir_path) / file
                    try:
                        size = path.stat().st_size
                    except OSError:
                        continue
                    total_size += size
                    category = os.path.relpath(root_dir_path, root).split(os.sep)[0]
                    if category == ".":
                        category = "Root"
                    stats[category] = stats.get(category, 0) + size
        except Exception as exc:
            logger.warning(f"Asset size analysis failed: {exc}")
            return {"ok": False, "error": str(exc)}

        formatted = {
            key: {"bytes": value, "label": _format_size(value)}
            for key, value in sorted(stats.items(), key=lambda item: item[1], reverse=True)
        }

        return {
            "ok": True,
            "root_dir": str(root),
            "total": {"bytes": total_size, "label": _format_size(total_size)},
            "categories": formatted,
        }
