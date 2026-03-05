from raptor.core.fs import vswhere_path, tmp_dir
from raptor.core.process import run_ex
from raptor.core.validation import ValidationResult, Severity
from raptor.doctor.checks.check import Check
from pathlib import Path
import json


_CPP_STANDARD = "/std:c++23preview"

# NOTE: This just tests a random feature of C++23 to see if it compiles correctly
_CPP_CODE = r"""#include <expected>
int main()
{
    std::expected<int, int> e = 21;
    return 0;
}
"""

class Cpp23Check(Check):
    type_id = "Cpp23Check"
    name = "C++23 Compiler Support"
    description = "Validates the compiler support for C++23"

    def validate(self) -> ValidationResult:
        result = run_ex([vswhere_path(), "-latest", "-format", "json"])
        if result is None or result.stderr:
            return ValidationResult(
                valid = False,
                severity = Severity.ERROR,
                message = "Failed to run 'requires' command on vswhere.exe. It is likely that the Visual Studio Installer is corrupt."
            )

        result_stdout = result.stdout.strip()
        if not result_stdout or (result_stdout == "[]"):
            return ValidationResult(
                valid = False,
                severity = Severity.ERROR,
                message = "Required Visual Studio workloads/components are missing!"
            )

        data = json.loads(result_stdout)
        if not data:
            return ValidationResult(
                valid = True,
                severity = Severity.ERROR,
                message = "vshwere.exe returned invalid JSON output."
            )

        install_path = Path(data[0]["installationPath"])
        msvc_root = install_path / "VC" / "Tools" / "MSVC"
        latest_msvc = max(msvc_root.iterdir(), key = lambda p: p.name)
        cl_path = latest_msvc / "bin" / "Hostx64" / "x64" / "cl.exe"

        if not cl_path.exists():
            return ValidationResult(
                valid = False,
                severity = Severity.ERROR,
                message = "cl.exe could not be found!"
            )

        cpp_file = tmp_dir() / "test.cpp"
        with open(cpp_file, 'w') as cpp:
            cpp.write(_CPP_CODE)

        vcvars = install_path / "VC" / "Auxiliary" / "Build" / "vcvars64.bat"
        if not vcvars.exists():
            return ValidationResult(
                valid = False,
                severity = Severity.ERROR,
                message = "vcvars64.bat could not be found!"
            )

        result = run_ex([vcvars, "&&", cl_path, "/c", _CPP_STANDARD, cpp_file], cwd = tmp_dir())
        if result is None or (result.returncode != 0):
            return ValidationResult(
                valid = False,
                severity = Severity.ERROR,
                message = "Compiler does not support C++23!"
            )

        return ValidationResult(
            valid = True,
            severity = Severity.NONE
        )
