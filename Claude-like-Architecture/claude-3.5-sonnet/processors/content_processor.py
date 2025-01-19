# processors/content_processor.py
import re
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import logging
from core.exceptions import ProcessingError

@dataclass
class ProcessedContent:
    """Processed content data."""
    original: Any
    processed: Any
    metadata: Dict[str, Any]
    timestamp: datetime
    processing_time: float

class ContentProcessor:
    """Processes and transforms content."""

    def __init__(self):
        self.processors: Dict[str, callable] = {}
        self.processed_content: List[ProcessedContent] = []
        self._initialize_processors()

    def process_content(self,
                       content: Any,
                       content_type: str,
                       options: Optional[Dict[str, Any]] = None) -> ProcessedContent:
        """Process content with specified processor."""
        try:
            start_time = datetime.now()
            
            # Get appropriate processor
            processor = self.processors.get(content_type)
            if not processor:
                raise ProcessingError(f"No processor found for type: {content_type}")

            # Process content
            processed = processor(content, options or {})

            # Create result
            result = ProcessedContent(
                original=content,
                processed=processed,
                metadata=options or {},
                timestamp=datetime.now(),
                processing_time=(datetime.now() - start_time).total_seconds()
            )
            
            self.processed_content.append(result)
            return result

        except Exception as e:
            logging.error(f"Content processing failed: {str(e)}")
            raise ProcessingError(f"Failed to process content: {str(e)}")

    def _initialize_processors(self) -> None:
        """Initialize content processors."""
        self.processors.update({
            'text': self._process_text,
            'code': self._process_code,
            'markdown': self._process_markdown,
            'json': self._process_json
        })

    def _process_text(self,
                     content: str,
                     options: Dict[str, Any]) -> str:
        """Process text content."""
        # Apply text transformations
        if options.get('lowercase', False):
            content = content.lower()
        if options.get('uppercase', False):
            content = content.upper()
        if options.get('strip', True):
            content = content.strip()
            
        return content

    def _process_code(self,
                     content: str,
                     options: Dict[str, Any]) -> str:
        """Process code content."""
        import re
        
        # Remove comments if specified
        if options.get('remove_comments', False):
            # Remove single-line comments
            content = re.sub(r'#.*$', '', content, flags=re.MULTILINE)
            # Remove multi-line comments
            content = re.sub(r'"""[\s\S]*?"""', '', content)
            
        # Format code if specified
        if options.get('format', True):
            # Basic indentation formatting
            lines = content.split('\n')
            indented = []
            indent_level = 0
            
            for line in lines:
                stripped = line.strip()
                if stripped.endswith(':'):
                    indented.append('    ' * indent_level + stripped)
                    indent_level += 1
                elif stripped in ['return', 'break', 'continue', 'pass']:
                    indent_level = max(0, indent_level - 1)
                    indented.append('    ' * indent_level + stripped)
                else:
                    indented.append('    ' * indent_level + stripped)
                    
            content = '\n'.join(indented)
            
        return content

    def _process_markdown(self,
                         content: str,
                         options: Dict[str, Any]) -> str:
        """Process markdown content."""
        # Normalize headers
        content = re.sub(r'^#+\s*', lambda m: '#' * len(m.group().strip()) + ' ',
                        content,
                        flags=re.MULTILINE)
        
        # Normalize lists
        content = re.sub(r'^[-*+]\s*', '- ', content, flags=re.MULTILINE)
        
        # Normalize code blocks
        content = re.sub(r'```\s*\n', '```\n', content)
        
        return content.strip()

    def _process_json(self,
                     content: Union[str, Dict, List],
                     options: Dict[str, Any]) -> Dict:
        """Process JSON content."""
        import json
        
        # Parse if string
        if isinstance(content, str):
            content = json.loads(content)
            
        # Format if specified
        if options.get('format', True):
            indent = options.get('indent', 2)
            content = json.dumps(content, indent=indent)
            
        return content

    def add_processor(self,
                     content_type: str,
                     processor: callable) -> None:
        """Add custom content processor."""
        self.processors[content_type] = processor

    def remove_processor(self, content_type: str) -> bool:
        """Remove content processor."""
        return bool(self.processors.pop(content_type, None))

    def get_processed_history(self) -> List[ProcessedContent]:
        """Get history of processed content."""
        return self.processed_content.copy()

    def clear_history(self) -> None:
        """Clear processing history."""
        self.processed_content.clear()