# tests/unit/test_controllers.py
import pytest
from datetime import datetime, timedelta
from typing import List
from uuid import UUID
from controllers.conversation import (
    ConversationFlow,
    ConversationContext,
    StateManager
)
from models.conversation import (
    Conversation,
    Message,
    ConversationState
)
from core.exceptions import ConversationError, ContextError, StateError


class TestConversationFlow:
    @pytest.fixture
    def conversation(self) -> Conversation:
        return Conversation()

    @pytest.fixture
    def flow_controller(self) -> ConversationFlow:
        return ConversationFlow()

    def test_manage_flow(self, flow_controller: ConversationFlow, conversation: Conversation):
        """Test managing the flow."""
        assert flow_controller.manage_flow(conversation)
        assert conversation.id in flow_controller.active_conversations

    def test_add_message(self, flow_controller: ConversationFlow, conversation: Conversation):
        """Test adding a message."""
        flow_controller.manage_flow(conversation)
        message = Message(role="user", content="Hello")
        assert flow_controller.add_message(conversation.id, message)
        assert len(conversation.messages) == 1

    def test_message_handling(self, flow_controller: ConversationFlow, conversation: Conversation):
        """Test message handling."""
        flow_controller.manage_flow(conversation)

        messages = [
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi!"),
            Message(role="user", content="How are you?"),
            Message(role="assistant", content="I'm doing well!")
        ]

        for msg in messages:
            assert flow_controller.add_message(conversation.id, msg)

        metrics = flow_controller.get_metrics(conversation.id)
        assert len(metrics) > 0
        assert metrics[-1].total_messages == len(messages)
        assert metrics[-1].engagement_score > 0

    def test_coherence_maintenance(self, flow_controller: ConversationFlow, conversation: Conversation):
        """Test conversation coherence."""
        flow_controller.manage_flow(conversation)

        messages = [
            Message(role="user", content="What is Python?"),
            Message(role="assistant", content="Python is a programming language."),
            Message(role="user", content="Can you tell me more about Python programming?"),
            Message(role="assistant", content="Python is known for its simplicity and readability.")
        ]

        for msg in messages:
            flow_controller.add_message(conversation.id, msg)

        coherence = flow_controller.maintain_coherence(conversation)
        assert coherence > 0.7

    def test_engagement_optimization(self, flow_controller: ConversationFlow, conversation: Conversation):
        """Test engagement optimization."""
        flow_controller.manage_flow(conversation)

        start_time = datetime.now()
        messages = []

        for i in range(5):
            msg_time = start_time + timedelta(seconds=i * 2)
            user_msg = Message(
                role="user",
                content=f"Message {i}",
                timestamp=msg_time
            )
            asst_msg = Message(
                role="assistant",
                content=f"Response {i}",
                timestamp=msg_time + timedelta(seconds=1)
            )
            messages.extend([user_msg, asst_msg])

        for msg in messages:
            flow_controller.add_message(conversation.id, msg)

        engagement = flow_controller.optimize_engagement(conversation)
        assert engagement > 0.6


class TestConversationContext:
    def test_manage_context(self):
        context = ConversationContext()
        conversation = Conversation()

        assert context.manage_context(conversation)
        assert conversation.id in context.context_items

    def test_add_context_item(self):
        context = ConversationContext()
        conversation = Conversation()
        context.manage_context(conversation)

        item_id = context.add_context_item(
            conversation.id,
            "Important information",
            importance=0.8
        )

        assert isinstance(item_id, UUID)
        assert len(context.get_context(conversation.id)) == 1

    def test_importance_threshold(self):
        context = ConversationContext()
        conversation = Conversation()
        context.manage_context(conversation, importance_threshold=0.7)

        context.add_context_item(
            conversation.id,
            "Less important",
            importance=0.5
        )

        items = context.get_context(conversation.id, min_importance=0.7)
        assert len(items) == 0


class TestStateManager:
    def test_initialize_state(self):
        manager = StateManager()
        conversation = Conversation()

        assert manager.initialize_state(conversation)
        assert conversation.id in manager.states

    def test_transition_state(self):
        manager = StateManager()
        conversation = Conversation()
        manager.initialize_state(conversation)

        assert manager.transition_state(
            conversation.id,
            ConversationState.ACTIVE,
            reason="Starting conversation"
        )

        assert manager.get_state(conversation.id) == ConversationState.ACTIVE

    def test_invalid_transition(self):
        manager = StateManager()
        conversation = Conversation()
        manager.initialize_state(conversation)

        with pytest.raises(StateError):
            manager.transition_state(
                conversation.id,
                ConversationState.COMPLETED
            )
