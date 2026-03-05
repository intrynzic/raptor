from raptor.config.loader import CONFIG
from raptor.core.git import hooks_dir as git_hooks_dir
from raptor.core.log import trace, info, error, log_validation_result
from raptor.core.validation import ValidationResult, Severity
from raptor.hooks.registry import HOOK_REGISTRY
from packaging.version import parse as parse_ver, Version
from pathlib import Path
import hashlib
import os


_HOOK_VER: Version = Version("1.1.0")
_HOOK_REQUIRED_VER: Version = Version(CONFIG.setup.get("git-hooks").min_version)

_HOOK_TEMPLATE = """#!/bin/sh
# {version}
# Raptor Git Hook

exec raptor hook run {hook_name} "$@"
"""

def validate() -> ValidationResult:
    for [hook_name, hook_fn] in HOOK_REGISTRY.items():
        git_hook_path = git_hooks_dir() / hook_name.replace('_', '-')

        if not _is_installed(git_hook_path):
            return ValidationResult(
                valid = False,
                severity = Severity.ERROR,
                message = f"Git '{hook_name}' hook is not installed!"
            )

        trace(f"Located installed Git hook at: \"{git_hook_path}\"")

        if not _check_hook_ver(git_hook_path):
            return ValidationResult(
                valid = False,
                severity = Severity.ERROR,
                message = f"Incorrect Git '{hook_name}' hook version installed!"
            )

        if not _check_hook_hash(hook_name, git_hook_path):
            return ValidationResult(
                valid = False,
                severity = Severity.ERROR,
                message = f"Git '{hook_name}' hook is corrupt!"
            )

    return ValidationResult(
        valid = True,
        severity = Severity.NONE
    )

# TODO: Find a new way to validate this
def install() -> bool:
    info("Installing Git hooks...")
    for [hook_name, hook_fn] in HOOK_REGISTRY.items():
        _install_hook(hook_name)

    return True

def ensure():
    result = validate()
    if result.valid:
        info("All Git hooks correctly installed.")
        return

    log_validation_result(result)
    install()

    # Revalidate after install
    post = validate()
    if not post.valid:
        error(f"Git hook installation failed!")
        log_validation_result(post)

        return

    info("All Git hooks correctly installed.")

def _is_installed(git_hook_path: Path) -> bool:
    return git_hook_path.exists()

def _check_hook_ver(git_hook_path: Path) -> bool:
    with open(git_hook_path, 'r') as hook:
        hook.readline() # Skip first line
        hook_ver = hook.readline()[1:].strip()

        return parse_ver(hook_ver) >= _HOOK_REQUIRED_VER

def _check_hook_hash(hook_name: str, git_hook_path: Path) -> bool:
    content_hash = hashlib.sha256(_format_hook_content(hook_name).encode("utf-8")).hexdigest()
    with open(git_hook_path, "rb") as git_hook:
        git_hook_hash = hashlib.sha256(git_hook.read()).hexdigest()

    return content_hash == git_hook_hash

def _install_hook(name: str):
    info(f"Installing Git {name} hook v({_HOOK_VER})...")

    if not git_hooks_dir().exists():
        os.makedirs(git_hooks_dir())

    content = _format_hook_content(name)
    git_hook_path = git_hooks_dir() / name.replace('_', "-")

    trace(f"Writing hook to: \"{git_hook_path}\"...")
    git_hook_path.write_text(content, newline = '\n')
    git_hook_path.chmod(0o755)

def _format_hook_content(name: str) -> str:
    return _HOOK_TEMPLATE.format(version = _HOOK_VER, hook_name = name)
