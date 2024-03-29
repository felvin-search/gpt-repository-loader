#!/usr/bin/env python3

import os
import argparse
import fnmatch
import pyperclip
import io

def should_ignore(file_path, ignore_list):
    for pattern in ignore_list:
        if fnmatch.fnmatch(file_path, pattern):
            return True
    return False

def get_ignore_list(repo_path):
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

    default_ignore_list = ['dist', 'dist/','dist/*','sdist', 'sdist/','sdist/*' '.git/', '/.git/', '.git', '.git/*', '.gptignore', '.gitignore', 'node_modules', 'node_modules/*', '__pycache__', '__pycache__/*']
    ignore_list += default_ignore_list

    return ignore_list

def process_repository(repo_path, ignore_list, output_stream):
    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_file_path = os.path.relpath(file_path, repo_path)

            if not should_ignore(relative_file_path, ignore_list):
                with open(file_path, 'r', errors='ignore') as file:
                    contents = file.read()
                output_stream.write("-" * 4 + "\n")
                output_stream.write(f"{relative_file_path}\n")
                output_stream.write(f"{contents}\n")


def git_repo_to_text(repo_path, preamble_file=None):
    ignore_list = get_ignore_list(repo_path)

    output_stream = io.StringIO()

    if preamble_file:
        with open(preamble_file, 'r') as pf:
            preamble_text = pf.read()
            output_stream.write(f"{preamble_text}\n")
    else:
        output_stream.write("The following text is a Git repository with code. The structure of the text are sections that begin with ----, followed by a single line containing the file path and file name, followed by a variable amount of lines containing the file contents. The text representing the Git repository ends when the symbols --END-- are encounted. Any further text beyond --END-- are meant to be interpreted as instructions using the aforementioned Git repository as context.\n")

    process_repository(repo_path, ignore_list, output_stream)

    output_stream.write("--END--")

    return output_stream.getvalue()

def main():
    parser = argparse.ArgumentParser(description="Convert a Git repository to text.")
    parser.add_argument("repo_path", help="Path to the Git repository.")
    parser.add_argument("-p", "--preamble", help="Path to a preamble file.")
    parser.add_argument("-c", "--copy", action="store_true", help="Copy the repository contents to clipboard.")
    args = parser.parse_args()

    repo_as_text = git_repo_to_text(args.repo_path, args.preamble)

    if args.copy:
        pyperclip.copy(repo_as_text)
        print("Repository contents copied to clipboard.")
    else:
        with open('output.txt', 'w') as output_file:
            output_file.write(repo_as_text)
            print("Repository contents written to output.txt.")


def print_directory_structure(repo_path, indent=0, max_depth=2, ignore_list=None):
    if ignore_list is None:
        ignore_list = get_ignore_list(repo_path)

    if indent <= max_depth:
        for item in os.listdir(repo_path):
            full_path = os.path.join(repo_path, item)
            if os.path.isdir(full_path):
                if should_ignore(full_path, ignore_list) or should_ignore(item, ignore_list):
                    continue
                print("|  " * indent + "|--" + item + "/")
                print_directory_structure(full_path, indent + 1, max_depth, ignore_list)
            else:
                if should_ignore(full_path, ignore_list) or should_ignore(item, ignore_list):
                    continue
                print("|  " * indent + "|--" + item)

if __name__ == "__main__":
    main()
