import os
import json
import subprocess
from typing import List, Set
from platformdirs import user_data_dir
from .file import is_valid_file, get_all_files_in_directory

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
    new_pins = set()
    for item in items:
        if item.endswith("@tmux"):
            new_pins.add(item)
        else:
            new_pins.add(os.path.abspath(item))
    updated_pins = list(existing_pins.union(new_pins))
    save_pinned_items(updated_pins)
    return len(updated_pins) - len(existing_pins)

def remove_pins(items: List[str]) -> int:
    existing_pins = set(get_pinned_items())
    items_to_remove = set()
    for item in items:
        if item.endswith("@tmux"):
            items_to_remove.add(item)
        else:
            items_to_remove.add(os.path.abspath(item))
    updated_pins = list(existing_pins - items_to_remove)
    save_pinned_items(updated_pins)
    return len(existing_pins) - len(updated_pins)

def clear_pins():
    save_pinned_items([])

def get_unique_files(pinned_items: List[str]) -> Set[str]:
    unique_files = set()
    for item in pinned_items:
        if item.endswith("@tmux"):
            continue
        elif os.path.isfile(item) and is_valid_file(item):
            unique_files.add(os.path.abspath(item))
        elif os.path.isdir(item):
            unique_files.update(get_all_files_in_directory(item))
    return unique_files


def add_term(sessions: List[str]) -> int:
    existing_pins = set(get_pinned_items())
    new_pins = set(f"{session}@tmux" for session in sessions)
    updated_pins = list(existing_pins.union(new_pins))
    save_pinned_items(updated_pins)
    return len(updated_pins) - len(existing_pins)

def remove_term(sessions: List[str]) -> int:
    existing_pins = set(get_pinned_items())
    items_to_remove = set(f"{session}@tmux" for session in sessions)
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