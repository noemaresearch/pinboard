import os
import json
import pyclip
from typing import List, Set
from platformdirs import user_data_dir
import subprocess

DATA_DIR = user_data_dir("pinboard")
PINBOARD_FILE = os.path.join(DATA_DIR, "pinboard.json")

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def get_pinned_items() -> List[str]:
    ensure_data_dir()
    if os.path.exists(PINBOARD_FILE):
        with open(PINBOARD_FILE, 'r') as f:
            return json.load(f)
    return []

def save_pinned_items(items: List[str]):
    ensure_data_dir()
    with open(PINBOARD_FILE, 'w') as f:
        json.dump(items, f)

def add_pins(items: List[str]) -> int:
    existing_pins = set(get_pinned_items())
    new_pins = set(os.path.abspath(item) for item in items)
    updated_pins = list(existing_pins.union(new_pins))
    save_pinned_items(updated_pins)
    return len(updated_pins) - len(existing_pins)

def remove_pins(items: List[str]) -> int:
    existing_pins = set(get_pinned_items())
    items_to_remove = set(os.path.abspath(item) for item in items)
    updated_pins = list(existing_pins - items_to_remove)
    save_pinned_items(updated_pins)
    return len(existing_pins) - len(updated_pins)

def clear_pins():
    save_pinned_items([])

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

def get_unique_files(pinned_items: List[str]) -> Set[str]:
    unique_files = set()
    for item in pinned_items:
        if item.startswith("term:"):
            continue
        elif os.path.isfile(item) and is_valid_file(item):
            unique_files.add(os.path.abspath(item))
        elif os.path.isdir(item):
            unique_files.update(get_all_files_in_directory(item))
    return unique_files

def copy_pinboard():
    pinned_items = get_pinned_items()
    unique_files = get_unique_files(pinned_items)
    content = ["Table of contents"]

    for item in pinned_items:
        if item.startswith("term:"):
            content.append(f"- {item[5:]} (Term)")
        elif os.path.isfile(item) and is_valid_file(item):
            content.append(f"- {os.path.relpath(item)}")
        elif os.path.isdir(item):
            content.append(f"- {os.path.relpath(item)}/ (Directory)")
            dir_files = get_all_files_in_directory(item)
            for file in dir_files:
                content.append(f"  - {os.path.relpath(file)}")

    content.append("")

    for file in sorted(unique_files):
        content.append(f"# {os.path.basename(file)}")
        content.append(file)
        content.append("```")
        try:
            with open(file, "r") as f:
                content.append(f.read())
        except Exception as e:
            content.append(f"Error reading file: {str(e)}")
        content.append("```")
        content.append("")

    for item in pinned_items:
        if item.startswith("term:"):
            session_name = item[5:]
            content.append(f"# Term: {session_name}")
            content.append("```")
            content.append(get_term_content(session_name))
            content.append("```")
            content.append("")

    pyclip.copy("\n".join(content))

def update_file(file_path: str, new_content: str):
    with open(file_path, "w") as f:
        f.write(new_content)

def add_new_file(file_path: str, content: str):
    with open(file_path, "w") as f:
        f.write(content)
    add_pins([file_path])
    
def add_term(sessions: List[str]) -> int:
    existing_pins = set(get_pinned_items())
    new_pins = set(f"term:{session}" for session in sessions)
    updated_pins = list(existing_pins.union(new_pins))
    save_pinned_items(updated_pins)
    return len(updated_pins) - len(existing_pins)

def remove_term(sessions: List[str]) -> int:
    existing_pins = set(get_pinned_items())
    items_to_remove = set(f"term:{session}" for session in sessions)
    updated_pins = list(existing_pins - items_to_remove)
    save_pinned_items(updated_pins)
    return len(existing_pins) - len(updated_pins)

def get_term_content(session_name: str) -> str:
    try:
        output = subprocess.check_output(
            ["tmux", "capture-pane", "-p", "-t", session_name],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        return output.strip()
    except subprocess.CalledProcessError as e:
        return f"Error capturing term content: {e.output}"