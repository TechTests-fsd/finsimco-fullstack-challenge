from enum import Enum

class TermKey(str, Enum):
    """Pure value object for term keys - no logic."""
    
    # Game 1 terms
    EBITDA = "ebitda"
    INTEREST_RATE = "interest_rate"
    MULTIPLE = "multiple"
    FACTOR_SCORE = "factor_score"
    
    # Game 2 terms - Company Pricing (Team 1) and Shares Bid (Team 2)
    COMPANY1_PRICE = "company1_price"
    COMPANY1_SHARES = "company1_shares"
    COMPANY2_PRICE = "company2_price"
    COMPANY2_SHARES = "company2_shares"
    COMPANY3_PRICE = "company3_price"
    COMPANY3_SHARES = "company3_shares"
    INVESTOR1_BID_C1 = "investor1_bid_c1"
    INVESTOR1_BID_C2 = "investor1_bid_c2"
    INVESTOR1_BID_C3 = "investor1_bid_c3"
    INVESTOR2_BID_C1 = "investor2_bid_c1"
    INVESTOR2_BID_C2 = "investor2_bid_c2"
    INVESTOR2_BID_C3 = "investor2_bid_c3"
    INVESTOR3_BID_C1 = "investor3_bid_c1"
    INVESTOR3_BID_C2 = "investor3_bid_c2"
    INVESTOR3_BID_C3 = "investor3_bid_c3"
    
    COMPANY1_DEAL_APPROVAL = "company1_deal_approval"
    COMPANY2_DEAL_APPROVAL = "company2_deal_approval"
    COMPANY3_DEAL_APPROVAL = "company3_deal_approval"