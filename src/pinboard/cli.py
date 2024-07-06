import typer
import os
from typing import List
from .file_operations import add_pins, clear_pins, copy_pinboard, get_pinned_items, remove_pins
from .config import set_llm_config
from .llm import edit_files, inline_edit
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
def rm(items: List[str] = typer.Argument(..., help="File or folder paths to remove from the pinboard")):
    """Remove file or folder paths from the pinboard."""
    removed_count = remove_pins(items)
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
def edit(message: str, with_clipboard: bool = typer.Option(False, "--with-clipboard", help="Edit using clipboard content")):
    """Edit pinned files using the configured LLM."""
    if with_clipboard:
        clipboard_content = get_clipboard_content()
        inline_edit(message, clipboard_content)
    else:
        edit_files(message)

@app.command()
def ls():
    """List all pinned files and folders."""
    pinned_items = get_pinned_items()
    if pinned_items:
        typer.echo("Pinned items:")
        for item in pinned_items:
            item_type = "Directory" if os.path.isdir(item) else "File"
            typer.echo(f"- [{item_type}] {item}")
    else:
        typer.echo("No items are currently pinned.")

if __name__ == "__main__":
    app()