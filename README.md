# Pinboard

Pinboard is a command-line tool for managing file references and terminal sessions when working with raw language models. It's designed to streamline codebase-level development workflows, allowing users to request contextual, in-place file updates and interact with pinned content efficiently.

## Usage

```
$ pin add README.md src/pinboard pyproject.toml
Added 3 new item(s) to the pinboard.

# Add a tmux session to the pinboard.
$ pin add my-session@tmux
Added 1 new item(s) to the pinboard.

$ pin ls
Pinned Items (4 total):
- File: /path/to/README.md
- Directory: /path/to/src/pinboard
- File: /path/to/pyproject.toml
- Tmux Session: my-session

# Remove some items.
$ pin rm my-session@tmux pyproject.toml
Removed 2 item(s) from the pinboard.

# Clear the entire pinboard.
$ pin rm
Pinboard cleared.

# Format files as a unified string for external prompting.
$ pin cp
Pinboard contents copied to clipboard.

# File editing and asking questions happen through the sh command.
$ pin sh "add setup instructions in readme"
Querying language model for a response...
Updated file: /path/to/README.md

# Clipboard content can also be included in the unified string.
$ pin sh -clip "add docstring to selected function"
Querying language model for a response...
Updated file: /path/to/src/pinboard/llm.py

# Editing can also yield new files.
$ pin sh "create a minimal contributing md and reference it in the readme"
Querying language model for a response...
Updated file: /path/to/README.md
Added file: /path/to/CONTRIBUTING.md

# New files get automatically pinned.
$ pin ls
Pinned Items (3 total):
- File: /path/to/README.md
- Directory: /path/to/src/pinboard
- File: /path/to/CONTRIBUTING.md

# Ask questions about pinned files.
$ pin sh "where is the 'sh' command implemented?"
Querying language model for a response...
The 'sh' command is implemented in the file /path/to/pinboard/src/pinboard/cli.py. It's defined as a Typer command function named 'sh' that takes optional parameters for the message and including clipboard content.

# Interactive mode.
$ pin sh
Starting pin shell. Type 'exit' to end the session.
> ls
Pinned Items (3 total):
- File: /path/to/README.md
- Directory: /path/to/src/pinboard
- File: /path/to/CONTRIBUTING.md
> add newfile.txt
Added 1 new item(s) to the pinboard.
> update the pin ls command to print the total number of pinned items
Updated file: /path/to/src/pinboard/cli.py
> exit
```

## Installation

1. Ensure Python 3.8 or later is installed.

2. Install `pipx`:
   ```
   $ pip install pipx
   $ pipx ensurepath
   ```

3. Install Pinboard:
   ```
   $ pipx install git+https://github.com/paulbricman/pinboard.git
   ```

4. Configure your language model:
   ```
   $ pin llm anthropic/claude-3-5-sonnet-20240620
   $ export ANTHROPIC_API_KEY=your_api_key_here
   ```

## Contributing

Contributions are welcome. For details, see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache 2.0 License