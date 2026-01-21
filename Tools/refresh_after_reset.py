import requests, json, datetime, os, time
from typing import Any, Dict
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORT_PATH = DATA_DIR / "repo_analysis_report.json"
SOURCES_PATH = DATA_DIR / "wizard101_data_sources.json"
PLAN_PATH = ROOT / "docs" / "project_integration_plan.json"

with REPORT_PATH.open("r", encoding="utf-8") as f:
    existing = json.load(f)
repo_urls = [r.get("html_url") for r in existing.get("repos", []) if r.get("html_url")]
now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")

session = requests.Session()
session.headers.update(
    {
        "User-Agent": "wizard101-smart-trainer-metadata",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
)

kw_map = {
    "RL_training": ["rl", "reinforcement learning", "gym", "unity", "agent", "rllib"],
    "Model_based_RL": ["dreamer", "model-based"],
    "Imitation_Learning": ["imitation", "behavior cloning"],
    "Vision_OCR": [
        "vision",
        "ocr",
        "yolo",
        "detectron",
        "object detection",
        "template",
        "screenshot",
        "image recognition",
        "opencv",
    ],
    "GUI_Automation": ["automation", "mouse", "keyboard", "gui automation", "input"],
    "Pathfinding_Navigation": ["pathfinding", "navigation", "navmesh", "recast"],
    "Inventory_Image_Categorization": [
        "inventory",
        "dataset",
        "annotation",
        "label",
        "cvat",
        "label-studio",
    ],
    "Installer_Packaging": [
        "installer",
        "packaging",
        "electron",
        "pyinstaller",
        "builder",
    ],
    "Dev_Tools_Integrations": [
        "logging",
        "tracking",
        "wandb",
        "mlflow",
        "ci",
        "metrics",
    ],
    "Dashboard_UI": [
        "dashboard",
        "ui",
        "viewer",
        "streamlit",
        "dearpygui",
        "pysimplegui",
    ],
}
lang_bonus = {"Python", "JavaScript", "TypeScript", "C#", "C++"}


def license_category(spdx):
    if not spdx:
        return "unknown", "unknown"
    su = spdx.upper()
    permissive = {
        "MIT",
        "BSD-3-CLAUSE",
        "BSD-2-CLAUSE",
        "APACHE-2.0",
        "ISC",
        "UNLICENSE",
    }
    copyleft = {"GPL-3.0", "GPL-2.0", "LGPL-3.0", "LGPL-2.1", "AGPL-3.0"}
    if su in permissive:
        return "permissive", True
    if su in copyleft:
        return "copyleft", False
    return "other", "unknown"


def axis_score(axis, text, stars, pushed_at, primary_language):
    stars = stars or 0
    base = min(50, int(50 * stars / 10000))
    bonus = 0
    if pushed_at:
        try:
            dt = datetime.datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            days = (datetime.datetime.now(datetime.timezone.utc) - dt).days
            if days <= 365:
                bonus = 15
            elif days <= 730:
                bonus = 8
        except Exception:
            pass
    text_low = text.lower()
    kw_count = sum(1 for kw in kw_map.get(axis, []) if kw.lower() in text_low)
    kw_points = min(25, kw_count * 8)
    return max(0, min(100, base + bonus + kw_points))


def ease_score(text, stars, pushed_at, primary_language):
    stars = stars or 0
    base = min(50, int(50 * stars / 10000))
    bonus = 0
    if pushed_at:
        try:
            dt = datetime.datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            days = (datetime.datetime.now(datetime.timezone.utc) - dt).days
            if days <= 365:
                bonus += 15
            elif days <= 730:
                bonus += 8
        except Exception:
            pass
    if primary_language in lang_bonus:
        bonus += 10
    text_low = text.lower()
    if "example" in text_low or "tutorial" in text_low or "demo" in text_low:
        bonus += 10
    if "test" in text_low or "ci" in text_low or "docs" in text_low:
        bonus += 5
    return max(0, min(100, base + bonus))


def recommendation_from_scores(scores, license_cat):
    if scores.get("Vision_OCR", 0) >= 60 or scores.get("RL_training", 0) >= 60:
        return (
            "use_directly"
            if license_cat in {"permissive", "other"}
            else "fork_and_extend"
        )
    if scores.get("Vision_OCR", 0) >= 40 or scores.get("RL_training", 0) >= 40:
        return "fork_and_extend"
    if (
        scores.get("Installer_Packaging", 0) >= 40
        or scores.get("GUI_Automation", 0) >= 40
    ):
        return "use_directly"
    return "study_and_extract_patterns"


def maybe_wait(resp):
    rem = resp.headers.get("X-RateLimit-Remaining")
    reset = resp.headers.get("X-RateLimit-Reset")
    try:
        if rem is not None and int(rem) <= 1 and reset:
            wait = max(0, int(reset) - int(time.time()) + 2)
            if wait > 0:
                time.sleep(wait)
    except Exception:
        pass


repos_out = []
for url in repo_urls:
    entry = {"owner": None, "name": None, "html_url": url}
    if "github.com" not in url:
        entry.update(
            {
                "description": None,
                "topics": [],
                "license": None,
                "stars": 0,
                "forks": 0,
                "open_issues": 0,
                "primary_language": None,
                "created_at": None,
                "pushed_at": None,
                "size_kb": 0,
                "readme_excerpt": None,
                "keywords": [],
                "scores": {},
                "scoring_basis": "Non-GitHub URL",
                "license_assessment": {
                    "category": "unknown",
                    "reuse_allowed": "unknown",
                },
                "recommendation": "low_priority",
                "suggested_next_steps": ["Manual review needed"],
                "error": "Non-GitHub entry",
            }
        )
        repos_out.append(entry)
        continue
    try:
        owner, name = url.rstrip("/").split("/")[-2:]
        entry["owner"] = owner
        entry["name"] = name
        api_url = f"https://api.github.com/repos/{owner}/{name}"
        resp = session.get(api_url, timeout=15)
        if resp.status_code != 200:
            entry["error"] = f"HTTP {resp.status_code}"
            repos_out.append(entry)
            maybe_wait(resp)
            continue
        meta = resp.json()
        desc = meta.get("description") or ""
        text_blob = desc
        scores = {
            axis: axis_score(
                axis,
                text_blob,
                meta.get("stargazers_count"),
                meta.get("pushed_at"),
                meta.get("language"),
            )
            for axis in kw_map.keys()
        }
        scores["Ease_of_Integration"] = ease_score(
            text_blob,
            meta.get("stargazers_count"),
            meta.get("pushed_at"),
            meta.get("language"),
        )
        lic = meta.get("license") or {}
        lic_cat, reuse = license_category(lic.get("spdx_id"))
        rec = recommendation_from_scores(scores, lic_cat)
        entry.update(
            {
                "description": meta.get("description"),
                "topics": meta.get("topics", []),
                "license": lic.get("spdx_id") or lic.get("name"),
                "stars": meta.get("stargazers_count"),
                "forks": meta.get("forks_count"),
                "open_issues": meta.get("open_issues_count"),
                "primary_language": meta.get("language"),
                "created_at": meta.get("created_at"),
                "pushed_at": meta.get("pushed_at"),
                "size_kb": meta.get("size"),
                "readme_excerpt": None,
                "keywords": [],
                "scores": scores,
                "scoring_basis": f"stars={meta.get('stargazers_count')}, activity={meta.get('pushed_at')}, desc_len={len(text_blob)}",
                "license_assessment": {"category": lic_cat, "reuse_allowed": reuse},
                "recommendation": rec,
                "suggested_next_steps": [],
            }
        )
        maybe_wait(resp)
    except Exception as e:
        entry.update(
            {
                "description": entry.get("description"),
                "topics": [],
                "license": None,
                "stars": 0,
                "forks": 0,
                "open_issues": 0,
                "primary_language": None,
                "created_at": None,
                "pushed_at": None,
                "size_kb": 0,
                "readme_excerpt": None,
                "keywords": [],
                "scores": {},
                "scoring_basis": "error",
                "license_assessment": {
                    "category": "unknown",
                    "reuse_allowed": "unknown",
                },
                "recommendation": "low_priority",
                "suggested_next_steps": [],
                "error": str(e),
            }
        )
    repos_out.append(entry)

report: Dict[str, Any] = {
    "project": "Wizard101-smart-trainer-repo-analysis",
    "timestamp": now,
    "repos": repos_out,
    "summary": {},
}
rec_counts = Counter([r.get("recommendation", "unknown") for r in repos_out])
report["summary"]["counts_by_recommendation"] = dict(rec_counts)
sorted_repos = sorted(
    [r for r in repos_out if isinstance(r.get("stars"), int)],
    key=lambda x: x.get("stars", 0),
    reverse=True,
)
report["summary"]["top_candidates"] = [r.get("html_url") for r in sorted_repos[:7]]
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)

