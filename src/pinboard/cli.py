from pinboard.shell import run_command
from .config import get_succeed_operations, clear_succeed_operations
import re
import typer
import os
import json
import shlex
from typing import List, Dict, Optional
from rich import print
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from rich import box
from .pin import add_pins, clear_pins, get_pinned_items, remove_pins
from .clip import copy_pinboard
from .config import set_llm_config, get_last_operation, get_file_version, clear_last_operation
from .utils import get_clipboard_content
from .format import print_success, print_error, print_info, print_file_change
from .file import update_file, remove_file
from .llm import chat as llm_chat, succeed_chat

app = typer.Typer()
console = Console()

@app.command()
def add(items: List[str] = typer.Argument(..., help="File or folder paths to add to the pinboard, or tmux sessions with @tmux suffix")):
    """
    Add file or folder paths to the pinboard, or tmux sessions with @tmux suffix.

    This command allows you to pin specific files, entire folders, or tmux sessions for quick access and manipulation.
    For tmux sessions, append '@tmux' to the session name (e.g., 'mysession@tmux').

    If a folder is added, all valid files within that folder (and its subfolders) will be included in the pinboard.
    """
    valid_items = []
    invalid_items = []

    for item in items:
        if item.endswith("@tmux"):
            # For tmux sessions, we can't easily check if they exist, so we'll assume they're valid
            valid_items.append(item)
        elif os.path.exists(item):
            valid_items.append(item)
        else:
            invalid_items.append(item)

    if invalid_items:
        print_error(f"The following items do not exist and cannot be added: {', '.join(invalid_items)}")

    added_count = add_pins(valid_items)
    if added_count == 0:
        print_info("No new items added to the pinboard.")
    else:
        print_success(f"Added {added_count} new item(s) to the pinboard.")

@app.command()
def rm(items: Optional[List[str]] = typer.Argument(None, help="File or folder paths, or tmux sessions to remove from the pinboard")):
    """
    Remove specified items from the pinboard or clear the entire pinboard if no items are specified.

    This command allows you to unpin specific files, folders, or tmux sessions from the pinboard.
    If no arguments are provided, it will clear the entire pinboard.

    For tmux sessions, append '@tmux' to the session name (e.g., 'mysession@tmux').
    """
    if items:
        removed_count = remove_pins(items)
        if removed_count == 0:
            print_info("No items were removed from the pinboard.")
        else:
            print_success(f"Removed {removed_count} item(s) from the pinboard.")
    else:
        clear_pins()
        print_success("Pinboard cleared.")

@app.command()
def cp():
    """
    Copy the contents of the pinboard to the clipboard.

    This command generates a formatted text representation of all pinned items,
    including file contents and tmux session outputs, and copies it to the system clipboard.
    This is useful for quickly sharing the current state of your pinboard or for use with language models.
    """
    copy_pinboard()
    print_success("Pinboard contents copied to clipboard.")

@app.command()
def llm(model: str):
    """
    Configure the Language Model (LLM) to use for editing files and answering questions.

    This command sets the specific LLM model to be used for all subsequent operations that require AI assistance.
    Currently, only Anthropic models are supported.

    Args:
        model: The identifier of the LLM model (e.g., 'anthropic/claude-3-5-sonnet-20240620')
    """
    set_llm_config(model)
    print_success(f"LLM set to {model}.")

@app.command()
def ls():
    """
    List all pinned files, folders, and tmux sessions.

    This command displays a formatted table showing all items currently pinned in the pinboard.
    It categorizes items as files, directories, or tmux sessions for easy overview.
    """
    pinned_items = get_pinned_items()
    if pinned_items:
        table = Table(
            border_style="blue",
            box=box.ROUNDED,
            expand=False,
            show_header=True,
            header_style="bold"
        )
        table.add_column("Type")
        table.add_column(f"Item ({len(pinned_items)} total)")

        for item in pinned_items:
            if item.endswith("@tmux"):
                table.add_row("Tmux Session", item[:-5])
            elif os.path.isdir(item):
                table.add_row("Directory", item)
            else:
                table.add_row("File", item)

        console.print(table)
    else:
        print_info("The pinboard is currently empty.")

def execute_pin_command(command: str):
    """Execute a pin command without the 'pin' prefix."""
    args = shlex.split(command)
    if not args:
        return

    cmd = args[0]
    remaining_args = args[1:]

    if cmd == "add":
        add(remaining_args)
    elif cmd == "rm":
        rm(remaining_args)
    elif cmd == "cp":
        cp()
    elif cmd == "llm":
        if remaining_args:
            llm(remaining_args[0])
        else:
            print_error("Please provide a model name for the llm command.")
    elif cmd == "ls":
        ls()
    elif cmd == "undo":
        undo()
    else:
        print_error(f"Unknown command: {cmd}")

