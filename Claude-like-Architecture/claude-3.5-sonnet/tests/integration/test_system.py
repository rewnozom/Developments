# tests/integration/test_system.py
import pytest
from pathlib import Path
from models.conversation import Conversation
from processors import InputProcessor, ContentProcessor
from controllers.conversation import ConversationFlow
from core.exceptions import SystemError

class TestSystemIntegration:
    def test_system_workflow(self, tmp_path: Path):
        # Initialize components
        input_processor = InputProcessor()
        content_processor = ContentProcessor()
        conversation_flow = ConversationFlow()
        
        # Process input
        input_result = input_processor.process_input(
            "Hello, how are you?",
            "text"
        )
# tests/integration/test_system.py (continued)
        assert input_result.validation_result['valid']
        
        # Process content
        content_result = content_processor.process_content(
            input_result.content,
            "text",
            {"lowercase": True}
        )
        
        # Create conversation
        conversation = Conversation()
        conversation_flow.manage_flow(conversation)
        
        # Add processed message
        message = Message(
            role="user",
            content=content_result.processed
        )
        conversation_flow.add_message(conversation.id, message)
        
        # Verify workflow
        assert len(conversation.messages) == 1
        assert conversation.messages[0].content == "hello, how are you?"
        
        # Test error handling
        with pytest.raises(SystemError):
            input_processor.process_input("", "text")  # Empty input
            
    def test_component_interaction(self):
        # Initialize components
        input_processor = InputProcessor()
        content_processor = ContentProcessor()
        conversation_flow = ConversationFlow()
        
        # Test component interaction
        conversation = Conversation()
        conversation_flow.manage_flow(conversation)
        
        # Process multiple messages
        messages = [
            "Hello!",
            "How are you?",
            "Let's talk about Python"
        ]
        
        for content in messages:
            # Process input
            input_result = input_processor.process_input(content, "text")
            
            # Process content
            content_result = content_processor.process_content(
                input_result.content,
                "text"
            )
            
            # Add to conversation
            message = Message(
                role="user",
                content=content_result.processed
            )
            conversation_flow.add_message(conversation.id, message)
            
        # Verify interaction
        assert len(conversation.messages) == len(messages)
        assert conversation_flow.get_metrics(conversation.id)[-1].total_messages == len(messages)