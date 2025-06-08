from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from enum import Enum


class ValidationSeverity(Enum):
    """Enum for validation error severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class ValidationError:
    """A simple, clean object to hold all the info about one validation problem."""
    field: str
    message: str
    value: Decimal
    code: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    context: Optional[str] = None
    
    def is_critical(self) -> bool:
        """Check if this is a critical error that blocks input."""
        return self.severity == ValidationSeverity.ERROR
    
    def is_warning(self) -> bool:
        """Check if this is a warning that allows continuation."""
        return self.severity == ValidationSeverity.WARNING
    
    def is_info(self) -> bool:
        """Check if this is informational context."""
        return self.severity == ValidationSeverity.INFO
    
    def get_display_icon(self) -> str:
        """Get display icon for CLI."""
        if self.severity == ValidationSeverity.ERROR:
            return "❌"
        elif self.severity == ValidationSeverity.WARNING:
            return "⚠️"
        else:
            return "ℹ️" 