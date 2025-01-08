#!/usr/bin/env python3

import os
import argparse
import fnmatch
import pyperclip
import io
import subprocess
import textwrap
from token_count import TokenCount
from tabulate import tabulate
from .version import __version__
tc = TokenCount(model_name="gpt-3.5-turbo")

def should_ignore(file_path, ignore_patterns):
    """
    Check if a file should be ignored based on ignore patterns.
    Handles glob patterns including **, *, directory-specific matches,
    and ensures any files/subdirectories under an ignored directory are also ignored.

    Args:
        file_path (str): Path to the file to check
        ignore_patterns (list): List of ignore patterns

    Returns:
        bool: True if file should be ignored, False otherwise
    """
    # Normalize path separators to forward slashes for consistent matching
    file_path = file_path.replace(os.sep, '/')
    file_path_parts = file_path.split('/')

    for pattern in ignore_patterns:
        # First check if any parent directory of this file matches a directory pattern
        # This ensures we ignore all contents of ignored directories
        if not pattern.startswith('*'):  # Only do this for concrete directory patterns
            pattern_no_wildcards = pattern.rstrip('/*')  # Remove trailing /* if present
            pattern_parts = pattern_no_wildcards.split('/')

            # Check if this pattern might be a directory pattern
            if not any(part for part in pattern_parts if '*' in part):
                # For each possible parent directory of the file
                for i in range(len(file_path_parts)):
                    parent_path = '/'.join(file_path_parts[:i])
                    if parent_path == pattern_no_wildcards:
                        return True
        # Normalize pattern separators
        pattern = pattern.replace(os.sep, '/')

        # Convert glob patterns to regex patterns
        if pattern.startswith('**/'):
            # **/ at start means match this pattern at any directory level
            if fnmatch.fnmatch(file_path, pattern[3:]) or fnmatch.fnmatch(file_path, f"*/{pattern[3:]}"):
                return True
        elif pattern.endswith('/**'):
            # /** at end means match anything under this directory
            dir_path = pattern[:-3]
            if file_path.startswith(dir_path):
                return True
        elif '**' in pattern:
            # Handle ** in middle of pattern
            parts = pattern.split('**')
            if len(parts) == 2:
                start, end = parts
                if file_path.startswith(start) and file_path.endswith(end):
                    return True
        elif pattern.startswith('*/'):
            # */ at start means match in any immediate subdirectory
            if fnmatch.fnmatch(file_path, pattern[2:]) or fnmatch.fnmatch(file_path, pattern):
                return True
        elif pattern.endswith('/*'):
            # /* at end means match anything in that directory
            dir_path = pattern[:-2]
            parent_dir = os.path.dirname(file_path)
            if parent_dir == dir_path or file_path.startswith(f"{dir_path}/"):
                return True
        else:
            # Handle basic glob patterns
            if fnmatch.fnmatch(file_path, pattern):
                return True
            # Also match against basename as fallback
            if fnmatch.fnmatch(os.path.basename(file_path), pattern):
                return True
            # Handle directory-specific matches
            if '/' in pattern and fnmatch.fnmatch(file_path, f"*/{pattern}"):
                return True

    return False

def get_ignore_list(repo_path, ignore_js_ts_config=True, additional_ignores=None, ignore_tests=False):
    ignore_list = []
    ignore_file_path = None

    gpt_ignore_path = os.path.join(repo_path, ".gptignore")
    git_ignore_path = os.path.join(repo_path, ".gitignore")

    if os.path.exists(gpt_ignore_path):
        ignore_file_path = gpt_ignore_path
    elif os.path.exists(git_ignore_path):
        ignore_file_path = git_ignore_path
    else:
        print("No ignore file present")

    if ignore_file_path:
        with open(ignore_file_path, 'r') as ignore_file:
            for line in ignore_file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                ignore_list.append(line)

    if additional_ignores:
        ignore_list.extend(additional_ignores)

    default_ignore_list = ['dist', 'dist/','dist/*','sdist', 'sdist/','sdist/*' '.git/', '/.git/', '.git', '.git/*', '.gptignore', '.gitignore', 'node_modules', 'node_modules/*', '__pycache__', '__pycache__/*', '**/package-lock.json', '**/yarn.lock', '**/yarn-error.log', '**/pnpm-lock.yaml']
    image_ignore_list = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp', '*.ico', '*.cur', '*.tiff', '*.webp', '*.avif', "*.svg", "*.icns", "*.heic"]
    video_ignore_list = ['*.mp4', '*.mov', '*.wmv', '*.avi', '*.mkv', '*.flv', '*.webm', '*.mp3', '*.wav', '*.aac', '*.m4a', '*.mpa', '*.mpeg', '*.mpe', '*.mpg', '*.mpi', '*.mpt', '*.mpx', '*.ogv', '*.webm', '*.wmv', '*.yuv']
    audio_ignore_list = ['*.mp3', '*.wav', '*.aac', '*.m4a', '*.mpa', '*.mpeg', '*.mpe', '*.mpg', '*.mpi', '*.mpt', '*.mpx', '*.ogv', '*.webm', '*.wmv', '*.yuv']
    font_ignore_list = ['*.ttf', '*.otf', '*.woff', '*.woff2', '*.eot', '*.fnt', '*.fon']
    js_ts_config_ignore_list = ['**/tailwind.config.js','**/*.babelrc', '**/.babelrc', '**/*.babel.config.js', '**/*.tsconfig.json', '**/tsconfig.json', '**/*.tslint.json', '**/tslint.json', '**/*.eslintrc', '**/*.prettierrc', '**/*.webpack.config.js', '**/*.rollup.config.js']
    misc_ignore_list = ['**/.DS_Store', '**/.DS_Store/*']

    build_ignore_list = ['**/build/', '**/dist/']
    egg_info_ignore_list = ['**/*.egg-info']
    compiled_python_ignore_list = ['**/*.pyc', '**/__pycache__', '**/*.whl']
    env_ignore_list = ['**/.env', '**/.env.*']
    test_ignore_list = ['**/test', '**/tests', '**/__tests__', '**/__test__']

    ignore_list += default_ignore_list + image_ignore_list + video_ignore_list + audio_ignore_list + font_ignore_list + build_ignore_list + egg_info_ignore_list + compiled_python_ignore_list + env_ignore_list + misc_ignore_list

    if ignore_js_ts_config:
        ignore_list += js_ts_config_ignore_list

    if ignore_tests:
        ignore_list += test_ignore_list

    return ignore_list

