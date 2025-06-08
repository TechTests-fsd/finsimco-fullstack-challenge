from decimal import Decimal
from typing import Dict, Optional, Any
from ..entities.team_data import TeamData
from ..value_objects.term_key import TermKey


class Game2AnalyticsService:
    """
    Pure domain service for Game 2 calculations and analytics.
    """
    
    @staticmethod
    def calculate_shares_bid_for(team2_data: TeamData) -> Dict[str, Decimal]:
        """
        Adds up all the investor bids for each of the 3 companies.
        """
        result = {}
        
        for company_num in range(1, 4):
            total_bids = Decimal('0')
            
            for investor_num in range(1, 4):
                bid_key = getattr(TermKey, f'INVESTOR{investor_num}_BID_C{company_num}')
                bid_value = team2_data.get_term_value(bid_key)
                if bid_value is not None:
                    total_bids += bid_value
            
            result[f'company{company_num}'] = total_bids
        
        return result
    
    @staticmethod
    def calculate_capital_raised(
        company_pricing: Dict[str, Dict[str, Decimal]], 
        shares_bid_for: Dict[str, Decimal]
    ) -> Dict[str, Any]:
        """
        Calculates capital raised. If oversubscribed, it returns 'Allocate' instead of a number.
        """
        result = {}
        
        for company_key in ['company1', 'company2', 'company3']:
            pricing_info = company_pricing.get(company_key, {})
            price = pricing_info.get('price', Decimal('0'))
            available_shares = pricing_info.get('shares', Decimal('0'))
            total_bids = shares_bid_for.get(company_key, Decimal('0'))
            
            if total_bids <= available_shares:
                capital_raised = price * total_bids
            else:
                capital_raised = "Allocate"
            
            result[company_key] = capital_raised
        
        return result
    
    @staticmethod
    def calculate_subscription_status(
        company_pricing: Dict[str, Dict[str, Decimal]], 
        shares_bid_for: Dict[str, Decimal]
    ) -> Dict[str, str]:
        """
        Figures out if a company is 'Filled', 'Under', or 'Over' subscribed.
        """
        result = {}
        
        for company_key in ['company1', 'company2', 'company3']:
            pricing_info = company_pricing.get(company_key, {})
            available_shares = pricing_info.get('shares', Decimal('0'))
            total_bids = shares_bid_for.get(company_key, Decimal('0'))
            
            if total_bids == available_shares:
                status = "Filled"
            elif total_bids < available_shares:
                status = "Under"
            else:
                status = "Over"
            
            result[company_key] = status
        
        return result
    
    @staticmethod
    def find_most_bids_company(shares_bid_for: Dict[str, Decimal]) -> str:
        """Find which company received the most bids from investors."""
        max_bids = Decimal('0')
        max_company = None
        
        for company_key, total_bids in shares_bid_for.items():
            if total_bids > max_bids:
                max_bids = total_bids
                max_company = company_key
        
        if max_company:
            company_num = max_company.replace('company', '')
            return f"Company {company_num}"
        else:
            return "No data"
    
    @staticmethod
    def extract_company_pricing(team1_data: TeamData) -> Dict[str, Dict[str, Decimal]]:
        """A helper to pull out just the price/shares info from Team 1's data blob."""
        result = {}
        
        for company_num in range(1, 4):
            price_key = getattr(TermKey, f'COMPANY{company_num}_PRICE')
            shares_key = getattr(TermKey, f'COMPANY{company_num}_SHARES')
            
            price = team1_data.get_term_value(price_key)
            shares = team1_data.get_term_value(shares_key)
            
            if price is not None and shares is not None:
                result[f'company{company_num}'] = {
                    'price': price,
                    'shares': shares
                }
        
        return result
    
    @staticmethod
    def extract_investor_bids(team2_data: TeamData) -> Dict[str, Dict[str, Optional[Decimal]]]:
        """A helper to pull out all the investor bids from Team 2's data blob."""
        result = {}
        
        for investor_num in range(1, 4):
            investor_bids = {}
            for company_num in range(1, 4):
                bid_key = getattr(TermKey, f'INVESTOR{investor_num}_BID_C{company_num}')
                bid_value = team2_data.get_term_value(bid_key)
                investor_bids[f'company{company_num}'] = bid_value
            
            result[f'investor{investor_num}'] = investor_bids
        
        return result
    
    @classmethod
    def calculate_full_summary(
        cls, 
        team1_data: Optional[TeamData], 
        team2_data: Optional[TeamData]
    ) -> Dict:
        """
        The main public method. Takes both teams' data and runs all the other calculations in this class to produce the final summary report.
        """
        if not team1_data or not team2_data:
            return {}
        
        company_pricing = cls.extract_company_pricing(team1_data)
        investor_bids = cls.extract_investor_bids(team2_data)
        
        shares_bid_for = cls.calculate_shares_bid_for(team2_data)
        capital_raised = cls.calculate_capital_raised(company_pricing, shares_bid_for)
        subscription_status = cls.calculate_subscription_status(company_pricing, shares_bid_for)
        most_bids_company = cls.find_most_bids_company(shares_bid_for)
        
        companies_summary = {}
        for company_key in ['company1', 'company2', 'company3']:
            companies_summary[company_key] = {
                'shares_bid_for': shares_bid_for.get(company_key, Decimal('0')),
                'capital_raised': capital_raised.get(company_key, 'N/A'),
                'subscription': subscription_status.get(company_key, 'N/A'),
                'available_shares': company_pricing.get(company_key, {}).get('shares', Decimal('0')),
                'price_per_share': company_pricing.get(company_key, {}).get('price', Decimal('0'))
            }
        
        return {
            'companies': companies_summary,
            'most_bids_company': most_bids_company,
            'team1_pricing': company_pricing,
            'team2_bids': investor_bids
        } 