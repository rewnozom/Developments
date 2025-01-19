# controllers/safety/validation.py
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from enum import Enum
from core.exceptions import ValidationError

class ValidationType(Enum):
    """Types of safety validation."""
    INPUT = "input"
    OUTPUT = "output"
    SYSTEM = "system"
    CUSTOM = "custom"

@dataclass
class ValidationRule:
    """Safety validation rule."""
    name: str
    type: ValidationType
    validator: callable
    enabled: bool = True
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ValidationResult:
    """Result of safety validation."""
    rule_name: str
    passed: bool
    issues: List[str]
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class SafetyValidator:
    """Handles safety validation and verification."""

    def __init__(self):
        self.validation_rules: Dict[str, ValidationRule] = {}
        self.validation_history: Dict[UUID, List[ValidationResult]] = {}
        self._initialize_validators()

    def validate_safety(self,
                    content: Any,
                    content_id: UUID,
                    validation_type: Optional[ValidationType] = None,
                    rules: Optional[List[str]] = None) -> List[ValidationResult]:
        """Validate content safety."""
        try:
            # Validate UUID
            if not isinstance(content_id, UUID):
                raise ValidationError("Invalid content ID type")
                
            if not content:
                raise ValidationError("Content cannot be empty")
                
            if validation_type is not None and not isinstance(validation_type, ValidationType):
                raise ValidationError("Invalid validation type")

            results = []
            
            # Determine which rules to apply
            rules_to_apply = self._get_applicable_rules(validation_type, rules)
            
            if not rules_to_apply:
                raise ValidationError("No applicable validation rules found")

            # Apply validation rules
            for rule in rules_to_apply:
                try:
                    if not callable(rule.validator):
                        raise ValidationError(f"Invalid validator function for {rule.name}")
                        
                    validation = rule.validator(content)
                    if not isinstance(validation, dict) or 'passed' not in validation:
                        raise ValidationError(f"Invalid validation result format for {rule.name}")
                        
                    result = ValidationResult(
                        rule_name=rule.name,
                        passed=validation['passed'],
                        issues=validation.get('issues', []),
                        timestamp=datetime.now(),
                        metadata=validation.get('metadata')
                    )
                    results.append(result)
                except Exception as e:
                    results.append(ValidationResult(
                        rule_name=rule.name,
                        passed=False,
                        issues=[str(e)],
                        timestamp=datetime.now(),
                        metadata={'error': 'validation_failed'}
                    ))

            # Store results
            if content_id not in self.validation_history:
                self.validation_history[content_id] = []
            self.validation_history[content_id].extend(results)

            return results

        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Safety validation failed: {str(e)}")

    def _initialize_validators(self) -> None:
        """Initialize validation rules."""
        # Input validation rules
        self.validation_rules.update({
            'input_sanitization': ValidationRule(
                name='input_sanitization',
                type=ValidationType.INPUT,
                validator=self._validate_input_sanitization
            ),
            'input_size': ValidationRule(
                name='input_size',
                type=ValidationType.INPUT,
                validator=self._validate_input_size
            )
        })

        # Output validation rules
        self.validation_rules.update({
            'output_safety': ValidationRule(
                name='output_safety',
                type=ValidationType.OUTPUT,
                validator=self._validate_output_safety
            ),
            'output_formatting': ValidationRule(
                name='output_formatting',
                type=ValidationType.OUTPUT,
                validator=self._validate_output_formatting
            )
        })

        # System validation rules
        self.validation_rules.update({
            'system_state': ValidationRule(
                name='system_state',
                type=ValidationType.SYSTEM,
                validator=self._validate_system_state
            ),
            'resource_usage': ValidationRule(
                name='resource_usage',
                type=ValidationType.SYSTEM,
                validator=self._validate_resource_usage
            )
        })

    def _get_applicable_rules(self,
                            validation_type: Optional[ValidationType],
                            rule_names: Optional[List[str]]) -> List[ValidationRule]:
        """Get applicable validation rules."""
        rules = []
        
        for name, rule in self.validation_rules.items():
            if not rule.enabled:
                continue
                
            if rule_names and name not in rule_names:
                continue
                
            if validation_type and rule.type != validation_type:
                continue
                
            rules.append(rule)
            
        return rules

    def _validate_input_sanitization(self, content: Any) -> Dict[str, Any]:
        """Validate input sanitization."""
        issues = []
        metadata = {}

        if isinstance(content, str):
            # Check for potentially dangerous patterns
            import re
            dangerous_patterns = [
                (r'<script', 'Script tags not allowed'),
                (r'javascript:', 'JavaScript protocol not allowed'),
                (r'data:', 'Data URI not allowed')
            ]
            
            for pattern, message in dangerous_patterns:
                if re.search(pattern, content, re.I):
                    issues.append(message)

        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'metadata': metadata
        }

    def _validate_input_size(self, content: Any) -> Dict[str, Any]:
        """Validate input size."""
        issues = []
        metadata = {'size': 0}

        if isinstance(content, str):
            size = len(content)
            metadata['size'] = size
            
            if size > 1000000:  # 1MB
                issues.append("Input size exceeds maximum limit")

        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'metadata': metadata
        }

    def _validate_output_safety(self, content: Any) -> Dict[str, Any]:
        """Validate output safety."""
        issues = []
        metadata = {}

        if isinstance(content, str):
            # Check for sensitive data patterns
            import re
            sensitive_patterns = [
                (r'\b\d{16}\b', 'Possible credit card number'),
                (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'Possible email address'),
                (r'\b\d{3}-\d{2}-\d{4}\b', 'Possible SSN')
            ]
            
            for pattern, message in sensitive_patterns:
                if re.search(pattern, content):
                    issues.append(message)

        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'metadata': metadata
        }

    def _validate_output_formatting(self, content: Any) -> Dict[str, Any]:
        """Validate output formatting."""
        issues = []
        metadata = {}

        if isinstance(content, str):
            # Check for proper formatting
            if '\x00' in content:
                issues.append("Output contains null bytes")
                
            if not content.isprintable():
                issues.append("Output contains non-printable characters")

        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'metadata': metadata
        }

    def _validate_system_state(self, content: Any) -> Dict[str, Any]:
       """Validate system state."""
       issues = []
       metadata = {}

       try:
           import psutil
           import os

           # Check system metrics
           cpu_percent = psutil.cpu_percent()
           memory_percent = psutil.virtual_memory().percent
           disk_percent = psutil.disk_usage('/').percent

           metadata.update({
               'cpu_percent': cpu_percent,
               'memory_percent': memory_percent,
               'disk_percent': disk_percent
           })

           # Check for concerning system states
           if cpu_percent > 90:
               issues.append("High CPU usage detected")
           if memory_percent > 90:
               issues.append("High memory usage detected")
           if disk_percent > 90:
               issues.append("Low disk space detected")

       except Exception as e:
           issues.append(f"System state check failed: {str(e)}")

       return {
           'passed': len(issues) == 0,
           'issues': issues,
           'metadata': metadata
       }

    def _validate_resource_usage(self, content: Any) -> Dict[str, Any]:
        """Validate resource usage."""
        issues = []
        metadata = {}

        try:
            # Check memory usage of content
            import sys
            content_size = sys.getsizeof(content)
            metadata['content_size'] = content_size

            # Set thresholds based on content type
            max_size = 1024 * 1024  # 1MB default
            if isinstance(content, str):
                max_size = 5 * 1024 * 1024  # 5MB for strings
            elif isinstance(content, (list, dict)):
                max_size = 10 * 1024 * 1024  # 10MB for collections

            if content_size > max_size:
                issues.append(f"Content size {content_size} exceeds maximum {max_size}")

        except Exception as e:
            issues.append(f"Resource usage check failed: {str(e)}")

        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'metadata': metadata
        }

    def add_validation_rule(self,
                            name: str,
                            rule_type: ValidationType,
                            validator: callable,
                            metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add custom validation rule."""
        if name in self.validation_rules:
            raise ValueError(f"Validation rule {name} already exists")

        self.validation_rules[name] = ValidationRule(
            name=name,
            type=rule_type,
            validator=validator,
            metadata=metadata
        )

    def remove_validation_rule(self, name: str) -> bool:
        """Remove validation rule."""
        return bool(self.validation_rules.pop(name, None))

    def enable_validation_rule(self, name: str) -> bool:
        """Enable validation rule."""
        if name not in self.validation_rules:
            return False
            
        self.validation_rules[name].enabled = True
        return True

    def disable_validation_rule(self, name: str) -> bool:
        """Disable validation rule."""
        if name not in self.validation_rules:
            return False
            
        self.validation_rules[name].enabled = False
        return True

    def get_validation_history(self,
                                content_id: UUID) -> List[ValidationResult]:
        """Get validation history for content."""
        return self.validation_history.get(content_id, [])

    def clear_history(self,
                        content_id: Optional[UUID] = None) -> None:
        """Clear validation history."""
        if content_id:
            self.validation_history.pop(content_id, None)
        else:
            self.validation_history.clear()

    def get_enabled_rules(self,
                            validation_type: Optional[ValidationType] = None) -> List[ValidationRule]:
        """Get enabled validation rules."""
        rules = [rule for rule in self.validation_rules.values() 
                if rule.enabled]
        
        if validation_type:
            rules = [rule for rule in rules 
                    if rule.type == validation_type]
            
        return rules

    def get_rule_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Get validation rule metadata."""
        if name not in self.validation_rules:
            return None
            
        return self.validation_rules[name].metadata

    def update_rule_metadata(self,
                            name: str,
                            metadata: Dict[str, Any]) -> bool:
        """Update validation rule metadata."""
        if name not in self.validation_rules:
            return False
            
        if self.validation_rules[name].metadata is None:
            self.validation_rules[name].metadata = {}
            
        self.validation_rules[name].metadata.update(metadata)
        return True