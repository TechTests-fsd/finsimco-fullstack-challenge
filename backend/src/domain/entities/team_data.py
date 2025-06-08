from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional

from ..value_objects.team_id import TeamId
from ..value_objects.term_key import TermKey


@dataclass
class TeamData:
    """Holds all the numbers that one team has entered for a game session."""
    
    session_id: str
    team_id: TeamId
    term_values: Dict[TermKey, Decimal]
    
    @classmethod
    def create(cls, session_id: str, team_id: TeamId, term_values: Optional[Dict[TermKey, Decimal]] = None) -> 'TeamData':
        """Create new team data entity."""
        return cls(
            session_id=session_id,
            team_id=team_id,
            term_values=term_values or {}
        )
    
    def get_term_value(self, term_key: TermKey) -> Optional[Decimal]:
        """Get value for a specific term."""
        return self.term_values.get(term_key)
    
    def update_term_value(self, term_key: TermKey, value: Decimal) -> 'TeamData':
        """Update a term value and return new instance."""
        new_values = self.term_values.copy()
        new_values[term_key] = value
        
        return TeamData(
            session_id=self.session_id,
            team_id=self.team_id,
            term_values=new_values
        )
    
    def has_term(self, term_key: TermKey) -> bool:
        """Check if term has been set."""
        return term_key in self.term_values 