import typer
import os
from typing import List
from .pin import add_pins, clear_pins, get_pinned_items, remove_pins
from .clip import copy_pinboard
from .term import add_term, remove_term
from .config import set_llm_config
from .llm import chat as llm_chat
from .utils import get_clipboard_content

app = typer.Typer()

@app.command()
def add(items: List[str] = typer.Argument(..., help="File or folder paths to add to the pinboard")):
    """Add file or folder paths to the pinboard."""
    added_count = add_pins(items)
    if added_count == 0:
        typer.echo("No new items added to the pinboard.")
    else:
        typer.echo(f"Added {added_count} new item(s) to the pinboard.")

@app.command()
def term(sessions: List[str] = typer.Argument(..., help="Term names to add to the pinboard")):
    """Add terms to the pinboard."""
    added_count = add_term(sessions)
    if added_count == 0:
        typer.echo("No new terms added to the pinboard.")
    else:
        typer.echo(f"Added {added_count} new term(s) to the pinboard.")

@app.command()
def rm(items: List[str] = typer.Argument(..., help="File, folder paths, or term names to remove from the pinboard")):
    """Remove file, folder paths, or term names from the pinboard."""
    removed_count = remove_pins(items) + remove_term(items)
    if removed_count == 0:
        typer.echo("No items were removed from the pinboard.")
    else:
        typer.echo(f"Removed {removed_count} item(s) from the pinboard.")

@app.command()
def clear():
    """Clear the contents of the pinboard."""
    clear_pins()
    typer.echo("Pinboard cleared.")

@app.command()
def cp():
    """Copy the contents of the pinboard to the clipboard."""
    copy_pinboard()
    typer.echo("Pinboard contents copied to clipboard.")

@app.command()
def llm(model: str):
    """Configure the LLM to use for editing files."""
    set_llm_config(model)
    typer.echo(f"LLM set to {model}.")

@app.command()
def chat(
    message: str = typer.Argument(None, help="Message to send to the LLM"),
    with_clipboard: bool = typer.Option(False, "--with-clipboard", "-clip", help="Include clipboard content in the chat"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Start an interactive chat session")
):
    """Chat with the LLM about pinned files, edit them, or ask questions."""
    clipboard_content = get_clipboard_content() if with_clipboard else None

    if interactive:
        typer.echo("Starting interactive chat session. Type 'exit' to end the session.")
        while True:
            message = typer.prompt("> ", prompt_suffix="")
            if message.lower() == 'exit':
                break
            process_chat_message(message, clipboard_content)
    elif message:
        process_chat_message(message, clipboard_content)
    else:
        typer.echo("Please provide a message or use the --interactive/-i flag to start an interactive session.")

def process_chat_message(message: str, clipboard_content: str = None):
    response = llm_chat(message, clipboard_content)
    
    if "<artifact" not in response:
        typer.echo(f'"{response}"')

@app.command()
def ls():
    """List all pinned files, folders, and terms."""
    pinned_items = get_pinned_items()
    if pinned_items:
        typer.echo(f"Pinned items ({len(pinned_items)} total):")
        for item in pinned_items:
            if item.startswith("term:"):
                typer.echo(f"- [Term] {item[5:]}")
            elif os.path.isdir(item):
                typer.echo(f"- [Directory] {item}")
            else:
                typer.echo(f"- [File] {item}")
    else:
        typer.echo("The pinboard is currently empty.")

if __name__ == "__main__":
    app()