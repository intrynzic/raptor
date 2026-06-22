import os
import platform
from functools import cache
from importlib.resources import files
from os import path
from pathlib import Path

# from raptor.config.loader import CONFIG
from raptor.core.log import critical
from raptor.core.process import run


@cache
def repo_root() -> Path:
    target = "raptor.toml"
    current = path.abspath(os.getcwd())

    while True:
        if path.isfile(path.join(current, "raptor.toml")):
            return Path(current)
        parent = path.dirname(current)

        if parent == current:
            critical(f"Could not find {target} in any parent directory of {os.getcwd()}!")
        current = parent


@cache
def vswhere_path() -> Path:
    return Path(r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe")


@cache
def msbuild_path() -> Path:
    res = run([vswhere_path(), "-latest", "-requires", "Microsoft.Component.MSBuild", "-find", r"MSBuild\**\Bin\MSBuild.exe"], capture=True)
    return Path(res)


@cache
def raptor_dir() -> Path:
    _DIR = repo_root() / ".raptor"
    if not _DIR.exists():
        os.makedirs(_DIR)

    return _DIR


@cache
def hooks_dir() -> Path:
    return raptor_dir() / "hooks"


@cache
def temp_dir() -> Path:
    _DIR = raptor_dir() / "temp"
    if not _DIR.exists():
        os.makedirs(_DIR)

    return _DIR


@cache
def docs_dir() -> Path:
    from raptor.config.loader import CONFIG # Lazy import to avoid circular dependency with git.py
    _DIR = repo_root() / ("docs" if CONFIG.paths.docs_dir is None else CONFIG.paths.docs_dir)
    if not _DIR.exists():
        os.makedirs(_DIR)

    return _DIR


@cache
def tools_dir() -> Path:
    from raptor.config.loader import CONFIG # Lazy import to avoid circular dependency with git.py
    _DIR = repo_root() / ("Tools" if CONFIG.paths.tools_dir is None else CONFIG.paths.tools_dir)
    if not _DIR.exists():
        os.makedirs(_DIR)

    return _DIR


@cache
def doxygen_dir() -> Path:
    return tools_dir() / "Doxygen"


@cache
def premake_path() -> Path:
    binary = "premake5.exe" if platform.system() == "Windows" else "premake5"
    path = Path(str(files("raptor").joinpath(f"bin/{binary}")))

    if not path.exists():
        critical(f'Premake5 binary not found at "{path}"!')
        return Path()

    return path
