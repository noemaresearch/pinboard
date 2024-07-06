import os
import json
from anthropic import Anthropic
import typer
from .config import get_llm_config
from .file_operations import get_pinned_items, update_file, add_new_file, get_all_files_in_directory
from .utils import get_file_content, parse_llm_response

def get_llm_client():
    return Anthropic()

def get_all_pinned_files():
    pinned_items = get_pinned_items()
    return [item for item in pinned_items if os.path.isfile(item)] + \
           [file for item in pinned_items if os.path.isdir(item) 
            for file in get_all_files_in_directory(item)]

def process_edit(message: str, clipboard_content: str = None):
    client = get_llm_client()
    config = get_llm_config()
    all_files = get_all_pinned_files()

    system_prompt = ("You are an AI assistant that edits files. Respond only with the full "
                     "content of each edited file using <artifact> tags. Follow these rules strictly:\n"
                     "1. Provide the complete file content for each edited file, not just the changes.\n"
                     "2. Use the file path as the identifier.\n"
                     "3. Place <artifact> and </artifact> tags at the beginning of a new line.\n"
                     "4. Do not include any explanations or comments outside the artifact tags.\n"
                     "5. Ensure there is no content before the first <artifact> tag or after the last </artifact> tag.")

    human_prompt = "Current files:\n\n"
    for file in all_files:
        human_prompt += f"<artifact identifier=\"{file}\">\n{get_file_content(file)}\n</artifact>\n\n"

    if clipboard_content:
        human_prompt += f"Clipboard content:\n{clipboard_content}\n\n"

    human_prompt += f"Make the following edits: {message}"

    typer.echo("Edits in progress...")
    response = client.messages.create(
        model=config["model"],
        max_tokens=3000,
        system=system_prompt,
        messages=[{"role": "user", "content": human_prompt}]
    )

    content = response.content[0].text if response.content else ""
    edited_files = parse_llm_response(content)

    for file_path, content in edited_files.items():
        if file_path in all_files:
            update_file(file_path, content)
            typer.echo(f"Updated file: {file_path}")
        else:
            add_new_file(file_path, content)
            typer.echo(f"Added new file: {file_path}")

    if not edited_files:
        typer.echo("No files were edited or added.")

def edit_files(message: str):
    process_edit(message)

def inline_edit(message: str, clipboard_content: str):
    process_edit(message, clipboard_content)