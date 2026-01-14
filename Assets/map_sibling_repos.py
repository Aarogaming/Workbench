import os
import json

def map_siblings(dev_library_path):
    mappings = {
        "Games": ["Audio/SFX", "Audio/Music", "Unreal/Environments", "Unreal/Props", "Visuals/LUTs"],
        "AndroidApp": ["Audio/SFX", "Visuals/LUTs", "Audio/Overlays"],
        "Maelstrom": ["Audio/Music", "Audio/SFX"],
        "Workbench": ["Tools/Software"]
    }
    
    report = "# Sibling Repo Asset Mapping\n\n"
    
    if not os.path.exists(dev_library_path):
        print(f"Path {dev_library_path} not found.")
        return

    siblings = [d for d in os.listdir(dev_library_path) if os.path.isdir(os.path.join(dev_library_path, d))]
    
    for sibling in siblings:
        report += f"## {sibling}\n"
        if sibling in mappings:
            report += "Suggested Asset Categories:\n"
            for cat in mappings[sibling]:
                report += f"- {cat}\n"
        else:
            report += "No specific mapping defined. General assets available.\n"
        report += "\n"

    with open('SIBLING_MAPPING.md', 'w') as f:
        f.write(report)
    print("Sibling mapping report generated: SIBLING_MAPPING.md")

if __name__ == "__main__":
    map_siblings("d:\\Dev library\\AaroneousAutomationSuite")
