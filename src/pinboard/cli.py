import typer
import os
from typing import List, Dict
from rich import print
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from .pin import add_pins, clear_pins, get_pinned_items, remove_pins
from .clip import copy_pinboard
from .term import add_term, remove_term
from .config import set_llm_config
from .llm import chat as llm_chat
from .utils import get_clipboard_content
from .format import print_success, print_error, print_info, print_file_change

app = typer.Typer()
console = Console()

@app.command()
def add(items: List[str] = typer.Argument(..., help="File or folder paths to add to the pinboard")):
    """Add file or folder paths to the pinboard."""
    added_count = add_pins(items)
    if added_count == 0:
        print_info("No new items added to the pinboard.")
    else:
        print_success(f"Added {added_count} new item(s) to the pinboard.")

@app.command()
def term(sessions: List[str] = typer.Argument(..., help="Term names to add to the pinboard")):
    """Add terms to the pinboard."""
    added_count = add_term(sessions)
    if added_count == 0:
        print_info("No new terms added to the pinboard.")
    else:
        print_success(f"Added {added_count} new term(s) to the pinboard.")

@app.command()
def rm(items: List[str] = typer.Argument(..., help="File, folder paths, or term names to remove from the pinboard")):
    """Remove file, folder paths, or term names from the pinboard."""
    removed_count = remove_pins(items) + remove_term(items)
    if removed_count == 0:
        print_info("No items were removed from the pinboard.")
    else:
        print_success(f"Removed {removed_count} item(s) from the pinboard.")

@app.command()
def clear():
    """Clear the contents of the pinboard."""
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
def chat(
    message: str = typer.Argument(None, help="Message to send to the LLM"),
    with_clipboard: bool = typer.Option(False, "--with-clipboard", "-clip", help="Include clipboard content in the chat"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Start an interactive chat session")
):
    """Chat with the LLM about pinned files, edit them, or ask questions."""
    clipboard_content = get_clipboard_content() if with_clipboard else None
    chat_history = []

    if interactive:
        print_info("Starting interactive chat session. Type 'exit' to end the session.")
        while True:
            message = typer.prompt("> ", prompt_suffix="")
            if message.lower() == 'exit':
                break
            response, file_change_summary = process_chat_message(message, clipboard_content, chat_history, interactive=True)
            chat_history.append({"role": "user", "content": message})
            if file_change_summary:
                chat_history.append({"role": "assistant", "content": file_change_summary})
            else:
                chat_history.append({"role": "assistant", "content": response})
    elif message:
        process_chat_message(message, clipboard_content, chat_history, interactive=False)
    else:
        print_error("Please provide a message or use the --interactive/-i flag to start an interactive session.")

def process_chat_message(message: str, clipboard_content: str = None, chat_history: List[Dict[str, str]] = None, interactive: bool = False):
    if not interactive:
        print_info("Querying language model for a response...")
    response, file_change_summary = llm_chat(message, clipboard_content, chat_history)
    
    if "<artifact" not in response:
        print(Panel(response, title="Response", title_align="left", expand=False, style="green"))
    return response, file_change_summary

@app.command()
def ls():
    """List all pinned files, folders, and terms."""
    pinned_items = get_pinned_items()
    if pinned_items:
        table = Table(title=f"Pinned Items ({len(pinned_items)} total)")
        table.add_column("Type", style="cyan")
        table.add_column("Item", style="green")

        for item in pinned_items:
            if item.startswith("term:"):
                table.add_row("Term", item[5:])
            elif os.path.isdir(item):
                table.add_row("Directory", item)
            else:
                table.add_row("File", item)

        console.print(table)
    else:
        print_info("The pinboard is currently empty.")

if __name__ == "__main__":
    app()