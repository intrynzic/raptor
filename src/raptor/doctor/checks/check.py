from abc import ABC, abstractmethod
from typing import Optional

from raptor.core.validation import Severity, ValidationResult


class Check(ABC):
    type_id: str = "base"
    name: str = "Unnamed check"
    description: str = ""

    def __init__(self):
        self.last_result: Optional[ValidationResult] = None

    @abstractmethod
    def validate(self) -> ValidationResult:
        """
        Run the diagnostic and return a ValidationResult.
        """
        pass

    def fix(self) -> bool:
        """
        Attempt to automatically fix the issue.
        Return True if fix succeeded, False otherwise.
        Default: not fixable.
        """
        return False

    def to_dict(self) -> dict:
        result = self.last_result

        return {
            "type_id": self.type_id,
            "name": self.name,
            "status": "pass" if result and result.valid else "fail",
            "severity": result.severity.name if result else None,
            "message": result.message if result else None
        }

    def from_dict(self, check_dict: dict):
        self.type_id = check_dict["type_id"]
        self.name = check_dict["name"]
        self.last_result = ValidationResult(
            valid = True if check_dict["status"] == "pass" else False,
            severity = Severity[check_dict["severity"]],
            message = check_dict["message"]
        )

    @property
    def can_fix(self) -> bool:
        return self.fix.__func__ is not Check.fix
