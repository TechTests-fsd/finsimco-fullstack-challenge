from enum import Enum

class SubscriptionStatus(Enum):
    """Value object for subscription status in Game 2."""
    
    FILLED = "filled"
    UNDER = "under" 
    OVER = "over"
    
    def __str__(self) -> str:
        return self.value 