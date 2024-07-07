import pyclip
import os
from .pin import get_pinned_items, get_unique_files
from .file import get_all_files_in_directory, is_valid_file
from .term import get_term_content

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