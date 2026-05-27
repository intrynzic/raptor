import os
import shutil
from pathlib import Path
from typing import Optional


# Feature detection for Windows registry features
try:
    import winreg
    PLATFORM_WIN32 = True
except ImportError:
    PLATFORM_WIN32 = False


def get_system_env_var(name: str) -> Optional[str]:
    if PLATFORM_WIN32:
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"System\CurrentControlSet\Control\Session Manager\Environment")
        try:
            return winreg.QueryValueEx(key, name)[0]
        except Exception:
            return None

    return os.environ.get(name)


def get_user_env_var(name: str) -> Optional[str]:
    if PLATFORM_WIN32:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Environment")
        try:
            return winreg.QueryValueEx(key, name)[0]
        except Exception:
            return None

    return os.environ.get(name)


def env_var_exists(name: str) -> bool:
    return name in os.environ


def where(cmd: str) -> Path:
    res = shutil.which(cmd)
    return Path(res).parent if res is not None else Path()
