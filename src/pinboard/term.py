import subprocess

def add_term(sessions):
    return [f"{session}@tmux" for session in sessions]

def remove_term(sessions):
    return [f"{session}@tmux" for session in sessions]

def get_term_content(session_name: str) -> str:
    try:
        output = subprocess.check_output(
            ["tmux", "capture-pane", "-p", "-t", session_name],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        return output.strip()
    except subprocess.CalledProcessError as e:
        return f"Error capturing term content: {e.output}"