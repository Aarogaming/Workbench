import json
import shutil
from pathlib import Path

WORKBENCH_ROOT = Path(__file__).resolve().parents[1]


class AssetManager:
    def __init__(self, index_path="asset_index.json"):
        path = Path(index_path)
        if not path.is_absolute():
            path = WORKBENCH_ROOT / path
        self.index_path = path
        self.assets = self._load_index()

    def _load_index(self):
        if self.index_path.exists():
            return json.loads(self.index_path.read_text(encoding="utf-8"))
        return []

    def find_assets(self, query):
        query = query.lower()
        return [
            a
            for a in self.assets
            if query in a["name"].lower() or query in a["category"].lower()
        ]

    def request_asset(self, asset_name, destination):
        for asset in self.assets:
            if asset["name"] == asset_name:
                src = WORKBENCH_ROOT / asset["path"]
                if src.exists():
                    destination_path = Path(destination)
                    destination_path.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, destination_path / asset_name)
                    print(f"Asset {asset_name} delivered to {destination_path}")
                    return True
        print(f"Asset {asset_name} not found.")
        return False


if __name__ == "__main__":
    # Example usage for AAS integration
    am = AssetManager()
    print(f"Manager initialized with {len(am.assets)} assets.")
