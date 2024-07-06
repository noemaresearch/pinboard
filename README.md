# Pinboard

Pinboard is a command-line tool for managing file references when working with raw language models. It's meant to streamline codebase-level development workflows, allowing users to request contextual, in-place file updates efficiently.

## Usage

```bash
$ pin add README.md src/pinboard pyproject.toml
Added 3 new item(s) to the pinboard.

$ pin rm pyproject.toml
Removed 1 item(s) from the pinboard.

$ pin ls
Pinned items:
- [File] /path/to/README.md
- [Directory] /path/to/src/pinboard

# Format files as a unified string for external prompting.
$ pin cp
Pinboard contents copied to clipboard.

$ pin llm anthropic/claude-3-5-sonnet-20240620
LLM set to anthropic/claude-3-5-sonnet-20240620.

# File editing happens in-place, new version should just show up in your editor.
$ pin edit "add setup instructions in readme"
Querying claude-3-5-sonnet-20240620 for edits...
Updated file: /path/to/README.md

# Clipboard content can also be included in the unified string.
$ pin edit -clip "add docstring to selected function"
Querying claude-3-5-sonnet-20240620 for edits...
Updated file: /path/to/src/pinboard/llm.py

# Editing can also yield new files.
$ pin edit "create a minimal contributing md and reference it in the readme"
Querying claude-3-5-sonnet-20240620 for edits...
Updated file: /path/to/README.md
Added new file: /path/to/CONTRIBUTING.md

# New files get automatically pinned.
$ pin ls
Pinned items:
- [File] /path/to/README.md
- [Directory] /path/to/src/pinboard
- [File] /path/to/CONTRIBUTING.md

# Ask questions about pinned files.
$ pin ask "Where is the 'ask' command implemented?"
Querying claude-3-5-sonnet-20240620 for an answer...
The 'ask' command is implemented in the file /path/to/pinboard/src/pinboard/cli.py. It's defined as a Typer command function named 'ask' that takes a message parameter and calls the ask_question function from the llm module.

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

We welcome contributions to Pinboard! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more information on how to get started.

## License

Apache 2.0 License