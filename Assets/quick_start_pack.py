import json
import shutil
from pathlib import Path

WORKBENCH_ROOT = Path(__file__).resolve().parents[1]


def create_quick_start(root_dir):
    root_path = (
        WORKBENCH_ROOT
        if str(root_dir).strip() in {"", "."}
        else Path(root_dir).resolve()
    )
    index_path = root_path / "asset_index.json"
    if not index_path.exists():
        print("Index not found.")
        return

    assets = json.loads(index_path.read_text(encoding="utf-8"))

    # Curated list of "essential" assets
    essentials = [
        "100 Epic LUTs Pack",
        "50 Cinematic Essentials LUTs Pack",
        "VFX Portals Pack",
        "Unreal Material Pack",
        "10 Dust Explosions Pack",
        "200 Ultimate Fonts Bundle",
    ]

    qs_dir = root_path / "QuickStart"
    qs_dir.mkdir(parents=True, exist_ok=True)

    for asset in assets:
        if any(e in asset["name"] for e in essentials):
            src = root_path / asset["path"]
            if src.exists():
                print(f"Adding to QuickStart: {asset['name']}")
                shutil.copy2(src, qs_dir / asset["name"])


if __name__ == "__main__":
    create_quick_start(".")
