from dataclasses import dataclass
from uuid import UUID
from ...domain.value_objects.term_key import TermKey

@dataclass(frozen=True)
class ToggleApprovalCommand:
    """Command to toggle approval status for a specific term."""
    
    session_id: UUID
    term_key: TermKey
