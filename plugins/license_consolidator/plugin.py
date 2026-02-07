from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List

from core.plugin_manifest import get_hive_metadata
from loguru import logger


def _consolidate(root: Path, apply_changes: bool) -> List[Dict[str, Any]]:
    license_dir = root / "Docs" / "Licenses"
    actions: List[Dict[str, Any]] = []

    actions.append({"action": "mkdir", "path": str(license_dir)})
    if apply_changes:
        license_dir.mkdir(parents=True, exist_ok=True)

    for current_root, _, files in os.walk(root):
        if "Docs" in current_root or "tools" in current_root:
            continue
        for file in files:
            if "license" in file.lower() and file.endswith(".txt"):
                src_path = Path(current_root) / file
                folder_name = Path(current_root).name
                new_name = f"{folder_name}_{file}"
                dest_path = license_dir / new_name
                actions.append({
                    "action": "copy",
                    "from": str(src_path),
                    "to": str(dest_path),
                })
                if apply_changes:
                    shutil.copy2(src_path, dest_path)

    return actions


class Plugin:
    def __init__(self, hub: Any = None, manifest: Dict[str, Any] | None = None):
        self.hub = hub
        self.manifest = manifest or {}
        hive_meta = get_hive_metadata(self.manifest)
        self.hive = str(hive_meta.get("hive") or "workbench").lower()

    def commands(self) -> Dict[str, Any]:
        return {"workbench.license.consolidate": self.consolidate}

    def consolidate(self, root_dir: str = ".", apply_changes: bool = False) -> Dict[str, Any]:
        root = Path(root_dir).resolve()
        if not root.exists():
            return {"ok": False, "error": f"Root not found: {root}"}

        try:
            actions = _consolidate(root, apply_changes)
        except Exception as exc:
            logger.warning(f"License consolidation failed: {exc}")
            return {"ok": False, "error": str(exc)}

        return {
            "ok": True,
            "root_dir": str(root),
            "applied": bool(apply_changes),
            "actions": actions,
        }
