# Pinboard

Pinboard is a command-line tool for managing file references when working with raw language models. It's designed to streamline codebase-level development workflows, allowing users to request contextual, in-place file updates efficiently.

## Usage

### Basics

![](/media/basics.png)

### Tmux

![](/media/tmux.png)

### Interactive

![](/media/interactive.png)

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