# services/validation.py
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ValidationLevel(Enum):
    """Validation level enumeration."""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    CUSTOM = "custom"

@dataclass
class ValidationRule:
    """Represents a validation rule."""
    name: str
    description: str
    validator: callable
    level: ValidationLevel
    parameters: Dict[str, Any]

@dataclass
class ValidationResult:
    """Result of validation operation."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]
    timestamp: datetime

class ValidationService:
    """Service for content and data validation."""

    def __init__(self, default_level: ValidationLevel = ValidationLevel.STANDARD):
        self.default_level = default_level
        self.rules: Dict[str, ValidationRule] = {}
        self.validation_history: List[ValidationResult] = []
        self._initialize_default_rules()

    def validate(self, 
                content: Any, 
                level: Optional[ValidationLevel] = None,
                custom_rules: Optional[List[ValidationRule]] = None) -> ValidationResult:
        """Validate content using specified rules."""
        level = level or self.default_level
        errors = []
        warnings = []
        
        # Apply standard rules
        rules = self._get_rules_for_level(level)
        if custom_rules:
            rules.extend(custom_rules)

        for rule in rules:
            try:
                if not rule.validator(content, **rule.parameters):
                    errors.append(f"Validation failed for rule: {rule.name}")
            except Exception as e:
                warnings.append(f"Error applying rule {rule.name}: {str(e)}")

        result = ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={"level": level.value},
            timestamp=datetime.now()
        )
        
        self.validation_history.append(result)
        return result

    def add_rule(self, rule: ValidationRule) -> None:
        """Add a new validation rule."""
        if rule.name in self.rules:
            raise ValueError(f"Rule {rule.name} already exists")
        self.rules[rule.name] = rule

    def remove_rule(self, rule_name: str) -> bool:
        """Remove a validation rule."""
        return bool(self.rules.pop(rule_name, None))

    def get_validation_history(self) -> List[ValidationResult]:
        """Get validation history."""
        return self.validation_history

    def _initialize_default_rules(self) -> None:
        """Initialize default validation rules."""
        # Content presence check
        self.add_rule(ValidationRule(
            name="content_presence",
            description="Checks if content is not empty",
            validator=lambda x, **kwargs: bool(x),
            level=ValidationLevel.BASIC,
            parameters={}
        ))

        # Type check
        self.add_rule(ValidationRule(
            name="type_check",
            description="Checks content type",
            validator=lambda x, type_name, **kwargs: isinstance(x, type_name),
            level=ValidationLevel.BASIC,
            parameters={"type_name": object}
        ))

    def _get_rules_for_level(self, level: ValidationLevel) -> List[ValidationRule]:
        """Get validation rules for specified level."""
        return [rule for rule in self.rules.values() if rule.level.value <= level.value]

    def create_custom_validation(self, 
                               rules: List[ValidationRule]) -> callable:
        """Create custom validation function from rules."""
        def custom_validator(content: Any) -> ValidationResult:
            return self.validate(content, 
                               level=ValidationLevel.CUSTOM,
                               custom_rules=rules)
        return custom_validator