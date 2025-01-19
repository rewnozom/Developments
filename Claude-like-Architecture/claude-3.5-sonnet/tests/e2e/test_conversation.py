# tests/e2e/test_conversation.py
import pytest
from datetime import datetime, timedelta
from models.conversation import Conversation, Message, ConversationState
from controllers.conversation import ConversationFlow, ConversationContext, StateManager
from processors import InputProcessor, ContentProcessor, FormatProcessor

class TestEndToEndConversation:
    def test_complete_conversation_flow(self):
        # Initialize all components
        input_processor = InputProcessor()
        content_processor = ContentProcessor()
        format_processor = FormatProcessor()
        
        flow = ConversationFlow()
        context = ConversationContext()
        state = StateManager()
        
        # Create conversation
        conversation = Conversation()
        
        # Initialize systems
        state.initialize_state(conversation)
        context.manage_context(conversation)
        flow.manage_flow(conversation)
        
        # Process user input
        user_inputs = [
            "Hello!",
            "Can you help me with Python?",
            "How do I create a list?",
            "Thank you!"
        ]
        
        for user_input in user_inputs:
            # Process input
            input_result = input_processor.process_input(
                user_input,
                "text"
            )
            
            # Process content
            content_result = content_processor.process_content(
                input_result.content,
                "text"
            )
            
            # Format response
            format_result = format_processor.format_content(
                content_result.processed,
                "text"
            )
            
            # Add user message
            user_message = Message(
                role="user",
                content=format_result.content
            )
            flow.add_message(conversation.id, user_message)
            
            # Simulate assistant response
            assistant_response = f"Processing: {user_input}"
            assistant_message = Message(
                role="assistant",
                content=assistant_response
            )
            flow.add_message(conversation.id, assistant_message)
            
        # Verify conversation state
        assert state.get_state(conversation.id) == ConversationState.ACTIVE
        assert len(conversation.messages) == len(user_inputs) * 2  # User + Assistant messages
        
        # Check context
        context_items = context.get_context(conversation.id)
        assert len(context_items) > 0
        
        # Verify metrics
        metrics = flow.get_metrics(conversation.id)
        assert metrics[-1].total_messages == len(conversation.messages)
        assert metrics[-1].engagement_score > 0
        
        # End conversation
        state.transition_state(
            conversation.id,
            ConversationState.COMPLETED,
            reason="Conversation completed successfully"
        )
        
        assert state.get_state(conversation.id) == ConversationState.COMPLETED
        
    def test_error_recovery_flow(self):
        # Initialize components
        flow = ConversationFlow()
        context = ConversationContext()
        state = StateManager()
        
        conversation = Conversation()
        
        # Initialize systems
        state.initialize_state(conversation)
        context.manage_context(conversation)
        flow.manage_flow(conversation)
        
        # Start normal conversation
        message = Message(role="user", content="Hello!")
        flow.add_message(conversation.id, message)
        
        # Simulate error
        try:
            flow.add_message(UUID(), message)  # Invalid conversation ID
        except Exception:
            # Transition to error state
            state.transition_state(
                conversation.id,
                ConversationState.ERROR,
                reason="Error occurred"
            )
            
        assert state.get_state(conversation.id) == ConversationState.ERROR
        
        # Attempt recovery
        state.transition_state(
            conversation.id,
            ConversationState.INITIALIZED,
            reason="Recovery attempt"
        )
        
        # Resume conversation
        message = Message(role="user", content="Recovered!")
        flow.add_message(conversation.id, message)
        
        state.transition_state(
            conversation.id,
            ConversationState.ACTIVE,
            reason="Recovery successful"
        )
        
        assert state.get_state(conversation.id) == ConversationState.ACTIVE
        
    def test_performance_metrics(self):
        # Initialize components
        flow = ConversationFlow()
        conversation = Conversation()
        flow.manage_flow(conversation)
        
        # Generate test messages with controlled timing
        start_time = datetime.now()
        
        for i in range(5):
            # User message
            user_message = Message(
                role="user",
                content=f"Message {i}",
                timestamp=start_time + timedelta(seconds=i*2)
            )
            flow.add_message(conversation.id, user_message)
            
            # Assistant response
            assistant_message = Message(
                role="assistant",
                content=f"Response {i}",
                timestamp=start_time + timedelta(seconds=i*2 + 1)
            )
            flow.add_message(conversation.id, assistant_message)
            
        # Get metrics
        metrics = flow.get_metrics(conversation.id)
        final_metrics = metrics[-1]
        
        # Verify metrics
        assert final_metrics.total_messages == 10  # 5 pairs of messages
        assert 0 < final_metrics.average_response_time <= 2  # Response within 2 seconds
        assert 0 <= final_metrics.topic_changes <= 5  # Some topic changes expected
        assert 0 <= final_metrics.engagement_score <= 1  # Valid engagement score