# interfaces/generator.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Generic, TypeVar
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

T = TypeVar('T')  # Type variable for generated content

class GenerationType(Enum):
    """Types of content generation."""
    TEXT = "text"
    CODE = "code"
    ARTIFACT = "artifact"
    RESPONSE = "response"
    CUSTOM = "custom"

@dataclass
class GenerationMetadata:
    """Metadata for generation operations."""
    generation_id: str
    type: GenerationType
    timestamp: datetime
    parameters: Dict[str, Any]
    metrics: Dict[str, Any]

@dataclass
class GenerationResult(Generic[T]):
    """Result of generation operations."""
    success: bool
    content: T
    metadata: GenerationMetadata
    errors: List[str]
    warnings: List[str]

class BaseGenerator(ABC, Generic[T]):
    """Abstract base class for all generators."""

    def __init__(self, generation_type: GenerationType):
        self.generation_type = generation_type
        self.generation_history: List[GenerationMetadata] = []

    @abstractmethod
    def generate(self, parameters: Dict[str, Any]) -> GenerationResult[T]:
        """Main generation method."""
        pass

    @abstractmethod
    def validate(self, content: T) -> bool:
        """Validate generated content."""
        pass

    @abstractmethod
    def optimize(self, content: T) -> T:
        """Optimize generated content."""
        pass

    def create_metadata(self, 
                       generation_id: str, 
                       parameters: Dict[str, Any]) -> GenerationMetadata:
        """Create metadata for generation operation."""
        metadata = GenerationMetadata(
            generation_id=generation_id,
            type=self.generation_type,
            timestamp=datetime.now(),
            parameters=parameters,
            metrics={}
        )
        self.generation_history.append(metadata)
        return metadata

    def get_generation_history(self) -> List[GenerationMetadata]:
        """Get history of generation operations."""
        return self.generation_history

    def create_result(self,
                     success: bool,
                     content: T,
                     generation_id: str,
                     parameters: Dict[str, Any],
                     errors: List[str] = None,
                     warnings: List[str] = None) -> GenerationResult[T]:
        """Create a standardized generation result."""
        return GenerationResult(
            success=success,
            content=content,
            metadata=self.create_metadata(generation_id, parameters),
            errors=errors or [],
            warnings=warnings or []
        )

    @abstractmethod
    def can_generate(self, parameters: Dict[str, Any]) -> bool:
        """Check if generator can handle given parameters."""
        pass

    @abstractmethod
    def estimate_resources(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate resources needed for generation."""
        pass

    def add_metric(self, 
                  generation_id: str, 
                  metric_name: str, 
                  metric_value: Any) -> None:
        """Add metric to generation metadata."""
        for metadata in self.generation_history:
            if metadata.generation_id == generation_id:
                metadata.metrics[metric_name] = metric_value
                break

    def get_metrics(self, generation_id: str) -> Dict[str, Any]:
        """Get metrics for specific generation."""
        for metadata in self.generation_history:
            if metadata.generation_id == generation_id:
                return metadata.metrics
        return {}