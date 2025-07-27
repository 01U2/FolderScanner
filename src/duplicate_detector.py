import hashlib
import os
from collections import defaultdict
from pathlib import Path


def calculate_file_hash(file_path, hash_algorithm='md5'):
    """
    Calculate hash of a file using specified algorithm.
    
    Args:
        file_path (str): Path to the file
        hash_algorithm (str): Hash algorithm to use ('md5' or 'sha256')
        
    Returns:
        str: Hexadecimal hash string or None if file cannot be read
    """
    try:
        if hash_algorithm.lower() == 'sha256':
            hash_obj = hashlib.sha256()
        else:
            hash_obj = hashlib.md5()
            
        with open(file_path, 'rb') as f:
            # Read file in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
                
        return hash_obj.hexdigest()
    except (IOError, OSError):
        return None


def find_duplicates(file_list):
    """
    Group files by hash to identify duplicates.
    
    Args:
        file_list (list): List of file dictionaries with 'Path' key
        
    Returns:
        dict: Dictionary with hash as key and list of duplicate files as value
    """
    hash_groups = defaultdict(list)
    
    for file_info in file_list:
        if file_info.get('Type') == 'File':
            file_path = file_info.get('Path')
            if file_path and os.path.exists(file_path):
                file_hash = calculate_file_hash(file_path)
                if file_hash:
                    # Add file size for additional validation
                    try:
                        file_size = os.path.getsize(file_path)
                        file_info_with_hash = file_info.copy()
                        file_info_with_hash['Hash'] = file_hash
                        file_info_with_hash['Size'] = file_size
                        hash_groups[file_hash].append(file_info_with_hash)
                    except OSError:
                        continue
    
    # Return only groups with duplicates (more than 1 file)
    duplicates = {hash_val: files for hash_val, files in hash_groups.items() if len(files) > 1}
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
    
    for hash_val, files in duplicates.items():
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
                'Hash': hash_val
            })
        group_id += 1
    
    return results


def get_duplicate_statistics(duplicates):
    """
    Get statistics about duplicates found.
    
    Args:
        duplicates (dict): Dictionary from find_duplicates()
        
    Returns:
        dict: Statistics about duplicates
    """
    total_duplicate_files = sum(len(files) for files in duplicates.values())
    total_groups = len(duplicates)
    total_wasted_space = 0
    
    for files in duplicates.values():
        if files:
            # Calculate wasted space (keep one copy, others are waste)
            file_size = files[0].get('Size', 0)
            wasted_copies = len(files) - 1
            total_wasted_space += file_size * wasted_copies
    
    return {
        'total_duplicate_files': total_duplicate_files,
        'total_groups': total_groups,
        'total_wasted_space_bytes': total_wasted_space,
        'total_wasted_space_mb': round(total_wasted_space / (1024 * 1024), 2)
    }