from enum import Enum

class ApprovalStatus(Enum):
    """Value object representing approval status for simulation terms."""
    TBD = "tbd"
    OK = "ok"
    
    def is_approved(self) -> bool:
        """Check if status represents approval."""
        return self == ApprovalStatus.OK
    
    def toggle(self) -> 'ApprovalStatus':
        """Toggle between TBD and OK states."""
        return ApprovalStatus.OK if self == ApprovalStatus.TBD else ApprovalStatus.TBD 