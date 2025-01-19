# processors/format_processor.py
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import logging
from core.exceptions import ProcessingError

@dataclass
class FormattedContent:
    """Formatted content data."""
    content: Any
    format_type: str
    metadata: Dict[str, Any]
    timestamp: datetime

class FormatProcessor:
    """Processes content formatting."""

    def __init__(self):
        self.formatters: Dict[str, callable] = {}
        self.formatted_content: List[FormattedContent] = []
        self._initialize_formatters()

    def format_content(self,
                      content: Any,
                      format_type: str,
                      options: Optional[Dict[str, Any]] = None) -> FormattedContent:
        """Format content with specified formatter."""
        try:
            # Get appropriate formatter
            formatter = self.formatters.get(format_type)
            if not formatter:
                raise ProcessingError(f"No formatter found for type: {format_type}")

            # Format content
            formatted = formatter(content, options or {})

            # Create result
            result = FormattedContent(
                content=formatted,
                format_type=format_type,
                metadata=options or {},
                timestamp=datetime.now()
            )
            
            self.formatted_content.append(result)
            return result

        except Exception as e:
            logging.error(f"Content formatting failed: {str(e)}")
            raise ProcessingError(f"Failed to format content: {str(e)}")

    def _initialize_formatters(self) -> None:
        """Initialize content formatters."""
        self.formatters.update({
            'text': self._format_text,
            'code': self._format_code,
            'markdown': self._format_markdown,
            'html': self._format_html
        })

    def _format_text(self,
                    content: str,
                    options: Dict[str, Any]) -> str:
        """Format text content."""
        # Apply text formatting
        if options.get('wrap', False):
            width = options.get('width', 80)
            content = self._wrap_text(content, width)
            
        if options.get('align') == 'center':
            content = self._center_text(content)
            
        return content

    def _format_code(self,
                    content: str,
                    options: Dict[str, Any]) -> str:
        """Format code content."""
        language = options.get('language', '')
        
        # Add code block markers
        if language:
            content = f"```{language}\n{content}\n```"
        else:
            content = f"```\n{content}\n```"
            
        return content

    def _format_markdown(self,
                        content: str,
                        options: Dict[str, Any]) -> str:
        """Format markdown content."""
        # Apply markdown formatting
        if options.get('toc', False):
            content = self._add_table_of_contents(content)
            
        if options.get('numbered_headers', False):
            content = self._number_headers(content)
            
        return content

    def _format_html(self,
                    content: str,
                    options: Dict[str, Any]) -> str:
        """Format HTML content."""
        import html
        
        # Escape HTML if needed
        if options.get('escape', True):
            content = html.escape(content)
            
        # Wrap in tags if specified
        tag = options.get('tag', 'div')
        classes = options.get('classes', '')
        
        if tag:
            content = f"<{tag} class='{classes}'>{content}</{tag}>"
            
        return content

    def _wrap_text(self,
                   text: str,
                   width: int) -> str:
        """Wrap text to specified width."""
        import textwrap
        return textwrap.fill(text, width=width)

    def _center_text(self, text: str) -> str:
        """Center align text."""
        lines = text.split('\n')
        max_width = max(len(line) for line in lines)
        return '\n'.join(line.center(max_width) for line in lines)

    def _add_table_of_contents(self, content: str) -> str:
        """Add table of contents to markdown."""
        import re
        
        # Extract headers
        headers = re.findall(r'^(#+)\s*(.+)$', content, re.MULTILINE)
        
        if not headers:
            return content
            
        # Generate TOC
        toc = ["# Table of Contents\n"]
        
        for level, title in headers:
            depth = len(level) - 1
            link = title.lower().replace(' ', '-')
            toc.append(f"{'    ' * depth}- [{title}](#{link})")
            
        return '\n'.join(toc) + '\n\n' + content

    def _number_headers(self, content: str) -> str:
        """Add numbers to markdown headers."""
        import re
        
        lines = content.split('\n')
        numbers = [0] * 6  # Track numbers for up to 6 levels
        
        for i, line in enumerate(lines):
                        header_match = re.match(r'^(#+)\s*(.+)$', line)
        if header_match:
                level = len(header_match.group(1))
                title = header_match.group(2)
                
                # Update numbering
                numbers[level - 1] += 1
                for j in range(level, 6):
                    numbers[j] = 0
                    
                # Create number prefix
                number = '.'.join(str(n) for n in numbers[:level] if n > 0)
                
                # Replace line with numbered header
                lines[i] = f"{'#' * level} {number} {title}"
                
        return '\n'.join(lines)

    def add_formatter(self,
                        format_type: str,
                        formatter: callable) -> None:
        """Add custom content formatter."""
        self.formatters[format_type] = formatter

    def remove_formatter(self, format_type: str) -> bool:
        """Remove content formatter."""
        return bool(self.formatters.pop(format_type, None))

    def get_formatting_history(self) -> List[FormattedContent]:
        """Get history of formatted content."""
        return self.formatted_content.copy()

    def clear_history(self) -> None:
        """Clear formatting history."""
        self.formatted_content.clear()
