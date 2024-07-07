import os
import json
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