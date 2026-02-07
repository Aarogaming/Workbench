import os
import json


def format_size(size):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024


def analyze_size(root_dir):
    stats = {}
    total_size = 0

    for root, dirs, files in os.walk(root_dir):
        if "tools" in root or ".git" in root:
            continue
        for file in files:
            path = os.path.join(root, file)
            size = os.path.getsize(path)
            total_size += size

            category = os.path.relpath(root, root_dir).split(os.sep)[0]
            if category == ".":
                category = "Root"

            stats[category] = stats.get(category, 0) + size

    print("Asset Size Analysis:")
    print("-" * 30)
    for cat, size in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        print(f"{cat:15}: {format_size(size)}")
    print("-" * 30)
    print(f"Total Size     : {format_size(total_size)}")


if __name__ == "__main__":
    analyze_size(".")
