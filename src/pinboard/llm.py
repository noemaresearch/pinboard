import os
import json
from anthropic import Anthropic
import typer
from rich.console import Console
from .config import get_llm_config
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

def chat(message: str, clipboard_content: str = None):
    client = get_llm_client()
    config = get_llm_config()
    all_files = get_all_pinned_files()

    system_prompt = ("You are an AI assistant that can answer questions about files and edit them. "
                     "If the user asks for any kinds of changes, respond with the edited content using <artifactEdit> tags. "
                     "If the user instead asks a question, provide a concise and informative response. "
                     "Follow these rules strictly:\n"
                     "1. For edits, use <artifactEdit> tags with 'identifier', 'from', and 'to' attributes.\n"
                     "2. The 'from' attribute is inclusive, and the 'to' attribute is exclusive.\n"
                     "3. For new files, use <artifactEdit> tags with only the 'identifier' attribute.\n"
                     "4. Use correct, absolute file paths as identifiers.\n"
                     "5. Provide only the changed content within the <artifactEdit> tags.\n"
                     "6. To remove lines, provide an empty content within the <artifactEdit> tags.\n"
                     "7. When creating new files or modifying existing ones, update import statements in all affected files to maintain consistency.\n"
                     "8. Proactively identify and update any files that may be impacted by changes in module structure or file organization.\n"
                     "9. Pinned term objects (starting with 'term:') are read-only. You can only update, add, or remove files.\n"
                     "10. For questions, provide a direct answer without using <artifactEdit> tags.\n"
                     "11. Accurately preserve tab indentation when producing artifactEdits. The content inside <artifactEdit> tags will be directly injected at the specified locations, so maintaining correct indentation is crucial.")

    human_prompt = "Current files:\n\n"
    for file in all_files:
        human_prompt += f"<artifact identifier=\"{file}\">\n{get_numbered_file_content(file)}\n</artifact>\n\n"

    pinned_items = get_pinned_items()
    for item in pinned_items:
        if item.startswith("term:"):
            session_name = item[5:]
            human_prompt += f"<artifact identifier=\"{item}\">\n{get_term_content(session_name)}\n</artifact>\n\n"

    if clipboard_content:
        human_prompt += f"Clipboard content:\n{clipboard_content}\n\n"

    human_prompt += f"User: {message}"

    response = client.messages.create(
        model=config["model"],
        max_tokens=4000,
        system=system_prompt,
        messages=[{"role": "user", "content": human_prompt}]
    )

    content = response.content[0].text if response.content else ""
    
    if "<artifactEdit" in content:
        edited_files = parse_llm_response(content)
        for file_path, edits in edited_files.items():
            if file_path.startswith("term:"):
                print_info(f"Skipping read-only term object: {file_path}")
            elif isinstance(edits, list):
                file_content = get_file_content(file_path)
                updated_content = apply_edits(file_content, edits)
                if updated_content.strip() == "":
                    remove_file(file_path)
                    print_file_change("Removed", file_path)
                else:
                    update_file(file_path, updated_content)
                    print_file_change("Updated", file_path)
            elif isinstance(edits, str):  # New file
                add_new_file(file_path, edits)
                print_file_change("Added", file_path)
        
        if not edited_files:
            print_info("No files were edited, added, or removed.")
    
    return content