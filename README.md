# gpt-repository-loader

## Installation

`pip install gpt-repository-loader`

## Linux Requirements
On Linux, ensure that you have `xclip` installed for clipboard functionality. You can install it using:
```bash
sudo apt-get install xclip  # Debian/Ubuntu
sudo yum install xclip      # Fedora/CentOS
```

## How to use?
Go to the directory you are interested in, run
```
gpt-repository-loader . -c
```
This will copy ALL the git tracked content in the repository on clipboard and then you can use [Gemini](https://aistudio.google.com/app/prompts/new_chat)/[Claude](https://claude.ai)/[ChatGPT](https://chatgpt.com) to ask questions on it.

### Available Command Line Flags
* `repo_path`: (Required) Path to the Git repository.
* `-p`, `--preamble`: Path to a preamble file to include before the repository content.
* `-c`, `--copy`: Copies the repository contents to the clipboard. If not provided, the output will be written to a file named `output.txt` in the current directory.
* `-i`, `--ignore`: Additional file paths or patterns to ignore. You can specify multiple paths or patterns.
* `--include-js-ts-config`: Include JavaScript and TypeScript config files (which are ignored by default).
* `-l`, `--list`: List all files with their token counts.

### Examples
```bash
# Ignore specific files or directories
gpt-repository-loader . -c -i "*.log" "temp_files/" "config.ini"

# Include JS/TS config files and ignore a specific directory
gpt-repository-loader . --include-js-ts-config -i "node_modules/"

# List all files with their token counts
gpt-repository-loader . -l
```

## What to use it for?
- Build a README for codebases
- Work with Legacy code
- Debug issues

Gemini's 1M context window is REALLLY big, and it under utilized.
