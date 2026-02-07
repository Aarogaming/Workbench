from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from core.plugin_manifest import get_hive_metadata
from loguru import logger


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
        index = Path(index_path)
        if not index.is_absolute():
            index = Path.cwd() / index
        if not index.exists():
            return {"ok": False, "error": f"Index not found: {index}"}

        try:
            assets = json.loads(index.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning(f"Asset index read failed: {exc}")
            return {"ok": False, "error": str(exc)}

        needle = query.lower().strip()
        results: List[Dict[str, Any]] = []
        for asset in assets:
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
