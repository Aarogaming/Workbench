import requests, json, datetime
from typing import Any, Dict, List

repos = [
    "https://github.com/Unity-Technologies/ml-agents",
    "https://github.com/Farama-Foundation/Gymnasium",
    "https://github.com/DLR-RM/stable-baselines3",
    "https://github.com/ray-project/ray",
    "https://github.com/deepmind/acme",
    "https://github.com/astooke/rlpyt",
    "https://github.com/DLR-RM/rl-baselines3-zoo",
    "https://github.com/openai/imitation",
    "https://github.com/opencv/opencv",
    "https://github.com/ultralytics/ultralytics",
    "https://github.com/ultralytics/yolov5",
    "https://github.com/facebookresearch/detectron2",
    "https://github.com/JaidedAI/EasyOCR",
    "https://github.com/tesseract-ocr/tesseract",
    "https://github.com/tzutalin/labelImg",
    "https://github.com/opencv/cvat",
    "https://github.com/heartexlabs/label-studio",
    "https://github.com/BoboTiG/python-mss",
    "https://github.com/AirtestProject/Airtest",
    "https://github.com/RaiMan/SikuliX1",
    "https://github.com/asweigart/pyautogui",
    "https://github.com/moses-palmer/pynput",
    "https://github.com/SerpentAI/SerpentAI",
    "https://github.com/ardamavi/Game-Bot",
    "https://github.com/botman99/ue4-unreal-automation-tool",
    "https://github.com/microsoft/agent-lightning",
    "https://github.com/michaelbianchi7/Game-AI",
    "https://github.com/recastnavigation/RecastNavigation",
    "https://github.com/networkx/networkx",
    "https://github.com/stonier/py_trees",
    "https://github.com/pytransitions/transitions",
    "https://github.com/wandb/wandb",
    "https://github.com/mlflow/mlflow",
    "https://github.com/streamlit/streamlit",
    "https://github.com/hoffstadt/DearPyGui",
    "https://github.com/PySimpleGUI/PySimpleGUI",
    "https://github.com/pyinstaller/pyinstaller",
    "https://github.com/electron-userland/electron-builder",
    "https://github.com/obsproject/obs-studio",
    "https://github.com/pallets/flask",
    "https://github.com/pytorch/vision",
]

keywords_list = [
    "rl",
    "reinforcement learning",
    "imitation learning",
    "unity",
    "gym",
    "training",
    "replay",
    "dataset",
    "vision",
    "ocr",
    "yolov5",
    "detectron",
    "object detection",
    "template matching",
    "image recognition",
    "screenshot",
    "inventory",
    "label",
    "annotation",
    "pathfinding",
    "navigation",
    "recast",
    "behavior tree",
    "py_trees",
    "fsm",
    "actions",
    "gui automation",
    "input injection",
    "mouse",
    "keyboard",
    "installer",
    "packaging",
    "electron",
    "pyinstaller",
    "dashboard",
    "streamlit",
    "dearpygui",
    "logging",
    "wandb",
    "mlflow",
    "examples",
    "tutorial",
    "examples/unity",
    "examples/unreal",
    "windows",
    "cross-platform",
    "python",
    "c#",
    "c++",
    "docker",
]

session = requests.Session()
headers = {"Accept": "application/vnd.github+json", "User-Agent": "repo-eval-script"}
headers_topics = headers.copy()
headers_topics["Accept"] = "application/vnd.github.mercy-preview+json"
headers_readme = {
    "Accept": "application/vnd.github.v3.raw",
    "User-Agent": "repo-eval-script",
}

now = datetime.datetime.now(datetime.timezone.utc)


def license_category(spdx):
    if not spdx:
        return "unknown", "unknown"
    spdx_upper = spdx.upper()
    if any(x in spdx_upper for x in ["MIT", "BSD", "APACHE", "ISC", "ZLIB", "MPL"]):
        return "permissive", "true"
    if any(x in spdx_upper for x in ["GPL", "LGPL", "AGPL"]):
        return "copyleft", "false"
    return "other", "unknown"


