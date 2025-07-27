import os
import shutil
from pathlib import Path

def replicate_folder_structure(source, destination, include_files=False, extensions=None, progress_callback=None):
    replicated = []
    total_operations = 0
    completed_operations = 0
    
    # First pass: count total operations for progress tracking
    if progress_callback and progress_callback.get('update_status'):
        progress_callback['update_status']("Counting items to replicate...")
    
    for dirpath, dirnames, filenames in os.walk(source):
        total_operations += len(dirnames)  # Count folders
        if include_files:
            for filename in filenames:
                if not extensions or any(filename.lower().endswith(ext.lower()) for ext in extensions):
                    total_operations += 1  # Count files that will be copied
    
    # Second pass: actual replication with progress tracking
    for dirpath, dirnames, filenames in os.walk(source):
        # Check for cancellation
        if progress_callback and progress_callback.get('check_cancelled', lambda: False)():
            break
            
        # Replicate folders
        for dirname in dirnames:
            # Check for cancellation before processing each item
            if progress_callback and progress_callback.get('check_cancelled', lambda: False)():
                break
                
            source_path = Path(os.path.join(dirpath, dirname)).as_posix()
            relative_path = Path(os.path.relpath(source_path, source)).as_posix()
            dest_path = Path(os.path.join(destination, relative_path)).as_posix()
            
            # Update progress
            if progress_callback:
                if progress_callback.get('update_status'):
                    progress_callback['update_status'](f"Creating folder: {relative_path}")
                if progress_callback.get('update_progress') and total_operations > 0:
                    progress = (completed_operations / total_operations) * 100
                    progress_callback['update_progress'](progress)
            
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
            completed_operations += 1

        # Copy files if enabled
        if include_files:
            for filename in filenames:
                # Check for cancellation before processing each item
                if progress_callback and progress_callback.get('check_cancelled', lambda: False)():
                    break
                    
                file_ext = os.path.splitext(filename)[1]

                # Skip if extensions are specified and file doesn't match
                if extensions and not any(filename.lower().endswith(ext.lower()) for ext in extensions):
                    continue

                source_file = Path(os.path.join(dirpath, filename)).as_posix()
                relative_file_path = Path(os.path.relpath(source_file, source)).as_posix()
                dest_file = Path(os.path.join(destination, relative_file_path)).as_posix()
                dest_folder = os.path.dirname(dest_file)
                
                # Update progress
                if progress_callback:
                    if progress_callback.get('update_status'):
                        progress_callback['update_status'](f"Copying file: {relative_file_path}")
                    if progress_callback.get('update_progress') and total_operations > 0:
                        progress = (completed_operations / total_operations) * 100
                        progress_callback['update_progress'](progress)

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
                completed_operations += 1

    return replicated
