import os
import json
import hashlib


def get_file_size(path):
    try:
        return os.path.getsize(path)
    except:
        return 0


def generate_index(root_dir):
    asset_index = []
    for root, dirs, files in os.walk(root_dir):
        if "tools" in root or ".git" in root:
            continue
        for file in files:
            if file.endswith((".zip", ".7z", ".exe", ".url", ".txt")):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, root_dir)
                asset_index.append(
                    {
                        "name": file,
                        "path": rel_path.replace("\\", "/"),
                        "size": get_file_size(full_path),
                        "category": (
                            rel_path.split(os.sep)[0] if os.sep in rel_path else "Root"
                        ),
                        "extension": os.path.splitext(file)[1].lower(),
                    }
                )

    with open("asset_index.json", "w") as f:
        json.dump(asset_index, f, indent=4)
    print(f"Indexed {len(asset_index)} assets.")


if __name__ == "__main__":
    generate_index(".")
