from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Severity(Enum):
    NONE = "NONE"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class ValidationResult:
    valid: bool
    severity: Severity
    message: Optional[str] = None
