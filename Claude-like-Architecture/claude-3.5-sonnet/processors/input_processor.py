# processors/input_processor.py
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import logging
from core.exceptions import ProcessingError

@dataclass
class ProcessedInput:
    """Processed input data."""
    content: Any
    metadata: Dict[str, Any]
    timestamp: datetime
    validation_result: Optional[Dict[str, Any]] = None

class InputProcessor:
    """Processes and validates input data."""

    def __init__(self):
        self.processed_inputs: List[ProcessedInput] = []
        self.validation_rules: Dict[str, callable] = {}
        self._initialize_validators()

    def process_input(self, 
                     input_data: Any,
                     input_type: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> ProcessedInput:
        """Process input data."""
        try:
            # Validate input
            validation_result = self._validate_input(input_data, input_type)
            if not validation_result['valid']:
                raise ProcessingError(
                    f"Input validation failed: {validation_result['errors']}"
                )

            # Process based on type
            processed_content = self._process_by_type(input_data, input_type)

            # Create processed input
            processed = ProcessedInput(
                content=processed_content,
                metadata=metadata or {},
                timestamp=datetime.now(),
                validation_result=validation_result
            )
            
            self.processed_inputs.append(processed)
            return processed

        except Exception as e:
            logging.error(f"Input processing failed: {str(e)}")
            raise ProcessingError(f"Failed to process input: {str(e)}")

    def _initialize_validators(self) -> None:
        """Initialize input validators."""
        self.validation_rules.update({
            'text': self._validate_text,
            'number': self._validate_number,
            'json': self._validate_json,
            'list': self._validate_list
        })

    def _validate_input(self,
                       input_data: Any,
                       input_type: Optional[str] = None) -> Dict[str, Any]:
        """Validate input data."""
        validator = self.validation_rules.get(
            input_type,
            self._validate_generic
        )

        try:
            is_valid = validator(input_data)
            return {
                'valid': is_valid,
                'errors': [] if is_valid else ['Validation failed']
            }
        except Exception as e:
            return {
                'valid': False,
                'errors': [str(e)]
            }

    def _validate_generic(self, data: Any) -> bool:
        """Generic input validation."""
        return data is not None

    def _validate_text(self, text: str) -> bool:
        """Validate text input."""
        return isinstance(text, str) and bool(text.strip())

    def _validate_number(self, number: Union[int, float]) -> bool:
        """Validate numeric input."""
        return isinstance(number, (int, float))

    def _validate_json(self, json_data: Any) -> bool:
        """Validate JSON input."""
        import json
        try:
            if isinstance(json_data, str):
                json.loads(json_data)
            return True
        except Exception:
            return False

    def _validate_list(self, data: List) -> bool:
        """Validate list input."""
        return isinstance(data, list)

    def _process_by_type(self,
                        input_data: Any,
                        input_type: Optional[str] = None) -> Any:
        """Process input based on type."""
        processors = {
            'text': self._process_text,
            'number': self._process_number,
            'json': self._process_json,
            'list': self._process_list
        }

        processor = processors.get(input_type, lambda x: x)
        return processor(input_data)

    def _process_text(self, text: str) -> str:
        """Process text input."""
        return text.strip()

    def _process_number(self, number: Union[int, float]) -> Union[int, float]:
        """Process numeric input."""
        return number

    def _process_json(self, json_data: Any) -> Dict:
        """Process JSON input."""
        import json
        if isinstance(json_data, str):
            return json.loads(json_data)
        return json_data

    def _process_list(self, data: List) -> List:
        """Process list input."""
        return list(data)

    def add_validator(self,
                     input_type: str,
                     validator: callable) -> None:
        """Add custom validator."""
        self.validation_rules[input_type] = validator

    def get_processed_history(self) -> List[ProcessedInput]:
        """Get history of processed inputs."""
        return self.processed_inputs.copy()

    def clear_history(self) -> None:
        """Clear processing history."""
        self.processed_inputs.clear()