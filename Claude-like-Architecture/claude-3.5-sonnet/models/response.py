from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

class ResponseType(Enum):
    """Enumeration of response types."""
    TEXT = "text"
    CODE = "code"
    ERROR = "error"
    FUNCTION = "function"
    ARTIFACT = "artifact"
    MARKDOWN = "markdown"
    HTML = "html"
    SVG = "svg"
    MERMAID = "mermaid"
    REACT = "react"

@dataclass
class ResponseMetadata:
    """Metadata for a response."""
    created_at: datetime
    processing_time: float
    model: str
    tokens: int
    context_tokens: int
    prompt_tokens: int
    finish_reason: Optional[str] = None
    custom_data: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> bool:
        """Validate metadata fields."""
        try:
            assert self.tokens >= 0, "Tokens must be non-negative"
            assert self.context_tokens >= 0, "Context tokens must be non-negative"
            assert self.prompt_tokens >= 0, "Prompt tokens must be non-negative"
            assert self.processing_time >= 0, "Processing time must be non-negative"
            assert self.model, "Model identifier cannot be empty"
            return True
        except AssertionError as e:
            raise ValueError(f"Metadata validation failed: {str(e)}")

@dataclass
class ResponseFormat:
    """Format specifications for a response."""
    type: ResponseType
    template: Optional[str] = None
    style: Optional[Dict[str, Any]] = None
    constraints: Optional[Dict[str, Any]] = None

    def validate(self) -> bool:
        """Validate format specifications."""
        try:
            if self.template:
                assert isinstance(self.template, str), "Template must be a string"
            if self.constraints:
                assert isinstance(self.constraints, dict), "Constraints must be a dictionary"
            if self.style:
                assert isinstance(self.style, dict), "Style must be a dictionary"
            return True
        except AssertionError as e:
            raise ValueError(f"Format validation failed: {str(e)}")

@dataclass
class Response:
    """Represents a response from the assistant."""
    content: str
    type: ResponseType
    metadata: ResponseMetadata
    id: UUID = field(default_factory=uuid4)
    format: Optional[ResponseFormat] = None
    parent_id: Optional[UUID] = None
    references: List[UUID] = field(default_factory=list)
    artifacts: List[UUID] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "id": str(self.id),
            "content": self.content,
            "type": self.type.value,
            "metadata": {
                "created_at": self.metadata.created_at.isoformat(),
                "processing_time": self.metadata.processing_time,
                "model": self.metadata.model,
                "tokens": self.metadata.tokens,
                "context_tokens": self.metadata.context_tokens,
                "prompt_tokens": self.metadata.prompt_tokens,
                "finish_reason": self.metadata.finish_reason,
                "custom_data": self.metadata.custom_data
            },
            "format": {
                "type": self.format.type.value,
                "template": self.format.template,
                "style": self.format.style,
                "constraints": self.format.constraints
            } if self.format else None,
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "references": [str(ref) for ref in self.references],
            "artifacts": [str(art) for art in self.artifacts],
            "error": self.error
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Response':
        """Create response from dictionary."""
        metadata = ResponseMetadata(
            created_at=datetime.fromisoformat(data["metadata"]["created_at"]),
            processing_time=data["metadata"]["processing_time"],
            model=data["metadata"]["model"],
            tokens=data["metadata"]["tokens"],
            context_tokens=data["metadata"]["context_tokens"],
            prompt_tokens=data["metadata"]["prompt_tokens"],
            finish_reason=data["metadata"].get("finish_reason"),
            custom_data=data["metadata"].get("custom_data", {})
        )

        format_data = data.get("format")
        format_obj = None
        if format_data:
            format_obj = ResponseFormat(
                type=ResponseType(format_data["type"]),
                template=format_data.get("template"),
                style=format_data.get("style"),
                constraints=format_data.get("constraints")
            )

        return cls(
            id=UUID(data["id"]),
            content=data["content"],
            type=ResponseType(data["type"]),
            metadata=metadata,
            format=format_obj,
            parent_id=UUID(data["parent_id"]) if data.get("parent_id") else None,
            references=[UUID(ref) for ref in data.get("references", [])],
            artifacts=[UUID(art) for art in data.get("artifacts", [])],
            error=data.get("error")
        )

    def add_reference(self, reference_id: UUID) -> None:
        """Add a reference to the response."""
        if reference_id not in self.references:
            self.references.append(reference_id)

    def add_artifact(self, artifact_id: UUID) -> None:
        """Add an artifact to the response."""
        if artifact_id not in self.artifacts:
            self.artifacts.append(artifact_id)

    def update_metadata(self, key: str, value: Any) -> None:
        """Update custom metadata."""
        self.metadata.custom_data[key] = value

    @property
    def total_tokens(self) -> int:
        """Calculate total tokens used."""
        return (self.metadata.tokens + 
                self.metadata.context_tokens + 
                self.metadata.prompt_tokens)

    def validate(self) -> bool:
        """Validate response content and metadata."""
        try:
            assert self.content, "Content cannot be empty"
            assert isinstance(self.content, str), "Content must be a string"
            
            # Validate metadata
            self.metadata.validate()
            
            # Validate format if present
            if self.format:
                self.format.validate()
                assert self.format.type == self.type, "Format type must match response type"
            
            # Validate references and artifacts
            assert all(isinstance(ref, UUID) for ref in self.references), "Invalid reference ID"
            assert all(isinstance(art, UUID) for art in self.artifacts), "Invalid artifact ID"
            
            # Validate error field
            if self.error:
                assert isinstance(self.error, str), "Error must be a string"
                
            return True
        except AssertionError as e:
            raise ValueError(f"Response validation failed: {str(e)}")

    @classmethod
    def create_error(cls, error_message: str, metadata: Optional[ResponseMetadata] = None) -> 'Response':
        """Create an error response."""
        if not metadata:
            metadata = ResponseMetadata(
                created_at=datetime.now(),
                processing_time=0.0,
                model="error",
                tokens=0,
                context_tokens=0,
                prompt_tokens=0,
                finish_reason="error"
            )
        
        return cls(
            content=error_message,
            type=ResponseType.ERROR,
            metadata=metadata,
            error=error_message
        )