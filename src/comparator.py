import os
import hashlib
from pathlib import Path
from datetime import datetime

def get_folder_contents(folder_path):
    """
    Get a comprehensive view of folder contents including metadata.
    Returns a dictionary with file/folder paths as keys and metadata as values.
    """
    contents = {}
    
    for root, dirs, files in os.walk(folder_path):
        # Process directories
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            relative_path = os.path.relpath(dir_path, folder_path)
            
            try:
                stat_info = os.stat(dir_path)
                contents[relative_path] = {
                    'type': 'folder',
                    'name': dir_name,
                    'path': dir_path,
                    'relative_path': relative_path,
                    'modified_time': datetime.fromtimestamp(stat_info.st_mtime),
                    'size': 0,  # Folders don't have size
                    'exists': True
                }
            except (OSError, FileNotFoundError):
                # Handle cases where folder might be inaccessible
                contents[relative_path] = {
                    'type': 'folder',
                    'name': dir_name,
                    'path': dir_path,
                    'relative_path': relative_path,
                    'modified_time': None,
                    'size': 0,
                    'exists': False
                }
        
        # Process files
        for file_name in files:
            file_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(file_path, folder_path)
            
            try:
                stat_info = os.stat(file_path)
                contents[relative_path] = {
                    'type': 'file',
                    'name': file_name,
                    'path': file_path,
                    'relative_path': relative_path,
                    'modified_time': datetime.fromtimestamp(stat_info.st_mtime),
                    'size': stat_info.st_size,
                    'exists': True
                }
            except (OSError, FileNotFoundError):
                # Handle cases where file might be inaccessible
                contents[relative_path] = {
                    'type': 'file',
                    'name': file_name,
                    'path': file_path,
                    'relative_path': relative_path,
                    'modified_time': None,
                    'size': 0,
                    'exists': False
                }
    
    return contents

def compare_folders(folder1_path, folder2_path):
    """
    Compare two folders and return differences.
    Returns a list of comparison results with status indicators.
    """
    contents1 = get_folder_contents(folder1_path)
    contents2 = get_folder_contents(folder2_path)
    
    all_paths = set(contents1.keys()) | set(contents2.keys())
    comparison_results = []
    
    for relative_path in sorted(all_paths):
        item1 = contents1.get(relative_path)
        item2 = contents2.get(relative_path)
        
        # Determine status
        if item1 and item2:
            # Item exists in both folders
            if item1['type'] != item2['type']:
                status = 'Type Mismatch'
                status_detail = f"Type changed from {item1['type']} to {item2['type']}"
            elif item1['type'] == 'file':
                # Compare file metadata
                if item1['size'] != item2['size']:
                    status = 'Modified'
                    status_detail = f"Size changed: {item1['size']} → {item2['size']} bytes"
                elif item1['modified_time'] != item2['modified_time']:
                    status = 'Modified'
                    status_detail = f"Modified time changed"
                else:
                    status = 'Same'
                    status_detail = 'Identical'
            else:
                # Folder comparison
                if item1['modified_time'] != item2['modified_time']:
                    status = 'Modified'
                    status_detail = 'Modified time changed'
                else:
                    status = 'Same'
                    status_detail = 'Identical'
        elif item1 and not item2:
            # Item exists only in folder1
            status = 'Only in Folder 1'
            status_detail = f'Missing from {os.path.basename(folder2_path)}'
        elif item2 and not item1:
            # Item exists only in folder2
            status = 'Only in Folder 2'
            status_detail = f'Missing from {os.path.basename(folder1_path)}'
        else:
            # This shouldn't happen, but handle it just in case
            status = 'Error'
            status_detail = 'Unexpected comparison state'
        
        # Create result entry
        result = {
            'Relative Path': relative_path,
            'Name': item1['name'] if item1 else item2['name'],
            'Type': item1['type'] if item1 else item2['type'],
            'Status': status,
            'Status Detail': status_detail,
            'Folder 1 Path': item1['path'] if item1 else '',
            'Folder 1 Size': item1['size'] if item1 and item1['type'] == 'file' else '',
            'Folder 1 Modified': item1['modified_time'].strftime('%Y-%m-%d %H:%M:%S') if item1 and item1['modified_time'] else '',
            'Folder 2 Path': item2['path'] if item2 else '',
            'Folder 2 Size': item2['size'] if item2 and item2['type'] == 'file' else '',
            'Folder 2 Modified': item2['modified_time'].strftime('%Y-%m-%d %H:%M:%S') if item2 and item2['modified_time'] else ''
        }
        
        comparison_results.append(result)
    
    return comparison_results

def get_comparison_summary(comparison_results):
    """
    Generate a summary of the comparison results.
    """
    status_counts = {}
    for result in comparison_results:
        status = result['Status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    total_items = len(comparison_results)
    
    summary = {
        'Total Items': total_items,
        'Same': status_counts.get('Same', 0),
        'Modified': status_counts.get('Modified', 0),
        'Only in Folder 1': status_counts.get('Only in Folder 1', 0),
        'Only in Folder 2': status_counts.get('Only in Folder 2', 0),
        'Type Mismatch': status_counts.get('Type Mismatch', 0),
        'Errors': status_counts.get('Error', 0)
    }
    
    return summary