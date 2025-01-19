# interfaces/controller.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ControllerMetadata:
    """Metadata for controller operations."""
    operation_id: str
    timestamp: datetime
    controller_type: str
    status: str
    metrics: Dict[str, Any]

@dataclass
class ControllerResult:
    """Base result class for controller operations."""
    success: bool
    message: str
    data: Any
    metadata: ControllerMetadata

class BaseController(ABC):
    """Abstract base class for all controllers."""

    def __init__(self):
        self.metadata = {}
        self.operations_history: List[ControllerMetadata] = []

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize controller resources."""
        pass

    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Validate input data."""
        pass

    @abstractmethod
    def process(self, data: Any) -> ControllerResult:
        """Process data using the controller."""
        pass

    @abstractmethod
    def cleanup(self) -> bool:
        """Cleanup controller resources."""
        pass

    def create_metadata(self, operation_id: str, status: str) -> ControllerMetadata:
        """Create metadata for an operation."""
        metadata = ControllerMetadata(
            operation_id=operation_id,
            timestamp=datetime.now(),
            controller_type=self.__class__.__name__,
            status=status,
            metrics={}
        )
        self.operations_history.append(metadata)
        return metadata

    def get_operation_history(self) -> List[ControllerMetadata]:
        """Get history of operations."""
        return self.operations_history

    def create_result(self, 
                     success: bool, 
                     message: str, 
                     data: Any, 
                     operation_id: str) -> ControllerResult:
        """Create a standardized result object."""
        return ControllerResult(
            success=success,
            message=message,
            data=data,
            metadata=self.create_metadata(operation_id, "completed" if success else "failed")
        )