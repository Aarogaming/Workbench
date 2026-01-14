import os
import zipfile

def test_archives(root_dir):
    corrupt_files = []
    py7zr_available = False
    try:
        import py7zr
        py7zr_available = True
    except ImportError:
        print("py7zr not installed. Skipping .7z files.")

    for root, dirs, files in os.walk(root_dir):
        if 'tools' in root or '.git' in root:
            continue
        for file in files:
            path = os.path.join(root, file)
            if file.endswith('.zip'):
                try:
                    with zipfile.ZipFile(path, 'r') as z:
                        if z.testzip() is not None:
                            corrupt_files.append(path)
                except Exception as e:
                    corrupt_files.append(f"{path} (Error: {str(e)})")
            elif file.endswith('.7z') and py7zr_available:
                try:
                    import py7zr
                    with py7zr.SevenZipFile(path, mode='r') as z:
                        z.list()
                except Exception as e:
                    corrupt_files.append(f"{path} (Error: {str(e)})")

    if corrupt_files:
        print("Corrupt or unreadable archives found:")
        for f in corrupt_files:
            print(f"- {f}")
    else:
        print("All tested archives passed basic integrity check.")

if __name__ == "__main__":
    test_archives(".")
