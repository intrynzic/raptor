import raptor.setup.hooks as hooks
from raptor.core.validation import ValidationResult
from raptor.doctor.checks.check import Check


class GitHooksCheck(Check):
    type_id = "GitHooksCheck"
    name = "Git Hooks"
    description = "Validates the installed Git Hooks."

    def validate(self) -> ValidationResult:
        return hooks.validate()

    def fix(self) -> bool:
        return hooks.install()