def get_files_to_process(repo_path, ignore_list):
    git_files = subprocess.check_output(["git", "ls-files"], cwd=repo_path, universal_newlines=True).splitlines()
    return [file_path for file_path in git_files if not should_ignore(file_path, ignore_list)]

def read_file_contents(repo_path, file_path):
    full_path = os.path.join(repo_path, file_path)
    try:
        with open(full_path, 'r', errors='ignore') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Warning: File not found: {file_path}")
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
    return None

def process_repository(repo_path, ignore_list, output_stream, list_files=False):
    files_to_process = get_files_to_process(repo_path, ignore_list)
    total_tokens = 0
    file_token_pairs = []

    for file_path in files_to_process:
        contents = read_file_contents(repo_path, file_path)
        if contents is not None:
            try:
                file_tokens = tc.num_tokens_from_string(contents)
                total_tokens += file_tokens
                file_token_pairs.append((file_path, file_tokens, contents))
            except Exception as e:
                print(f"Error counting tokens for {file_path}")
                file_token_pairs.append((file_path, 0, contents))

    # Sort by token count in descending order
    file_token_pairs.sort(key=lambda x: x[1], reverse=True)

    if list_files:
        # Prepare table data with wrapped paths
        table_data = []
        for file_path, file_tokens, _ in file_token_pairs:
            wrapped_path = '\n'.join(textwrap.wrap(file_path, width=80))
            table_data.append([wrapped_path, file_tokens])

        # Print formatted table
        print(tabulate(table_data,
                      headers=['File Path', 'Tokens'],
                      tablefmt='grid',
                      colalign=('left', 'right')))
        print(f"\nTotal tokens: {total_tokens}")

    for file_path, file_tokens, contents in file_token_pairs:
        output_stream.write("-" * 4 + "\n")
        output_stream.write(f"{file_path}\n")
        output_stream.write(f"{contents}\n")

    return total_tokens

def git_repo_to_text(repo_path, preamble_file=None, ignore_list=None, list_files=False):
    if ignore_list is None:
        ignore_list = get_ignore_list(repo_path)

    output_stream = io.StringIO()

    if preamble_file:
        with open(preamble_file, 'r') as pf:
            preamble_text = pf.read()
            output_stream.write(f"{preamble_text}\n")
    else:
        output_stream.write("The following text is a Git repository with code. The structure of the text are sections that begin with ----, followed by a single line containing the file path and file name, followed by a variable amount of lines containing the file contents. The text representing the Git repository ends when the symbols --END-- are encounted. Any further text beyond --END-- are meant to be interpreted as instructions using the aforementioned Git repository as context.\n")

    total_tokens = process_repository(repo_path, ignore_list, output_stream, list_files)

    output_stream.write("--END--")

    return output_stream.getvalue(), total_tokens

def main():
    parser = argparse.ArgumentParser(description="Convert a Git repository to text.")
    parser.add_argument("repo_path", nargs='?', help="Path to the Git repository.")
    parser.add_argument("-p", "--preamble", help="Path to a preamble file.")
    parser.add_argument("-c", "--copy", action="store_true", help="Copy the repository contents to clipboard.")
    parser.add_argument("--include-js-ts-config", action="store_false", dest="ignore_js_ts_config", help="Include JavaScript and TypeScript config files.")
    parser.add_argument("-i", "--ignore", nargs="+", help="Additional file paths or patterns to ignore.")
    parser.add_argument("-l", "--list", action="store_true", help="List all files with their token counts.")
    parser.add_argument("--ignore-tests", action="store_true", help="Ignore test files and directories.")
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    args = parser.parse_args()

    if not args.repo_path:
        parser.print_help()
        return

    ignore_list = get_ignore_list(args.repo_path, args.ignore_js_ts_config, args.ignore, args.ignore_tests)
    repo_as_text, total_tokens = git_repo_to_text(args.repo_path, args.preamble, ignore_list, args.list)

    if args.copy:
        pyperclip.copy(repo_as_text)
        print(f"Repository contents copied to clipboard. Number of GPT tokens: {total_tokens}")
    else:
        with open('output.txt', 'w') as output_file:
            output_file.write(repo_as_text)
        print(f"Repository contents written to output.txt. Number of GPT tokens: {total_tokens}")

def print_directory_structure(repo_path, indent=0, max_depth=2, ignore_list=None):
    if ignore_list is None:
        ignore_list = get_ignore_list(repo_path)

    if indent <= max_depth:
        for item in os.listdir(repo_path):
            full_path = os.path.join(repo_path, item)
            relative_path = os.path.relpath(full_path, repo_path)
            if not should_ignore(relative_path, ignore_list):
                if os.path.isdir(full_path):
                    print("|  " * indent + "|--" + item + "/")
                    print_directory_structure(full_path, indent + 1, max_depth, ignore_list)
                else:
                    print("|  " * indent + "|--" + item)

if __name__ == "__main__":
    main()
