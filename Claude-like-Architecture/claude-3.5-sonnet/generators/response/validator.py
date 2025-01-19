# generators/response/validator.py
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import re
from core.exceptions import ValidationError

@dataclass
class ValidationConfig:
    """Configuration for response validation."""
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    required_fields: Optional[List[str]] = None
    prohibited_patterns: Optional[List[str]] = None
    content_filters: Optional[Dict[str, Any]] = None
    validation_level: str = "standard"  # strict, standard, or basic

@dataclass
class ValidationResult:
    """Result of response validation."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]
    timestamp: datetime

class ResponseValidator:
    """Validates response content and structure."""

    def __init__(self, config: Optional[ValidationConfig] = None):
        self.config = config or ValidationConfig()
        self.validators: Dict[str, callable] = {}
        self.content_filters: Dict[str, callable] = {}
        self.warning_patterns: List[str] = []
        self._initialize_validators()

    def validate_response(self, 
                         response: Any,
                         context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate response content."""
        errors = []
        warnings = []
        metadata = {}

        try:
            # Basic validation
            if not response:
                errors.append("Response cannot be empty")
                return self._create_result(errors, warnings, metadata)

            # Length validation
            if isinstance(response, str):
                length = len(response)
                if self.config.max_length and length > self.config.max_length:
                    errors.append(f"Response exceeds maximum length of {self.config.max_length}")
                if self.config.min_length and length < self.config.min_length:
                    errors.append(f"Response below minimum length of {self.config.min_length}")
                metadata['length'] = length

            # Content validation
            content_issues = self._validate_content(response)
            errors.extend(content_issues.get('errors', []))
            warnings.extend(content_issues.get('warnings', []))

            # Structure validation
            if self.config.required_fields:
                missing_fields = self._check_required_fields(response)
                errors.extend(missing_fields)

            # Pattern validation
            if self.config.prohibited_patterns:
                pattern_issues = self._check_patterns(response)
                errors.extend(pattern_issues)

            # Content filtering
            if self.config.content_filters:
                filter_issues = self._apply_content_filters(response)
                errors.extend(filter_issues.get('errors', []))
                warnings.extend(filter_issues.get('warnings', []))

            # Context-specific validation
            if context:
                context_issues = self._validate_context(response, context)
                errors.extend(context_issues.get('errors', []))
                warnings.extend(context_issues.get('warnings', []))

            # Additional validation based on level
            if self.config.validation_level == "strict":
                strict_issues = self._strict_validation(response)
                errors.extend(strict_issues.get('errors', []))
                warnings.extend(strict_issues.get('warnings', []))

            return self._create_result(errors, warnings, metadata)

        except Exception as e:
            raise ValidationError(f"Validation failed: {str(e)}")

    def _initialize_validators(self) -> None:
        """Initialize validation components."""
        # Content validators
        self.validators.update({
            'text': self._validate_text,
            'code': self._validate_code,
            'json': self._validate_json,
            'html': self._validate_html
        })

        # Content filters
        self.content_filters.update({
            'profanity': self._filter_profanity,
            'pii': self._filter_pii,
            'security': self._filter_security,
            'sentiment': self._filter_sentiment
        })

        # Warning patterns
        self.warning_patterns = [
            r'(?i)warning|caution|notice',
            r'(?i)todo|fixme|xxx',
            r'(?i)deprecated|obsolete'
        ]

    def _validate_content(self, response: Any) -> Dict[str, List[str]]:
        """Validate response content."""
        errors = []
        warnings = []

        # Determine content type and apply appropriate validator
        content_type = self._determine_content_type(response)
        validator = self.validators.get(content_type)
        
        if validator:
            result = validator(response)
            errors.extend(result.get('errors', []))
            warnings.extend(result.get('warnings', []))

        return {
            'errors': errors,
            'warnings': warnings
        }

    def _validate_text(self, text: str) -> Dict[str, List[str]]:
        """Validate text content."""
        errors = []
        warnings = []

        # Check for empty or whitespace content
        if not text.strip():
            errors.append("Text content is empty")
            return {'errors': errors, 'warnings': warnings}

        # Check for repeated characters/words
        if re.search(r'(.)\1{4,}', text):
            warnings.append("Contains excessive repeated characters")
        
        if re.search(r'\b(\w+)\s+\1\b', text, re.IGNORECASE):
            warnings.append("Contains repeated words")

        # Check for sentence structure
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            if sentence.strip() and not sentence[0].isupper():
                warnings.append("Sentence should start with capital letter")

        # Check for common issues
        if len(text.split()) < 3:
            warnings.append("Response might be too brief")
        
        if len(max(text.split(), key=len)) > 30:
            warnings.append("Contains very long words")

        return {
            'errors': errors,
            'warnings': warnings
        }

    def _validate_code(self, code: str) -> Dict[str, List[str]]:
        """Validate code content."""
        errors = []
        warnings = []

        # Check for basic syntax
        try:
            import ast
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Code syntax error: {str(e)}")
            return {'errors': errors, 'warnings': warnings}

        # Check for dangerous patterns
        dangerous_patterns = [
            (r'eval\s*\(', "Use of eval() detected"),
            (r'exec\s*\(', "Use of exec() detected"),
            (r'import\s+os', "Direct OS import detected"),
            (r'subprocess', "Subprocess usage detected")
        ]

        for pattern, message in dangerous_patterns:
            if re.search(pattern, code):
                errors.append(message)

        # Check for best practices
        if not any(line.strip().startswith('def ') for line in code.split('\n')):
            warnings.append("Consider breaking code into functions")

        if 'print(' in code:
            warnings.append("Consider using logging instead of print statements")

        return {
            'errors': errors,
            'warnings': warnings
        }

    def _validate_json(self, content: str) -> Dict[str, List[str]]:
        """Validate JSON content."""
        errors = []
        warnings = []

        try:
            import json
            parsed = json.loads(content)

            # Check structure
            if isinstance(parsed, dict):
                if not parsed:
                    warnings.append("Empty JSON object")
                else:
                    # Check for common fields
                    if 'id' in parsed and not isinstance(parsed['id'], (str, int)):
                        warnings.append("'id' field should be string or integer")
                    
                    if 'timestamp' in parsed:
                        try:
                            datetime.fromisoformat(parsed['timestamp'].replace('Z', '+00:00'))
                        except ValueError:
                            warnings.append("Invalid timestamp format")

            elif isinstance(parsed, list):
                if not parsed:
                    warnings.append("Empty JSON array")
                elif not all(isinstance(item, dict) for item in parsed):
                    warnings.append("Array items should be objects")

        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {str(e)}")

        return {
            'errors': errors,
            'warnings': warnings
        }

    def _validate_html(self, html: str) -> Dict[str, List[str]]:
        """Validate HTML content."""
        errors = []
        warnings = []

        try:
            from html.parser import HTMLParser

            class HTMLValidator(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.tags = []
                    self.errors = []
                    self.warnings = []

                def handle_starttag(self, tag, attrs):
                    self.tags.append(tag)
                    # Check for accessibility
                    if tag in ['img', 'area']:
                        if not any(attr[0] == 'alt' for attr in attrs):
                            self.warnings.append(f"{tag} tag missing alt attribute")
                    elif tag == 'a':
                        if not any(attr[0] == 'href' for attr in attrs):
                            self.warnings.append("Anchor tag missing href attribute")

                def handle_endtag(self, tag):
                    if not self.tags or self.tags[-1] != tag:
                        self.errors.append(f"Mismatched tag: {tag}")
                    else:
                        self.tags.pop()

            validator = HTMLValidator()
            validator.feed(html)

            if validator.tags:
                errors.append(f"Unclosed tags: {', '.join(validator.tags)}")
            
            errors.extend(validator.errors)
            warnings.extend(validator.warnings)

            # Check for script tags
            if '<script' in html:
                errors.append("Script tags are not allowed")

            # Check for inline styles
            if 'style="' in html:
                warnings.append("Consider using CSS classes instead of inline styles")

        except Exception as e:
            errors.append(f"HTML validation failed: {str(e)}")

        return {
            'errors': errors,
            'warnings': warnings
        }

    def _determine_content_type(self, response: Any) -> str:
        """Determine content type of response."""
        if isinstance(response, str):
            if response.strip().startswith('{') or response.strip().startswith('['):
                return 'json'
            elif response.strip().startswith('<'):
                return 'html'
            elif any(keyword in response for keyword in ['def ', 'class ', 'import ']):
                return 'code'
            return 'text'
        return 'unknown'

    def _check_required_fields(self, response: Any) -> List[str]:
        """Check for required fields in response."""
        missing_fields = []
        
        if isinstance(response, dict):
            for field in self.config.required_fields or []:
                if field not in response:
                    missing_fields.append(f"Missing required field: {field}")
                    
        return missing_fields

    def _check_patterns(self, response: str) -> List[str]:
        """Check for prohibited patterns in response."""
        issues = []
        
        for pattern in self.config.prohibited_patterns or []:
            if re.search(pattern, str(response), re.IGNORECASE):
                issues.append(f"Contains prohibited pattern: {pattern}")
                
        return issues

    def _apply_content_filters(self, response: Any) -> Dict[str, List[str]]:
        """Apply content filters to response."""
        errors = []
        warnings = []

        for filter_name, filter_config in (self.config.content_filters or {}).items():
            filter_func = self.content_filters.get(filter_name)
            if filter_func:
                result = filter_func(response, filter_config)
                errors.extend(result.get('errors', []))
                warnings.extend(result.get('warnings', []))

        return {
            'errors': errors,
            'warnings': warnings
        }

    def _filter_profanity(self, content: str, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Filter profanity from content."""
        errors = []
        warnings = []
        
        profanity_patterns = config.get('patterns', [])
        for pattern in profanity_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                errors.append("Contains inappropriate language")
                break
                
        return {'errors': errors, 'warnings': warnings}

    def _filter_pii(self, content: str, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Filter personally identifiable information."""
        errors = []
        warnings = []
        
        pii_patterns = {
            r'\b\d{3}-\d{2}-\d{4}\b': "Possible SSN detected",
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b': "Email address detected",
            r'\b\d{16}\b': "Possible credit card number detected"
        }
        
        for pattern, message in pii_patterns.items():
            if re.search(pattern, content):
                errors.append(message)
                
        return {'errors': errors, 'warnings': warnings}

    def _filter_security(self, content: str, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Filter security-sensitive content."""
        errors = []
        warnings = []
        
        security_patterns = {
            r'password\s*=': "Possible password in content",
            r'api[_-]key\s*=': "Possible API key in content",
            r'secret[_-]key\s*=': "Possible secret key in content"
        }
        
        for pattern, message in security_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                errors.append(message)
                
        return {'errors': errors, 'warnings': warnings}

    def _filter_sentiment(self, content: str, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Filter based on sentiment analysis."""
        warnings = []
        
        # Simple sentiment analysis based on keywords
        negative_patterns = [
            r'(?i)hate|awful|terrible|worst',
            r'(?i)stupid|idiot|dumb',
            r'(?i)never|nothing|none'
        ]
        
        for pattern in negative_patterns:
            if re.search(pattern, content):
                warnings.append("Contains potentially negative sentiment")
                break
                
        return {'errors': [], 'warnings': warnings}

    def _validate_context(self, response: Any, context: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate response against context."""
        errors = []
        warnings = []

        # Check response relevance
        if 'topic' in context and isinstance(response, str):
            if context['topic'].lower() not in response.lower():
                warnings.append("Response may not be relevant to the topic")

        # Check response format
        if 'format' in context:
            if not self._validate_format(response, context['format']):
                errors.append(f"Response does not match required format: {context['format']}")

        # Check response complexity
        if 'complexity' in context:
            complexity_issues = self._check_complexity(response, context['complexity'])
            warnings.extend(complexity_issues)

        return {
            'errors': errors,
            'warnings': warnings
        }

    def _validate_format(self, response: Any, required_format: str) -> bool:
        """Validate response format."""
        try:
            if required_format == 'json':
            # generators/response/validator.py (continued)
                import json
                json.loads(str(response))
                return True
            elif required_format == 'list':
                return isinstance(response, (list, tuple))
            elif required_format == 'dict':
                return isinstance(response, dict)
            elif required_format == 'number':
                return isinstance(response, (int, float))
            elif required_format == 'boolean':
                return isinstance(response, bool)
            return True
        except Exception:
            return False

    def _check_complexity(self, response: str, target_complexity: str) -> List[str]:
        """Check response complexity level."""
        warnings = []
        
        if isinstance(response, str):
            # Calculate average word length
            words = response.split()
            if not words:
                return ["Response too short to assess complexity"]
                
            avg_word_length = sum(len(word) for word in words) / len(words)
            
            # Calculate average sentence length
            sentences = [s.strip() for s in re.split(r'[.!?]+', response) if s.strip()]
            if not sentences:
                return ["Response lacks proper sentence structure"]
                
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            
            # Assess complexity
            if target_complexity == 'simple':
                if avg_word_length > 5:
                    warnings.append("Word length suggests response may be too complex")
                if avg_sentence_length > 15:
                    warnings.append("Sentence length suggests response may be too complex")
                    
            elif target_complexity == 'technical':
                if avg_word_length < 4:
                    warnings.append("Word length suggests response may be too simple")
                if avg_sentence_length < 10:
                    warnings.append("Sentence length suggests response may be too simple")

        return warnings

    def _strict_validation(self, response: Any) -> Dict[str, List[str]]:
        """Perform strict validation checks."""
        errors = []
        warnings = []

        if isinstance(response, str):
            # Check for proper capitalization
            sentences = re.split(r'[.!?]+\s+', response)
            for sentence in sentences:
                if sentence and not sentence[0].isupper():
                    errors.append("All sentences must start with capital letter")

            # Check for proper punctuation
            if not re.search(r'[.!?]$', response.strip()):
                errors.append("Response must end with proper punctuation")

            # Check for formatting consistency
            if re.search(r'\s{2,}', response):
                errors.append("Multiple consecutive spaces not allowed")

            # Check for parentheses/bracket matching
            if not self._check_balanced_pairs(response):
                errors.append("Unmatched parentheses or brackets")

            # Check for list consistency
            list_items = re.findall(r'^\s*[-*•]\s+.*$', response, re.MULTILINE)
            if list_items:
                first_marker = re.match(r'^\s*([-*•])', list_items[0]).group(1)
                for item in list_items:
                    if not item.lstrip().startswith(first_marker):
                        errors.append("Inconsistent list markers")
                        break

        elif isinstance(response, (list, tuple)):
            # Check for type consistency
            if response:
                first_type = type(response[0])
                if not all(isinstance(item, first_type) for item in response):
                    errors.append("List items must be of consistent type")

        elif isinstance(response, dict):
            # Check key naming consistency
            keys = list(response.keys())
            if keys:
                if any(key.islower() for key in keys) and any(key.isupper() for key in keys):
                    errors.append("Inconsistent key casing")
                if any('_' in key for key in keys) and any('-' in key for key in keys):
                    errors.append("Inconsistent key separator style")

        return {
            'errors': errors,
            'warnings': warnings
        }

    def _check_balanced_pairs(self, text: str) -> bool:
        """Check for balanced parentheses and brackets."""
        stack = []
        pairs = {')': '(', ']': '[', '}': '{'}
        
        for char in text:
            if char in '({[':
                stack.append(char)
            elif char in ')}]':
                if not stack or stack.pop() != pairs[char]:
                    return False
                    
        return len(stack) == 0

    def _create_result(self, 
                        errors: List[str], 
                        warnings: List[str], 
                        metadata: Dict[str, Any]) -> ValidationResult:
        """Create validation result."""
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata=metadata,
            timestamp=datetime.now()
        )

    def add_validator(self, content_type: str, validator: callable) -> None:
        """Add custom content validator."""
        if content_type in self.validators:
            raise ValueError(f"Validator for {content_type} already exists")
        self.validators[content_type] = validator

    def add_content_filter(self, filter_name: str, filter_func: callable) -> None:
        """Add custom content filter."""
        if filter_name in self.content_filters:
            raise ValueError(f"Filter {filter_name} already exists")
        self.content_filters[filter_name] = filter_func

    def add_warning_pattern(self, pattern: str) -> None:
        """Add custom warning pattern."""
        if pattern not in self.warning_patterns:
            self.warning_patterns.append(pattern)

    def get_validators(self) -> List[str]:
        """Get list of registered validators."""
        return list(self.validators.keys())

    def get_content_filters(self) -> List[str]:
        """Get list of registered content filters."""
        return list(self.content_filters.keys())

    def get_warning_patterns(self) -> List[str]:
        """Get list of warning patterns."""
        return self.warning_patterns.copy()