from pathlib import Path
from zipfile import ZipFile

import typer
from packaging.version import Version
from packaging.version import parse as parse_ver

from raptor.config.loader import CONFIG
from raptor.core.fs import tmp_dir, tools_dir
from raptor.core.log import critical, error, info, log_validation_result, trace, warn
from raptor.core.net import download_file
from raptor.core.process import run
from raptor.core.validation import Severity, ValidationResult

_DOXYGEN_REQUIRED_VER: Version = Version(CONFIG.setup.get("doxygen").min_version)
_DOXYGEN_DIR: Path = tools_dir() / "Doxygen"
_DOXYGEN_PATH: Path = _DOXYGEN_DIR / "doxygen.exe"

_DOXYGEN_ARCHIVE_NAME: str = f"doxygen-{_DOXYGEN_REQUIRED_VER}.windows.x64.bin.zip"
_DOXYGEN_ARCHIVE_URL: str = (
    f"https://github.com/doxygen/doxygen/releases/download/Release_{str(_DOXYGEN_REQUIRED_VER).replace('.', '_')}/{_DOXYGEN_ARCHIVE_NAME}"
)
_DOXYGEN_ARCHIVE_DIR: Path = tmp_dir()
_DOXYGEN_ARCHIVE_PATH: Path = _DOXYGEN_ARCHIVE_DIR / _DOXYGEN_ARCHIVE_NAME


def validate() -> ValidationResult:
    if not _is_installed():
        return ValidationResult(valid=False, severity=Severity.ERROR, message="Doxygen is not installed or could not be found.")

    if not _check_doxygen_ver():
        return ValidationResult(valid=False, severity=Severity.WARNING, message="Incorrect Doxygen version installed.")

    if not _check_doxygen_install():
        return ValidationResult(valid=False, severity=Severity.ERROR, message="The Doxygen install is corrupted!")

    return ValidationResult(valid=True, severity=Severity.NONE)


def download_archive():
    if not _DOXYGEN_ARCHIVE_PATH.exists():
        trace(f'Downloading "{_DOXYGEN_ARCHIVE_URL}" to "{_DOXYGEN_ARCHIVE_PATH.parent}"...')
        download_file(_DOXYGEN_ARCHIVE_URL, _DOXYGEN_ARCHIVE_PATH)
    else:
        info(f'Correct Doxygen release archive located at: "{_DOXYGEN_ARCHIVE_PATH}".')


def install() -> bool:
    download_archive()
    info("Installing Doxygen...")

    with ZipFile(_DOXYGEN_ARCHIVE_PATH, "r") as archive:
        archive.extractall(_DOXYGEN_DIR)

    return True


def ensure():
    result = validate()
    if result.valid:
        info(f'Correct Doxygen version (v{_DOXYGEN_REQUIRED_VER}) located at: "{_DOXYGEN_DIR}".')
        return

    log_validation_result(result)

    if not typer.confirm(f"Would you like to install Doxygen v{_DOXYGEN_REQUIRED_VER}?", default=True):
        return

    if not install():
        critical("Doxygen installation failed!")
        return

    # Revalidate after install
    post = validate()
    if not post.valid:
        critical("Doxygen installation failed!")
        return

    info("Doxygen installed successfully.")


def _is_installed() -> bool:
    return _DOXYGEN_PATH.exists()


def _check_doxygen_ver() -> bool:
    try:
        # Format: <version> (<commit-hash>)
        # Example: 1.16.1 (669aeeefca743c148e2d935b3d3c69535c7491e6)
        doxygen_ver = run([_DOXYGEN_PATH, "--version"], capture=True)
        doxygen_ver = doxygen_ver[: doxygen_ver.find("(")].strip()
    except Exception:
        error("Failure running doxygen.exe! The installed version of Doxygen is corrupt.")
        return False

    if parse_ver(doxygen_ver) < _DOXYGEN_REQUIRED_VER:
        warn(f"You don't have the correct Doxygen version installed! (Project requires v{_DOXYGEN_REQUIRED_VER}).")
        return False

    return True


def _check_doxygen_install() -> bool:
    # NOTE: Check if the required binaries are present in the _DOXYGEN_DIR folder
    REQUIRED_BINARIES: list[str] = ["doxygen.exe", "doxyindexer.exe", "doxysearch.cgi.exe", "doxywizard.exe", "libclang.dll"]

    corrupted = False
    for file in REQUIRED_BINARIES:
        file_path = _DOXYGEN_DIR / file
        if not file_path.exists():
            error(f'Doxygen required binary "{file}" is missing!')
            corrupted = True

    return not corrupted
