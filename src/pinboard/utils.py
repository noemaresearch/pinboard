import pyclip
import re
import os
from typing import List, Dict, Union
from .pin import get_pinned_items, get_unique_files

def get_clipboard_content():
    return pyclip.paste().decode('utf-8')

def get_file_content(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return f.read()

def get_numbered_file_content(file_path: str) -> str:
    with open(file_path, 'r') as f:
        lines = f.readlines()
    return ''.join(f"{i+1}: {line}" for i, line in enumerate(lines))

def parse_llm_response(response: str) -> Dict[str, Union[str, List[Dict[str, Union[str, int]]]]]:
    artifact_edit_pattern = r'<artifactEdit identifier="([^"]+)" from="(\d+)" to="(\d+)">(.*?)</artifactEdit>'
    new_file_pattern = r'<artifactEdit identifier="([^"]+)">(.*?)</artifactEdit>'
    
    pinned_items = get_pinned_items()
    pinned_files = get_unique_files(pinned_items)
    pinned_folders = [item for item in pinned_items if os.path.isdir(item)]
    
    artifact_edits = {}
    for identifier, from_line, to_line, content in re.findall(artifact_edit_pattern, response, re.DOTALL):
        if identifier in pinned_files or any(identifier.startswith(folder) for folder in pinned_folders):
            if identifier not in artifact_edits:
                artifact_edits[identifier] = []
            artifact_edits[identifier].append({
                'from': int(from_line),
                'to': int(to_line),
                'content': content.strip("\n")
            })
    
    new_files = {}
    for identifier, content in re.findall(new_file_pattern, response, re.DOTALL):
        if identifier in pinned_files or any(identifier.startswith(folder) for folder in pinned_folders):
            new_files[identifier] = content.strip()
    
    return {**artifact_edits, **new_files}

def apply_edits(file_content: str, edits: List[Dict[str, Union[str, int]]]) -> str:
    lines = file_content.split('\n')
    for edit in sorted(edits, key=lambda x: x['from'], reverse=True):
        from_line = edit['from'] - 1
        to_line = edit['to']
        new_content = edit['content'].split('\n')
        lines[from_line:to_line] = new_content
    return '\n'.join(lines)