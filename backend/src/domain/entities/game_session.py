from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from ..value_objects.game_type import GameType


class SessionStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class GameSession:
    """Domain entity representing a simulation game session."""
    
    id: str
    game_type: GameType
    status: SessionStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    @classmethod
    def create(cls, session_id: str, game_type: GameType) -> 'GameSession':
        """Factory method to create new game session."""
        return cls(
            id=session_id,
            game_type=game_type,
            status=SessionStatus.ACTIVE,
            created_at=datetime.utcnow()
        )
    
    def complete(self) -> None:
        """Completes the session. Can only be called on an active session."""
        # This logic might need to change if we ever add a 'paused' state.
        if self.status != SessionStatus.ACTIVE:
            raise ValueError(f"Session {self.id} is not active, cannot complete.")
        
        self.status = SessionStatus.COMPLETED
        self.completed_at = datetime.utcnow()
    
    def cancel(self) -> None:
        """Cancel the game session."""
        if self.status == SessionStatus.COMPLETED:
            raise ValueError(f"Session {self.id} is already completed, cannot cancel.")
        
        self.status = SessionStatus.CANCELLED
        self.completed_at = datetime.utcnow()
    
    @property
    def is_active(self) -> bool:
        """Check if session is currently active."""
        return self.status == SessionStatus.ACTIVE
