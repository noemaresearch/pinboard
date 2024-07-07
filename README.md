# Pinboard

Pinboard is a command-line tool for managing file references when working with raw language models. It's designed to streamline codebase-level development workflows, allowing users to request contextual, in-place file updates efficiently.

## Usage

```
$ pin add README.md src/pinboard pyproject.toml
╭─ Success ────────────────────────────╮
│ Added 3 new item(s) to the pinboard. │
╰──────────────────────────────────────╯

# Add a tmux session to the pinboard.
$ pin term my-session
╭─ Success ────────────────────────────╮
│ Added 1 new term(s) to the pinboard. │
╰──────────────────────────────────────╯

$ pin ls
                     Pinned Items (4 total)
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Type      ┃ Item                                              ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ File      │ /path/to/README.md                                │
│ Directory │ /path/to/src/pinboard                             │
│ File      │ /path/to/pyproject.toml                           │
│ Term      │ my-session                                        │
└───────────┴───────────────────────────────────────────────────┘

# Remove some items.
$ pin rm my-session pyproject.toml
╭─ Success ────────────────────────────╮
│ Removed 2 item(s) from the pinboard. │
╰──────────────────────────────────────╯

# Format files as a unified string for external prompting.
$ pin cp
╭─ Success ─────────────────────────────────╮
│ Pinboard contents copied to clipboard.    │
╰───────────────────────────────────────────╯

$ pin llm anthropic/claude-3-5-sonnet-20240620
╭─ Success ────────────────────────────────────────────────────╮
│ LLM set to anthropic/claude-3-5-sonnet-20240620.             │
╰──────────────────────────────────────────────────────────────╯

# File editing and asking questions happen through the chat command.
$ pin chat "add setup instructions in readme"
╭─ Info ────────────────────────────────────────────╮
│ Querying language model for a response...         │
╰───────────────────────────────────────────────────╯
╭─ Info ────────────────────────────────────────────╮
│ Updated file: /path/to/README.md                  │
╰───────────────────────────────────────────────────╯

# Clipboard content can also be included in the unified string.
$ pin chat -clip "add docstring to selected function"
╭─ Info ────────────────────────────────────────────╮
│ Querying language model for a response...         │
╰───────────────────────────────────────────────────╯
╭─ Info ────────────────────────────────────────────╮
│ Updated file: /path/to/src/pinboard/llm.py        │
╰───────────────────────────────────────────────────╯

# Editing can also yield new files.
$ pin chat "create a minimal contributing md and reference it in the readme"
╭─ Info ────────────────────────────────────────────╮
│ Querying language model for a response...         │
╰───────────────────────────────────────────────────╯
╭─ Info ────────────────────────────────────────────╮
│ Updated file: /path/to/README.md                  │
╰───────────────────────────────────────────────────╯
╭─ Success ─────────────────────────────────────────╮
│ Added file: /path/to/CONTRIBUTING.md              │
╰───────────────────────────────────────────────────╯

# New files get automatically pinned.
$ pin ls
                     Pinned Items (3 total)
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Type      ┃ Item                                              ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ File      │ /path/to/README.md                                │
│ Directory │ /path/to/src/pinboard                             │
│ File      │ /path/to/CONTRIBUTING.md                          │
└───────────┴───────────────────────────────────────────────────┘

# Ask questions about pinned files.
$ pin chat "where is the 'chat' command implemented?"
╭─ Info ────────────────────────────────────────────╮
│ Querying language model for a response...         │
╰───────────────────────────────────────────────────╯
╭─ Response ────────────────────────────────────────────────────────╮
│                                                                   │
│ The 'chat' command is implemented in the file                     │
│ /path/to/pinboard/src/pinboard/cli.py. It's defined as a Typer    │
│ command function named 'chat' that takes optional parameters for  │
│ the message, including clipboard content, and an interactive mode │
│ flag.                                                             │
╰───────────────────────────────────────────────────────────────────╯

# Interactive chat mode.
$ pin chat -i
╭─ Info ──────────────────────────────────────────────────────────────╮
│ Starting interactive chat session. Type 'exit' to end the session.  │
╰─────────────────────────────────────────────────────────────────────╯
> update the pin ls command to print the total number of pinned items
╭─ Info ────────────────────────────────────────────╮
│ Querying language model for a response...         │
╰───────────────────────────────────────────────────╯
╭─ Info ────────────────────────────────────────────╮
│ Updated file: /path/to/src/pinboard/cli.py        │
╰───────────────────────────────────────────────────╯
> exit

$ pin clear
╭─ Success ────────────────────────────────╮
│ Pinboard cleared.                        │
╰──────────────────────────────────────────╯
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