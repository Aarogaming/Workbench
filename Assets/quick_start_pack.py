import json
import os
import shutil


def create_quick_start(root_dir):
    index_path = "asset_index.json"
    if not os.path.exists(index_path):
        print("Index not found.")
        return

    with open(index_path, "r") as f:
        assets = json.load(f)

    # Curated list of "essential" assets
    essentials = [
        "100 Epic LUTs Pack",
        "50 Cinematic Essentials LUTs Pack",
        "VFX Portals Pack",
        "Unreal Material Pack",
        "10 Dust Explosions Pack",
        "200 Ultimate Fonts Bundle",
    ]

    qs_dir = os.path.join(root_dir, "QuickStart")
    os.makedirs(qs_dir, exist_ok=True)

    for asset in assets:
        if any(e in asset["name"] for e in essentials):
            src = asset["path"]
            if os.path.exists(src):
                print(f"Adding to QuickStart: {asset['name']}")
                shutil.copy2(src, os.path.join(qs_dir, asset["name"]))


if __name__ == "__main__":
    create_quick_start(".")
