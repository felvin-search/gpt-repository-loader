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
* `--filter-content`: Use a lightweight LLM to filter out irrelevant content (requires a local LLM model).
* `--model-path`: Path to the LLM model file for content filtering (optional, defaults to LLAMA_MODEL_PATH environment variable).
* `--ignore-tests`: Ignore test files and directories.

### Examples
```bash
# Ignore specific files or directories
gpt-repository-loader . -c -i "*.log" "temp_files/" "config.ini"

# Include JS/TS config files and ignore a specific directory
gpt-repository-loader . --include-js-ts-config -i "node_modules/"

# List all files with their token counts
gpt-repository-loader . -l

# Use content filtering with a local LLM model
gpt-repository-loader . -c --filter-content --model-path /path/to/llama-model.bin

# Use content filtering with default model path (set via environment variable)
export LLAMA_MODEL_PATH=/path/to/llama-model.bin
gpt-repository-loader . -c --filter-content
```

### Content Filtering
The `--filter-content` option uses a lightweight local LLM to analyze file contents and filter out irrelevant files such as:
- Build artifacts
- Generated code
- Cache files
- Temporary data
- Binary files

This helps reduce token usage and improve context relevance when working with large repositories. The filtering process requires a local LLM model (compatible with llama.cpp). You can specify the model path using the `--model-path` option or set it via the `LLAMA_MODEL_PATH` environment variable.

## What to use it for?
- Build a README for codebases
- Work with Legacy code
- Debug issues
- Analyze large repositories efficiently with content filtering

Gemini's 1M context window is REALLLY big, and it under utilized.