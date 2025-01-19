# interfaces/processor.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ProcessingStage(Enum):
    """Enum for processing stages."""
    INITIALIZATION = "initialization"
    VALIDATION = "validation"
    PROCESSING = "processing"
    OPTIMIZATION = "optimization"
    COMPLETION = "completion"

@dataclass
class ProcessingMetadata:
    """Metadata for processing operations."""
    process_id: str
    stage: ProcessingStage
    timestamp: datetime
    duration: float
    metrics: Dict[str, Any]

@dataclass
class ProcessingResult:
    """Result of processing operations."""
    success: bool
    input_data: Any
    output_data: Any
    metadata: ProcessingMetadata
    errors: List[str]

class BaseProcessor(ABC):
    """Abstract base class for all processors."""

    def __init__(self):
        self.processing_history: List[ProcessingMetadata] = []
        self.current_process_id: Optional[str] = None

    @abstractmethod
    def process(self, data: Any) -> ProcessingResult:
        """Main processing method."""
        pass

    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Validate input data."""
        pass

    @abstractmethod
    def optimize(self, data: Any) -> Any:
        """Optimize processed data."""
        pass

    def create_metadata(self, 
                       process_id: str, 
                       stage: ProcessingStage, 
                       duration: float) -> ProcessingMetadata:
        """Create metadata for processing operation."""
        metadata = ProcessingMetadata(
            process_id=process_id,
            stage=stage,
            timestamp=datetime.now(),
            duration=duration,
            metrics={}
        )
        self.processing_history.append(metadata)
        return metadata

    def get_processing_history(self) -> List[ProcessingMetadata]:
        """Get history of processing operations."""
        return self.processing_history

    def create_result(self,
                     success: bool,
                     input_data: Any,
                     output_data: Any,
                     process_id: str,
                     duration: float,
                     errors: List[str] = None) -> ProcessingResult:
        """Create a standardized processing result."""
        return ProcessingResult(
            success=success,
            input_data=input_data,
            output_data=output_data,
            metadata=self.create_metadata(
                process_id=process_id,
                stage=ProcessingStage.COMPLETION,
                duration=duration
            ),
            errors=errors or []
        )