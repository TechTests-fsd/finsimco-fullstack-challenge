from abc import ABC
from dataclasses import dataclass
from decimal import Decimal

class CapitalRaised(ABC):
    """Abstract base for capital raised results."""
    pass

@dataclass(frozen=True)
class CapitalAmount(CapitalRaised):
    """Specific capital amount raised."""
    
    amount: Decimal
    
    def __str__(self) -> str:
        return str(self.amount)

@dataclass(frozen=True)
class AllocationNeeded(CapitalRaised):
    """Indicates allocation is needed due to over-subscription."""
    
    def __str__(self) -> str:
        return "Allocate" 