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
    from Tools.repo_compare import CANONICAL_URLS, scan_local_repos, parse_github, normalize_git_url, find_git_remote, is_git_repo
except Exception as exc:  # pragma: no cover - import guard
    CANONICAL_URLS = []
    scan_local_repos = None
    parse_github = None
    normalize_git_url = None
    find_git_remote = None
    is_git_repo = None
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
        return {
            "workbench.repo.compare": self.compare_repos,
        }

    def compare_repos(self, scan_path: str = ".") -> Dict[str, Any]:
        if scan_local_repos is None:
            return {
                "ok": False,
                "error": f"repo_compare import failed: {_IMPORT_ERROR}",
            }

        try:
            scan_path = str(Path(scan_path).resolve())
            candidates, git_repos = scan_local_repos(scan_path)
        except Exception as exc:
            logger.warning(f"Repo scan failed: {exc}")
            return {"ok": False, "error": str(exc)}

        exact_match = []
        present_different_remote = []
        present_not_git = []
        missing = []

        seen_paths = set()

        for url in CANONICAL_URLS:
            owner, repo = parse_github(url)
            if repo:
                names_to_check = {repo.lower(), f"{owner.lower()}-{repo.lower()}"}
            else:
                name = url.rstrip("/").split("/")[-1] or url
                names_to_check = {name.lower()}

            found_path = None
            for name in names_to_check:
                if name in candidates:
                    found_path = candidates[name][0]
                    break

            if not found_path:
                missing.append(
                    {"name": repo or list(names_to_check)[0], "canonical_url": url}
                )
                continue

            seen_paths.add(str(Path(found_path).resolve()))

            if is_git_repo(found_path):
                remote = normalize_git_url(find_git_remote(found_path))
                canonical_norm = normalize_git_url(url)
                entry = {
                    "name": repo or Path(found_path).name,
                    "owner": owner,
                    "canonical_url": url,
                    "local_path": found_path,
                    "remote_url": remote,
                }
                if (
                    remote
                    and canonical_norm
                    and remote.rstrip("/") == canonical_norm.rstrip("/")
                ):
                    exact_match.append(entry)
                else:
                    present_different_remote.append(entry)
            else:
                present_not_git.append(
                    {
                        "name": repo or Path(found_path).name,
                        "local_path": found_path,
                    }
                )

        extra_local_repos = []
        for repo_path in git_repos:
            resolved = str(Path(repo_path).resolve())
            if resolved in seen_paths:
                continue
            remote = normalize_git_url(find_git_remote(repo_path))
            extra_local_repos.append(
                {
                    "name": Path(repo_path).name,
                    "local_path": repo_path,
                    "remote_url": remote,
                }
            )

        return {
            "ok": True,
            "scan_path": scan_path,
            "exact_match": exact_match,
            "present_different_remote": present_different_remote,
            "present_not_git": present_not_git,
            "missing": missing,
            "extra_local_repos": extra_local_repos,
        }
