from raptor.core.validation import ValidationResult
from raptor.doctor.checks.check import Check
import raptor.setup.dotnet as dotnet


class DotNetCheck(Check):
    type_id = "DotNetCheck"
    name = ".NET SDK"
    description = "Validates the .NET SDK installation."

    def validate(self) -> ValidationResult:
        return dotnet.validate()

    def fix(self) -> bool:
        return dotnet.install()
