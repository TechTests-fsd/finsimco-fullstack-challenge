from typing import Dict, Set, List
from decimal import Decimal
from ..value_objects.term_key import TermKey
from ..value_objects.term_metadata import TermMetadata, TermDataType, BusinessRule, ContextualRule, RuleCondition
from dataclasses import dataclass
from enum import Enum
from ..value_objects.approval import ApprovalStatus
from ..value_objects.game_type import GameType
from ..value_objects.team_id import TeamId
from ..value_objects.validation_error import ValidationError, ValidationSeverity

@dataclass(frozen=True)
class TeamRole:
    """Immutable team role definition"""
    name: str
    description: str

@dataclass(frozen=True)
class GameMetadata:
    """Immutable game metadata"""
    name: str
    description: str
    roles: Dict[TeamId, TeamRole]
    completion_message: str

@dataclass(frozen=True) 
class GameDefinition:
    """Immutable game definition with all configuration"""
    metadata: GameMetadata
    terms: Set[TermKey]
    term_metadata: Dict[TermKey, TermMetadata]

class GameConfiguration:
    """
    The master config file for everything. All rules, terms, and metadata for all games live here. If you need to change how a game works, this is the first place to look.
    """
    
    TERM_METADATA: Dict[TermKey, TermMetadata] = {
        # Game 1 - FBITDA Valuation Terms
        TermKey.EBITDA: TermMetadata(
            key="EBITDA",
            display_name="EBITDA",
            unit="£",
            data_type=TermDataType.CURRENCY,
            min_value=Decimal("0"),
            max_value=Decimal("1000000000"),
            precision=0,
            description="Earnings Before Interest, Taxes, Depreciation, and Amortization",
            business_rules=[
                BusinessRule(
                    name="Small_Business",
                    min_value=Decimal("0"),
                    max_value=Decimal("10000000"),
                    description="Small to medium enterprises"
                ),
                BusinessRule(
                    name="Large_Enterprise",
                    min_value=Decimal("10000001"),
                    max_value=Decimal("100000000"),
                    description="Large enterprises"
                ),
                BusinessRule(
                    name="Mega_Corporation",
                    min_value=Decimal("100000001"),
                    max_value=Decimal("1000000000"),
                    description="Mega corporations requiring board approval"
                )
            ],
            contextual_rules=[
                ContextualRule(
                    condition=RuleCondition.ABOVE,
                    threshold=Decimal("100000000"), 
                    message="High EBITDA (>£100M) - Board approval may be required",
                    code="EBITDA_BOARD_APPROVAL_REQUIRED",
                    severity="warning"
                )
            ]
        ),
        TermKey.INTEREST_RATE: TermMetadata(
            key="INTEREST_RATE",
            display_name="Interest Rate",
            unit="%",
            data_type=TermDataType.PERCENTAGE,
            min_value=Decimal("0"),
            max_value=Decimal("100"),
            precision=2,
            description="Cost of capital for debt financing",
            business_rules=[
                BusinessRule(
                    name="Low_Risk",
                    min_value=Decimal("0"),
                    max_value=Decimal("5"),
                    description="Low risk, favorable market conditions"
                ),
                BusinessRule(
                    name="Moderate_Risk",
                    min_value=Decimal("5.01"),
                    max_value=Decimal("10"),
                    description="Moderate risk, normal market conditions"
                ),
                BusinessRule(
                    name="High_Risk",
                    min_value=Decimal("10.01"),
                    max_value=Decimal("100"),
                    description="High risk, challenging market conditions"
                )
            ],
            contextual_rules=[
                ContextualRule(
                    condition=RuleCondition.ABOVE,
                    threshold=Decimal("15"),
                    message="High interest rate (>15%) - Consider refinancing options",
                    code="INTEREST_RATE_REFINANCING_ADVISORY",
                    severity="warning"
                )
            ]
        ),
        TermKey.MULTIPLE: TermMetadata(
            key="MULTIPLE",
            display_name="Valuation Multiple",
            unit="x",
            data_type=TermDataType.DECIMAL,
            min_value=Decimal("0.1"),
            max_value=Decimal("50"),
            precision=1,
            description="Industry-specific EBITDA multiplier",
            business_rules=[
                BusinessRule(
                    name="Distressed_Valuation",
                    min_value=Decimal("0.1"),
                    max_value=Decimal("5"),
                    description="Distressed or declining industry"
                ),
                BusinessRule(
                    name="Standard_Valuation",
                    min_value=Decimal("5.1"),
                    max_value=Decimal("15"),
                    description="Standard industry multiples"
                ),
                BusinessRule(
                    name="Premium_Valuation",
                    min_value=Decimal("15.1"),
                    max_value=Decimal("50"),
                    description="Premium or high-growth industry"
                )
            ],
            contextual_rules=[
                ContextualRule(
                    condition=RuleCondition.ABOVE,
                    threshold=Decimal("20"),
                    message="Very high multiple (>20x) - Verify market comparables",
                    code="MULTIPLE_MARKET_VERIFICATION_REQUIRED",
                    severity="warning"
                )
            ]
        ),
        TermKey.FACTOR_SCORE: TermMetadata(
            key="FACTOR_SCORE",
            display_name="Risk Factor Score",
            unit="",
            data_type=TermDataType.DECIMAL,
            min_value=Decimal("0.1"),
            max_value=Decimal("2.0"),
            precision=2,
            description="Risk adjustment factor (1.0 = neutral, <1.0 = risky, >1.0 = premium)",
            business_rules=[
                BusinessRule(
                    name="High_Risk",
                    min_value=Decimal("0.1"),
                    max_value=Decimal("0.8"),
                    description="High risk factors present"
                ),
                BusinessRule(
                    name="Neutral_Risk",
                    min_value=Decimal("0.81"),
                    max_value=Decimal("1.2"),
                    description="Neutral risk profile"
                ),
                BusinessRule(
                    name="Premium_Quality",
                    min_value=Decimal("1.21"),
                    max_value=Decimal("2.0"),
                    description="Premium quality with low risk"
                )
            ],
            contextual_rules=[
                ContextualRule(
                    condition=RuleCondition.BELOW,
                    threshold=Decimal("0.5"),
                    message="High risk score (<0.5) - Review risk mitigation strategies",
                    code="FACTOR_RISK_MITIGATION_REVIEW",
                    severity="warning"
                )
            ]
        ),
        
        TermKey.COMPANY1_PRICE: TermMetadata(
            key="COMPANY1_PRICE",
            display_name="Company 1 Price",
            unit="#",
            data_type=TermDataType.INTEGER,
            min_value=Decimal("1"),
            max_value=Decimal("100"),
            precision=0,
            description="Share price for Company 1",
            business_rules=[],
            contextual_rules=[]
        ),
        TermKey.COMPANY1_SHARES: TermMetadata(
            key="COMPANY1_SHARES",
            display_name="Company 1 Shares",
            unit="#",
            data_type=TermDataType.INTEGER,
            min_value=Decimal("1000"),
            max_value=Decimal("50000"),
            precision=0,
            description="Number of shares for Company 1",
            business_rules=[],
            contextual_rules=[]
        ),
        TermKey.COMPANY2_PRICE: TermMetadata(
            key="COMPANY2_PRICE",
            display_name="Company 2 Price",
            unit="#",
            data_type=TermDataType.INTEGER,
            min_value=Decimal("1"),
            max_value=Decimal("100"),
            precision=0,
            description="Share price for Company 2",
            business_rules=[],
            contextual_rules=[]
        ),
        TermKey.COMPANY2_SHARES: TermMetadata(
            key="COMPANY2_SHARES",
            display_name="Company 2 Shares",
            unit="#",
            data_type=TermDataType.INTEGER,
            min_value=Decimal("1000"),
            max_value=Decimal("50000"),
            precision=0,
            description="Number of shares for Company 2",
            business_rules=[],
            contextual_rules=[]
        ),
        TermKey.COMPANY3_PRICE: TermMetadata(
            key="COMPANY3_PRICE",
            display_name="Company 3 Price",
            unit="#",
            data_type=TermDataType.INTEGER,
            min_value=Decimal("1"),
            max_value=Decimal("100"),
            precision=0,
            description="Share price for Company 3",
            business_rules=[],
            contextual_rules=[]
        ),
        TermKey.COMPANY3_SHARES: TermMetadata(
            key="COMPANY3_SHARES",
            display_name="Company 3 Shares",
            unit="#",
            data_type=TermDataType.INTEGER,
            min_value=Decimal("1000"),
            max_value=Decimal("50000"),
            precision=0,
            description="Number of shares for Company 3",
            business_rules=[],
            contextual_rules=[]
        ),
        # Team 2 Investor Bids
        TermKey.INVESTOR1_BID_C1: TermMetadata(
            key="INVESTOR1_BID_C1",
            display_name="Investor 1 Bid C1",
            unit="#",
            data_type=TermDataType.INTEGER,
            min_value=Decimal("0"),
            max_value=Decimal("20000"),
            precision=0,
            description="Investor 1 bid for Company 1 shares",
            business_rules=[],
            contextual_rules=[]
        ),
        TermKey.INVESTOR1_BID_C2: TermMetadata(
            key="INVESTOR1_BID_C2",
            display_name="Investor 1 Bid C2",
            unit="#",
            data_type=TermDataType.INTEGER,
            min_value=Decimal("0"),
            max_value=Decimal("20000"),
            precision=0,
            description="Investor 1 bid for Company 2 shares",
            business_rules=[],
            contextual_rules=[]
        ),
        TermKey.INVESTOR1_BID_C3: TermMetadata(
            key="INVESTOR1_BID_C3",
            display_name="Investor 1 Bid C3",
            unit="#",
            data_type=TermDataType.INTEGER,
            min_value=Decimal("0"),
            max_value=Decimal("20000"),
            precision=0,
            description="Investor 1 bid for Company 3 shares",
            business_rules=[],
            contextual_rules=[]
        ),
        TermKey.INVESTOR2_BID_C1: TermMetadata(
            key="INVESTOR2_BID_C1",
            display_name="Investor 2 Bid C1",
            unit="#",
            data_type=TermDataType.INTEGER,
            min_value=Decimal("0"),
            max_value=Decimal("20000"),
            precision=0,
            description="Investor 2 bid for Company 1 shares",
            business_rules=[],
            contextual_rules=[]
        ),
        TermKey.INVESTOR2_BID_C2: TermMetadata(
            key="INVESTOR2_BID_C2",
            display_name="Investor 2 Bid C2",
            unit="#",
            data_type=TermDataType.INTEGER,
            min_value=Decimal("0"),
            max_value=Decimal("20000"),
            precision=0,
            description="Investor 2 bid for Company 2 shares",
            business_rules=[],
            contextual_rules=[]
        ),
        TermKey.INVESTOR2_BID_C3: TermMetadata(
            key="INVESTOR2_BID_C3",
            display_name="Investor 2 Bid C3",
            unit="#",
            data_type=TermDataType.INTEGER,
            min_value=Decimal("0"),
            max_value=Decimal("20000"),
            precision=0,
            description="Investor 2 bid for Company 3 shares",
            business_rules=[],
            contextual_rules=[]
        ),
        TermKey.INVESTOR3_BID_C1: TermMetadata(
            key="INVESTOR3_BID_C1",
            display_name="Investor 3 Bid C1",
            unit="#",
            data_type=TermDataType.INTEGER,
            min_value=Decimal("0"),
            max_value=Decimal("20000"),
            precision=0,
            description="Investor 3 bid for Company 1 shares",
            business_rules=[],
            contextual_rules=[]
        ),
        TermKey.INVESTOR3_BID_C2: TermMetadata(
            key="INVESTOR3_BID_C2",
            display_name="Investor 3 Bid C2",
            unit="#",
            data_type=TermDataType.INTEGER,
            min_value=Decimal("0"),
            max_value=Decimal("20000"),
            precision=0,
            description="Investor 3 bid for Company 2 shares",
            business_rules=[],
            contextual_rules=[]
        ),
        TermKey.INVESTOR3_BID_C3: TermMetadata(
            key="INVESTOR3_BID_C3",
            display_name="Investor 3 Bid C3",
            unit="#",
            data_type=TermDataType.INTEGER,
            min_value=Decimal("0"),
            max_value=Decimal("20000"),
            precision=0,
            description="Investor 3 bid for Company 3 shares",
            business_rules=[],
            contextual_rules=[]
        ),
        
        # Game 2 Deal Approval Terms
        TermKey.COMPANY1_DEAL_APPROVAL: TermMetadata(
            key="COMPANY1_DEAL_APPROVAL",
            display_name="Company 1 Deal Finalization",
            unit="",
            data_type=TermDataType.TEXT,
            min_value=Decimal("0"),
            max_value=Decimal("1"),
            precision=0,
            description="Final approval for the outcome of Company 1's trading",
            business_rules=[],
            contextual_rules=[]
        ),
        TermKey.COMPANY2_DEAL_APPROVAL: TermMetadata(
            key="COMPANY2_DEAL_APPROVAL",
            display_name="Company 2 Deal Finalization",
            unit="",
            data_type=TermDataType.TEXT,
            min_value=Decimal("0"),
            max_value=Decimal("1"),
            precision=0,
            description="Final approval for the outcome of Company 2's trading",
            business_rules=[],
            contextual_rules=[]
        ),
        TermKey.COMPANY3_DEAL_APPROVAL: TermMetadata(
            key="COMPANY3_DEAL_APPROVAL",
            display_name="Company 3 Deal Finalization",
            unit="",
            data_type=TermDataType.TEXT,
            min_value=Decimal("0"),
            max_value=Decimal("1"),
            precision=0,
            description="Final approval for the outcome of Company 3's trading",
            business_rules=[],
            contextual_rules=[]
        )
    }

    GAME_DEFINITIONS: Dict[GameType, GameDefinition] = {
        GameType.GAME_1: GameDefinition(
            metadata=GameMetadata(
                name="FBITDA Valuation",
                description="Financial valuation simulation using EBITDA multiples",
                roles={
                    TeamId.TEAM_ONE: TeamRole(
                        name="Input Terms",
                        description="Enter financial metrics for valuation calculation"
                    ),
                    TeamId.TEAM_TWO: TeamRole(
                        name="Approve Terms", 
                        description="Review and approve submitted financial terms"
                    )
                },
                completion_message="🎉 FBITDA Valuation Complete! All terms approved by Team 2."
            ),
            terms={
                TermKey.EBITDA,
                TermKey.INTEREST_RATE,
                TermKey.MULTIPLE,
                TermKey.FACTOR_SCORE
            },
            term_metadata={
                k: v for k, v in TERM_METADATA.items() 
                if k in {TermKey.EBITDA, TermKey.INTEREST_RATE, TermKey.MULTIPLE, TermKey.FACTOR_SCORE}
            }
        ),
        
        GameType.GAME_2: GameDefinition(
            metadata=GameMetadata(
                name="Company Trading Simulation",
                description="Multi-company pricing and investment bidding simulation",
                roles={
                    TeamId.TEAM_ONE: TeamRole(
                        name="Company Pricing Team",
                        description="Set price and shares for Company 1, 2, and 3"
                    ),
                    TeamId.TEAM_TWO: TeamRole(
                        name="Investment Bidding Team",
                        description="Submit investment bids for each company"
                    )
                },
                completion_message="🎉 Trading Simulation Complete! All bids approved and deals finalized."
            ),
            terms={
                TermKey.COMPANY1_PRICE, TermKey.COMPANY1_SHARES,
                TermKey.COMPANY2_PRICE, TermKey.COMPANY2_SHARES,
                TermKey.COMPANY3_PRICE, TermKey.COMPANY3_SHARES,
                TermKey.INVESTOR1_BID_C1, TermKey.INVESTOR1_BID_C2, TermKey.INVESTOR1_BID_C3,
                TermKey.INVESTOR2_BID_C1, TermKey.INVESTOR2_BID_C2, TermKey.INVESTOR2_BID_C3,
                TermKey.INVESTOR3_BID_C1, TermKey.INVESTOR3_BID_C2, TermKey.INVESTOR3_BID_C3,
                TermKey.COMPANY1_DEAL_APPROVAL, TermKey.COMPANY2_DEAL_APPROVAL, TermKey.COMPANY3_DEAL_APPROVAL
            },
            term_metadata={
                k: v for k, v in TERM_METADATA.items()
                if k in {
                    TermKey.COMPANY1_PRICE, TermKey.COMPANY1_SHARES,
                    TermKey.COMPANY2_PRICE, TermKey.COMPANY2_SHARES,
                    TermKey.COMPANY3_PRICE, TermKey.COMPANY3_SHARES,
                    TermKey.INVESTOR1_BID_C1, TermKey.INVESTOR1_BID_C2, TermKey.INVESTOR1_BID_C3,
                    TermKey.INVESTOR2_BID_C1, TermKey.INVESTOR2_BID_C2, TermKey.INVESTOR2_BID_C3,
                    TermKey.INVESTOR3_BID_C1, TermKey.INVESTOR3_BID_C2, TermKey.INVESTOR3_BID_C3,
                    TermKey.COMPANY1_DEAL_APPROVAL, TermKey.COMPANY2_DEAL_APPROVAL, TermKey.COMPANY3_DEAL_APPROVAL
                }
            }
        )
    }

    @classmethod
    def get_game_metadata(cls, game_type: GameType) -> GameMetadata:
        """Get game metadata for UI display and role descriptions"""
        return cls.GAME_DEFINITIONS[game_type].metadata

    @classmethod
    def get_game_terms(cls, game_type: GameType) -> Set[TermKey]:
        """Get all terms for a specific game type"""
        return cls.GAME_DEFINITIONS[game_type].terms

    @classmethod
    def get_game_term_metadata(cls, game_type: GameType) -> Dict[TermKey, TermMetadata]:
        """Get term metadata for a specific game"""
        return cls.GAME_DEFINITIONS[game_type].term_metadata

    @classmethod
    def get_term_metadata(cls, term_key: TermKey) -> TermMetadata:
        """Get metadata for a specific term"""
        return cls.TERM_METADATA[term_key]

    @classmethod
    def is_valid_term_for_game(cls, game_type: GameType, term_key: TermKey) -> bool:
        """Just a quick check to see if a term is actually part of a given game."""
        return term_key in cls.GAME_DEFINITIONS[game_type].terms

    @classmethod
    def get_team_role_description(cls, game_type: GameType, team_id: TeamId) -> str:
        """Get team role description for UI display"""
        game_meta = cls.get_game_metadata(game_type)
        team_role = game_meta.roles[team_id]
        return f"Team {team_id.value} - {team_role.name}"

    @classmethod
    def get_completion_message(cls, game_type: GameType) -> str:
        """Get game completion message"""
        return cls.get_game_metadata(game_type).completion_message

    # Game 2 Company Term Mapping
    COMPANY_TERM_MAP = {
        1: {'price': TermKey.COMPANY1_PRICE, 'shares': TermKey.COMPANY1_SHARES},
        2: {'price': TermKey.COMPANY2_PRICE, 'shares': TermKey.COMPANY2_SHARES},
        3: {'price': TermKey.COMPANY3_PRICE, 'shares': TermKey.COMPANY3_SHARES},
    }
    
    INVESTOR_TERM_MAP = {
        (1, 1): TermKey.INVESTOR1_BID_C1, (1, 2): TermKey.INVESTOR1_BID_C2, (1, 3): TermKey.INVESTOR1_BID_C3,
        (2, 1): TermKey.INVESTOR2_BID_C1, (2, 2): TermKey.INVESTOR2_BID_C2, (2, 3): TermKey.INVESTOR2_BID_C3,
        (3, 1): TermKey.INVESTOR3_BID_C1, (3, 2): TermKey.INVESTOR3_BID_C2, (3, 3): TermKey.INVESTOR3_BID_C3,
    }

    @classmethod
    def get_all_game_types(cls) -> List[GameType]:
        """Get all available game types"""
        return list(cls.GAME_DEFINITIONS.keys())
    
    @classmethod
    def get_company_terms(cls, company_num: int) -> Dict[str, TermKey]:
        """Get price and shares terms for a specific company."""
        return cls.COMPANY_TERM_MAP[company_num]
    
    @classmethod
    def get_investor_term(cls, investor_num: int, company_num: int) -> TermKey:
        """Get investor bid term for specific investor-company combination."""
        return cls.INVESTOR_TERM_MAP[(investor_num, company_num)] 