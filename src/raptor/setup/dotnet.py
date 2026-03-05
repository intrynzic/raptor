from pathlib import Path

import typer
from packaging.version import Version
from packaging.version import parse as parse_ver

from raptor.config.loader import CONFIG
from raptor.core.environ import where
from raptor.core.fs import tmp_dir
from raptor.core.git import repo_root
from raptor.core.log import critical, error, info, log_validation_result, trace, warn
from raptor.core.net import download_file
from raptor.core.process import run, run_and_wait
from raptor.core.validation import Severity, ValidationResult

_DOTNET_CMD: str = "dotnet"
_DOTNET_INSTALLER_VER: Version = Version(CONFIG.setup.get("dotnet").min_version)

_DOTNET_INSTALLER_NAME: str = f"dotnet-sdk-{_DOTNET_INSTALLER_VER}-win-x64.exe"
_DOTNET_INSTALLER_URL: str = f"https://builds.dotnet.microsoft.com/dotnet/Sdk/{_DOTNET_INSTALLER_VER}/{_DOTNET_INSTALLER_NAME}"
_DOTNET_INSTALLER_DIR: Path = tmp_dir()
_DOTNET_INSTALLER_PATH: Path = _DOTNET_INSTALLER_DIR / _DOTNET_INSTALLER_NAME

def validate() -> ValidationResult:
    if not _is_installed():
        return ValidationResult(
            valid = False,
            severity = Severity.ERROR,
            message = ".NET SDK is not installed or could not be found!"
        )

    dotnet_path = _dotnet_path()

    if not _check_dotnet_ver(dotnet_path):
        return ValidationResult(
            valid = False,
            severity = Severity.WARNING,
            message = "Incorrect .NET SDK version installed."
        )

    if not _check_dotnet_install(dotnet_path):
        return ValidationResult(
            valid = False,
            severity = Severity.ERROR,
            message = "The installed .NET SDK is corrupted!"
        )

    return ValidationResult(
        valid = True,
        severity = Severity.NONE
    )

def download_installer():
    if not _DOTNET_INSTALLER_PATH.exists():
        trace(f"Downloading \"{_DOTNET_INSTALLER_URL}\" to \"{_DOTNET_INSTALLER_PATH.parent}\"...")
        download_file(_DOTNET_INSTALLER_URL, _DOTNET_INSTALLER_PATH)
    else:
        info(f"Correct .NET SDK installer located at: \"{_DOTNET_INSTALLER_PATH}\".")

# TODO: Find a better way to validate this
def install() -> bool:
    download_installer()
    info("Running .NET SDK installer...")
    run_and_wait(_DOTNET_INSTALLER_PATH, cwd = repo_root())

    return True

def ensure():
    result = validate()
    if result.valid:
        info(f"Correct .NET SDK (v{_DOTNET_INSTALLER_VER}) located at: \"{_dotnet_path()}\".")
        return

    log_validation_result(result)

    if not typer.confirm(f"Would you like to install .NET SDK v{_DOTNET_INSTALLER_VER}?", default = True):
        return

    if not install():
        critical(".NET SDK installation failed!")
        return

    # Revalidate after install
    post = validate()
    if not post.valid:
        critical(".NET SDK installation failed!")
        return

    info(".NET SDK installed successfully.")

def _dotnet_path() -> Path:
    return where(_DOTNET_CMD)

def _is_installed() -> bool:
    return _dotnet_path().exists()

def _check_dotnet_ver(dotnet_path: Path) -> bool:
    try:
        dotnet_ver = run([(dotnet_path / "dotnet.exe"), "--version"], capture = True)
    except:
        error("Failure running dotnet.exe! The installed .NET SDK is corrupt.")
        return False

    if parse_ver(dotnet_ver) < _DOTNET_INSTALLER_VER:
        warn(f"You don't have the correct .NET SDK version installed! (Project requires v{_DOTNET_INSTALLER_VER}).")
        return False

    return True

def _check_dotnet_install(dotnet_path: Path) -> bool:
    # Check the most important parts of SDK for existence
    latest_netcore = max((dotnet_path / "shared" / "Microsoft.NETCore.App").iterdir(), key = lambda p: p.name)
    if not latest_netcore.exists():
        return False

    latest_hostfxr = max((dotnet_path / "host" / "fxr").iterdir(), key = lambda p: p.name) / "hostfxr.dll"
    if not latest_hostfxr.exists():
        return False

    return True
