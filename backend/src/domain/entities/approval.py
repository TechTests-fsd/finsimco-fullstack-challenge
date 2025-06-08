from dataclasses import dataclass

from ..value_objects.approval import ApprovalStatus
from ..value_objects.term_key import TermKey


@dataclass
class Approval:
    """Entity representing approval status for a term."""
    
    session_id: str
    term_key: TermKey
    status: ApprovalStatus
    
    @classmethod
    def create(cls, session_id: str, term_key: TermKey, status: ApprovalStatus) -> 'Approval':
        """Create new approval entity."""
        return cls(
            session_id=session_id,
            term_key=term_key,
            status=status
        )
    
    def is_approved(self) -> bool:
        """Check if the term is approved."""
        return self.status == ApprovalStatus.OK
    
    def is_pending(self) -> bool:
        """Check if the term is pending approval."""
        return self.status == ApprovalStatus.TBD
    
    def toggle(self) -> 'Approval':
        """Toggle approval status between TBD and OK."""
        new_status = ApprovalStatus.OK if self.status == ApprovalStatus.TBD else ApprovalStatus.TBD
        
        return Approval(
            session_id=self.session_id,
            term_key=self.term_key,
            status=new_status
        )
    
    def reset_to_tbd(self) -> 'Approval':
        """Reset approval status to TBD."""
        return Approval(
            session_id=self.session_id,
            term_key=self.term_key,
            status=ApprovalStatus.TBD
        ) 