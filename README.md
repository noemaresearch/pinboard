# Pinboard

Pinboard is a command-line tool for managing file references when working with raw language models. It's designed to streamline codebase-level development workflows, allowing users to request contextual, in-place file updates efficiently.

## Usage

![](/media/basics.png)

![](/media/demo.png)

![](/media/tmux.png)

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
   $ pipx install git+https://github.com/noemaresearch/pinboard.git
   ```

4. Configure your language model:
   ```
   $ pin llm anthropic/claude-3-5-sonnet-20240620
   $ export ANTHROPIC_API_KEY=your_api_key_here
   ```

## Documentation

**Usage**:

```console
$ pin [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `add`: Add file or folder paths to the pinboard,...
* `cp`: Copy the contents of the pinboard to the...
* `llm`: Configure the Language Model (LLM) to use...
* `ls`: List all pinned files, folders, and tmux...
* `rm`: Remove specified items from the pinboard...
* `sh`: Start an interactive shell or send a...

## `pin add`

Add file or folder paths to the pinboard, or tmux sessions with @tmux suffix.

This command allows you to pin specific files, entire folders, or tmux sessions for quick access and manipulation.
For tmux sessions, append '@tmux' to the session name (e.g., 'mysession@tmux').

If a folder is added, all valid files within that folder (and its subfolders) will be included in the pinboard.

**Usage**:

```console
$ pin add [OPTIONS] ITEMS...
```

**Arguments**:

* `ITEMS...`: File or folder paths to add to the pinboard, or tmux sessions with @tmux suffix  [required]

**Options**:

* `--help`: Show this message and exit.

## `pin cp`

Copy the contents of the pinboard to the clipboard.

This command generates a formatted text representation of all pinned items,
including file contents and tmux session outputs, and copies it to the system clipboard.
This is useful for quickly sharing the current state of your pinboard or for use with language models.

**Usage**:

```console
$ pin cp [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `pin llm`

Configure the Language Model (LLM) to use for editing files and answering questions.

This command sets the specific LLM model to be used for all subsequent operations that require AI assistance.
Currently, only Anthropic models are supported.

Args:
    model: The identifier of the LLM model (e.g., 'anthropic/claude-3-opus-20240229')

**Usage**:

```console
$ pin llm [OPTIONS] MODEL
```

**Arguments**:

* `MODEL`: [required]

**Options**:

* `--help`: Show this message and exit.

## `pin ls`

List all pinned files, folders, and tmux sessions.

This command displays a formatted table showing all items currently pinned in the pinboard.
It categorizes items as files, directories, or tmux sessions for easy overview.

**Usage**:

```console
$ pin ls [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `pin rm`

Remove specified items from the pinboard or clear the entire pinboard if no items are specified.

This command allows you to unpin specific files, folders, or tmux sessions from the pinboard.
If no arguments are provided, it will clear the entire pinboard.

For tmux sessions, append '@tmux' to the session name (e.g., 'mysession@tmux').

**Usage**:

```console
$ pin rm [OPTIONS] [ITEMS]...
```

**Arguments**:

* `[ITEMS]...`: File or folder paths, or tmux sessions to remove from the pinboard

**Options**:

* `--help`: Show this message and exit.

## `pin sh`

Start an interactive shell or send a one-time message to the LLM about pinned files.

This command allows you to interact with the AI assistant to ask questions about pinned files,
request file edits, or perform other operations on your codebase. It can be used in two modes:
1. Interactive shell: If no message is provided, it starts an interactive session.
2. One-time message: If a message is provided, it processes that message and exits.

In the interactive mode, you can use pinboard commands (add, rm, cp, llm, ls) directly.
The AI assistant can make changes to your files based on your requests.

Args:
    message: The message to send to the LLM (optional, for one-time processing)
    with_clipboard: Include the current clipboard content in the chat context

**Usage**:

```console
$ pin sh [OPTIONS] [MESSAGE]
```

**Arguments**:

* `[MESSAGE]`: Message to send to the LLM for one-time processing

**Options**:

* `-clip, --with-clipboard`: Include clipboard content in the chat context
* `--help`: Show this message and exit.

## License

Apache 2.0 License