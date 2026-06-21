import raptor.setup.doxygen as doxygen
from raptor.core.validation import ValidationResult
from raptor.doctor.checks.check import Check


class DoxygenCheck(Check):
    type_id = "DoxygenCheck"
    name = "Doxygen"
    description = "Validates the Doxygen installation."

    def validate(self) -> ValidationResult:
        return doxygen.validate()

    def fix(self) -> bool:
        return doxygen.install()
