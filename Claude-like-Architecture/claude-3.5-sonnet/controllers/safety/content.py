# controllers/safety/content.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from enum import Enum
from core.exceptions import SafetyError

class SafetyLevel(Enum):
    """Safety level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    STRICT = "strict"

class ContentType(Enum):
    """Content type enumeration."""
    TEXT = "text"
    CODE = "code"
    MARKDOWN = "markdown"
    HTML = "html"
    CUSTOM = "custom"

@dataclass
class SafetyCheck:
    """Individual safety check result."""
    name: str
    passed: bool
    issues: List[str]
    level: SafetyLevel
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class SafetyReport:
    """Comprehensive safety report."""
    checks: List[SafetyCheck]
    passed: bool
    issues: List[str]
    timestamp: datetime

class ContentSafety:
    """Handles content safety checks and filtering."""

    def __init__(self, default_level: SafetyLevel = SafetyLevel.MEDIUM):
        self.default_level = default_level
        self.safety_checks: Dict[str, callable] = {}
        self.safety_history: Dict[UUID, List[SafetyReport]] = {}
        self._initialize_checks()

    def check_safety(self,
                    content: Any,
                    content_id: UUID,
                    content_type: ContentType = ContentType.TEXT,
                    safety_level: Optional[SafetyLevel] = None) -> SafetyReport:
        """Check content safety."""
        try:
            # Validate UUID
            if not isinstance(content_id, UUID):
                raise SafetyError("Invalid content ID type")
                
            if not content:
                raise SafetyError("Content cannot be empty")
                
            if not isinstance(content_type, ContentType):
                raise SafetyError("Invalid content type")

            safety_level = safety_level or self.default_level
            if not isinstance(safety_level, SafetyLevel):
                raise SafetyError("Invalid safety level")

            # Run safety checks
            checks = []
            issues = []
            
            for name, check in self.safety_checks.items():
                try:
                    if not callable(check):
                        raise SafetyError(f"Invalid check function for {name}")
                        
                    result = check(content, content_type, safety_level)
                    if not isinstance(result, dict) or 'passed' not in result or 'issues' not in result:
                        raise SafetyError(f"Invalid check result format for {name}")
                        
                    checks.append(SafetyCheck(
                        name=name,
                        passed=result['passed'],
                        issues=result['issues'],
                        level=safety_level,
                        timestamp=datetime.now(),
                        metadata=result.get('metadata', {})
                    ))
                    if not result['passed']:
                        issues.extend(result['issues'])
                except Exception as e:
                    issues.append(f"Check {name} failed: {str(e)}")
                    checks.append(SafetyCheck(
                        name=name,
                        passed=False,
                        issues=[str(e)],
                        level=safety_level,
                        timestamp=datetime.now(),
                        metadata={}
                    ))

            # Create report
            report = SafetyReport(
                checks=checks,
                passed=len(issues) == 0,
                issues=issues,
                timestamp=datetime.now()
            )

            # Store history
            if content_id not in self.safety_history:
                self.safety_history[content_id] = []
            self.safety_history[content_id].append(report)

            return report

        except SafetyError:
            raise
        except Exception as e:
            raise SafetyError(f"Safety check failed: {str(e)}")

    def _initialize_checks(self) -> None:
        """Initialize safety checks."""
        self.safety_checks.update({
            'content_filter': self._check_content_filter,
            'code_safety': self._check_code_safety,
            'link_safety': self._check_link_safety,
            'xss_protection': self._check_xss_protection,
            'input_validation': self._check_input_validation
        })

    def _check_content_filter(self,
                            content: Any,
                            content_type: ContentType,
                            safety_level: SafetyLevel) -> Dict[str, Any]:
        """Check content against safety filters."""
        issues = []
        metadata = {}

        # Implement content filtering logic based on safety level
        if isinstance(content, str):
            # Check for prohibited content
            prohibited_patterns = self._get_prohibited_patterns(safety_level)
            for pattern, description in prohibited_patterns.items():
                if pattern.search(content):
                    issues.append(f"Prohibited content found: {description}")

        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'metadata': metadata
        }

    def _check_code_safety(self,
                          content: Any,
                          content_type: ContentType,
                          safety_level: SafetyLevel) -> Dict[str, Any]:
        """Check code safety."""
        issues = []
        metadata = {}

        if content_type == ContentType.CODE:
            # Check for dangerous imports/patterns
            dangerous_patterns = self._get_dangerous_code_patterns(safety_level)
            for pattern, description in dangerous_patterns.items():
                if pattern.search(str(content)):
                    issues.append(f"Potentially unsafe code pattern: {description}")

        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'metadata': metadata
        }

    def _check_link_safety(self,
                          content: Any,
                          content_type: ContentType,
                          safety_level: SafetyLevel) -> Dict[str, Any]:
        """Check link safety."""
        issues = []
        metadata = {}

        if isinstance(content, str):
            # Extract and check links
            import re
            links = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', content)
            
            for link in links:
                if not self._is_safe_link(link, safety_level):
                    issues.append(f"Potentially unsafe link: {link}")

        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'metadata': {'links_found': len(links) if 'links' in locals() else 0}
        }

    def _check_xss_protection(self,
                            content: Any,
                            content_type: ContentType,
                            safety_level: SafetyLevel) -> Dict[str, Any]:
        """Check for XSS vulnerabilities."""
        issues = []
        metadata = {}

        if content_type in [ContentType.HTML, ContentType.MARKDOWN]:
            # Check for potential XSS patterns
            xss_patterns = self._get_xss_patterns(safety_level)
            for pattern, description in xss_patterns.items():
                if pattern.search(str(content)):
                    issues.append(f"Potential XSS vulnerability: {description}")

        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'metadata': metadata
        }

    def _check_input_validation(self,
                              content: Any,
                              content_type: ContentType,
                              safety_level: SafetyLevel) -> Dict[str, Any]:
        """Check input validation."""
        issues = []
        metadata = {}

        # Implement input validation based on content type
        if content_type == ContentType.TEXT:
            if not self._validate_text_input(content, safety_level):
                issues.append("Invalid text input")
        elif content_type == ContentType.CODE:
            if not self._validate_code_input(content, safety_level):
                issues.append("Invalid code input")

        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'metadata': metadata
        }

    def _get_prohibited_patterns(self, safety_level: SafetyLevel) -> Dict[str, str]:
        """Get prohibited content patterns based on safety level."""
        import re
        patterns = {
            re.compile(r'malicious|harmful|dangerous', re.I): 
                "Potentially harmful content"
        }
        
        if safety_level in [SafetyLevel.HIGH, SafetyLevel.STRICT]:
            patterns.update({
                re.compile(r'hack|exploit|vulnerability', re.I): 
                    "Security-sensitive content"
            })
            
        return patterns

    def _get_dangerous_code_patterns(self, safety_level: SafetyLevel) -> Dict[str, str]:
        """Get dangerous code patterns based on safety level."""
        import re
        patterns = {
            re.compile(r'eval\s*\('): "Use of eval()",
            re.compile(r'exec\s*\('): "Use of exec()",
            re.compile(r'subprocess'): "Use of subprocess"
        }
        
        if safety_level == SafetyLevel.STRICT:
            patterns.update({
                re.compile(r'os\.'): "Direct OS operations",
                re.compile(r'sys\.'): "System operations"
            })
            
        return patterns

    def _get_xss_patterns(self, safety_level: SafetyLevel) -> Dict[str, str]:
        """Get XSS patterns based on safety level."""
        import re
        patterns = {
            re.compile(r'<script'): "Script tag",
            re.compile(r'javascript:'): "JavaScript protocol"
        }
        
        if safety_level in [SafetyLevel.HIGH, SafetyLevel.STRICT]:
            patterns.update({
                re.compile(r'on\w+\s*='): "Event handlers",
                re.compile(r'data:'): "Data URI"
            })
            
        return patterns

    def _validate_text_input(self,
                           content: str,
                           safety_level: SafetyLevel) -> bool:
        """Validate text input."""
        if not isinstance(content, str):
            return False
            
        # Add additional validation based on safety level
        if safety_level == SafetyLevel.STRICT:
            # Stricter validation rules
            pass
            
        return True

    def _validate_code_input(self,
                           content: str,
                           safety_level: SafetyLevel) -> bool:
        """Validate code input."""
        if not isinstance(content, str):
            return False
            
        # Add additional validation based on safety level
        if safety_level == SafetyLevel.STRICT:
            # Stricter validation rules
            pass
            
        return True

    def _is_safe_link(self,
                      link: str,
                      safety_level: SafetyLevel) -> bool:
        """Check if link is safe."""
        # Implement link safety checks
        # This could involve checking against allowlist/blocklist
        # or using external services
        return True  # Placeholder

    def add_safety_check(self,
                        name: str,
                        check_function: callable) -> None:
        """Add custom safety check."""
        if name in self.safety_checks:
            raise ValueError(f"Check {name} already exists")
            
        self.safety_checks[name] = check_function

    def remove_safety_check(self, name: str) -> bool:
        """Remove safety check."""
        return bool(self.safety_checks.pop(name, None))

    def get_safety_history(self,
                          content_id: UUID) -> List[SafetyReport]:
        """Get safety check history for content."""
        return self.safety_history.get(content_id, [])

    def clear_history(self,
                     content_id: Optional[UUID] = None) -> None:
        """Clear safety check history."""
        if content_id:
            self.safety_history.pop(content_id, None)
        else:
            self.safety_history.clear()