def relevance_scores(meta, kws):
    stars = meta.get("stars") or 0
    pushed = meta.get("pushed_at")
    recent = False
    if pushed:
        try:
            recent = (
                now - datetime.datetime.fromisoformat(pushed.replace("Z", ""))
            ).days <= 730
        except Exception:
            pass
    kw_lower = [k.lower() for k in kws]
    rl_hit = any(
        term in kw_lower
        for term in [
            "rl",
            "reinforcement learning",
            "imitation",
            "gym",
            "unity",
            "training",
        ]
    )
    vision_hit = any(
        term in kw_lower
        for term in [
            "vision",
            "ocr",
            "yolov5",
            "detectron",
            "object detection",
            "template matching",
            "image recognition",
            "screenshot",
            "label",
            "annotation",
            "inventory",
        ]
    )
    gui_hit = any(
        term in kw_lower
        for term in [
            "gui automation",
            "input injection",
            "mouse",
            "keyboard",
            "automation",
        ]
    )
    path_hit = any(term in kw_lower for term in ["pathfinding", "navigation", "recast"])
    inv_hit = any(
        term in kw_lower
        for term in ["inventory", "label", "annotation", "object detection"]
    )
    installer_hit = any(
        term in kw_lower
        for term in ["installer", "packaging", "electron", "pyinstaller"]
    )
    dev_hit = any(
        term in kw_lower for term in ["logging", "wandb", "mlflow", "docker", "ci"]
    )
    dash_hit = any(
        term in kw_lower
        for term in ["dashboard", "streamlit", "dearpygui", "pysimplegui", "ui"]
    )

    def base(hit, default=0):
        if hit:
            score = 70
            if recent:
                score += 10
            if stars > 1000:
                score += 10
            return min(score, 100)
        return default

    scores = {
        "RL_training": base(rl_hit),
        "Vision_OCR": base(vision_hit),
        "GUI_Automation": base(gui_hit),
        "Pathfinding_Navigation": base(path_hit),
        "Inventory_Image_Categorization": base(inv_hit),
        "Installer_Packaging": base(installer_hit),
        "Dev_Tools_Integrations": base(dev_hit),
        "Dashboard_UI": base(dash_hit),
    }
    ease = 30
    if stars > 1000:
        ease += 40
    elif stars > 100:
        ease += 20
    if recent:
        ease += 20
    scores["Ease_of_Integration"] = min(ease, 100)

    basis_parts = []
    if rl_hit:
        basis_parts.append("rl keywords")
    if vision_hit:
        basis_parts.append("vision/ocr keywords")
    if gui_hit:
        basis_parts.append("gui automation keywords")
    if path_hit:
        basis_parts.append("pathfinding keywords")
    if installer_hit:
        basis_parts.append("packaging keywords")
    if dev_hit:
        basis_parts.append("dev/logging keywords")
    if recent:
        basis_parts.append("recent activity")
    if stars > 1000:
        basis_parts.append(">1k stars")
    basis = ", ".join(basis_parts) if basis_parts else "no relevant keywords detected"
    return scores, basis


def recommendation(scores, lic_cat):
    top = max(scores.values())
    if top >= 70 and lic_cat == "permissive":
        if (
            scores["Vision_OCR"] >= 70
            or scores["GUI_Automation"] >= 70
            or scores["Installer_Packaging"] >= 70
            or scores["Dashboard_UI"] >= 70
        ):
            return "use_directly"
        if scores["RL_training"] >= 70 or scores["Pathfinding_Navigation"] >= 70:
            return "study_and_extract_patterns"
    if top >= 70:
        return "study_and_extract_patterns"
    return "low_priority"


def suggested_steps(name):
    steps = []
    nl = (name or "").lower()
    if any(
        x in nl
        for x in ["yolo", "ultralytics", "detectron", "opencv", "easyocr", "tesseract"]
    ):
        steps.append("prototype vision/OCR for UI and inventory")
    if any(x in nl for x in ["airtest", "sikuli", "pyautogui", "pynput", "game-bot"]):
        steps.append("evaluate image+input automation for SmartPlay")
    if any(
        x in nl
        for x in [
            "ml-agents",
            "gymnasium",
            "stable-baselines",
            "acme",
            "rlpyt",
            "imitation",
            "rl-baselines3-zoo",
        ]
    ):
        steps.append("spike RL/env for minigame or routing")
    if "recast" in nl:
        steps.append("explore navmesh/pathfinding for travel")
    if any(x in nl for x in ["pyinstaller", "electron-builder"]):
        steps.append("assess packaging for trainer")
    if any(x in nl for x in ["streamlit", "dearpygui", "pysimplegui"]):
        steps.append("prototype dashboard UI")
    return steps[:3]


