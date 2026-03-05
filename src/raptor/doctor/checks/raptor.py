from raptor.core.fs import tools_dir
from raptor.core.git import repo_root
from raptor.core.process import run
from raptor.core.validation import ValidationResult, Severity
from raptor.doctor.checks.check import Check


class RaptorCheck(Check):
    type_id = "RaptorCheck"
    name = "Intricate-Raptor"
    description = "Validates this installation of Intricate-Raptor."

    def validate(self) -> ValidationResult:
        # TODO: This must ALL be reworked!
        root = repo_root()
        devtools_dir = str(tools_dir() / "DevTools").replace('\\', '/')

        installed_ver = run(["repo", "--version"], cwd = root, capture = True)
        repo_ver = run(["python", "-c",
                        f"import sys; sys.path.insert(0, '{devtools_dir}'); import raptor; print(raptor.__version__)"],
                        cwd = root, capture = True)

        if installed_ver != repo_ver:
            return ValidationResult(
                valid = False,
                severity = Severity.ERROR,
                message = "Incorrect Intricate-Raptor version installed!"
            )

        return ValidationResult(
            valid = True,
            severity = Severity.NONE
        )

    def fix(self) -> bool:
        root = repo_root()

        # TODO: This is incorrect, must be installed from PyPI!
        res = run(["python", "-m", "pip", "install", f"\"{tools_dir() / "raptor"}\"", "--quiet"], cwd = root, capture = True)

        return len(res) != 0
