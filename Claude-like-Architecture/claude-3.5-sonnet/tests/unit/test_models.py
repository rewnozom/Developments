# tests/unit/test_models.py
import pytest
from datetime import datetime
from uuid import UUID, uuid4
from models.conversation import (
    Conversation,
    Message,
    MessageRole,
    ConversationState
)
from models.artifacts import Artifact, ArtifactType
from models.llm_models import (
    ModelProvider,
    ModelConfig,
    ModelResponse,
    LLMManager
)


class TestConversation:
    def test_create_conversation(self):
        conversation = Conversation()
        assert isinstance(conversation.id, UUID)
        assert len(conversation.messages) == 0
        assert conversation.state == ConversationState.ACTIVE

    def test_add_message(self):
        conversation = Conversation()
        message = Message(role="user", content="Hello")
        
        conversation.add_message(message)
        assert len(conversation.messages) == 1
        assert conversation.metadata.total_messages == 1

    def test_get_context_window(self):
        conversation = Conversation()
        
        # Add messages with tokens
        for i in range(5):
            message = Message(
                role="user",
                content=f"Message {i}",
                tokens=10
            )
            conversation.add_message(message)
        
        context = conversation.get_context_window(max_tokens=25)
        assert len(context) <= 3  # Should only include last 2-3 messages


class TestMessage:
    def test_create_message(self):
        message = Message(role="user", content="Hello")
        
        assert isinstance(message.id, UUID)
        assert message.role == "user"
        assert message.content == "Hello"
        assert isinstance(message.timestamp, datetime)

    def test_message_to_dict(self):
        message = Message(role="user", content="Hello")
        data = message.to_dict()
        
        assert isinstance(data, dict)
        assert data['role'] == "user"
        assert data['content'] == "Hello"

    def test_message_from_dict(self):
        data = {
            'id': str(uuid4()),
            'role': "user",
            'content': "Hello",
            'timestamp': datetime.now().isoformat()
        }
        
        message = Message.from_dict(data)
        assert isinstance(message, Message)
        assert message.role == "user"
        assert message.content == "Hello"


class TestArtifact:
    def test_create_artifact(self):
        artifact = Artifact(
            type=ArtifactType.CODE,
            content="print('hello')",
            identifier="test-code",
            title="Test Code"
        )
        
        assert isinstance(artifact.id, UUID)
        assert artifact.type == ArtifactType.CODE
        assert artifact.validate()

    def test_invalid_content(self):
        artifact = Artifact(
            type=ArtifactType.CODE,
            content="",  # Empty content
            identifier="test-code",
            title="Test Code"
        )
        
        validation = artifact.validate()
        assert not validation.valid
        assert len(validation.errors) > 0

    def test_update_content(self):
        artifact = Artifact(
            type=ArtifactType.CODE,
            content="print('hello')",
            identifier="test-code",
            title="Test Code"
        )
        
        artifact.update_content("print('world')")
        assert artifact.content == "print('world')"
        assert artifact.metadata.modified_at > artifact.metadata.created_at


class TestLLMModels:
    @pytest.fixture
    def llm_manager(self) -> LLMManager:
        return LLMManager()

    def test_model_configuration(self, llm_manager: LLMManager):
        """Test model configuration."""
        assert llm_manager.current_model
        assert llm_manager.current_model in llm_manager.models

        model_config = llm_manager.models[llm_manager.current_model]
        assert isinstance(model_config, ModelConfig)
        assert model_config.temperature >= 0
        assert model_config.max_tokens > 0

    @pytest.mark.asyncio
    async def test_response_generation(self, llm_manager: LLMManager):
        """Test response generation."""
        messages = [
            {"role": "user", "content": "Hello"}
        ]

        response = await llm_manager.generate_response(messages)
        assert isinstance(response, ModelResponse)
        assert response.content
        assert response.total_tokens > 0

    def test_model_switching(self, llm_manager: LLMManager):
        """Test model switching."""
        original_model = llm_manager.current_model
        
        # Switch to different model
        available_models = list(llm_manager.models.keys())
        different_model = next(m for m in available_models if m != original_model)
        
        llm_manager.set_current_model(different_model)
        assert llm_manager.current_model == different_model

        # Switch back
        llm_manager.set_current_model(original_model)
        assert llm_manager.current_model == original_model