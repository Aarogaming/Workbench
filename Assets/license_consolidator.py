import os
import shutil

def consolidate_licenses(root_dir):
    license_dir = os.path.join(root_dir, 'Docs', 'Licenses')
    os.makedirs(license_dir, exist_ok=True)
    
    license_count = 0
    for root, dirs, files in os.walk(root_dir):
        if 'Docs' in root or 'tools' in root:
            continue
        for file in files:
            if 'license' in file.lower() and file.endswith('.txt'):
                src_path = os.path.join(root, file)
                # Create a unique name based on the folder it came from
                folder_name = os.path.basename(root)
                new_name = f"{folder_name}_{file}"
                dest_path = os.path.join(license_dir, new_name)
                
                print(f"Consolidating license: {file} from {folder_name}")
                shutil.copy2(src_path, dest_path)
                license_count += 1
                
    print(f"Consolidated {license_count} license files to {license_dir}")

if __name__ == "__main__":
    consolidate_licenses(".")
