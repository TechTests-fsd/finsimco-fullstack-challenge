from abc import ABC, abstractmethod
from decimal import Decimal

from ...domain.value_objects.team_id import TeamId
from ...domain.value_objects.term_key import TermKey
from ...domain.value_objects.approval import ApprovalStatus


class IPubSubService(ABC):
    """Port for pub/sub service operations."""
    
    @abstractmethod
    def publish_team_data_update(
        self, 
        session_id: str, 
        team_id: TeamId, 
        term_key: TermKey, 
        value: Decimal
    ) -> None:
        """Publish team data update notification."""
        raise NotImplementedError
    
    @abstractmethod
    def publish_approval_update(
        self, 
        session_id: str, 
        term_key: TermKey, 
        status: ApprovalStatus
    ) -> None:
        """Publish approval status update notification."""
        raise NotImplementedError 