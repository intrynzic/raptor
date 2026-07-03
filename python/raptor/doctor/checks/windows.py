from pathlib import Path

from raptor.core.fs import vswhere_path
from raptor.core.process import run_ex
from raptor.core.validation import Severity, ValidationResult
from raptor.doctor.checks.check import Check

_VS_WINDOWS_SDK_COMPONENT: str = "Microsoft.VisualStudio.Component.Windows10SDK"


class WindowsCheck(Check):
    type_id = "WindowsCheck"
    name = "Windows SDK"
    description = "Validates the Windows SDK installation."

    def validate(self) -> ValidationResult:
        # Check if Windows SDK is installed via vswhere
        result = run_ex([vswhere_path(), "-latest", "-requires", _VS_WINDOWS_SDK_COMPONENT])
        if result is None:
            return ValidationResult(valid=False, severity=Severity.ERROR, message="Visual Studio's Windows SDK component is missing!")

        # Windows SDK
        sdk_root = Path(r"C:\Program Files (x86)\Windows Kits\10")
        if not sdk_root.exists():
            return ValidationResult(valid=False, severity=Severity.ERROR, message="Windows SDK directory is missing!")

        include_root = sdk_root / "Include"
        if not include_root.exists():
            return ValidationResult(valid=False, severity=Severity.ERROR, message="Windows SDK include directory is missing!")

        # Windows SDK headers
        latest_sdk = max(include_root.iterdir(), key=lambda p: p.name)
        if not (latest_sdk / "um" / "windows.h").exists():
            return ValidationResult(
                valid=False, severity=Severity.CRITICAL, message="windows.h could not be found in the installed Windows SDK!"
            )

        # Universal CRT (C standard headers)
        if not (latest_sdk / "ucrt" / "stdio.h").exists():
            return ValidationResult(valid=False, severity=Severity.ERROR, message="Windows universal C runtime headers are missing!")

        return ValidationResult(valid=True, severity=Severity.NONE)
