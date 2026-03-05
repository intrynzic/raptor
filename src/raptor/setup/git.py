from raptor.config.loader import CONFIG
from raptor.core.environ import where
from raptor.core.log import trace, info, warn, error, critical, log_validation_result
from raptor.core.net import download_file
from raptor.core.process import run, run_and_wait
from raptor.core.validation import ValidationResult, Severity
from packaging.version import parse as parse_ver, Version
from pathlib import Path
import re
import typer


_GIT_CMD: str = "git"
_GIT_REQUIRED_VER: Version = Version(CONFIG.setup.get("git").min_version)
_GIT_INSTALLER_VER: str = f"{_GIT_REQUIRED_VER}.windows.1"

_GIT_INSTALLER_NAME: str = f"Git-{_GIT_REQUIRED_VER}-64-bit.exe"
_GIT_INSTALLER_URL: str = f"https://github.com/git-for-windows/git/releases/download/v{_GIT_INSTALLER_VER}/{_GIT_INSTALLER_NAME}"
_GIT_INSTALLER_DIR: Path = Path("./tmp") # NOTE: Can't use tmp_dir since it relies on Git to find repo_root
_GIT_INSTALLER_PATH: Path = _GIT_INSTALLER_DIR / _GIT_INSTALLER_NAME

def validate() -> ValidationResult:
    if not _is_installed():
        return ValidationResult(
            valid = False,
            severity = Severity.ERROR,
            message = "Git for Windows is not installed or could not be found!"
        )

    git_path = _git_path()

    if not _check_git_ver(git_path):
        return ValidationResult(
            valid = False,
            severity = Severity.ERROR,
            message = "Incorrect Git for Windows version installed."
        )

    if not _check_git_install(git_path):
        return ValidationResult(
            valid = False,
            severity=  Severity.ERROR,
            message = "The installed Git for Windows package is corrupted!"
        )

    return ValidationResult(
        valid = True,
        severity = Severity.NONE
    )

def download_installer():
    if not _GIT_INSTALLER_PATH.exists():
        trace(f"Downloading \"{_GIT_INSTALLER_URL}\" to \"{_GIT_INSTALLER_PATH.parent}\"...")
        download_file(_GIT_INSTALLER_URL, _GIT_INSTALLER_PATH)
    else:
        info(f"Correct Git for Windows installer located at: \"{_GIT_INSTALLER_PATH}\".")

# TODO: Find a better way to validate this
def install() -> bool:
    download_installer()
    info("Running Git for Windows installer...")
    run_and_wait(_GIT_INSTALLER_PATH, cwd = ".")

    return True

def ensure():
    result = validate()
    if result.valid:
        info(f"Correct Git for Windows package located at: \"{_git_path()}\".")
        return

    log_validation_result(result)

    if not typer.confirm(f"Would you like to install Git for Windows v{_GIT_REQUIRED_VER}?", default = True):
        return

    if not install():
        critical("Git for Windows installation failed!")
        return

    # Revalidate after install
    post = validate()
    if not post.valid:
        critical("Git for Windows installation failed!")
        return

    info("Git for Windows installed successfully.")

def _git_path() -> Path:
    # NOTE: Usually results in the child folder "cmd" inside the Git install,
    # but we want the parent directory here.
    return where(_GIT_CMD).parent

def _is_installed() -> bool:
    return _git_path().exists()

def _check_git_ver(git_path: Path) -> bool:
    try:
        git_output = run([(git_path / "cmd" / "git.exe"), "--version"], capture = True)
    except:
        error("Failure running git.exe! The installed Git for Windows package is corrupt.")
        return False

    # Format: "git version 2.47.1.windows.2"
    match = re.search(r"git version (.+)", git_output)
    if not match:
        error(f"Unable to parse Git version output: \"{git_output}\"!")
        return False

    git_ver = match.group(1)
    match = re.match(r"(\d+(?:\.\d+)*)", git_ver) # Extract leading numeric dot segments (removes the .windows.2)
    if not match:
        error(f"Unable to parse Git version output: \"{git_output}\"!")
        return False

    git_ver = match.group(1)
    if parse_ver(git_ver) < _GIT_REQUIRED_VER:
        warn(f"The installed Git for Windows package v{git_ver} is too old! (Project requires v{_GIT_REQUIRED_VER} or newer).")
        return False

    return True

def _check_git_install(git_path: Path) -> bool:
    # Check Git's most important files for existence
    required_paths = [
        "cmd/git.exe",
        "bin/git.exe",
        "git-bash.exe",
        "git-cmd.exe",
    ]

    for rel in required_paths:
        if not (git_path / rel).exists():
            return False

    return True
