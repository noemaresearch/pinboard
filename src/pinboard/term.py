import subprocess
from typing import List
from .pin import get_pinned_items, save_pinned_items

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