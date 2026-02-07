import json
import os
import shutil


class AssetManager:
    def __init__(self, index_path="asset_index.json"):
        self.index_path = index_path
        self.assets = self._load_index()

    def _load_index(self):
        if os.path.exists(self.index_path):
            with open(self.index_path, "r") as f:
                return json.load(f)
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
                src = asset["path"]
                if os.path.exists(src):
                    os.makedirs(destination, exist_ok=True)
                    shutil.copy2(src, os.path.join(destination, asset_name))
                    print(f"Asset {asset_name} delivered to {destination}")
                    return True
        print(f"Asset {asset_name} not found.")
        return False


if __name__ == "__main__":
    # Example usage for AAS integration
    am = AssetManager()
    print(f"Manager initialized with {len(am.assets)} assets.")
