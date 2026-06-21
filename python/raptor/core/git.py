from functools import cache
from pathlib import Path

from raptor.core.process import run


@cache
def repo_root() -> Path:
    return Path(run(["git", "rev-parse", "--show-toplevel"], capture=True, quiet=True))


@cache
def git_dir() -> Path:
    return repo_root() / ".git"


@cache
def hooks_dir() -> Path:
    return git_dir() / "hooks"
