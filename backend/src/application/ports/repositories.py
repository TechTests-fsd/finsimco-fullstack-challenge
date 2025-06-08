from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from decimal import Decimal

from ...domain.value_objects.team_id import TeamId
from ...domain.value_objects.term_key import TermKey


class IGameSessionRepository(ABC):
    """Port for game session repository operations."""
    
    @abstractmethod
    def add(self, session: 'GameSession') -> None:
        """Save a new game session"""
        raise NotImplementedError
    
    @abstractmethod
    def get_by_id(self, session_id: str) -> Optional['GameSession']:
        """Find game session by ID"""
        raise NotImplementedError
    
    @abstractmethod
    def get_active_sessions(self) -> List['GameSession']:
        """Find all active game sessions"""
        raise NotImplementedError

    @abstractmethod
    def save(self, session: 'GameSession') -> None:
        """Update existing game session"""
        raise NotImplementedError


class ITeamDataRepository(ABC):
    """Port for team data repository operations."""
    
    @abstractmethod
    def save(self, team_data: 'TeamData') -> None:
        """Save or update team data"""
        raise NotImplementedError
    
    @abstractmethod
    def get_by_session_and_team(self, session_id: str, team_id: TeamId) -> Optional['TeamData']:
        """Find team data by session and team"""
        raise NotImplementedError
    
    @abstractmethod
    def get_by_session(self, session_id: str) -> Dict[TeamId, 'TeamData']:
        """Find all team data for a session"""
        raise NotImplementedError


class IApprovalRepository(ABC):
    """Port for managing the approval state of simulation terms."""
    
    @abstractmethod
    def save(self, approval: 'Approval') -> None:
        """Save or update approval state"""
        raise NotImplementedError

    @abstractmethod
    def get_by_session(self, session_id: str) -> List['Approval']:
        """Get all approvals for a session"""
        raise NotImplementedError
    
    @abstractmethod
    def get_by_session_and_term(self, session_id: str, term_key: TermKey) -> Optional['Approval']:
        """Get approval state for a specific term in a session"""
        raise NotImplementedError 