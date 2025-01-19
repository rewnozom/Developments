# generators/response/builder.py

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
import re
import ast
from models.conversation import Message
from models.response import Response, ResponseType, ResponseMetadata
from core.exceptions import ResponseGenerationError

@dataclass
class ResponseConfig:
    """Configuration for response generation."""
    response_type: ResponseType
    max_length: Optional[int] = None
    style_guide: Optional[Dict[str, Any]] = None
    formatting_rules: Optional[Dict[str, Any]] = None
    include_metadata: bool = True
    validation_rules: Optional[Dict[str, Any]] = None
    maintain_context: bool = True
    enable_citations: bool = False
    custom_settings: Optional[Dict[str, Any]] = None
    help_url: Optional[str] = None

class ResponseBuilder:
    """Builds and formats responses."""

    def __init__(self, config: Optional[ResponseConfig] = None):
        self.config = config or ResponseConfig(response_type=ResponseType.TEXT)
        self.formatters: Dict[ResponseType, callable] = {}
        self.validators: Dict[ResponseType, callable] = {}
        self.pre_processors: Dict[str, callable] = {}
        self.post_processors: Dict[str, callable] = {}
        self.enhancers: Dict[ResponseType, callable] = {}
        self._initialize_processors()

    def build_response(self,
                      content: str,
                      response_type: Optional[ResponseType] = None,
                      context: Optional[Dict[str, Any]] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> Response:
        """Build a formatted response."""
        try:
            response_type = response_type or self.config.response_type

            # Pre-process content
            processed_content = self._pre_process_content(content, response_type)

            # Format content
            formatted_content = self._format_content(processed_content, response_type)

            # Validate content
            validation_result = self._validate_content(formatted_content, response_type)
            if not validation_result['valid']:
                raise ResponseGenerationError(
                    f"Response validation failed: {', '.join(validation_result['errors'])}"
                )

            # Enhance content
            enhanced_content = self._enhance_content(formatted_content, response_type)

            # Post-process content
            final_content = self._post_process_content(enhanced_content, response_type)

            # Truncate content if necessary
            if self.config.max_length:
                final_content = self._truncate_content(final_content, self.config.max_length)

            # Create response metadata
            response_metadata = ResponseMetadata(
                timestamp=datetime.now(),
                type=response_type,
                length=len(final_content),
                context=context or {},
                custom_data=metadata or {}
            ) if self.config.include_metadata else None

            # Create response
            response = Response(
                content=final_content,
                type=response_type,
                metadata=response_metadata
            )

            return response

        except Exception as e:
            raise ResponseGenerationError(f"Response building failed: {str(e)}")

    def _initialize_processors(self) -> None:
        """Initialize response processors."""
        # Pre-processors
        self.pre_processors.update({
            'text': self._pre_process_text,
            'code': self._pre_process_code,
            'error': self._pre_process_error
        })

        # Formatters
        self.formatters.update({
            ResponseType.TEXT: self._format_text,
            ResponseType.HTML: self._format_html,
            ResponseType.MARKDOWN: self._format_markdown,
            ResponseType.CODE: self._format_code,
            ResponseType.ERROR: self._format_error
        })

        # Validators
        self.validators.update({
            ResponseType.TEXT: self._validate_text,
            ResponseType.HTML: self._validate_html,
            ResponseType.MARKDOWN: self._validate_markdown,
            ResponseType.CODE: self._validate_code,
            ResponseType.ERROR: self._validate_error
        })

        # Enhancers
        self.enhancers.update({
            ResponseType.TEXT: self._enhance_text,
            ResponseType.HTML: self._enhance_html,
            ResponseType.MARKDOWN: self._enhance_markdown,
            ResponseType.CODE: self._enhance_code,
            ResponseType.ERROR: self._enhance_error
        })

        # Post-processors
        self.post_processors.update({
            'text': self._post_process_text,
            'code': self._post_process_code,
            'error': self._post_process_error
        })

    def _pre_process_content(self, content: str, response_type: ResponseType) -> str:
        """Pre-process response content."""
        processor = self.pre_processors.get(response_type.value)
        if not processor:
            return content
        return processor(content)

    def _format_content(self, content: str, response_type: ResponseType) -> str:
        """Format response content."""
        formatter = self.formatters.get(response_type)
        if not formatter:
            return content
        return formatter(content)

    def _validate_content(self, content: str, response_type: ResponseType) -> Dict[str, Any]:
        """Validate response content."""
        validator = self.validators.get(response_type)
        if not validator:
            return {'valid': True, 'errors': [], 'warnings': []}
        return validator(content)

    def _enhance_content(self, content: str, response_type: ResponseType) -> str:
        """Enhance response content."""
        enhancer = self.enhancers.get(response_type)
        if not enhancer:
            return content
        return enhancer(content)

    def _post_process_content(self, content: str, response_type: ResponseType) -> str:
        """Post-process response content."""
        processor = self.post_processors.get(response_type.value)
        if not processor:
            return content
        return processor(content)

    # =====================
    # Pre-processors
    # =====================

    def _pre_process_text(self, content: str) -> str:
        """Pre-process text response."""
        # Clean up whitespace
        content = content.strip()
        content = re.sub(r'\s+', ' ', content)

        # Handle quotes
        content = re.sub(r'(?<!["\']):(\w+):', r'"\1"', content)

        # Add spacing around punctuation
        content = re.sub(r'([.,!?])(\w)', r'\1 \2', content)

        return content

    def _pre_process_code(self, content: str) -> str:
        """Pre-process code response."""
        # Remove trailing whitespace
        lines = [line.rstrip() for line in content.split('\n')]

        # Normalize empty lines
        content = '\n'.join(lines)
        content = re.sub(r'\n{3,}', '\n\n', content)

        # Remove shebang if present
        if content.startswith('#!'):
            content = re.sub(r'^#!.*\n', '', content)

        return content

    def _pre_process_error(self, content: str) -> str:
        """Pre-process error response."""
        # Format error message
        if not content.lower().startswith('error'):
            content = f"Error: {content}"

        # Add timestamp
        content = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {content}"

        return content

    # =====================
    # Formatters
    # =====================

    def _format_text(self, content: str) -> str:
        """Format text response."""
        # Basic text formatting
        content = content.strip()

        # Apply formatting rules
        if self.config.formatting_rules:
            if self.config.formatting_rules.get('capitalize_sentences', False):
                content = '. '.join(s.capitalize() for s in content.split('. '))

            if self.config.formatting_rules.get('wrap_paragraphs', False):
                paragraphs = content.split('\n\n')
                wrapped_paragraphs = []
                for para in paragraphs:
                    if len(para) > 80:
                        words = para.split()
                        lines = []
                        current_line = []
                        current_length = 0
                        for word in words:
                            if current_length + len(word) + 1 <= 80:
                                current_line.append(word)
                                current_length += len(word) + 1
                            else:
                                lines.append(' '.join(current_line))
                                current_line = [word]
                                current_length = len(word)
                        if current_line:
                            lines.append(' '.join(current_line))
                        wrapped_paragraphs.append('\n'.join(lines))
                    else:
                        wrapped_paragraphs.append(para)
                content = '\n\n'.join(wrapped_paragraphs)

        # Apply length limits
        if self.config.max_length:
            content = self._truncate_text(content, self.config.max_length)

        return content

    def _format_html(self, content: str) -> str:
        """Format HTML content."""
        # Basic HTML formatting
        content = content.strip()

        # Format indentation
        lines = content.split('\n')
        indent_level = 0
        formatted_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith('</'):
                indent_level = max(0, indent_level - 1)
            formatted_lines.append('  ' * indent_level + stripped)
            if (stripped.endswith('>') and
                not stripped.endswith('/>') and
                not stripped.startswith('</') and
                not stripped.startswith('<!')):
                indent_level += 1

        content = '\n'.join(formatted_lines)

        return content

    def _format_markdown(self, content: str) -> str:
        """Format Markdown content."""
        # Basic Markdown formatting
        content = content.strip()

        # Format headers
        content = re.sub(r'^(#{1,6})\s*', r'\1 ', content, flags=re.MULTILINE)

        # Format lists
        content = re.sub(r'^\s*[-*+]\s*', '- ', content, flags=re.MULTILINE)
        content = re.sub(r'^\s*(\d+\.)\s*', r'\1 ', content, flags=re.MULTILINE)

        # Format code blocks
        content = re.sub(r'```\s*(\w*)\n', r'```\1\n', content)

        return content

    def _format_code(self, content: str) -> str:
        """Format code content."""
        # Basic code formatting
        content = content.strip()

        # Remove excessive blank lines
        content = re.sub(r'\n{3,}', '\n\n', content)

        # Format indentation
        lines = content.split('\n')
        formatted_lines = []
        indent_level = 0

        for line in lines:
            stripped = line.strip()
            if stripped.endswith(':'):
                formatted_lines.append('    ' * indent_level + stripped)
                indent_level += 1
            elif stripped in ['return', 'break', 'continue', 'pass']:
                indent_level = max(0, indent_level - 1)
                formatted_lines.append('    ' * indent_level + stripped)
            else:
                formatted_lines.append('    ' * indent_level + stripped)

        content = '\n'.join(formatted_lines)

        return content

    def _format_error(self, content: str) -> str:
        """Format error response."""
        # Add error prefix if not present
        if not content.lower().startswith('error'):
            content = f"Error: {content}"

        # Add timestamp
        if self.config.formatting_rules and self.config.formatting_rules.get('timestamp_errors', True):
            content = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {content}"

        # Add stack trace formatting if present
        stack_trace_match = re.search(r'Traceback \(most recent call last\):(.*?)(?=\w+Error:|$)', 
                                      content, re.DOTALL)
        if stack_trace_match:
            stack_trace = stack_trace_match.group(1)
            formatted_trace = '\n'.join('  ' + line.strip() 
                                      for line in stack_trace.split('\n') if line.strip())
            content = content.replace(stack_trace, '\n' + formatted_trace + '\n')

        return content

    # =====================
    # Validators
    # =====================

    def _validate_text(self, content: str) -> Dict[str, Any]:
        """Validate text response."""
        errors = []
        warnings = []

        # Basic validation
        if not content.strip():
            errors.append("Response content cannot be empty")

        # Length validation
        if self.config.validation_rules:
            max_length = self.config.validation_rules.get('max_length')
            if max_length and len(content) > max_length:
                errors.append(f"Content exceeds maximum length of {max_length}")

            prohibited_patterns = self.config.validation_rules.get('prohibited_patterns', [])
            for pattern in prohibited_patterns:
                if re.search(pattern, content):
                    errors.append(f"Content contains prohibited pattern: {pattern}")

        # Content formatting
        sentences = content.split('. ')
        for i, sentence in enumerate(sentences):
            if sentence and sentence[0].islower():
                warnings.append(f"Sentence {i+1} does not start with a capital letter")
            if sentence and not sentence.strip('.').strip():
                errors.append(f"Empty sentence at position {i+1}")

        # Quotation marks
        quotes = re.findall(r'["\']', content)
        if len(quotes) % 2 != 0:
            errors.append("Unmatched quotation marks")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def _validate_html(self, content: str) -> Dict[str, Any]:
        """Validate HTML content."""
        errors = []
        warnings = []

        if not content:
            errors.append("Empty content")
            return {'valid': False, 'errors': errors, 'warnings': warnings}

        # Check for balanced tags
        tag_stack = []
        for tag in re.finditer(r'</?([a-zA-Z0-9]+)[^>]*>', content):
            tag_name = tag.group(1)
            if tag.group(0).startswith('</'):
                if not tag_stack or tag_stack[-1] != tag_name:
                    errors.append(f"Unmatched closing tag: {tag_name}")
                    continue
                tag_stack.pop()
            elif not tag.group(0).endswith('/>') and not tag.group(0).startswith('<!'):
                tag_stack.append(tag_name)

        if tag_stack:
            errors.append(f"Unclosed tags: {', '.join(tag_stack)}")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def _validate_markdown(self, content: str) -> Dict[str, Any]:
        """Validate Markdown content."""
        errors = []
        warnings = []

        if not content:
            errors.append("Empty content")
            return {'valid': False, 'errors': errors, 'warnings': warnings}

        # Check for unclosed code blocks
        code_blocks = content.count('```')
        if code_blocks % 2 != 0:
            errors.append("Unclosed code block")

        # Check for valid headers
        for line in content.split('\n'):
            if line.startswith('#'):
                if not re.match(r'^#{1,6}\s', line):
                    errors.append("Invalid header format")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def _validate_code(self, content: str) -> Dict[str, Any]:
        """Validate code content."""
        errors = []
        warnings = []

        if not content.strip():
            errors.append("Code content cannot be empty")
            return {'valid': False, 'errors': errors, 'warnings': warnings}

        # Check for basic syntax issues
        try:
            ast.parse(content)
        except SyntaxError as e:
            errors.append(f"Invalid code syntax: {str(e)}")

        # Check indentation consistency
        lines = content.split('\n')
        indent_size = self.config.style_guide.get('indent_size') if self.config.style_guide else 4
        for i, line in enumerate(lines, 1):
            if line.strip():  # Ignore empty lines
                leading_spaces = len(line) - len(line.lstrip(' '))
                if leading_spaces % indent_size != 0:
                    warnings.append(f"Inconsistent indentation at line {i}")

        # Check for common issues
        if 'import' in content and not content.strip().startswith('import'):
            warnings.append("Import statements should be at the top")

        if '\t' in content:
            warnings.append("Tab characters found, consider using spaces")

        # Line length
        max_line_length = self.config.style_guide.get('max_line_length', 80) if self.config.style_guide else 80
        for i, line in enumerate(lines, 1):
            if len(line) > max_line_length:
                warnings.append(f"Line {i} exceeds maximum length of {max_line_length}")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def _validate_error(self, content: str) -> Dict[str, Any]:
        """Validate error response."""
        errors = []
        warnings = []

        if not content.strip():
            errors.append("Error content cannot be empty")

        # Check error format
        if not content.lower().startswith(('error', '[', '(')):
            warnings.append("Error message should start with 'Error:' or a timestamp")

        # Check for timestamp
        if self.config.formatting_rules and self.config.formatting_rules.get('timestamp_errors', True):
            if not re.match(r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]', content):
                warnings.append("Error message should include timestamp")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    # =====================
    # Enhancers
    # =====================

    def _enhance_text(self, content: str) -> str:
        """Enhance text content."""
        # Fix common formatting issues
        content = re.sub(r'\s+\.', '.', content)  # Fix space before period
        content = re.sub(r'\s+,', ',', content)  # Fix space before comma
        content = re.sub(r'\s+$', '', content, flags=re.MULTILINE)  # Remove trailing spaces

        # Ensure proper spacing after punctuation
        content = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', content)

        return content

    def _enhance_html(self, content: str) -> str:
        """Enhance HTML content."""
        # Add basic accessibility attributes
        content = re.sub(r'<img([^>]*)>', lambda m: self._enhance_img_tag(m.group(1)), content)
        content = re.sub(r'<a([^>]*)>', lambda m: self._enhance_anchor_tag(m.group(1)), content)
        content = re.sub(r'<button([^>]*)>', lambda m: self._enhance_button_tag(m.group(1)), content)

        return content

    def _enhance_markdown(self, content: str) -> str:
        """Enhance Markdown content."""
        # Add reference links for URLs
        urls = list(re.finditer(r'(?<!\[)(?<!\()http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content))
        for i, match in enumerate(urls, 1):
            url = match.group(0)
            reference = f'[{i}]'
            content = content.replace(url, f'[{url}]{reference}')
            content += f'\n{reference}: {url}'

        return content

    def _enhance_code(self, content: str) -> str:
        """Enhance code content."""
        # Add basic docstring if missing
        if not re.search(r'"""(.*?)"""', content, re.DOTALL):
            lines = content.split('\n')
            indent = re.match(r'^\s*', lines[0]).group(0) if lines else ''
            lines.insert(1, f'{indent}"""Add description here."""')
            content = '\n'.join(lines)

        # Prepare code with annotations or warnings if needed
        if 'TODO' in content:
            content += '\n# TODO: Review and complete this section.'

        return content

    def _enhance_error(self, content: str) -> str:
        """Enhance error content."""
        # Append help URL if available
        if self.config.help_url:
            content += f"\n\nFor more information, visit: {self.config.help_url}"

        return content

    # =====================
    # Post-processors
    # =====================

    def _post_process_text(self, content: str) -> str:
        """Post-process text response."""
        # Add citations if enabled
        if self.config.enable_citations and '[citation needed]' in content:
            content += '\n\nNote: Some statements require citations.'

        # Add context reference if enabled
        if self.config.maintain_context and self.config.custom_settings:
            context = self.config.custom_settings.get('context_reference')
            if context:
                content += f"\n\nContext: {context}"

        return content

    def _post_process_code(self, content: str) -> str:
        """Post-process code response."""
        # Add execution warning if needed
        if 'os.' in content or 'subprocess.' in content:
            content = "# CAUTION: This code contains system operations. Review before execution.\n\n" + content

        return content

    def _post_process_error(self, content: str) -> str:
        """Post-process error response."""
        # Add help reference if available
        if self.config.help_url:
            content += f"\n\nFor more information, visit: {self.config.help_url}"

        return content

    # =====================
    # Enhancements for HTML Tags
    # =====================

    def _enhance_img_tag(self, attributes: str) -> str:
        """Enhance img tag with accessibility attributes."""
        if 'alt=' not in attributes:
            attributes += ' alt="Image"'
        return f'<img{attributes}>'

    def _enhance_anchor_tag(self, attributes: str) -> str:
        """Enhance anchor tag with accessibility attributes."""
        if 'aria-label=' not in attributes and 'title=' not in attributes:
            attributes += ' aria-label="Link"'
        return f'<a{attributes}>'

    def _enhance_button_tag(self, attributes: str) -> str:
        """Enhance button tag with accessibility attributes."""
        if 'aria-label=' not in attributes and 'title=' not in attributes:
            attributes += ' aria-label="Button"'
        return f'<button{attributes}>'

    # =====================
    # Utilities
    # =====================

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text while preserving word boundaries."""
        if len(text) <= max_length:
            return text

        truncated = text[:max_length].rsplit(' ', 1)[0]
        return truncated + '...'

    def _truncate_content(self, content: str, max_length: int) -> str:
        """Truncate content while preserving meaning."""
        if len(content) <= max_length:
            return content

        # Try to truncate at sentence boundary
        sentences = content.split('. ')
        truncated = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence) + 2  # +2 for '. '
            if current_length + sentence_length <= max_length:
                truncated.append(sentence)
                current_length += sentence_length
            else:
                break

        return '. '.join(truncated) + '...'

