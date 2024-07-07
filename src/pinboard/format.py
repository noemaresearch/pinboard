from rich.console import Console
from rich.panel import Panel

console = Console()

def print_success(message: str):
    console.print(Panel(message, title="Success", title_align="left", style="green", expand=False))

def print_error(message: str):
    console.print(Panel(message, title="Error", title_align="left", style="red", expand=False))

def print_info(message: str):
    console.print(Panel(message, title="Info", title_align="left", style="blue", expand=False))

def print_file_change(action: str, file_path: str):
    if action == "Added":
        print_success(f"{action} file: {file_path}")
    elif action == "Updated":
        print_info(f"{action} file: {file_path}")
    elif action == "Removed":
        print_error(f"{action} file: {file_path}")