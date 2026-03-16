import os
import platform
from functools import cache
from importlib.resources import as_file, files
from pathlib import Path

from raptor.config.loader import CONFIG
from raptor.core.git import repo_root
from raptor.core.log import critical
from raptor.core.process import run


@cache
def vswhere_path() -> Path:
    return Path(r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe")


@cache
def msbuild_path() -> Path:
    res = run([vswhere_path(), "-latest", "-requires", "Microsoft.Component.MSBuild", "-find", r"MSBuild\**\Bin\MSBuild.exe"], capture=True)
    return Path(res)


@cache
def hooks_dir() -> Path:
    return repo_root() / ".raptor" / "hooks"


@cache
def tmp_dir() -> Path:
    _DIR = repo_root() / ("tmp" if CONFIG.paths.temp_dir is None else CONFIG.paths.temp_dir)
    if not _DIR.exists():
        os.makedirs(_DIR)

    return _DIR


@cache
def docs_dir() -> Path:
    _DIR = repo_root() / ("docs" if CONFIG.paths.docs_dir is None else CONFIG.paths.docs_dir)
    if not _DIR.exists():
        os.makedirs(_DIR)

    return _DIR


@cache
def tools_dir() -> Path:
    _DIR = repo_root() / ("Tools" if CONFIG.paths.tools_dir is None else CONFIG.paths.tools_dir)
    if not _DIR.exists():
        os.makedirs(_DIR)

    return _DIR


@cache
def doxygen_dir() -> Path:
    return tools_dir() / "Doxygen"


@cache
def premake_path() -> Path:
    system = platform.system()
    match system:
        case "Windows":
            binary = "premake5-windows.exe"
        case "Linux":
            binary = "premake5-linux"
        case "Darwin":
            binary = "premake5-macosx-x64"
        case _:
            critical(f"Unsupported platform '{system}'!")

    # TODO: Rename this import and the folder structure to intricate_raptor
    premake_res = files("raptor").joinpath(f"bin/premake/{binary}")
    with as_file(premake_res) as p:
        return Path(p)
