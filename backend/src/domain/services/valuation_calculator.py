from decimal import Decimal
from typing import Optional
from ..value_objects.subscription_status import SubscriptionStatus
from ..value_objects.capital_raised import CapitalRaised, CapitalAmount, AllocationNeeded

class ValuationCalculator:
    """
    A pure calculator. Just give it numbers, and it gives you back a result. No database, no side effects.
    """
    
    @staticmethod
    def calculate_game1_valuation(
        ebitda: Decimal, 
        multiple: Decimal, 
        factor_score: Decimal
    ) -> Decimal:
        """Calculate FBITDA valuation using the standard formula"""
        return ebitda * multiple * factor_score
    
    def calculate_game2_capital_raised(
        self,
        price: Decimal,
        available_shares: Decimal,
        total_bid_shares: Decimal,
    ) -> CapitalRaised:
        """Calculate capital raised for Game 2 companies."""
        if total_bid_shares <= available_shares:
            return CapitalAmount(amount=price * available_shares)
        else:
            return AllocationNeeded()
    
    def calculate_subscription_status(
        self,
        available_shares: Decimal,
        total_bid_shares: Decimal,
    ) -> SubscriptionStatus:
        """Calculate subscription status for Game 2 companies."""
        if total_bid_shares == available_shares:
            return SubscriptionStatus.FILLED
        elif total_bid_shares < available_shares:
            return SubscriptionStatus.UNDER
        else:
            return SubscriptionStatus.OVER
    
    def sum_investor_bids(self, bids: list[Decimal]) -> Decimal:
        """Sum all investor bids for a company."""
        return sum(bids)
