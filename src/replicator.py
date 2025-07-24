import os
import shutil
from pathlib import Path

def replicate_folder_structure(source, destination, include_files=False, extensions=None):
    replicated = []

    for dirpath, dirnames, filenames in os.walk(source):
        # Replicate folders
        for dirname in dirnames:
            source_path = os.path.join(dirpath, dirname)
            relative_path = os.path.relpath(source_path, source)
            dest_path = os.path.join(destination, relative_path)
            try:
                os.makedirs(dest_path, exist_ok=True)
                status = 'Folder Replicated'
            except Exception as e:
                status = f'Folder Failed: {e}'
            replicated.append({
                'Type': 'Folder',
                'Name': dirname,
                'Source Path': source_path,
                'Destination Path': dest_path,
                'Extension': '',
                'Status': status
            })

        # Copy files if enabled
        if include_files:
            for filename in filenames:
                file_ext = os.path.splitext(filename)[1]

                # Skip if extensions are specified and file doesn't match
                if extensions and not any(filename.lower().endswith(ext.lower()) for ext in extensions):
                    continue

                source_file = os.path.join(dirpath, filename)
                relative_file_path = os.path.relpath(source_file, source)
                dest_file = os.path.join(destination, relative_file_path)
                dest_folder = os.path.dirname(dest_file)

                try:
                    os.makedirs(dest_folder, exist_ok=True)
                    shutil.copy2(source_file, dest_file)
                    status = 'File Copied'
                except Exception as e:
                    status = f'File Failed: {e}'

                replicated.append({
                    'Type': 'File',
                    'Name': filename,
                    'Source Path': source_file,
                    'Destination Path': dest_file,
                    'Extension': file_ext,
                    'Status': status
                })

    return replicated
