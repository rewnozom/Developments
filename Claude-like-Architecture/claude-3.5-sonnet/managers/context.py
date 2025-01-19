# managers/context.py
from typing import Dict, List, Optional, Any, Deque
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class ContextItem:
    """Individual context item."""
    id: UUID
    content: Any
    timestamp: datetime
    priority: int
    ttl: Optional[int] = None
    metadata: Dict[str, Any] = None

class ContextManager:
    """Manages conversation context and state."""

    def __init__(self, max_context_size: int = 1000):
        self.max_context_size = max_context_size
        self.context: Deque[ContextItem] = deque(maxlen=max_context_size)
        self.priority_items: Dict[UUID, ContextItem] = {}
        self.last_cleanup: datetime = datetime.now()

    def add_context(self, 
                content: Any,
                priority: int = 0,
                ttl: Optional[int] = None,
                metadata: Optional[Dict[str, Any]] = None) -> UUID:
        """Add item to context."""
        try:
            if content is None:
                raise ContextError("Content cannot be None")
                
            if not isinstance(priority, int):
                raise ContextError("Priority must be an integer")
                
            if ttl is not None and not isinstance(ttl, (int, float)):
                raise ContextError("TTL must be a number")
                
            if metadata is not None and not isinstance(metadata, dict):
                raise ContextError("Metadata must be a dictionary")

            item_id = UUID.uuid4()  # Generate UUID explicitly
            
            item = ContextItem(
                id=item_id,
                content=content,
                timestamp=datetime.now(),
                priority=priority,
                ttl=ttl,
                metadata=metadata or {}
            )

            if priority > 0:
                self.priority_items[item.id] = item

            self.context.append(item)
            self._cleanup_expired()
            return item.id

        except Exception as e:
            raise ContextError(f"Failed to add context: {str(e)}")

    def get_context(self, 
                   max_items: Optional[int] = None,
                   min_priority: int = 0) -> List[ContextItem]:
        """Get context items."""
        self._cleanup_expired()
        
        items = [item for item in self.context 
                if item.priority >= min_priority]
        
        if max_items:
            items = items[-max_items:]
            
        return items

    def update_context(self,
                      item_id: UUID,
                      content: Optional[Any] = None,
                      priority: Optional[int] = None,
                      ttl: Optional[int] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update context item."""
        for item in self.context:
            if item.id == item_id:
                if content is not None:
                    item.content = content
                if priority is not None:
                    item.priority = priority
                    if priority > 0:
                        self.priority_items[item.id] = item
                    elif item.id in self.priority_items:
                        del self.priority_items[item.id]
                if ttl is not None:
                    item.ttl = ttl
                if metadata is not None:
                    item.metadata = metadata
                return True
        return False

    def remove_context(self, item_id: UUID) -> bool:
        """Remove context item."""
        self.context = deque(
            [item for item in self.context if item.id != item_id],
            maxlen=self.max_context_size
        )
        self.priority_items.pop(item_id, None)
        return True

    def clear_context(self, 
                     preserve_priority: bool = True) -> None:
        """Clear all context items."""
        if preserve_priority:
            self.context = deque(
                self.priority_items.values(),
                maxlen=self.max_context_size
            )
        else:
            self.context.clear()
            self.priority_items.clear()

    def _cleanup_expired(self) -> None:
        """Clean up expired context items."""
        now = datetime.now()
        if (now - self.last_cleanup).total_seconds() < 60:
            return

        self.context = deque(
            [item for item in self.context if not self._is_expired(item)],
            maxlen=self.max_context_size
        )
        
        # Clean up priority items
        expired_priorities = [
            item_id for item_id, item in self.priority_items.items()
            if self._is_expired(item)
        ]
        for item_id in expired_priorities:
            del self.priority_items[item_id]

        self.last_cleanup = now

    def _is_expired(self, item: ContextItem) -> bool:
        """Check if context item is expired."""
        if item.ttl is None:
            return False
        age = (datetime.now() - item.timestamp).total_seconds()
        return age > item.ttl

    def get_context_size(self) -> int:
        """Get current context size."""
        return len(self.context)

    def get_priority_items(self) -> Dict[UUID, ContextItem]:
        """Get all priority items."""
        return self.priority_items.copy()

    def optimize_context(self) -> None:
        """Optimize context by removing low-priority items."""
        if len(self.context) < self.max_context_size * 0.9:
            return

        # Keep high-priority items and recent items
        items = sorted(
            self.context,
            key=lambda x: (x.priority, x.timestamp),
            reverse=True
        )
        
        self.context = deque(
            items[:self.max_context_size],
            maxlen=self.max_context_size
        )

class ContextError(Exception):
    """Base class for context-related errors."""
    pass

class ContextLimitError(ContextError):
    """Raised when context size limit is reached."""
    pass

class ContextItemNotFoundError(ContextError):
    """Raised when context item is not found."""
    pass