
import os
from pathlib import Path

def collect_folders_and_files(root_folder, include_files=False, extensions=None, progress_callback=None):
    data = []
    processed_count = 0

    for dirpath, dirnames, filenames in os.walk(root_folder):
        # Check for cancellation
        if progress_callback and progress_callback.get('check_cancelled', lambda: False)():
            break
            
        # Update progress status
        if progress_callback and progress_callback.get('update_status'):
            progress_callback['update_status'](f"Scanning: {dirpath}")
        
        # Collect folder info
        for dirname in dirnames:
            # Check for cancellation before processing each item
            if progress_callback and progress_callback.get('check_cancelled', lambda: False)():
                break
                
            data.append({
                'Type': 'Folder',
                'Name': dirname,
                'Path': Path(os.path.join(dirpath, dirname)).as_posix(),
                'Extension': ''
            })
            processed_count += 1

        # Collect file info if enabled
        if include_files:       
            for filename in filenames:
                # Check for cancellation before processing each item
                if progress_callback and progress_callback.get('check_cancelled', lambda: False)():
                    break
                    
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
                processed_count += 1
                
                # Update progress status for files periodically
                if progress_callback and progress_callback.get('update_status') and processed_count % 50 == 0:
                    progress_callback['update_status'](f"Scanning: {dirpath} ({processed_count} items found)")

    return data

