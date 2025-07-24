
import os

def replicate_folder_structure(source, destination):
    replicated = []
    for dirpath, dirnames, _ in os.walk(source):
        for dirname in dirnames:
            source_path = os.path.join(dirpath, dirname)
            relative_path = os.path.relpath(source_path, source)
            dest_path = os.path.join(destination, relative_path)
            try:
                os.makedirs(dest_path, exist_ok=True)
                status = 'Replicated'
            except Exception as e:
                status = f'Failed: {e}'
            replicated.append({
                'Name': dirname,
                'Source Path': source_path,
                'Destination Path': dest_path,
                'Status': status
            })
    return replicated
