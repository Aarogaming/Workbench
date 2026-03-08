import json
import os
from pathlib import Path

WORKBENCH_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXTENSIONS = {".zip", ".7z", ".exe", ".url", ".txt"}


def get_file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def resolve_root_dir(root_dir: str) -> Path:
    candidate = (root_dir or ".").strip()
    if candidate in {"", "."}:
        return WORKBENCH_ROOT
    return Path(candidate).resolve()


def generate_index(root_dir: str = "."):
    root_path = resolve_root_dir(root_dir)
    asset_index = []
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d.casefold() not in {"tools", ".git"}]
        for file in files:
            full_path = Path(root) / file
            if full_path.suffix.lower() not in DEFAULT_EXTENSIONS:
                continue
            rel_path = full_path.relative_to(root_path)
            category = rel_path.parts[0] if len(rel_path.parts) > 1 else "Root"
            asset_index.append(
                {
                    "name": file,
                    "path": str(rel_path).replace("\\", "/"),
                    "size": get_file_size(full_path),
                    "category": category,
                    "extension": full_path.suffix.lower(),
                }
            )

    target = root_path / "asset_index.json"
    target.write_text(json.dumps(asset_index, indent=2), encoding="utf-8")
    print(f"Indexed {len(asset_index)} assets.")


if __name__ == "__main__":
    generate_index(".")
