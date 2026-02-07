from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List

from core.plugin_manifest import get_hive_metadata
from loguru import logger


def _cleanup_names(root_dir: Path, apply_changes: bool) -> List[Dict[str, Any]]:
    actions: List[Dict[str, Any]] = []
    for root, _, files in os.walk(root_dir, topdown=False):
        if "tools" in root or ".git" in root:
            continue
        for name in files:
            new_name = name.replace("+", " ").replace("%20", " ")
            if "(1)" in new_name:
                new_name = new_name.replace("(1)", "").strip()
            if new_name == name:
                continue
            old_path = Path(root) / name
            new_path = Path(root) / new_name
            if new_path.exists():
                actions.append({
                    "action": "delete",
                    "path": str(old_path),
                    "reason": "duplicate",
                })
                if apply_changes:
                    old_path.unlink()
            else:
                actions.append({
                    "action": "rename",
                    "from": str(old_path),
                    "to": str(new_path),
                })
                if apply_changes:
                    old_path.rename(new_path)
    return actions


def _restructure_assets(root_dir: Path, apply_changes: bool) -> List[Dict[str, Any]]:
    actions: List[Dict[str, Any]] = []
    dirs_to_create = [
        "Visuals/LUTs",
        "Tools/Software",
        "Audio/SFX",
        "Audio/Music",
        "Audio/Overlays",
    ]
    for rel_path in dirs_to_create:
        target = root_dir / rel_path
        actions.append({"action": "mkdir", "path": str(target)})
        if apply_changes:
            target.mkdir(parents=True, exist_ok=True)

    eldamar_path = root_dir / "Audio" / "Eldamar Studios"
    if eldamar_path.exists():
        for file in eldamar_path.iterdir():
            if not file.is_file():
                continue
            if "LUTs" in file.name:
                dest = root_dir / "Visuals" / "LUTs" / file.name
            elif any(tag in file.name for tag in ["Backgrounds", "Overlays", "Transitions", "Titles"]):
                dest = root_dir / "Audio" / "Overlays" / file.name
            elif any(tag in file.name for tag in ["Explosions", "Particles", "Impact", "Fire"]):
                dest = root_dir / "Audio" / "SFX" / file.name
            else:
                continue
            actions.append({"action": "move", "from": str(file), "to": str(dest)})
            if apply_changes:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file), str(dest))

    programs_path = root_dir / "Audio" / "Programs"
    if programs_path.exists():
        for file in programs_path.iterdir():
            dest = root_dir / "Tools" / "Software" / file.name
            actions.append({"action": "move", "from": str(file), "to": str(dest)})
            if apply_changes:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file), str(dest))
        actions.append({"action": "rmdir", "path": str(programs_path)})
        if apply_changes:
            try:
                programs_path.rmdir()
            except OSError:
                pass

    return actions


class Plugin:
    def __init__(self, hub: Any = None, manifest: Dict[str, Any] | None = None):
        self.hub = hub
        self.manifest = manifest or {}
        hive_meta = get_hive_metadata(self.manifest)
        self.hive = str(hive_meta.get("hive") or "workbench").lower()

    def commands(self) -> Dict[str, Any]:
        return {"workbench.asset.cleanup": self.cleanup_assets}

    def cleanup_assets(self, root_dir: str = ".", apply_changes: bool = False) -> Dict[str, Any]:
        root = Path(root_dir).resolve()
        if not root.exists():
            return {"ok": False, "error": f"Root not found: {root}"}

        try:
            rename_actions = _cleanup_names(root, apply_changes)
            structure_actions = _restructure_assets(root, apply_changes)
        except Exception as exc:
            logger.warning(f"Asset cleanup failed: {exc}")
            return {"ok": False, "error": str(exc)}

        return {
            "ok": True,
            "root_dir": str(root),
            "applied": bool(apply_changes),
            "actions": rename_actions + structure_actions,
        }
