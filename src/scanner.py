
import os
from pathlib import Path

def collect_folders_and_files(root_folder, include_files=False, extensions=None):
    data = []

    for dirpath, dirnames, filenames in os.walk(root_folder):
        # Collect folder info
        for dirname in dirnames:
            data.append({
                'Type': 'Folder',
                'Name': dirname,
                'Path': Path(os.path.join(dirpath, dirname)).as_posix(),
                'Extension': ''
            })

        # Collect file info if enabled
        if include_files:       
            for filename in filenames:
                file_ext = os.path.splitext(filename)[1]

                # Skip if extensions filter is applied and file doesn't match
                if extensions and not any(filename.lower().endswith(ext.lower()) for ext in extensions):
                    continue

                data.append({
                    'Type': 'File',
                    'Name': filename,
                    'Path': Path(os.path.join(dirpath, filename)).as_posix(),
                    'Extension': file_ext
                })

    return data

