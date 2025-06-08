from enum import Enum

class TeamId(Enum):
    """Value object representing a team identifier."""
    
    TEAM_ONE = 1
    TEAM_TWO = 2
    
    def __int__(self) -> int:
        return self.value
    
    def is_team_one(self) -> bool:
        """Check if this is Team 1."""
        return self == TeamId.TEAM_ONE
    
    def is_team_two(self) -> bool:
        """Check if this is Team 2."""
        return self == TeamId.TEAM_TWO
    