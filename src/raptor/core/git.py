from functools import cache
from pathlib import Path

from raptor.core.process import run

import os # Review(Adam): Should the whole os module be imported, or just the functions that are used? (os.path and os.getcwd)
from os import path as os_path
from os import getcwd as os_getcwd


@cache
def repo_root() -> Path:
    target = "raptor.toml" # This indicates the root of the repository
    current = os_path.abspath(os.getcwd()) # Get the absolute path of the current working directory

    while True:
        if os_path.isfile(os_path.join(current, "raptor.toml")): # Check if the target file exists in the current path
            return Path(current) #return the current path as a Path object
        
        parent = os_path.dirname(current) # Get the parent directory of the current path

        if parent == current: # The root of the filesystem reached without finding target.
            raise FileNotFoundError(f"Could not find {target} in any parent directory of {os_getcwd()}")
        
        current = parent # Move up the parent directory and continue searching.


@cache
def git_dir() -> Path:
    return repo_root() / ".git"


@cache
def hooks_dir() -> Path:
    return git_dir() / "hooks"

## TESTING: The new repo_root() function.
if __name__ == "__main__":
    print("Repo root:", repo_root())