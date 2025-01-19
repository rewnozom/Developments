# controllers/conversation/context.py
from typing import Dict, List, Optional, Any, Deque
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4
from models.conversation import Conversation, Message
from core.exceptions import *

@dataclass
class ContextItem:
    """Individual context item."""
    id: UUID
    content: Any
    timestamp: datetime
    importance: float
    ttl: Optional[int] = None
    metadata: Dict[str, Any] = None

class ConversationContext:
    """Manages conversation context and memory."""

    def __init__(self, max_context_size: int = 1000):
        try:
            self.max_context_size = max_context_size
            self.context_items: Dict[UUID, Deque[ContextItem]] = {}
            self.importance_thresholds: Dict[UUID, float] = {}
            self.last_cleanup: datetime = datetime.now()
        except Exception as e:
            raise ContextInitializationError(
                f"Failed to initialize conversation context: {str(e)}",
                failed_component="initialization"
            )

    def manage_context(self, 
                      conversation: Conversation,
                      importance_threshold: float = 0.5) -> bool:
        """Manage conversation context."""
        try:
            if not isinstance(conversation.id, UUID):
                raise ValueError("Invalid conversation ID type")

            # Initialize context if needed
            if conversation.id not in self.context_items:
                self.context_items[conversation.id] = deque(maxlen=self.max_context_size)
                self.importance_thresholds[conversation.id] = importance_threshold

            # Process new messages
            self._process_new_messages(conversation)

            # Cleanup expired items
            self._cleanup_expired_items(conversation.id)

            return True

        except ValueError as e:
            raise ContextError(f"Invalid conversation format: {str(e)}")
        except Exception as e:
            raise ContextError(f"Context management failed: {str(e)}")

    def add_context_item(self,
                        conversation_id: UUID,
                        content: Any,
                        importance: float,
                        ttl: Optional[int] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> UUID:
        """Add item to conversation context."""
        if conversation_id not in self.context_items:
            raise ContextError("Conversation not found")

        try:
            new_id = uuid4()  # Generate UUID here
            item = ContextItem(
                id=new_id,  # Use the generated UUID
                content=content,
                timestamp=datetime.now(),
                importance=importance,
                ttl=ttl,
                metadata=metadata or {}
            )

            self.context_items[conversation_id].append(item)
            return new_id  # Return the new UUID

        except Exception as e:
            raise ContextError(f"Failed to add context item: {str(e)}")

    def get_context(self,
                   conversation_id: UUID,
                   min_importance: Optional[float] = None) -> List[ContextItem]:
        """Get context items for conversation."""
        if conversation_id not in self.context_items:
            return []

        items = list(self.context_items[conversation_id])
        
        if min_importance is not None:
            items = [item for item in items if item.importance >= min_importance]
            
        return items

    def update_importance(self,
                         conversation_id: UUID,
                         item_id: UUID,
                         importance: float) -> bool:
        """Update importance of context item."""
        if conversation_id not in self.context_items:
            return False

        for item in self.context_items[conversation_id]:
            if item.id == item_id:
                item.importance = importance
                return True
                
        return False

    def remove_context_item(self,
                          conversation_id: UUID,
                          item_id: UUID) -> bool:
        """Remove item from context."""
        if conversation_id not in self.context_items:
            return False

        self.context_items[conversation_id] = deque(
            [item for item in self.context_items[conversation_id]
             if item.id != item_id],
            maxlen=self.max_context_size
        )
        
        return True

    def clear_context(self,
                     conversation_id: UUID,
                     min_importance: Optional[float] = None) -> None:
        """Clear conversation context."""
        if conversation_id not in self.context_items:
            return

        if min_importance is not None:
            self.context_items[conversation_id] = deque(
                [item for item in self.context_items[conversation_id]
                 if item.importance >= min_importance],
                maxlen=self.max_context_size
            )
        else:
            self.context_items[conversation_id].clear()

    def _process_new_messages(self, conversation: Conversation) -> None:
        """Process new messages and update context."""
        last_processed = max(
            (item.timestamp for item in self.context_items[conversation.id]),
            default=datetime.min
        )
        
        new_messages = [
            msg for msg in conversation.messages
            if msg.timestamp > last_processed
        ]
        
        for message in new_messages:
            importance = self._calculate_message_importance(message)
            
            if importance >= self.importance_thresholds[conversation.id]:
                self.add_context_item(
                    conversation.id,
                    message.content,
                    importance,
                    metadata={'message_id': str(message.id)}
                )

    def _cleanup_expired_items(self, conversation_id: UUID) -> None:
        """Clean up expired context items."""
        now = datetime.now()
        
        # Only cleanup periodically
        if (now - self.last_cleanup).total_seconds() < 60:
            return

        self.context_items[conversation_id] = deque(
            [item for item in self.context_items[conversation_id]
                if not self._is_expired(item)],
            maxlen=self.max_context_size
        )
        
        self.last_cleanup = now

    def _is_expired(self, item: ContextItem) -> bool:
        """Check if context item is expired."""
        if item.ttl is None:
            return False
            
        age = (datetime.now() - item.timestamp).total_seconds()
        return age > item.ttl

    def _calculate_message_importance(self, message: Message) -> float:
        """Calculate importance score for message."""
        # Calculate based on multiple factors
        length_score = min(len(message.content) / 500.0, 1.0)
        
        # Higher importance for user messages
        role_score = 1.0 if message.role == "user" else 0.8
        
        # Higher importance for recent messages
        age = (datetime.now() - message.timestamp).total_seconds()
        time_score = max(0, 1.0 - (age / 3600.0))  # Decay over 1 hour
        
        # Calculate weighted average
        importance = (
            length_score * 0.3 +
            role_score * 0.4 +
            time_score * 0.3
        )
        
        return importance

    def optimize_context(self, conversation_id: UUID) -> None:
        """Optimize context by removing less important items."""
        if conversation_id not in self.context_items:
            return

        if len(self.context_items[conversation_id]) < self.max_context_size * 0.9:
            return

        # Keep only most important items
        items = sorted(
            self.context_items[conversation_id],
            key=lambda x: x.importance,
            reverse=True
        )
        
        self.context_items[conversation_id] = deque(
            items[:self.max_context_size],
            maxlen=self.max_context_size
        )

    def get_context_size(self, conversation_id: UUID) -> int:
        """Get current context size."""
        if conversation_id not in self.context_items:
            return 0
        return len(self.context_items[conversation_id])

    def get_importance_threshold(self, conversation_id: UUID) -> Optional[float]:
        """Get importance threshold for conversation."""
        return self.importance_thresholds.get(conversation_id)

    def update_importance_threshold(self,
                                    conversation_id: UUID,
                                    threshold: float) -> bool:
        """Update importance threshold for conversation."""
        if conversation_id not in self.context_items:
            return False
            
        self.importance_thresholds[conversation_id] = threshold
        return True