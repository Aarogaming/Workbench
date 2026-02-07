import os
import shutil


def cleanup_names(root_dir):
    for root, dirs, files in os.walk(root_dir, topdown=False):
        if "tools" in root or ".git" in root:
            continue
        for name in files:
            new_name = name.replace("+", " ").replace("%20", " ")
            if "(1)" in new_name:
                new_name = new_name.replace("(1)", "").strip()

            if new_name != name:
                old_path = os.path.join(root, name)
                new_path = os.path.join(root, new_name)
                if not os.path.exists(new_path):
                    print(f"Renaming: {name} -> {new_name}")
                    os.rename(old_path, new_path)
                else:
                    print(f"Duplicate found, deleting: {name}")
                    os.remove(old_path)


def restructure_assets(root_dir):
    # Create new directories
    dirs_to_create = [
        "Visuals/LUTs",
        "Tools/Software",
        "Audio/SFX",
        "Audio/Music",
        "Audio/Overlays",
    ]
    for d in dirs_to_create:
        os.makedirs(os.path.join(root_dir, d), exist_ok=True)

    # Move LUTs
    eldamar_path = os.path.join(root_dir, "Audio", "Eldamar Studios")
    if os.path.exists(eldamar_path):
        for file in os.listdir(eldamar_path):
            if "LUTs" in file:
                shutil.move(
                    os.path.join(eldamar_path, file),
                    os.path.join(root_dir, "Visuals", "LUTs", file),
                )
            elif (
                "Backgrounds" in file
                or "Overlays" in file
                or "Transitions" in file
                or "Titles" in file
            ):
                shutil.move(
                    os.path.join(eldamar_path, file),
                    os.path.join(root_dir, "Audio", "Overlays", file),
                )
            elif (
                "Explosions" in file
                or "Particles" in file
                or "Impact" in file
                or "Fire" in file
            ):
                shutil.move(
                    os.path.join(eldamar_path, file),
                    os.path.join(root_dir, "Audio", "SFX", file),
                )

    # Move Programs
    programs_path = os.path.join(root_dir, "Audio", "Programs")
    if os.path.exists(programs_path):
        for file in os.listdir(programs_path):
            shutil.move(
                os.path.join(programs_path, file),
                os.path.join(root_dir, "Tools", "Software", file),
            )
        os.rmdir(programs_path)


if __name__ == "__main__":
    cleanup_names(".")
    restructure_assets(".")
