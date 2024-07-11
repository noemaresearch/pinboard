import subprocess
import shlex
from typing import Tuple

def run_command(command: str, tail: int = 20) -> Tuple[int, str]:
    """
    Run a shell command and return its exit code and last N lines of output.
    
    Args:
        command (str): The shell command to run.
        tail (int): Number of last lines to capture from the output.
    
    Returns:
        Tuple[int, str]: The exit code and the last N lines of output.
    """
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        output_lines = []
        for line in process.stdout:
            output_lines.append(line)
        
        process.wait()
        exit_code = process.returncode
        
        # Get the last N lines of output
        last_n_lines = ''.join(output_lines[-tail:])
        
        return exit_code, last_n_lines
    
    except Exception as e:
        return 1, f"Error running command: {str(e)}"