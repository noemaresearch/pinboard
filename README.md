# Pinboard

Pinboard is a command-line tool for managing file references when working with raw language models. It's meant to streamline development workflows, allowing users to request contextual, in-place file updates efficiently.

## Usage

```bash
$ pin add file1.txt folder1/
Added 2 new item(s) to the pinboard.

$ pin rm file1.txt
Removed 1 item(s) from the pinboard.

$ pin ls
Pinned items:
- [Directory] /path/to/folder1/

$ pin cp # Aggregate files as a unified string for prompting.
Pinboard contents copied to clipboard.

$ pin llm anthropic/claude-3-5-sonnet-20240620
LLM set to anthropic/claude-3-5-sonnet-20240620.

$ pin edit "add installation instructions in readme"
Querying claude-3-5-sonnet-20240620 for edits...
Updated file: /path/to/README.md

$ pin edit --with-clipboard "add docstrings to the selected function"
Querying claude-3-5-sonnet-20240620 for edits...
Updated file: /path/to/source.py

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


## License

Apache 2.0 License