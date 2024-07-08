
import typer
import os
import shlex
from typing import List, Dict, Optional
from rich import print
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from rich import box
from .pin import add_pins, clear_pins, get_pinned_items, remove_pins
from .clip import copy_pinboard
from .config import set_llm_config
from .llm import chat as llm_chat
from .utils import get_clipboard_content
from .format import print_success, print_error, print_info, print_file_change

app = typer.Typer()
console = Console()

@app.command()
def add(items: List[str] = typer.Argument(..., help="File or folder paths to add to the pinboard, or tmux sessions with @tmux suffix")):
    """Add file or folder paths to the pinboard, or tmux sessions with @tmux suffix."""
    added_count = add_pins(items)
    if added_count == 0:
        print_info("No new items added to the pinboard.")
    else:
        print_success(f"Added {added_count} new item(s) to the pinboard.")

@app.command()
def rm(items: Optional[List[str]] = typer.Argument(None, help="File, folder paths, or tmux sessions to remove from the pinboard")):
    """Remove specified items from the pinboard or clear the entire pinboard if no items are specified."""
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
    """Copy the contents of the pinboard to the clipboard."""
    copy_pinboard()
    print_success("Pinboard contents copied to clipboard.")

@app.command()
def llm(model: str):
    """Configure the LLM to use for editing files."""
    set_llm_config(model)
    print_success(f"LLM set to {model}.")

@app.command()
def ls():
    """List all pinned files, folders, and tmux sessions."""
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
    else:
        print_error(f"Unknown command: {cmd}")

@app.command()
def sh(
    message: str = typer.Argument(None, help="Message to send to the LLM"),
    with_clipboard: bool = typer.Option(False, "--with-clipboard", "-clip", help="Include clipboard content in the chat"),
):
    """Start an interactive shell or send a one-time message to the LLM about pinned files, edit them, or ask questions."""
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
            
            if message.split()[0] in ["add", "rm", "cp", "llm", "ls"]:
                execute_pin_command(message)
            else:
                response, file_change_summary = process_chat_message(message, clipboard_content, chat_history, interactive=True)
                chat_history.append({"role": "user", "content": message})
                if file_change_summary:
                    chat_history.append({"role": "assistant", "content": file_change_summary})
                else:
                    chat_history.append({"role": "assistant", "content": response})
            
            print()
    else:
        process_chat_message(message, clipboard_content, chat_history, interactive=False)

def process_chat_message(message: str, clipboard_content: str = None, chat_history: List[Dict[str, str]] = None, interactive: bool = False):
    if not interactive:
        print_info("Querying language model for a response...")
    response, file_change_summary = llm_chat(message, clipboard_content, chat_history)
    
    if "<artifact" not in response:
        print(Panel(response, title="Response", title_align="left", expand=False, border_style="green"))
    return response, file_change_summary

if __name__ == "__main__":
    app()
