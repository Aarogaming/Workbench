import os
import zipfile
import json

def generate_previews(root_dir):
    previews = {}
    for root, dirs, files in os.walk(root_dir):
        if 'tools' in root or '.git' in root:
            continue
        for file in files:
            if file.endswith('.zip'):
                path = os.path.join(root, file)
                try:
                    with zipfile.ZipFile(path, 'r') as z:
                        # Get first 10 files as a "preview"
                        file_list = z.namelist()[:10]
                        previews[file] = file_list
                except:
                    previews[file] = ["Error reading archive"]

    with open('asset_previews.json', 'w') as f:
        json.dump(previews, f, indent=4)
    print("Asset previews generated: asset_previews.json")

if __name__ == "__main__":
    generate_previews(".")
