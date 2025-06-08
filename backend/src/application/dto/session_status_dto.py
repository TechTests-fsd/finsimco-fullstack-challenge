from dataclasses import dataclass
from typing import Dict, Optional
from decimal import Decimal
from ...domain.value_objects.team_id import TeamId
from ...domain.value_objects.term_key import TermKey
from ...domain.value_objects.approval import ApprovalStatus
from ...domain.value_objects.game_type import GameType


@dataclass(frozen=True)
class TeamDataDTO:
    """A simple data bucket for one team's numbers. Safe to pass to the UI."""
    session_id: str
    team_id: TeamId
    term_values: Dict[TermKey, Decimal]


@dataclass(frozen=True)
class ApprovalDTO:
    """A simple data bucket for a single TBD/OK status. Safe to pass to the UI."""
    session_id: str
    term_key: TermKey
    status: ApprovalStatus
    
    @property
    def is_approved(self) -> bool:
        """Check if approval is in OK status"""
        return self.status == ApprovalStatus.OK


@dataclass(frozen=True)
class GameSessionDTO:
    """A simple data bucket for the main game session info. Safe to pass to the UI."""
    id: str
    game_type: GameType
    status: str
    created_at: str
    completed_at: Optional[str] = None


@dataclass(frozen=True)
class SessionStatusDTO:
    """
    The big one. A single object that holds the entire state of a game session, all packed up and ready for the UI.
    """
    game_session: GameSessionDTO
    team_data: Dict[TeamId, TeamDataDTO]
    approvals: Dict[TermKey, ApprovalDTO]
    valuation: Optional[Decimal]
    is_complete: bool
    progress: Dict[str, int] 