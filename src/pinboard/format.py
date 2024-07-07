from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()

def print_success(message: str):
    console.print(Panel(message, title="Success", title_align="left", border_style="green", box=box.ROUNDED, expand=False))

def print_error(message: str):
    console.print(Panel(message, title="Error", title_align="left", border_style="red", box=box.ROUNDED, expand=False))

def print_info(message: str):
    console.print(Panel(message, title="Info", title_align="left", border_style="blue", box=box.ROUNDED, expand=False))

def print_file_change(action: str, file_path: str):
    if action == "Added":
        print_success(f"{action} file: {file_path}")
    elif action == "Updated":
        print_info(f"{action} file: {file_path}")
    elif action == "Removed":
        print_error(f"{action} file: {file_path}")