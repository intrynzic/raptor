import os
from functools import cache
from os import path as os_path
from pathlib import Path


@cache
def repo_root() -> Path:
    target = "raptor.toml"  # The root of the repository
    current = os_path.abspath(os.getcwd())  # The absolute path of the current working directory

    while True:
        if os_path.isfile(os_path.join(current, "raptor.toml")):  # Check whether target file exists in the current path
            return Path(current)
        parent = os_path.dirname(current)  # Get the parent directory of the current path

        if parent == current:  # The root of the filesystem reached without finding target.
            raise FileNotFoundError(f"Could not find {target} in any parent directory of {os.getcwd()}")
        current = parent  # Move up the parent directory and continue searching.


@cache
def git_dir() -> Path:
    return repo_root() / ".git"


@cache
def hooks_dir() -> Path:
    return git_dir() / "hooks"
