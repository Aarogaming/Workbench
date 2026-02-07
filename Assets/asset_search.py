import json
import sys
import os


def search_assets(query):
    index_path = "asset_index.json"
    if not os.path.exists(index_path):
        print("Error: asset_index.json not found. Run index_assets.py first.")
        return

    with open(index_path, "r") as f:
        assets = json.load(f)

    results = []
    query = query.lower()
    for asset in assets:
        if query in asset["name"].lower() or query in asset["category"].lower():
            results.append(asset)

    if not results:
        print(f"No assets found matching '{query}'")
    else:
        print(f"Found {len(results)} assets:")
        for res in results:
            print(f"- [{res['category']}] {res['name']} ({res['path']})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python asset_search.py <query>")
    else:
        search_assets(" ".join(sys.argv[1:]))
