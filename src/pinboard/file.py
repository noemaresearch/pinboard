import os
from typing import Set

def is_valid_file(file_path: str) -> bool:
    ignored_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.svg',
                          '.mp3', '.wav', '.ogg', '.mp4', '.avi', '.mov', '.wmv',
                          '.zip', '.tar', '.gz', '.rar', '.7z',
                          '.exe', '.dll', '.so', '.dylib',
                          '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'}
    
    return (not os.path.basename(file_path).startswith('.') and
            os.path.splitext(file_path)[1].lower() not in ignored_extensions)

def get_all_files_in_directory(directory: str) -> Set[str]:
    all_files = set()
    for root, dirs, files in os.walk(directory):
        # Ignore hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            file_path = os.path.abspath(os.path.join(root, file))
            if is_valid_file(file_path):
                all_files.add(file_path)
    return all_files

def update_file(file_path: str, new_content: str):
    with open(file_path, "w") as f:
        f.write(new_content)

def add_new_file(file_path: str, content: str):
    with open(file_path, "w") as f:
        f.write(content)

def remove_file(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)