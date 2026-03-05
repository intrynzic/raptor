import os
from pathlib import Path

import typer
from packaging.version import Version
from packaging.version import parse as parse_ver

from raptor.config.loader import CONFIG
from raptor.core.environ import get_system_env_var
from raptor.core.fs import tmp_dir
from raptor.core.git import repo_root
from raptor.core.log import critical, error, info, log_validation_result, trace, warn
from raptor.core.net import download_file
from raptor.core.process import run, run_and_wait
from raptor.core.validation import Severity, ValidationResult

_VULKAN_ENV: str = "VK_SDK_PATH"
_VULKAN_INSTALLER_VER: Version = Version(CONFIG.setup.get("vulkan").min_version)

_VULKAN_INSTALLER_NAME: str = f"vulkansdk-windows-X64-{_VULKAN_INSTALLER_VER}.exe"
_VULKAN_INSTALLER_URL: str = f"https://sdk.lunarg.com/sdk/download/{_VULKAN_INSTALLER_VER}/windows/{_VULKAN_INSTALLER_NAME}"
_VULKAN_INSTALLER_DIR: Path = tmp_dir()
_VULKAN_INSTALLER_PATH: Path = _VULKAN_INSTALLER_DIR / _VULKAN_INSTALLER_NAME


def validate() -> ValidationResult:
    if not _is_installed():
        return ValidationResult(valid=False, severity=Severity.ERROR, message="Vulkan SDK is not installed!")

    vk_path = _vk_path()

    if not _check_vk_ver(vk_path):
        return ValidationResult(valid=False, severity=Severity.WARNING, message="Incorrect Vulkan SDK version installed.")

    if not _check_vk_debug_libs(vk_path):
        return ValidationResult(valid=False, severity=Severity.ERROR, message="Vulkan SDK missing shader debug libraries!")

    return ValidationResult(valid=True, severity=Severity.NONE)


def download_installer():
    if not _VULKAN_INSTALLER_PATH.exists():
        trace(f'Downloading "{_VULKAN_INSTALLER_URL}" to "{_VULKAN_INSTALLER_PATH.parent}"...')
        download_file(_VULKAN_INSTALLER_URL, _VULKAN_INSTALLER_PATH)
    else:
        info(f'Correct Vulkan SDK installer located at: "{_VULKAN_INSTALLER_PATH}".')


# TODO: Find a better way to validate this
def install() -> bool:
    download_installer()
    info("Running Vulkan SDK installer...")
    run_and_wait(_VULKAN_INSTALLER_PATH, cwd=repo_root())

    return True


def ensure():
    result = validate()
    if result.valid:
        info(f'Correct Vulkan SDK (v{_VULKAN_INSTALLER_VER}) located at: "{_vk_path()}".')
        return

    log_validation_result(result)

    if not typer.confirm(f"Would you like to install Vulkan SDK v{_VULKAN_INSTALLER_VER}?", default=True):
        return

    if not install():
        critical("Vulkan SDK installation failed!")
        return

    # Revalidate after install
    post = validate()
    if not post.valid:
        critical("Vulkan SDK validation failed!")
        return

    info("Vulkan SDK installed successfully.")


def _vk_path() -> Path:
    vk_path = get_system_env_var(_VULKAN_ENV)
    if vk_path is None or not vk_path:
        return Path()

    return Path(vk_path)


def _is_installed() -> bool:
    return _vk_path().exists()


def _check_vk_ver(vk_path: Path) -> bool:
    VERSION_TOKEN: str = "Vulkan Instance Version: "

    try:
        sdk_output = run([os.path.normpath(f"{vk_path}/Bin/vulkanInfoSDK.exe")], capture=True)
        pos = sdk_output.find(VERSION_TOKEN) + len(VERSION_TOKEN)
        sdk_ver = sdk_output[pos : sdk_output.find("\n", pos)].strip()
    except Exception:
        error("No Vulkan ICD was found! The installed Vulkan drivers are either corrupt or this machine does not support Vulkan.")
        return False

    if parse_ver(sdk_ver) < _VULKAN_INSTALLER_VER:
        warn(f"You don't have the correct Vulkan SDK version installed! (Project requires v{_VULKAN_INSTALLER_VER}).")
        return False

    return True


def _check_vk_debug_libs(vk_path: Path) -> bool:
    return (vk_path / "Lib" / "shaderc_sharedd.lib").exists()
