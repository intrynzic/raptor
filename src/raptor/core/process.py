import subprocess
from pathlib import Path
from subprocess import CompletedProcess
from typing import Iterable

from raptor.core.log import command, error

StrOrPath = str | Path


def run(cmd: Iterable[StrOrPath], cwd: StrOrPath | None = None, capture: bool = False, quiet: bool = False) -> str:
    cmd = [str(c) for c in cmd]
    cwd = str(cwd) if cwd is not None else None

    if not quiet:
        command(f"{' '.join(cmd)}")

    if capture:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    else:
        result = subprocess.run(cmd, cwd=cwd)

    if result.returncode != 0:
        error(f"Command failed with code {result.returncode}!")
        return ""

    return str(result.stdout.strip()) if result.stdout else ""


def run_ex(cmd: Iterable[StrOrPath], cwd: StrOrPath | None = None, quiet: bool = False) -> CompletedProcess[str] | None:
    cmd = [str(c) for c in cmd]
    cwd = str(cwd) if cwd is not None else None

    if not quiet:
        command(f"{' '.join(cmd)}")

    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        error(f"Command failed with code {result.returncode}!")
        return result

    return result


def run_and_wait(exe_path: Path, cwd: StrOrPath | None = None):
    run(["cmd", "/c", "start", "/wait", "", exe_path], cwd=cwd)
