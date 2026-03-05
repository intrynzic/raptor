import json
from pathlib import Path

from raptor.core.fs import msbuild_path, vswhere_path
from raptor.core.process import run_ex
from raptor.core.validation import Severity, ValidationResult
from raptor.doctor.checks.check import Check

_VS_REQUIRED_COMPONENTS: list[str] = ["Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "Microsoft.VisualStudio.Workload.ManagedDesktop"]


class VisualStudioCheck(Check):
    type_id = "VisualStudioCheck"
    name = "Visual Studio"
    description = "Validates the Visual Studio installation and required workloads."

    def validate(self) -> ValidationResult:
        if not vswhere_path().exists():
            return ValidationResult(
                valid=False,
                severity=Severity.ERROR,
                message="vswhere.exe could not be found! The Visual Studio Installer may not be installed.",
            )

        if not msbuild_path().exists():
            return ValidationResult(
                valid=False,
                severity=Severity.ERROR,
                message="msbuild.exe could not be found! Visual Studio's MSBuild component is missing!",
            )

        result = run_ex([vswhere_path(), "-latest", "-format", "json", "-requires"] + _VS_REQUIRED_COMPONENTS)
        if result is None or result.stderr:
            return ValidationResult(
                valid=False,
                severity=Severity.ERROR,
                message="Failed to run 'requires' command on vswhere.exe. It is likely that the Visual Studio Installer is corrupt.",
            )

        result_stdout = result.stdout.strip()
        if not result_stdout or (result_stdout == "[]"):
            return ValidationResult(
                valid=False, severity=Severity.ERROR, message="Required Visual Studio workloads/components are missing!"
            )

        data = json.loads(result_stdout)
        if not data:
            return ValidationResult(valid=True, severity=Severity.ERROR, message="vshwere.exe returned invalid JSON output.")

        install_path = Path(data[0]["installationPath"])

        # MSVC tools
        msvc_root = install_path / "VC" / "Tools" / "MSVC"
        if not msvc_root.exists():
            return ValidationResult(valid=False, severity=Severity.ERROR, message="MSVC tools are missing!")

        # MSVC
        latest_msvc = max(msvc_root.iterdir(), key=lambda p: p.name)
        cl_path = latest_msvc / "bin" / "Hostx64" / "x64" / "cl.exe"
        if not cl_path.exists():
            return ValidationResult(valid=False, severity=Severity.ERROR, message="cl.exe could not be found!")

        # C++ standard headers
        include_dir = latest_msvc / "include"
        if not (include_dir / "iostream").exists():
            return ValidationResult(
                valid=False, severity=Severity.ERROR, message="C++ standard headers are missing! iostream could not be found."
            )

        return ValidationResult(valid=True, severity=Severity.NONE)
