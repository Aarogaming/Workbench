import json
import sys
from pathlib import Path

WORKBENCH_ROOT = Path(__file__).resolve().parents[1]


def resolve_index_path(index_path: str = "asset_index.json") -> Path:
    candidate = Path(index_path)
    if candidate.is_absolute():
        return candidate
    cwd_candidate = Path.cwd() / candidate
    if cwd_candidate.exists():
        return cwd_candidate
    return WORKBENCH_ROOT / candidate


def search_assets(query: str):
    index_path = resolve_index_path("asset_index.json")
    if not index_path.exists():
        print("Error: asset_index.json not found. Run index_assets.py first.")
        return

    assets = json.loads(index_path.read_text(encoding="utf-8"))

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