@app.command()
def sh(
    message: str = typer.Argument(None, help="Message to send to the LLM for one-time processing"),
    with_clipboard: bool = typer.Option(False, "--with-clipboard", "-clip", help="Include clipboard content in the chat context"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show full response from the language model")
):
    """
    Start an interactive shell or send a one-time message to the LLM about pinned files.

    This command allows you to interact with the AI assistant to ask questions about pinned files,
    request file edits, or perform other operations on your codebase. It can be used in two modes:
    1. Interactive shell: If no message is provided, it starts an interactive session.
    2. One-time message: If a message is provided, it processes that message and exits.

    In the interactive mode, you can use pinboard commands (add, rm, cp, llm, ls) directly.
    The AI assistant can make changes to your files based on your requests.

    Args:
        message: The message to send to the LLM (optional, for one-time processing)
        with_clipboard: Include the current clipboard content in the chat context
    """
    clipboard_content = get_clipboard_content() if with_clipboard else None
    chat_history = []
    if message is None:
        print_info("Starting pin shell. Type 'exit' to end the session.")
        print()
        while True:
            message = typer.prompt("> ", prompt_suffix="")
            print()  # Add an empty line after user input
            
            if message.lower() == 'exit':
                break
            
            if message.split()[0] in ["add", "rm", "cp", "llm", "ls", "undo"]:
                execute_pin_command(message)
            else:
                response = process_chat_message(message, clipboard_content, chat_history, interactive=True, verbose=verbose)
                chat_history.append({"role": "user", "content": message})
                chat_history.append({"role": "assistant", "content": response})
            
            print()
    else:
        process_chat_message(message, clipboard_content, chat_history, interactive=False, verbose=verbose)

def process_chat_message(message: str, clipboard_content: str = None, chat_history: List[Dict[str, str]] = None, interactive: bool = False, verbose: bool = False):
    if not interactive:
        print_info("Querying language model for a response...")
    response, _ = llm_chat(message, clipboard_content, chat_history)
    
    if "<artifact" not in response or verbose:
        response = re.sub(r'<artifactEdit[^>]*>.*?</artifactEdit>', "...", response, flags=re.DOTALL)
        print(Panel(response, title="Response", title_align="left", expand=False, border_style="green"))
        
    return response
        
@app.command()
def succeed(
    command: str = typer.Argument(..., help="Shell command to execute"),
    tail: int = typer.Option(20, "--tail", "-t", help="Number of lines to capture from command output"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show full response from the language model")
):
    """
    Execute a shell command and use the LLM to fix any errors until the command succeeds.

    This command runs the specified shell command and, if it fails, uses the AI assistant to
    make changes to the pinned files until the command succeeds (returns exit code 0).
    The process is iterative and can be undone in one go.

    Args:
        command: The shell command to execute.
        tail: Number of lines to capture from command output (default: 20).
        verbose: Show full response from the language model.
    """
    print_info(f"Executing command: {command}")
    exit_code, output = run_command(command, tail)
    iteration = 1

    while exit_code != 0:
        print_error(f"Command failed with exit code {exit_code}. Iteration {iteration}.")
        if output.strip():
            print(Panel(output, title=f"Last {tail} lines of output", title_align="left", expand=False, border_style="yellow"))

        response, file_changes = succeed_chat(command, output, verbose=verbose)
        
        if not file_changes:
            print_error("The language model couldn't make any changes. Aborting.")
            break

        print_info(f"Executing command: {command}")
        exit_code, output = run_command(command, tail)
        iteration += 1

    if exit_code == 0:
        print_success(f"Command succeeded after {iteration} iterations.")
    else:
        print_error(f"Command failed after {iteration} iterations. Unable to fix the issue.")

@app.command()
def undo():
    """
    Undo the last file changes made by the 'pin sh' or 'pin succeed' commands.

    This command reverts the added, updated, or removed files based on the last 'pin sh' or 'pin succeed' operation.
    It only undoes the most recent changes and cannot perform multiple undos.
    """
    last_operation = get_last_operation()
    succeed_operations = get_succeed_operations()

    if succeed_operations:
        for operation in reversed(succeed_operations):
            for file_path, action in operation.get("edited_files", {}).items():
                print_info(f"Undoing action '{action}' for file: {file_path}")
                if action == "added":
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print_file_change("Removed", file_path)
                    else:
                        print_error(f"File not found: {file_path}")
                elif action in ["updated", "removed"]:
                    previous_content = get_file_version(file_path)
                    if previous_content is not None:
                        update_file(file_path, previous_content)
                        print_file_change("Restored", file_path)
                    else:
                        print_error(f"No previous version found for: {file_path}")
        clear_succeed_operations()
        print_success("Undo operation for 'pin succeed' completed.")
    elif last_operation:
        edited_files = last_operation.get("edited_files", {})
        if not edited_files:
            print_info("No files were affected in the last operation.")
            return

        print_info(f"Files affected in the last operation: {', '.join(edited_files.keys())}")

        for file_path, action in edited_files.items():
            print_info(f"Undoing action '{action}' for file: {file_path}")
            if action == "added":
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print_file_change("Removed", file_path)
                else:
                    print_error(f"File not found: {file_path}")
            elif action in ["updated", "removed"]:
                previous_content = get_file_version(file_path)
                if previous_content is not None:
                    update_file(file_path, previous_content)
                    print_file_change("Restored", file_path)
                else:
                    print_error(f"No previous version found for: {file_path}")

        clear_last_operation()
        print_success("Undo operation for 'pin sh' completed.")
    else:
        print_error("No previous operation to undo.")

if __name__ == "__main__":
    app()