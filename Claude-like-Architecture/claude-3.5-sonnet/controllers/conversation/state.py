# controllers/conversation/state.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from enum import Enum
from models.conversation import Conversation
from core.exceptions import StateError

class ConversationState(Enum):
    """Enumeration of conversation states."""
    INITIALIZED = "initialized"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class StateTransition:
    """Record of state transition."""
    from_state: ConversationState
    to_state: ConversationState
    timestamp: datetime
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class StateManager:
    """Manages conversation state and transitions."""

    def __init__(self):
        self.states: Dict[UUID, ConversationState] = {}
        self.transitions: Dict[UUID, List[StateTransition]] = {}
        self.valid_transitions: Dict[ConversationState, List[ConversationState]] = {
            ConversationState.INITIALIZED: [ConversationState.ACTIVE, ConversationState.ERROR],
            ConversationState.ACTIVE: [ConversationState.PAUSED, ConversationState.COMPLETED, ConversationState.ERROR],
            ConversationState.PAUSED: [ConversationState.ACTIVE, ConversationState.COMPLETED, ConversationState.ERROR],
            ConversationState.COMPLETED: [ConversationState.ERROR],
            ConversationState.ERROR: [ConversationState.INITIALIZED]
        }

    def initialize_state(self, conversation: Conversation) -> bool:
        """Initialize conversation state."""
        try:
            if not isinstance(conversation.id, UUID):
                raise StateError("Invalid conversation ID type")

            if conversation.id in self.states:
                raise StateError("Conversation already initialized")

            self.states[conversation.id] = ConversationState.INITIALIZED
            self.transitions[conversation.id] = []
            
            return True

        except Exception as e:
            raise StateError(f"State initialization failed: {str(e)}")

    def transition_state(self,
                        conversation_id: UUID,
                        to_state: ConversationState,
                        reason: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Transition conversation to new state."""
        if conversation_id not in self.states:
            raise StateError("Conversation not found")

        current_state = self.states[conversation_id]

        # Validate transition
        if to_state not in self.valid_transitions[current_state]:
            raise StateError(f"Invalid state transition: {current_state} -> {to_state}")

        try:
            # Record transition
            transition = StateTransition(
                from_state=current_state,
                to_state=to_state,
                timestamp=datetime.now(),
                reason=reason,
                metadata=metadata
            )
            
            self.transitions[conversation_id].append(transition)

            # Update state
            self.states[conversation_id] = to_state
            
            return True

        except Exception as e:
            raise StateError(f"State transition failed: {str(e)}")

    def get_state(self, conversation_id: UUID) -> Optional[ConversationState]:
        """Get current state of conversation."""
        return self.states.get(conversation_id)

    def get_transitions(self, conversation_id: UUID) -> List[StateTransition]:
        """Get transition history for conversation."""
        return self.transitions.get(conversation_id, [])

    def validate_state(self,
                      conversation_id: UUID,
                      expected_state: ConversationState) -> bool:
        """Validate conversation is in expected state."""
        current_state = self.get_state(conversation_id)
        return current_state == expected_state

    def can_transition(self,
                      conversation_id: UUID,
                      to_state: ConversationState) -> bool:
        """Check if state transition is valid."""
        current_state = self.get_state(conversation_id)
        if not current_state:
            return False
            
        return to_state in self.valid_transitions[current_state]

    def get_valid_transitions(self,
                            conversation_id: UUID) -> List[ConversationState]:
        """Get valid transition states for conversation."""
        current_state = self.get_state(conversation_id)
        if not current_state:
            return []
            
        return self.valid_transitions[current_state]

    def reset_state(self, conversation_id: UUID) -> bool:
        """Reset conversation to initialized state."""
        if conversation_id not in self.states:
            return False

        try:
            return self.transition_state(
                conversation_id,
                ConversationState.INITIALIZED,
                reason="State reset"
            )
        except Exception:
            return False

    def clear_state(self, conversation_id: UUID) -> bool:
        """Clear conversation state and history."""
        self.states.pop(conversation_id, None)
        self.transitions.pop(conversation_id, None)
        return True