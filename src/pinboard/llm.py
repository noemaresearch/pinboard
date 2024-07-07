import os
import json
from anthropic import Anthropic
import typer
from .config import get_llm_config
from .file import update_file, add_new_file, get_all_files_in_directory, is_valid_file, remove_file
from .pin import get_pinned_items, remove_pins
from .term import get_term_content
from .utils import get_file_content, parse_llm_response

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
                     "If the user asks for any kinds of changes, respond with the full content of each edited file using <artifact> tags. "
                     "If the user instead asks a question, provide a concise and informative response. "
                     "Follow these rules strictly:\n"
                     "1. For edits, provide the complete file content for each edited file, not just the changes.\n"
                     "2. Surround new, updated, or removed files with <artifact> and </artifact> tags placed at the beginning of their respective lines.\n"
                     "3. Use the file path as the artifact tag identifier.\n"
                     "4. Do not include any explanations or comments outside the artifact tags for edits.\n"
                     "5. Ensure there is no content before the first <artifact> tag or after the last </artifact> tag for edits.\n"
                     "6. To remove a file, provide an empty content within the artifact tags.\n"
                     "7. When creating new files or modifying existing ones, update import statements in all affected files to maintain consistency.\n"
                     "8. Proactively identify and update any files that may be impacted by changes in module structure or file organization.\n"
                     "9. Pinned term objects (starting with 'term:') are read-only. You can only update, add, or remove files.\n"
                     "10. For questions, provide a direct answer without using artifact tags.")

    human_prompt = "Current files:\n\n"
    for file in all_files:
        human_prompt += f"<artifact identifier=\"{file}\">\n{get_file_content(file)}\n</artifact>\n\n"

    pinned_items = get_pinned_items()
    for item in pinned_items:
        if item.startswith("term:"):
            session_name = item[5:]
            human_prompt += f"<artifact identifier=\"{item}\">\n{get_term_content(session_name)}\n</artifact>\n\n"

    if clipboard_content:
        human_prompt += f"Clipboard content:\n{clipboard_content}\n\n"

    human_prompt += f"User: {message}"

    typer.echo(f"Querying {config['model']} for a response...")
    response = client.messages.create(
        model=config["model"],
        max_tokens=4000,
        system=system_prompt,
        messages=[{"role": "user", "content": human_prompt}]
    )

    content = response.content[0].text if response.content else ""
    
    if "<artifact" in content:
        edited_files = parse_llm_response(content)
        for file_path, file_content in edited_files.items():
            if file_path.startswith("term:"):
                typer.echo(f"Skipping read-only term object: {file_path}")
            elif file_path in all_files:
                if file_content.strip() == "":
                    remove_file(file_path)
                    typer.echo(f"Removed file: {file_path}")
                else:
                    update_file(file_path, file_content)
                    typer.echo(f"Updated file: {file_path}")
            else:
                add_new_file(file_path, file_content)
                typer.echo(f"Added new file: {file_path}")
        
        if not edited_files:
            typer.echo("No files were edited, added, or removed.")
    
    return content