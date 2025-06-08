from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal
from ...domain.value_objects.team_id import TeamId
from ...domain.value_objects.term_key import TermKey

@dataclass(frozen=True)
class UpdateTeamDataCommand:
    """Command to update team data for a specific term."""
    
    session_id: UUID
    team_id: TeamId
    term_key: TermKey
    value: Decimal
