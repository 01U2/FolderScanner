
import os
from pathlib import Path

def collect_folders_and_files(root_folder, include_files=False, extensions=None):
    data = []
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for dirname in dirnames:
            full_path = os.path.join(dirpath, dirname)
            parent = os.path.basename(dirpath)
            depth = len(Path(full_path).parts) - len(Path(root_folder).parts)
            data.append({
                'Type': 'Folder',
                'Name': dirname,
                'Path': full_path,
                'Parent': parent,
                'Extension': '',
                'Depth': depth
            })
        if include_files:
            for filename in filenames:
                if extensions:
                    if not any(filename.lower().endswith(ext.lower()) for ext in extensions):
                        continue
                full_path = os.path.join(dirpath, filename)
                parent = os.path.basename(dirpath)
                depth = len(Path(full_path).parts) - len(Path(root_folder).parts)
                ext = os.path.splitext(filename)[1]
                data.append({
                    'Type': 'File',
                    'Name': filename,
                    'Path': full_path,
                    'Parent': parent,
                    'Extension': ext,
                    'Depth': depth
                })
    return data
