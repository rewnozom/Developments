from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

class ConversationState(Enum):
    """Enumeration of conversation states."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    ERROR = "error"

class MessageRole(Enum):
    """Enumeration of message roles."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"

@dataclass
class Message:
    """Represents a single message in a conversation."""
    role: MessageRole
    content: str
    id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    function_call: Optional[Dict[str, Any]] = None
    tokens: Optional[int] = None
    parent_id: Optional[UUID] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": str(self.id),
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "function_call": self.function_call,
            "tokens": self.tokens,
            "parent_id": str(self.parent_id) if self.parent_id else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary."""
        return cls(
            id=UUID(data["id"]),
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
            function_call=data.get("function_call"),
            tokens=data.get("tokens"),
            parent_id=UUID(data["parent_id"]) if data.get("parent_id") else None,
        )

@dataclass
class ConversationMetadata:
    """Metadata for a conversation."""
    created_at: datetime
    modified_at: datetime
    total_messages: int
    total_tokens: int
    user_id: Optional[str]
    labels: List[str] = field(default_factory=list)
    custom_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Conversation:
    """Represents a conversation between user and assistant."""
    id: UUID = field(default_factory=uuid4)
    messages: List[Message] = field(default_factory=list)
    state: ConversationState = ConversationState.ACTIVE
    metadata: ConversationMetadata = field(default_factory=lambda: ConversationMetadata(
        created_at=datetime.now(),
        modified_at=datetime.now(),
        total_messages=0,
        total_tokens=0,
        user_id=None
    ))

    def add_message(self, message: Message) -> None:
        """Add a message to the conversation."""
        self.messages.append(message)
        self.metadata.total_messages += 1
        if message.tokens:
            self.metadata.total_tokens += message.tokens
        self.metadata.modified_at = datetime.now()

    def get_message(self, message_id: UUID) -> Optional[Message]:
        """Get a specific message by ID."""
        return next((msg for msg in self.messages if msg.id == message_id), None)

    def get_context_window(self, 
                         max_tokens: int,
                         from_message_id: Optional[UUID] = None) -> List[Message]:
        """Get context window of messages within token limit."""
        context = []
        total_tokens = 0
        messages = self.messages
        
        if from_message_id:
            start_idx = next((i for i, msg in enumerate(messages) 
                           if msg.id == from_message_id), 0)
            messages = messages[start_idx:]

        for msg in reversed(messages):
            if msg.tokens and total_tokens + msg.tokens > max_tokens:
                break
            context.insert(0, msg)
            if msg.tokens:
                total_tokens += msg.tokens

        return context

    def update_state(self, new_state: ConversationState) -> None:
        """Update conversation state."""
        self.state = new_state
        self.metadata.modified_at = datetime.now()

    def add_label(self, label: str) -> None:
        """Add a label to the conversation."""
        if label not in self.metadata.labels:
            self.metadata.labels.append(label)
            self.metadata.modified_at = datetime.now()

    def remove_label(self, label: str) -> bool:
        """Remove a label from the conversation."""
        if label in self.metadata.labels:
            self.metadata.labels.remove(label)
            self.metadata.modified_at = datetime.now()
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary."""
        return {
            "id": str(self.id),
            "state": self.state.value,
            "messages": [msg.to_dict() for msg in self.messages],
            "metadata": {
                "created_at": self.metadata.created_at.isoformat(),
                "modified_at": self.metadata.modified_at.isoformat(),
                "total_messages": self.metadata.total_messages,
                "total_tokens": self.metadata.total_tokens,
                "user_id": self.metadata.user_id,
                "labels": self.metadata.labels,
                "custom_data": self.metadata.custom_data
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create conversation from dictionary."""
        metadata = ConversationMetadata(
            created_at=datetime.fromisoformat(data["metadata"]["created_at"]),
            modified_at=datetime.fromisoformat(data["metadata"]["modified_at"]),
            total_messages=data["metadata"]["total_messages"],
            total_tokens=data["metadata"]["total_tokens"],
            user_id=data["metadata"]["user_id"],
            labels=data["metadata"]["labels"],
            custom_data=data["metadata"]["custom_data"]
        )
        
        return cls(
            id=UUID(data["id"]),
            messages=[Message.from_dict(msg) for msg in data["messages"]],
            state=ConversationState(data["state"]),
            metadata=metadata
        )