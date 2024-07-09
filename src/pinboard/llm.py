import os
import json
import re
from typing import Dict, List, Union
from anthropic import Anthropic
import typer
from rich.console import Console
from .config import get_llm_config, store_last_operation, store_file_version, clear_file_versions
from .file import update_file, add_new_file, get_all_files_in_directory, is_valid_file, remove_file
from .pin import get_pinned_items, remove_pins
from .term import get_term_content
from .utils import get_file_content, get_numbered_file_content, parse_llm_response, apply_edits
from .format import print_file_change, print_info

console = Console()

def get_llm_client():
    return Anthropic()

def get_all_pinned_files():
    pinned_items = get_pinned_items()
    return [item for item in pinned_items if os.path.isfile(item) and is_valid_file(item)] + \
           [file for item in pinned_items if os.path.isdir(item) 
            for file in get_all_files_in_directory(item)]

def generate_file_change_summary(edited_files: Dict[str, Union[str, List[Dict[str, Union[str, int]]]]]) -> str:
    summary = []
    for file_path, edits in edited_files.items():
        if file_path.endswith("@tmux"):
            summary.append(f"Skipped read-only term object: {file_path}")
        elif isinstance(edits, list):
            if any(edit['content'].strip() == "" for edit in edits):
                summary.append(f"Removed file: {file_path}")
            else:
                summary.append(f"Updated file: {file_path}")
        elif isinstance(edits, str):
            summary.append(f"Added file: {file_path}")
    return "\n".join(summary) if summary else "No files were edited, added, or removed."

def chat(message: str, clipboard_content: str = None, chat_history: List[Dict[str, str]] = None):
    client = get_llm_client()
    config = get_llm_config()
    all_files = get_all_pinned_files()

    system_prompt = ("You are an AI assistant that can answer questions about files and edit them. "
                     "If the user requests any kinds of codebase changes, respond with the appropriate edits using <artifactEdit> tags. "
                     "If the user asks a question, provide a succint response. "
                     "Follow these rules strictly:\n"
                     "1. For codebase changes, use <artifactEdit> tags with 'identifier', 'from', and 'to' attributes. For complete file rewrites, 'from' should be \"1\" and 'to' should be the last line number.\n"
                     "2. Both the 'from' and 'to' indices are inclusive. Set 'from' to exactly the first line of the intended edit, and 'to' to exactly the last edited line. Mind the newlines. The two indices my coincide for a single line being overwritten (e.g. 3-3) with zero, one, or more lines.\n"
                     "3. For genuinely new files that haven't existed before at all, use <artifactEdit> tags with only the 'identifier' attribute. Only skip 'from' and 'to' when the file doesn't exist. Otherwise, attempt edits between 'from' and 'to' line lumbers.\n"
                     "4. Make sure to only use correct, absolute file paths as identifiers.\n"
                     "5. Provide only the changed content within the <artifactEdit> tags.\n"
                     "6. Do NOT include line numbers (e.g. '1.') between <artifactEdit> </artifactEdit> tags child content, not even for newly created files. The line numbers are only meant to help you identify which lines to edit, and are not actually part of the pinned files.\n"
                     "7. To remove lines, provide no content within the <artifactEdit> tags.\n"
                     "8. When creating new files or modifying existing ones, surgically update references (e.g. import statements) in all affected files to maintain consistency. Proactively identify and update any files that may be impacted by changes in module structure or file organization.\n"
                     "9. Pinned term objects (ending with @tmux) are read-only. You can only update, add, or remove files.\n"
                     "10. For questions, provide a concise, direct answer without using <artifactEdit> tags at all.\n"
                     "11. Accurately preserve tab indentation when producing artifactEdits. The content inside <artifactEdit> tags will directly replace the referenced lines, so maintaining correct indentation is crucial.\n"
                     "12. If you intend to make edits in different parts of the same artifact, rewrite the entire artifact with all changes included in one big edit. In general, however, try to make precise, surgical edits.\n"
                     "13. If you intend to add a considerable number of novel lines to a file (e.g. an entirely new function, a series of new statement), attempt to make granular edits from and to a single line number which gets overwritten with the new content. Make sure to preserve the overwritten content in the new content in that case.\n")

    human_prompt = "Workspace overview. Current pinned items:\n\n"
    for file in all_files:
        human_prompt += f"<artifact identifier=\"{file}\">\n{get_numbered_file_content(file)}\n</artifact>\n\n"

    pinned_items = get_pinned_items()
    for item in pinned_items:
        if item.endswith("@tmux"):
            session_name = item[:-5]
            human_prompt += f"<artifact identifier=\"{item}\">\n{get_term_content(session_name)}\n</artifact>\n\n"

    if clipboard_content:
        human_prompt += f"Clipboard content:\n{clipboard_content}\n\n"
    
    messages = []
    if chat_history:
        messages.extend(chat_history)
        
    messages.append({"role": "user", "content": f"{human_prompt}\nUser: {message}"})

    response = client.messages.create(
        model=config["model"],
        max_tokens=4000,
        messages=messages,
        system=system_prompt,
    )

    content = response.content[0].text if response.content else ""
    if "<artifactEdit" in content:
        edited_files = parse_llm_response(content)
        last_operation = {"edited_files": {}}
        clear_file_versions()
        
        for file_path, edits in edited_files.items():
            if file_path.endswith("@tmux"):
                print_info(f"Skipping read-only term object: {file_path}")
            elif isinstance(edits, list):
                file_content = get_file_content(file_path)
                store_file_version(file_path, file_content)
                updated_content = apply_edits(file_content, edits)
                if updated_content.strip() == "":
                    remove_file(file_path)
                    print_file_change("Removed", file_path)
                    last_operation["edited_files"][file_path] = "removed"
                else:
                    update_file(file_path, updated_content)
                    for edit in edits:
                        print_file_change("Updated", file_path, edit["from"], edit["to"])
                    last_operation["edited_files"][file_path] = "updated"
            elif isinstance(edits, str):  # New file
                add_new_file(file_path, edits)
                print_file_change("Added", file_path)
                last_operation["edited_files"][file_path] = "added"
        
        store_last_operation(last_operation)
        if not edited_files:
            print_info("No files were edited, added, or removed.")
        
        # Generate a summary of file changes for the chat history
        file_change_summary = generate_file_change_summary(edited_files)
        
        return content, file_change_summary
    else:
        return content, None