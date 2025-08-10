import os
from collections import defaultdict
from pathlib import Path


def get_file_name(file_path):

    try:
        return os.path.basename(file_path).lower()
    except (TypeError, AttributeError):
        return None


def find_duplicates(file_list):
    name_groups = defaultdict(list)
    
    for file_info in file_list:
        if file_info.get('Type') == 'File':
            file_path = file_info.get('Path')
            if file_path and os.path.exists(file_path):
                filename = get_file_name(file_path)
                if filename:
                    # Add file size for additional information
                    try:
                        file_size = os.path.getsize(file_path)
                        file_info_with_name = file_info.copy()
                        file_info_with_name['File Name'] = filename
                        file_info_with_name['Size'] = file_size
                        name_groups[filename].append(file_info_with_name)
                    except OSError:
                        continue
    
    # Return only groups with duplicates (more than 1 file)
    duplicates = {filename: files for filename, files in name_groups.items() if len(files) > 1}
    return duplicates


def format_duplicate_results(duplicates):
    """
    Format duplicate detection results for Excel export.
    
    Args:
        duplicates (dict): Dictionary from find_duplicates()
        
    Returns:
        list: List of dictionaries formatted for Excel export
    """
    results = []
    group_id = 1
    
    for filename, files in duplicates.items():
        for i, file_info in enumerate(files):
            results.append({
                'Duplicate_Group': group_id,
                'File_Number': i + 1,
                'Total_in_Group': len(files),
                'Type': file_info.get('Type', 'File'),
                'Name': file_info.get('Name'),
                'Path': file_info.get('Path'),
                'Extension': file_info.get('Extension'),
                'Size_Bytes': file_info.get('Size'),
                'Hash': filename  # This is actually the filename for duplicate detection
            })
        group_id += 1
    
    return results


def get_duplicate_statistics(duplicates):
    total_duplicate_files = sum(len(files) for files in duplicates.values())
    return total_duplicate_files