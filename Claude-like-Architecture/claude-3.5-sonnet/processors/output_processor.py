# processors/output_processor.py
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import logging
from core.exceptions import ProcessingError

@dataclass
class ProcessedOutput:
    """Processed output data."""
    content: Any
    format_type: str
    metadata: Dict[str, Any]
    timestamp: datetime
    validation: Dict[str, Any]

class OutputProcessor:
    """Processes and validates output data."""

    def __init__(self):
        self.processors: Dict[str, callable] = {}
        self.validators: Dict[str, callable] = {}
        self.processed_outputs: List[ProcessedOutput] = []
        self._initialize_processors()
        self._initialize_validators()

    def process_output(self,
                      content: Any,
                      output_type: str,
                      metadata: Optional[Dict[str, Any]] = None) -> ProcessedOutput:
        """Process and validate output data."""
        try:
            # Get appropriate processor and validator
            processor = self.processors.get(output_type)
            validator = self.validators.get(output_type)
            
            if not processor:
                raise ProcessingError(f"No processor found for type: {output_type}")

            # Process output
            processed_content = processor(content)

            # Validate output
            validation_result = {
                'valid': True,
                'errors': []
            }
            
            if validator:
                try:
                    is_valid = validator(processed_content)
                    validation_result['valid'] = is_valid
                    if not is_valid:
                        validation_result['errors'].append("Validation failed")
                except Exception as e:
                    validation_result['valid'] = False
                    validation_result['errors'].append(str(e))

            # Create result
            result = ProcessedOutput(
                content=processed_content,
                format_type=output_type,
                metadata=metadata or {},
                timestamp=datetime.now(),
                validation=validation_result
            )
            
            self.processed_outputs.append(result)
            return result

        except Exception as e:
            logging.error(f"Output processing failed: {str(e)}")
            raise ProcessingError(f"Failed to process output: {str(e)}")

    def _initialize_processors(self) -> None:
        """Initialize output processors."""
        self.processors.update({
            'text': self._process_text_output,
            'json': self._process_json_output,
            'html': self._process_html_output,
            'xml': self._process_xml_output
        })

    def _initialize_validators(self) -> None:
        """Initialize output validators."""
        self.validators.update({
            'text': self._validate_text_output,
            'json': self._validate_json_output,
            'html': self._validate_html_output,
            'xml': self._validate_xml_output
        })

    def _process_text_output(self, content: str) -> str:
        """Process text output."""
        return str(content).strip()

    def _process_json_output(self, content: Any) -> str:
        """Process JSON output."""
        import json
        try:
            if isinstance(content, str):
                # Verify it's valid JSON
                json.loads(content)
                return content
            return json.dumps(content)
        except Exception as e:
            raise ProcessingError(f"Invalid JSON output: {str(e)}")

    def _process_html_output(self, content: str) -> str:
        """Process HTML output."""
        import html
        return html.escape(content)

    def _process_xml_output(self, content: str) -> str:
        """Process XML output."""
        import xml.etree.ElementTree as ET
        try:
            # Verify it's valid XML
            ET.fromstring(content)
            return content
        except Exception as e:
            raise ProcessingError(f"Invalid XML output: {str(e)}")

    def _validate_text_output(self, content: str) -> bool:
        """Validate text output."""
        return isinstance(content, str) and bool(content.strip())

    def _validate_json_output(self, content: str) -> bool:
        """Validate JSON output."""
        import json
        try:
            json.loads(content)
            return True
        except Exception:
            return False

    def _validate_html_output(self, content: str) -> bool:
        """Validate HTML output."""
        from html.parser import HTMLParser

        class HTMLValidator(HTMLParser):
            def __init__(self):
                super().__init__()
                self.valid = True

            def handle_data(self, data):
                pass

            def handle_starttag(self, tag, attrs):
                pass

            def handle_endtag(self, tag):
                pass

            def handle_error(self, message):
                self.valid = False

        validator = HTMLValidator()
        validator.feed(content)
        return validator.valid

    def _validate_xml_output(self, content: str) -> bool:
        """Validate XML output."""
        import xml.etree.ElementTree as ET
        try:
            ET.fromstring(content)
            return True
        except Exception:
            return False

    def add_processor(self,
                     output_type: str,
                     processor: callable,
                     validator: Optional[callable] = None) -> None:
        """Add custom output processor and validator."""
        self.processors[output_type] = processor
        if validator:
            self.validators[output_type] = validator

    def remove_processor(self, output_type: str) -> bool:
        """Remove output processor and validator."""
        self.validators.pop(output_type, None)
        return bool(self.processors.pop(output_type, None))

    def get_processing_history(self) -> List[ProcessedOutput]:
        """Get history of processed outputs."""
        return self.processed_outputs.copy()

    def clear_history(self) -> None:
        """Clear processing history."""
        self.processed_outputs.clear()