import os
import shutil
import sys


def ingest_asset(file_path, category):
    if not os.path.exists(file_path):
        print(f"Source file {file_path} not found.")
        return

    dest_dir = os.path.join(".", category)
    os.makedirs(dest_dir, exist_ok=True)

    file_name = os.path.basename(file_path)
    # Clean name
    clean_name = file_name.replace("+", " ").replace("%20", " ")
    dest_path = os.path.join(dest_dir, clean_name)

    print(f"Ingesting {file_name} into {category}...")
    shutil.copy2(file_path, dest_path)

    # Update index
    print("Updating asset index...")
    os.system("python tools/index_assets.py")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python asset_ingestion.py <file_path> <category>")
    else:
        ingest_asset(sys.argv[1], sys.argv[2])
