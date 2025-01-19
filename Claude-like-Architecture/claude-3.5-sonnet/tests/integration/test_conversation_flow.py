# tests/integration/test_conversation_flow.py
import pytest
from datetime import datetime
from models.conversation import Conversation, Message
from controllers.conversation import ConversationFlow, ConversationContext, StateManager, ConversationState

class TestConversationIntegration:
    def test_full_conversation_flow(self):
        # Initialize components
        flow = ConversationFlow()
        context = ConversationContext()
        state = StateManager()
        
        # Create conversation
        conversation = Conversation()
        
        # Initialize state and context
        state.initialize_state(conversation)
        context.manage_context(conversation)
        flow.manage_flow(conversation)
        
        # Add messages
        messages = [
            Message(role="user", content="Hello!"),
            Message(role="assistant", content="Hi! How can I help?"),
            Message(role="user", content="Tell me about Python"),
            Message(role="assistant", content="Python is a programming language...")
        ]
        
        for message in messages:
            flow.add_message(conversation.id, message)
            
        # Verify state
        assert state.get_state(conversation.id) == ConversationState.ACTIVE
        
        # Check metrics
        metrics = flow.get_metrics(conversation.id)
        assert len(metrics) > 0
        assert metrics[-1].total_messages == len(messages)
        
        # Verify context
        context_items = context.get_context(conversation.id)
        assert len(context_items) > 0
        
        # End conversation
        state.transition_state(
            conversation.id,
            ConversationState.COMPLETED,
            reason="Conversation completed"
        )
        
        assert state.get_state(conversation.id) == ConversationState.COMPLETED

    def test_error_handling(self):
        flow = ConversationFlow()
        context = ConversationContext()
        state = StateManager()
        
        conversation = Conversation()
        
        # Initialize components
        state.initialize_state(conversation)
        context.manage_context(conversation)
        flow.manage_flow(conversation)
        
        # Test error handling
        with pytest.raises(Exception):
            flow.add_message(UUID(), Message(role="user", content="Invalid"))
            
        # Verify error state
        state.transition_state(
            conversation.id,
            ConversationState.ERROR,
            reason="Error occurred"
        )
        
        assert state.get_state(conversation.id) == ConversationState.ERROR