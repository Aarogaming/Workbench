import json
import os
import sys
import subprocess
from datetime import datetime
from urllib.parse import urlparse


CANONICAL_URLS = [
    "https://github.com/Unity-Technologies/ml-agents",
    "https://github.com/Farama-Foundation/Gymnasium",
    "https://github.com/DLR-RM/stable-baselines3",
    "https://github.com/ray-project/ray",
    "https://github.com/opencv/opencv",
    "https://github.com/tesseract-ocr/tesseract",
    "https://github.com/RaiMan/SikuliX1",
    "https://github.com/AirtestProject/Airtest",
    "https://github.com/asweigart/pyautogui",
    "https://github.com/moses-palmer/pynput",
    "https://www.autohotkey.com/",
    "https://github.com/microsoft/malmo",
    "https://github.com/Farama-Foundation/retro",
    "https://github.com/electron/electron",
    "https://github.com/PySimpleGUI/PySimpleGUI",
    "https://www.riverbankcomputing.com/software/pyqt/intro",
    "https://github.com/hoffstadt/DearPyGui",
    "https://github.com/SerpentAI/SerpentAI",
    "https://github.com/ardamavi/Game-Bot",
    "https://github.com/microsoft/agent-lightning",
    "https://github.com/botman99/ue4-unreal-automation-tool",
    "https://github.com/michaelbianchi7/Game-AI",
]


def normalize_git_url(url: str) -> str:
    if not url:
        return ""
    url = url.strip()
    if url.startswith("git@github.com:"):
        path = url[len("git@github.com:") :]
        return f"https://github.com/{path}"
    if url.startswith("ssh://git@github.com/"):
        path = url[len("ssh://git@github.com/") :]
        return f"https://github.com/{path}"
    return url


def parse_github(url: str):
    parsed = urlparse(url)
    if parsed.netloc.lower() != "github.com":
        return None, None
    parts = [p for p in parsed.path.strip("/").split("/") if p]
    if len(parts) < 2:
        return None, None
    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    return owner, repo


def find_git_remote(path: str) -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", path, "remote", "get-url", "origin"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return out
    except subprocess.CalledProcessError:
        return ""


def is_git_repo(path: str) -> bool:
    if os.path.isdir(os.path.join(path, ".git")):
        return True
    try:
        out = subprocess.check_output(
            ["git", "-C", path, "rev-parse", "--is-inside-work-tree"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return out == "true"
    except subprocess.CalledProcessError:
        return False


def scan_local_repos(scan_path: str):
    candidates = {}
    for entry in os.scandir(scan_path):
        if entry.is_dir():
            key = entry.name.lower()
            candidates.setdefault(key, []).append(entry.path)
    git_repos = []
    for root, dirs, _ in os.walk(scan_path):
        if ".git" in dirs:
            git_repos.append(root)
            dirs[:] = []  # don't recurse further under git repos
    return candidates, git_repos


def main():
    try:
        scan_path = os.environ.get("SCAN_PATH", ".")
        if len(sys.argv) > 1:
            scan_path = sys.argv[1]
        scan_path = os.path.abspath(scan_path)

        candidates, git_repos = scan_local_repos(scan_path)

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
                missing.append({"name": repo or list(names_to_check)[0], "canonical_url": url})
                continue

            seen_paths.add(os.path.abspath(found_path))

            if is_git_repo(found_path):
                remote = normalize_git_url(find_git_remote(found_path))
                canonical_norm = normalize_git_url(url)
                entry = {
                    "name": repo or os.path.basename(found_path),
                    "owner": owner,
                    "canonical_url": url,
                    "local_path": found_path,
                    "remote_url": remote,
                }
                if remote and canonical_norm and remote.rstrip("/") == canonical_norm.rstrip("/"):
                    exact_match.append(entry)
                else:
                    present_different_remote.append(entry)
            else:
                present_not_git.append(
                    {
                        "name": repo or os.path.basename(found_path),
                        "local_path": found_path,
                    }
                )

        extra_local_repos = []
        for repo_path in git_repos:
            if os.path.abspath(repo_path) in seen_paths:
                continue
            remote = normalize_git_url(find_git_remote(repo_path))
            extra_local_repos.append(
                {
                    "name": os.path.basename(repo_path),
                    "local_path": repo_path,
                    "remote_url": remote,
                }
            )

        report = {
            "scan_path": scan_path,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "exact_match": exact_match,
            "present_different_remote": present_different_remote,
            "present_not_git": present_not_git,
            "missing": missing,
            "extra_local_repos": extra_local_repos,
        }

        print(json.dumps(report, indent=2))
        sys.exit(0)
    except Exception as e:
        err = {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        print(json.dumps(err, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
