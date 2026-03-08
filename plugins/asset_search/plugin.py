from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from core.plugin_manifest import get_hive_metadata
from loguru import logger

DEFAULT_ROOT = Path(__file__).resolve().parents[2]


def _resolve_index_path(index_path: str) -> Path:
    index = Path(index_path)
    if index.is_absolute():
        return index
    cwd_candidate = Path.cwd() / index
    if cwd_candidate.exists():
        return cwd_candidate
    return DEFAULT_ROOT / index


class Plugin:
    def __init__(self, hub: Any = None, manifest: Dict[str, Any] | None = None):
        self.hub = hub
        self.manifest = manifest or {}
        hive_meta = get_hive_metadata(self.manifest)
        self.hive = str(hive_meta.get("hive") or "workbench").lower()

    def commands(self) -> Dict[str, Any]:
        return {"workbench.asset.search": self.search_assets}

    def search_assets(
        self,
        query: str,
        index_path: str = "asset_index.json",
        limit: int = 50,
    ) -> Dict[str, Any]:
        index = _resolve_index_path(index_path)
        if not index.exists():
            return {"ok": False, "error": f"Index not found: {index}"}

        try:
            raw = json.loads(index.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                assets = raw
            elif isinstance(raw, dict):
                assets = raw.get("assets") or []
            else:
                raise ValueError("Unsupported index format")
        except Exception as exc:
            logger.warning(f"Asset index read failed: {exc}")
            return {"ok": False, "error": str(exc)}

        needle = query.lower().strip()
        results: List[Dict[str, Any]] = []
        for asset in assets:
            if not isinstance(asset, dict):
                continue
            name = str(asset.get("name", "")).lower()
            category = str(asset.get("category", "")).lower()
            if needle in name or needle in category:
                results.append(asset)

        if limit and limit > 0:
            results = results[:limit]

        return {
            "ok": True,
            "query": query,
            "count": len(results),
            "results": results,
        }
