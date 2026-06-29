import raptor.setup.git as git
from raptor.core.validation import ValidationResult
from raptor.doctor.checks.check import Check


class GitCheck(Check):
    type_id = "GitCheck"
    name = "Git for Windows"
    description = "Validates the Git for Windows installation."

    def validate(self) -> ValidationResult:
        return git.validate()

    def fix(self) -> bool:
        return git.install()
