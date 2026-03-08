from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

from core.plugin_manifest import get_hive_metadata
from loguru import logger

DEFAULT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_EXTENSIONS = (
    ".zip",
    ".7z",
    ".rar",
    ".exe",
    ".url",
    ".txt",
    ".pdf",
    ".md",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".tga",
    ".psd",
    ".svg",
    ".webp",
    ".mp3",
    ".wav",
    ".flac",
    ".ogg",
    ".mp4",
    ".mov",
    ".mkv",
    ".fbx",
    ".obj",
    ".blend",
    ".uasset",
    ".umap",
    ".pak",
    ".unitypackage",
    ".sbsar",
    ".aseprite",
    ".kra",
)


def _get_file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def _resolve_root_dir(root_dir: str) -> Path:
    candidate = (root_dir or ".").strip()
    if candidate in {"", "."}:
        return DEFAULT_ROOT
    return Path(candidate).resolve()


def _index_assets(root_dir: Path, extensions: tuple[str, ...]) -> List[Dict[str, Any]]:
    asset_index: List[Dict[str, Any]] = []
    allowed_extensions = {ext.lower() for ext in extensions}
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d.casefold() not in {"tools", ".git"}]
        for file in files:
            full_path = Path(root) / file
            if full_path.suffix.lower() not in allowed_extensions:
                continue
            rel_path = full_path.relative_to(root_dir)
            asset_index.append(
                {
                    "name": file,
                    "path": str(rel_path).replace("\\", "/"),
                    "size": _get_file_size(full_path),
                    "category": rel_path.parts[0] if len(rel_path.parts) > 1 else "Root",
                    "extension": full_path.suffix.lower(),
                }
            )
    return asset_index


class Plugin:
    def __init__(self, hub: Any = None, manifest: Dict[str, Any] | None = None):
        self.hub = hub
        self.manifest = manifest or {}
        hive_meta = get_hive_metadata(self.manifest)
        self.hive = str(hive_meta.get("hive") or "workbench").lower()

    def commands(self) -> Dict[str, Any]:
        return {"workbench.asset.index": self.index_assets}

    def index_assets(
        self,
        root_dir: str = ".",
        output_path: str = "asset_index.json",
        extensions: List[str] | None = None,
    ) -> Dict[str, Any]:
        root = _resolve_root_dir(root_dir)
        if not root.exists():
            return {"ok": False, "error": f"Root not found: {root}"}

        ext_tuple = tuple(extensions) if extensions else DEFAULT_EXTENSIONS
        try:
            assets = _index_assets(root, ext_tuple)
            target = Path(output_path)
            if not target.is_absolute():
                target = root / target
            target.write_text(json.dumps(assets, indent=2), encoding="utf-8")
        except Exception as exc:
            logger.warning(f"Asset index failed: {exc}")
            return {"ok": False, "error": str(exc)}

        return {
            "ok": True,
            "root_dir": str(root),
            "output_path": str(target),
            "count": len(assets),
        }
