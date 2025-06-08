from typing import List
from decimal import Decimal
from ..value_objects.term_key import TermKey
from ..value_objects.term_metadata import TermMetadata
from ..value_objects.validation_error import ValidationError
from .game_configuration import GameConfiguration

class TermValidationService:
    """The main validator for any term. It's stateless and gets all its rules from GameConfiguration. Give it a term and a value, it gives you back a list of problems."""
    
    @staticmethod
    def validate_term_value(term_key: TermKey, value: Decimal) -> List[ValidationError]:
        """Validate term value using metadata from GameConfiguration."""
        try:
            metadata = GameConfiguration.get_term_metadata(term_key)
        except ValueError as e:
            return [ValidationError(
                field=term_key.value,
                message=str(e),
                value=value,
                code="UNKNOWN_TERM"
            )]
        
        errors = []
        
        errors.extend(TermValidationService._validate_range(value, metadata))
        
        errors.extend(TermValidationService._validate_precision(value, metadata))
        
        errors.extend(TermValidationService._validate_business_classification(value, metadata))
        
        errors.extend(TermValidationService._validate_contextual_rules(value, metadata))
        
        return errors
    
    @staticmethod
    def _validate_range(value: Decimal, metadata: TermMetadata) -> List[ValidationError]:
        """Checks if the value is between the hard min/max limits."""
        errors = []
        
        if value < metadata.min_value:
            errors.append(ValidationError(
                field=metadata.key,
                message=f"{metadata.display_name} must be at least {metadata.format_value(metadata.min_value)}. Current: {metadata.format_value(value)}",
                value=value,
                code="BELOW_MINIMUM"
            ))
        
        if value > metadata.max_value:
            errors.append(ValidationError(
                field=metadata.key,
                message=f"{metadata.display_name} cannot exceed {metadata.format_value(metadata.max_value)}. Current: {metadata.format_value(value)}",
                value=value,
                code="ABOVE_MAXIMUM"
            ))
        
        return errors
    
    @staticmethod
    def _validate_precision(value: Decimal, metadata: TermMetadata) -> List[ValidationError]:
        """Validate decimal precision using metadata."""
        errors = []
        
        if value.as_tuple().exponent < -metadata.precision:
            errors.append(ValidationError(
                field=metadata.key,
                message=f"{metadata.display_name} precision limited to {metadata.precision} decimal places",
                value=value,
                code="EXCESS_PRECISION"
            ))
        
        return errors
    
    @staticmethod
    def _validate_business_classification(value: Decimal, metadata: TermMetadata) -> List[ValidationError]:
        """Provide business classification info based on business rules."""
        errors = []
        
        matching_rules = [
            rule for rule in metadata.business_rules 
            if rule.min_value <= value <= rule.max_value
        ]
        
        if matching_rules:
            best_match = matching_rules[0]
            errors.append(ValidationError(
                field=metadata.key,
                message=f"{metadata.display_name}: {best_match.description}",
                value=value,
                code="BUSINESS_CLASSIFICATION",
                severity="info"
            ))
        elif metadata.business_rules:
            errors.append(ValidationError(
                field=metadata.key,
                message=f"{metadata.display_name} of {metadata.format_value(value)} is outside typical business ranges",
                value=value,
                code="OUTSIDE_BUSINESS_RANGE",
                severity="warning"
            ))
        
        return errors
    
    @staticmethod
    def _validate_contextual_rules(value: Decimal, metadata: TermMetadata) -> List[ValidationError]:
        """Applies the specific 'if value > 100M, then show this warning' type of rules."""
        errors = []
        
        applicable_rules = metadata.get_applicable_contextual_rules(value)
        
        for rule in applicable_rules:
            errors.append(ValidationError(
                field=metadata.key,
                message=rule.message,
                value=value,
                code=rule.code,
                severity=rule.severity
            ))
        
        return errors 