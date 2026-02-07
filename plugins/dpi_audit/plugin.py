from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

from core.plugin_manifest import get_hive_metadata
from loguru import logger

WORKBENCH_ROOT = Path(__file__).resolve().parents[2]
if str(WORKBENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKBENCH_ROOT))

try:
    from Tools.dpi_audit import get_dpi_scaling
except Exception as exc:  # pragma: no cover - import guard
    get_dpi_scaling = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


class Plugin:
    def __init__(self, hub: Any = None, manifest: Dict[str, Any] | None = None):
        self.hub = hub
        self.manifest = manifest or {}
        hive_meta = get_hive_metadata(self.manifest)
        self.hive = str(hive_meta.get("hive") or "workbench").lower()

    def commands(self) -> Dict[str, Any]:
        return {"workbench.dpi.audit": self.audit_dpi}

    def audit_dpi(self) -> Dict[str, Any]:
        if get_dpi_scaling is None:
            return {
                "ok": False,
                "error": f"dpi_audit import failed: {_IMPORT_ERROR}",
            }
        try:
            scaling = float(get_dpi_scaling())
        except Exception as exc:
            logger.warning(f"DPI audit failed: {exc}")
            return {"ok": False, "error": str(exc)}

        status = "baseline" if scaling == 1.0 else "scaled"
        return {
            "ok": True,
            "scaling": scaling,
            "status": status,
        }
