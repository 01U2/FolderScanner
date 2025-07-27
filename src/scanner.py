
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

                file_path = Path(os.path.join(dirpath, filename)).as_posix()
                
                # Get file size
                try:
                    file_size = os.path.getsize(file_path)
                except OSError:
                    file_size = 0

                data.append({
                    'Type': 'File',
                    'Name': filename,
                    'Path': file_path,
                    'Extension': file_ext,
                    'Size': file_size
                })

    return data

