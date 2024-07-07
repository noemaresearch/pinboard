import os
import json
from typing import Dict, List, Union
from anthropic import Anthropic
import typer
from rich.console import Console
from .config import get_llm_config
from .file import update_file, add_new_file, get_all_files_in_directory, is_valid_file, remove_file
from .pin import get_pinned_items, remove_pins
from .pin import get_term_content
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
                     "If the user requests any kinds of codebase changes, respond with the edited content using <artifactEdit> tags. "
                     "If the user asks a question, provide a concise response. "
                     "Follow these rules strictly:\n"
                     "1. For edits (including complete file rewrites), use <artifactEdit> tags with 'identifier', 'from', and 'to' attributes.\n"
                     "2. The 'from' index is inclusive, and the 'to' index is exclusive. Set 'from' to exactly the first line of the intended edit.\n"
                     "3. For new files, use <artifactEdit> tags with only the 'identifier' attribute.\n"
                     "4. Use correct, absolute file paths as identifiers.\n"
                     "5. Provide only the changed content within the <artifactEdit> tags.\n"
                     "6. Do NOT include line numbers inside <artifactEdit> </artifactEdit> tags, as their contents will directly overwrite files.\n"
                     "7. To remove lines, provide an empty content within the <artifactEdit> tags.\n"
                     "8. When creating new files or modifying existing ones, update import statements in all affected files to maintain consistency.\n"
                     "9. Proactively identify and update any files that may be impacted by changes in module structure or file organization.\n"
                     "10. Pinned term objects (ending with @tmux) are read-only. You can only update, add, or remove files.\n"
                     "11. For questions, provide a direct answer without using <artifactEdit> tags.\n"
                     "12. Accurately preserve tab indentation when producing artifactEdits. The content inside <artifactEdit> tags will be directly injected at the specified locations, so maintaining correct indentation is crucial.\n"
                     "13. If you intend to make multiple edits to the same artifact, rewrite the entire artifact with all changes included as one big edit.\n")

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
        for file_path, edits in edited_files.items():
            if file_path.endswith("@tmux"):
                print_info(f"Skipping read-only term object: {file_path}")
            elif isinstance(edits, list):
                file_content = get_file_content(file_path)
                updated_content = apply_edits(file_content, edits)
                if updated_content.strip() == "":
                    remove_file(file_path)
                    print_file_change("Removed", file_path)
                else:
                    update_file(file_path, updated_content)
                    for edit in edits:
                        print_file_change("Updated", file_path, edit["from"], edit["to"])
            elif isinstance(edits, str):  # New file
                add_new_file(file_path, edits)
                print_file_change("Added", file_path)
        
        if not edited_files:
            print_info("No files were edited, added, or removed.")
        
        # Generate a summary of file changes for the chat history
        file_change_summary = generate_file_change_summary(edited_files)
        return content, file_change_summary
    else:
        return content, None