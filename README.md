# Pinboard

Almost all of this codebase has been produced by issuing high-level directives against pinned files. Pinboard is a command-line tool for managing file references when working with raw language models. It's meant to streamline codebase-level development workflows, allowing users to request contextual, in-place file updates efficiently.


## Usage

```
$ pin add README.md src/pinboard pyproject.toml
Added 3 new item(s) to the pinboard.

# Add a tmux session to the pinboard.
$ pin term my-session
Added 1 new term(s) to the pinboard.

$ pin ls
Pinned items (3 total):
- [File] /path/to/README.md
- [Directory] /path/to/src/pinboard
- [Term] my-session

# Remove some items.
$ pin rm my-session pyproject.toml
Removed 2 item(s) from the pinboard.

# Format files as a unified string for external prompting.
$ pin cp
Pinboard contents copied to clipboard.

$ pin llm anthropic/claude-3-5-sonnet-20240620
LLM set to anthropic/claude-3-5-sonnet-20240620.

# File editing and asking questions happen through the chat command.
$ pin chat "add setup instructions in readme"
Querying claude-3-5-sonnet-20240620 for a response...
Updated file: /path/to/README.md

# Clipboard content can also be included in the unified string.
$ pin chat -clip "add docstring to selected function"
Querying claude-3-5-sonnet-20240620 for a response...
Updated file: /path/to/src/pinboard/llm.py

# Editing can also yield new files.
$ pin chat "create a minimal contributing md and reference it in the readme"
Querying claude-3-5-sonnet-20240620 for a response...
Updated file: /path/to/README.md
Added new file: /path/to/CONTRIBUTING.md

# New files get automatically pinned.
$ pin ls
Pinned items (3 total):
- [File] /path/to/README.md
- [Directory] /path/to/src/pinboard
- [File] /path/to/CONTRIBUTING.md

# Ask questions about pinned files.
$ pin chat "where is the 'chat' command implemented?"
Querying claude-3-5-sonnet-20240620 for a response...
"The 'chat' command is implemented in the file /path/to/pinboard/src/pinboard/cli.py. It's defined as a Typer command function named 'chat' that takes optional parameters for the message, including clipboard content, and an interactive mode flag."

# Interactive chat mode.
$ pin chat -i
Starting interactive chat session. Type 'exit' to end the session.
> update the pin ls command to print the total number of pinned items
Querying claude-3-5-sonnet-20240620 for a response...
Updated file: /path/to/src/pinboard/cli.py
> exit

$ pin clear
Pinboard cleared.
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

4. Set up your Anthropic API key:
   ```
   $ export ANTHROPIC_API_KEY=your_api_key_here
   ```

## Contributing

Contributions are welcome. For details, see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache 2.0 License