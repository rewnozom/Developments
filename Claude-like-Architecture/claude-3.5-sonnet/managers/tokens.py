# managers/tokens.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class TokenType(Enum):
    """Types of tokens."""
    PROMPT = "prompt"
    COMPLETION = "completion"
    CONTEXT = "context"
    TOTAL = "total"

@dataclass
class TokenUsage:
    """Token usage information."""
    count: int
    type: TokenType
    timestamp: datetime
    metadata: Dict[str, Any]

class TokenManager:
    """Manages token allocation and tracking."""

    def __init__(self, 
                 max_tokens: int,
                 token_limits: Optional[Dict[TokenType, int]] = None):
        self.max_tokens = max_tokens
        self.token_limits = token_limits or {
            TokenType.PROMPT: max_tokens // 2,
            TokenType.COMPLETION: max_tokens // 2,
            TokenType.CONTEXT: max_tokens // 4,
            TokenType.TOTAL: max_tokens
        }
        self.token_usage: Dict[TokenType, List[TokenUsage]] = {
            token_type: [] for token_type in TokenType
        }

    def allocate_tokens(self, 
                       count: int,
                       token_type: TokenType,
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Allocate tokens for use."""
        if not self.can_allocate(count, token_type):
            return False

        usage = TokenUsage(
            count=count,
            type=token_type,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.token_usage[token_type].append(usage)
        return True

    def can_allocate(self, count: int, token_type: TokenType) -> bool:
        """Check if tokens can be allocated."""
        current_usage = self.get_current_usage(token_type)
        limit = self.token_limits[token_type]
        return current_usage + count <= limit

    def get_current_usage(self, token_type: TokenType) -> int:
        """Get current token usage for type."""
        return sum(usage.count for usage in self.token_usage[token_type])

    def get_available_tokens(self, token_type: TokenType) -> int:
        """Get number of available tokens."""
        current_usage = self.get_current_usage(token_type)
        limit = self.token_limits[token_type]
        return limit - current_usage

    def reset_usage(self, token_type: Optional[TokenType] = None) -> None:
        """Reset token usage tracking."""
        if token_type:
            self.token_usage[token_type].clear()
        else:
            for usage_list in self.token_usage.values():
                usage_list.clear()

    def get_usage_history(self, 
                         token_type: Optional[TokenType] = None,
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> Dict[TokenType, List[TokenUsage]]:
        """Get token usage history."""
        history = {}
        types_to_check = [token_type] if token_type else TokenType

        for t_type in types_to_check:
            usage_list = self.token_usage[t_type]
            filtered_usage = usage_list

            if start_time:
                filtered_usage = [u for u in filtered_usage 
                                if u.timestamp >= start_time]
            if end_time:
                filtered_usage = [u for u in filtered_usage 
                                if u.timestamp <= end_time]

            history[t_type] = filtered_usage

        return history

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get token usage statistics."""
        stats = {
            "total_allocated": sum(
                sum(u.count for u in usage_list)
                for usage_list in self.token_usage.values()
            ),
            "type_usage": {
                t_type.value: self.get_current_usage(t_type)
                for t_type in TokenType
            },
            "available": {
                t_type.value: self.get_available_tokens(t_type)
                for t_type in TokenType
            }
        }
        return stats

    def update_limits(self, 
                     token_type: TokenType,
                     new_limit: int) -> bool:
        """Update token limits."""
        if new_limit < 0 or new_limit > self.max_tokens:
            return False
            
        current_usage = self.get_current_usage(token_type)
        if current_usage > new_limit:
            return False
            
        self.token_limits[token_type] = new_limit
        return True

class TokenError(Exception):
    """Base class for token-related errors."""
    pass

class TokenLimitError(TokenError):
    """Raised when token limit is exceeded."""
    def __init__(self, message: str, requested: int, available: int):
        super().__init__(message)
        self.requested = requested
        self.available = available

class TokenTypeError(TokenError):
    """Raised when token type is invalid."""
    pass