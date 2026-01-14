import os
import shutil

def organize_unreal(root_dir):
    unreal_path = os.path.join(root_dir, 'Unreal')
    if not os.path.exists(unreal_path):
        return

    categories = {
        'Environments': ['airport', 'terminal', 'office', 'warehouse', 'station', 'market', 'construction', 'room', 'rooftop'],
        'Props': ['crates', 'barrels', 'seating', 'beds', 'barriers', 'signage', 'decal'],
        'Vehicles': ['vehicle', 'constructionvehicles', 'rocket'],
        'Materials': ['material', 'concrete', 'brick', 'plaster', 'roads', 'walkway']
    }

    for cat in categories:
        os.makedirs(os.path.join(unreal_path, cat), exist_ok=True)

    for file in os.listdir(unreal_path):
        if not file.endswith('.zip'):
            continue
        
        moved = False
        lower_file = file.lower()
        for cat, keywords in categories.items():
            if any(kw in lower_file for kw in keywords):
                shutil.move(os.path.join(unreal_path, file), os.path.join(unreal_path, cat, file))
                print(f"Moved {file} to Unreal/{cat}")
                moved = True
                break
        
        if not moved:
            print(f"Could not categorize {file}")

if __name__ == "__main__":
    organize_unreal(".")
