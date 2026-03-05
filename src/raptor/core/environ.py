import os
import shutil
import winreg
from pathlib import Path


def get_system_env_var(name: str) -> (str | None):
    key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"System\CurrentControlSet\Control\Session Manager\Environment")
    try:
        return winreg.QueryValueEx(key, name)[0]
    except:
        return None

def get_user_env_var(name: str) -> (str | None):
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Environment")
    try:
        return winreg.QueryValueEx(key, name)[0]
    except:
        return None

def create_user_env_var(name: str, value: str):
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Environment")
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
    except:
        print(f"Failed to create user environment variable {name}!")

def env_var_exists(name: str) -> bool:
    return name in os.environ

def where(cmd: str) -> Path:
    res = shutil.which(cmd)
    return Path(res).parent if res is not None else Path()