# plan rebuild
sources = {}
if os.path.isfile(SOURCES_PATH):
    try:
        with open(SOURCES_PATH, "r", encoding="utf-8-sig") as f:
            sources = json.load(f)
    except Exception:
        pass
plan = {
    "project": "Wizard101 Smart Trainer integration plan",
    "timestamp": now,
    "legal_ethics": {
        "status": "educational/experimental only",
        "rules": [
            "Public data or user-consented recordings only",
            "No live client/server interaction, no memory/net inspection",
            "Attribution required for third-party scripts/data",
        ],
    },
    "summary": report["summary"],
    "data_sources_preview": sources.get("sources", [])[:5],
    "milestones_90d": [
        {
            "phase": "0-30d",
            "goals": [
                "Lock legal/ethics guardrails in code (dev mode logging).",
                "Grow template/OCR library for HUD stats; measure accuracy baseline.",
                "Add script catalog with credits + provenance display.",
                "Prototype diagnostics dashboard.",
            ],
        },
        {
            "phase": "31-60d",
            "goals": [
                "Integrate behavior trees/FSM for SmartPlay task orchestration.",
                "Graph/path routing for common hubs using public maps.",
                "Add portable + installer build matrix and smoke tests.",
                "Seed dataset workflow with consented captures.",
            ],
        },
        {
            "phase": "61-90d",
            "goals": [
                "Optional YOLOv5 detector prototype.",
                "Optional offline RL experiments (no live game).",
                "UI polish + accessibility + About/Credits expansion.",
                "Publish contributor guide and auto-credit pipeline.",
            ],
        },
    ],
}
with open(PLAN_PATH, "w", encoding="utf-8") as f:
    json.dump(plan, f, indent=2)

print(json.dumps({"status": "ok", "repos": len(repos_out)}, indent=2))
