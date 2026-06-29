from functools import cache
from pathlib import Path

from raptor.core.fs import repo_root


@cache
def git_dir() -> Path:
    return repo_root() / ".git"


@cache
def hooks_dir() -> Path:
    return git_dir() / "hooks"
