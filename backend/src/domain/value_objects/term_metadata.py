from dataclasses import dataclass
from typing import Optional, List, Tuple
from decimal import Decimal
from enum import Enum

class TermDataType(Enum):
    """Data type classification for term values."""
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    INTEGER = "integer"
    DECIMAL = "decimal"
    DAYS = "days"
    TEXT = "text"

class RuleCondition(Enum):
    """Type-safe rule condition enum."""
    ABOVE = "above"
    BELOW = "below"
    EQUALS = "equals"

@dataclass(frozen=True)
class BusinessRule:
    """Business rule definition for term classification."""
    name: str
    min_value: Decimal
    max_value: Decimal
    description: str

@dataclass(frozen=True)
class ContextualRule:
    """Contextual validation rule for specific threshold warnings."""
    threshold: Decimal
    condition: RuleCondition
    message: str
    code: str
    severity: str = "warning"  # warning, info
    
    def applies_to(self, value: Decimal) -> bool:
        """Check if this rule applies to the given value."""
        if self.condition == RuleCondition.ABOVE:
            return value > self.threshold
        elif self.condition == RuleCondition.BELOW:
            return value < self.threshold
        elif self.condition == RuleCondition.EQUALS:
            return value == self.threshold
        return False

@dataclass(frozen=True)
class TermMetadata:
    """The 'master object' for a term. Holds everything we need to know about it: its name, validation rules, how to display it, etc."""
    
    key: str
    display_name: str
    description: str
    data_type: TermDataType
    unit: str
    min_value: Decimal
    max_value: Decimal
    precision: int
    business_rules: List[BusinessRule]
    contextual_rules: List[ContextualRule]
    help_text: Optional[str] = None
    is_required: bool = True
    
    def format_value(self, value: Decimal) -> str:
        """Format value according to term's display requirements."""
        if self.data_type == TermDataType.CURRENCY:
            return f"£{value:,.{self.precision}f}"
        elif self.data_type == TermDataType.PERCENTAGE:
            return f"{value:.{self.precision}f}%"
        elif self.data_type == TermDataType.DAYS:
            return f"{value:.0f} days"
        elif self.data_type == TermDataType.TEXT:
            return str(value)
        else:
            return f"{value:.{self.precision}f}"
    
    def get_range_description(self) -> str:
        """Creates the '100 - 500' string for the UI."""
        min_formatted = self.format_value(self.min_value)
        max_formatted = self.format_value(self.max_value)
        return f"{min_formatted} - {max_formatted}"
    
    def get_business_context(self, value: Decimal) -> Optional[str]:
        """Get business context label for the given value."""
        for rule in self.business_rules:
            if rule.min_value <= value <= rule.max_value:
                return rule.name.replace("_", " ").title()
        return "Outside typical ranges"
    
    def get_applicable_contextual_rules(self, value: Decimal) -> List[ContextualRule]:
        """Finds all the specific warnings that should be shown for this value."""
        return [rule for rule in self.contextual_rules if rule.applies_to(value)] 