# Pinboard CLI Tool

Pinboard is a Python-based CLI tool that helps users maintain a collection of file references, query an LLM based on their contents, and update them accordingly. It uses pipx, typer, pyclip, shelves, platformdirs, and the Anthropic API to provide a seamless experience for managing and editing files.

## Installation

1. Ensure you have Python 3.8 or later installed on your system.

2. Install `pipx` if you haven't already:
   ```
   pip install pipx
   pipx ensurepath
   ```

3. Install Pinboard using `pipx`:
   ```
   pipx install git+https://github.com/paulbricman/pinboard.git
   ```

4. Set up your Anthropic API key as an environment variable:
   ```
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

Pinboard provides the following commands:

- `pin add <FILE1> <FILE2> <FOLDER1> ...`: Add file or folder paths to the pinboard
- `pin rm <FILE1> <FILE2> <FOLDER1> ...`: Remove file or folder paths from the pinboard
- `pin clear`: Clear the contents of the pinboard
- `pin copy`: Copy the contents of the pinboard to the clipboard in a templated format
- `pin llm anthropic/claude-3-5-sonnet-20240620`: Set the LLM model to use for editing files (currently only Anthropic models are supported)
- `pin edit "message"`: Use the configured LLM to edit pinned files based on a given message
- `pin inline "message"`: Edit pinned files and clipboard content using the configured LLM
- `pin ls`: List all pinned files and folders

## License

This project is licensed under the Apache 2.0 License.