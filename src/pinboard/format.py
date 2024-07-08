from rich.console import Console
from rich.panel import Panel
from rich import box
from typing import Optional

console = Console()

def print_success(message: str):
    console.print(Panel(message, title="Success", title_align="left", border_style="green", box=box.ROUNDED, expand=False))

def print_error(message: str):
    console.print(Panel(message, title="Error", title_align="left", border_style="red", box=box.ROUNDED, expand=False))

def print_info(message: str):
    console.print(Panel(message, title="Info", title_align="left", border_style="blue", box=box.ROUNDED, expand=False))

def print_file_change(action: str, file_path: str, from_line: Optional[int] = None, to_line: Optional[int] = None):
    if action == "Added":
        print_success(f"{action} file: {file_path}")
    elif action == "Updated":
        if from_line is not None and to_line is not None:
            print_success(f"{action} file: {file_path} (lines {from_line}-{to_line})")
        else:
            print_success(f"{action} file: {file_path}")
    elif action == "Removed":
        print_success(f"{action} file: {file_path}")