results: List[Dict[str, Any]] = []
for url in repos:
    owner = name = None
    parts = url.strip().split("/")
    if len(parts) >= 2:
        owner, name = parts[-2], parts[-1]
    entry = {
        "owner": owner,
        "name": name,
        "html_url": url,
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
    }
    try:
        repo_api = f"https://api.github.com/repos/{owner}/{name}"
        r = session.get(repo_api, headers=headers, timeout=15)
        if r.status_code == 200:
            meta = r.json()
            entry.update(
                {
                    "description": meta.get("description"),
                    "license": (meta.get("license") or {}).get("spdx_id"),
                    "stars": meta.get("stargazers_count") or 0,
                    "forks": meta.get("forks_count") or 0,
                    "open_issues": meta.get("open_issues_count") or 0,
                    "primary_language": meta.get("language"),
                    "created_at": meta.get("created_at"),
                    "pushed_at": meta.get("pushed_at"),
                    "size_kb": meta.get("size") or 0,
                    "default_branch": meta.get("default_branch"),
                }
            )
        topics = session.get(repo_api, headers=headers_topics, timeout=15)
        if topics.status_code == 200:
            entry["topics"] = topics.json().get("topics", [])
        rd = session.get(f"{repo_api}/readme", headers=headers_readme, timeout=15)
        if rd.status_code == 200:
            entry["readme_excerpt"] = rd.text[:2048]
        text_blob = " ".join(
            filter(
                None,
                [entry.get("description") or "", entry.get("readme_excerpt") or ""],
            )
        )
        text_lower = text_blob.lower()
        matched = [kw for kw in keywords_list if kw.lower() in text_lower]
        entry["keywords"] = matched
        scores, basis = relevance_scores(entry, matched)
        entry["scores"] = scores
        entry["scoring_basis"] = basis
        lic_cat, reuse = license_category(entry.get("license"))
        entry["license_assessment"] = {
            "category": lic_cat,
            "reuse_allowed": (
                True if reuse == "true" else False if reuse == "false" else "unknown"
            ),
        }
        rec = recommendation(scores, lic_cat)
        entry["recommendation"] = rec
        entry["suggested_next_steps"] = suggested_steps(name)
    except Exception as e:
        entry["error"] = str(e)
    results.append(entry)

summary_counts: Dict[str, int] = {
    "use_directly": 0,
    "fork_and_extend": 0,
    "study_and_extract_patterns": 0,
    "dataset_or_tooling_only": 0,
    "low_priority": 0,
}
for r in results:
    rec_raw = r.get("recommendation", "low_priority")
    rec = rec_raw if isinstance(rec_raw, str) else "low_priority"
    summary_counts.setdefault(rec, 0)
    summary_counts[rec] += 1


def _score_key(entry: Dict[str, Any]) -> tuple[float, float]:
    scores = entry.get("scores")
    if not isinstance(scores, dict):
        return (0.0, 0.0)
    numeric_scores = {
        k: float(v) for k, v in scores.items() if isinstance(v, (int, float))
    }
    ease = float(numeric_scores.get("Ease_of_Integration", 0.0))
    max_score = max(numeric_scores.values(), default=0.0)
    return (ease, max_score)


sorted_repos = sorted(results, key=_score_key, reverse=True)
top_candidates = [r.get("html_url") for r in sorted_repos[:5]]

report = {
    "project": "Wizard101-smart-trainer-eval",
    "timestamp": datetime.datetime.now(datetime.timezone.utc)
    .isoformat()
    .replace("+00:00", "Z"),
    "repos": results,
    "summary": {
        "counts_by_recommendation": summary_counts,
        "top_candidates": top_candidates,
        "notes": "GitHub API unauthenticated; rate limits may apply.",
    },
}

print(json.dumps(report, indent=2))
