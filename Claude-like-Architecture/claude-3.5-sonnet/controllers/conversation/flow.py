# controllers/conversation/flow.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from models.conversation import Conversation, Message
from core.exceptions import ConversationError

@dataclass
class FlowMetrics:
    """Metrics for conversation flow."""
    total_messages: int
    average_response_time: float
    topic_changes: int
    engagement_score: float
    coherence_score: float

@dataclass
class FlowControl:
    """Control parameters for conversation flow."""
    max_turns: Optional[int] = None
    response_timeout: Optional[float] = None
    topic_limit: Optional[int] = None
    require_acknowledgment: bool = False
    maintain_context: bool = True

class ConversationFlow:
    """Controls conversation flow and progression."""

    def __init__(self):
        self.active_conversations: Dict[UUID, Conversation] = {}
        self.flow_metrics: Dict[UUID, List[FlowMetrics]] = {}
        self.flow_controls: Dict[UUID, FlowControl] = {}

    def manage_flow(self, 
                conversation: Conversation,
                control: Optional[FlowControl] = None) -> bool:
        """Manage conversation flow."""
        try:
            if not isinstance(conversation.id, UUID):
                raise ConversationError("Invalid conversation ID type")

            # Initialize flow control
            if control:
                self.flow_controls[conversation.id] = control
            elif conversation.id not in self.flow_controls:
                self.flow_controls[conversation.id] = FlowControl()

            # Track conversation
            self.active_conversations[conversation.id] = conversation

            # Update metrics
            self._update_metrics(conversation)

            # Check flow controls
            self._check_flow_controls(conversation)

            return True

        except Exception as e:
            raise ConversationError(f"Flow management failed: {str(e)}")

    def add_message(self,
                   conversation_id: UUID,
                   message: Message) -> bool:
        """Add message to conversation."""
        if conversation_id not in self.active_conversations:
            raise ConversationError("Conversation not found")

        conversation = self.active_conversations[conversation_id]
        
        try:
            # Check flow controls
            control = self.flow_controls[conversation_id]
            
            if control.max_turns and len(conversation.messages) >= control.max_turns:
                raise ConversationError("Maximum turns reached")

            # Add message
            conversation.add_message(message)

            # Update metrics
            self._update_metrics(conversation)

            return True

        except Exception as e:
            raise ConversationError(f"Failed to add message: {str(e)}")

    def maintain_coherence(self, conversation: Conversation) -> float:
        """Maintain and measure conversation coherence."""
        try:
            # Calculate coherence metrics
            topic_changes = self._calculate_topic_changes(conversation)
            context_adherence = self._calculate_context_adherence(conversation)
            flow_smoothness = self._calculate_flow_smoothness(conversation)

            # Calculate overall coherence score
            coherence_score = (
                (1.0 - topic_changes/max(len(conversation.messages), 1)) * 0.4 +
                context_adherence * 0.3 +
                flow_smoothness * 0.3
            )

            return coherence_score

        except Exception as e:
            raise ConversationError(f"Coherence calculation failed: {str(e)}")

    def optimize_engagement(self, conversation: Conversation) -> float:
        """Optimize and measure conversation engagement."""
        try:
            # Calculate engagement metrics
            response_times = self._calculate_response_times(conversation)
            interaction_depth = self._calculate_interaction_depth(conversation)
            user_participation = self._calculate_user_participation(conversation)

            # Calculate overall engagement score
            engagement_score = (
                (1.0 - min(response_times/5.0, 1.0)) * 0.3 +
                interaction_depth * 0.4 +
                user_participation * 0.3
            )

            return engagement_score

        except Exception as e:
            raise ConversationError(f"Engagement optimization failed: {str(e)}")

    def _update_metrics(self, conversation: Conversation) -> None:
        """Update flow metrics for conversation."""
        metrics = FlowMetrics(
            total_messages=len(conversation.messages),
            average_response_time=self._calculate_response_times(conversation),
            topic_changes=self._calculate_topic_changes(conversation),
            engagement_score=self.optimize_engagement(conversation),
            coherence_score=self.maintain_coherence(conversation)
        )

        if conversation.id not in self.flow_metrics:
            self.flow_metrics[conversation.id] = []
            
        self.flow_metrics[conversation.id].append(metrics)

    def _check_flow_controls(self, conversation: Conversation) -> None:
        """Check and enforce flow controls."""
        control = self.flow_controls[conversation.id]

        if control.max_turns and len(conversation.messages) > control.max_turns:
            raise ConversationError("Maximum turns exceeded")

        if control.response_timeout:
            if self._calculate_response_times(conversation) > control.response_timeout:
                raise ConversationError("Response timeout exceeded")

        if control.topic_limit:
            if self._calculate_topic_changes(conversation) > control.topic_limit:
                raise ConversationError("Topic change limit exceeded")

    def _calculate_response_times(self, conversation: Conversation) -> float:
        """Calculate average response times."""
        if len(conversation.messages) < 2:
            return 0.0

        response_times = []
        for i in range(1, len(conversation.messages)):
            time_diff = (conversation.messages[i].timestamp -
                        conversation.messages[i-1].timestamp).total_seconds()
            response_times.append(time_diff)

        return sum(response_times) / len(response_times)

    def _calculate_topic_changes(self, conversation: Conversation) -> int:
        """Calculate number of topic changes."""
        # Simple implementation - could be enhanced with NLP
        topic_changes = 0
        for i in range(1, len(conversation.messages)):
            if self._is_topic_change(conversation.messages[i-1],
                                   conversation.messages[i]):
                topic_changes += 1
        return topic_changes

    def _calculate_context_adherence(self, conversation: Conversation) -> float:
        """Calculate context adherence score."""
        # Simple implementation - could be enhanced with more sophisticated analysis
        if len(conversation.messages) < 2:
            return 1.0

        context_scores = []
        for i in range(1, len(conversation.messages)):
            context_scores.append(
                self._calculate_message_context_score(
                    conversation.messages[i-1],
                    conversation.messages[i]
                )
            )

        return sum(context_scores) / len(context_scores)

    def _calculate_flow_smoothness(self, conversation: Conversation) -> float:
        """Calculate conversation flow smoothness."""
        if len(conversation.messages) < 2:
            return 1.0

        smoothness_scores = []
        for i in range(1, len(conversation.messages)):
            smoothness_scores.append(
                self._calculate_transition_smoothness(
                    conversation.messages[i-1],
                    conversation.messages[i]
                )
            )

        return sum(smoothness_scores) / len(smoothness_scores)

    def _calculate_interaction_depth(self, conversation: Conversation) -> float:
        """Calculate interaction depth score."""
        if not conversation.messages:
            return 0.0

        # Calculate average message length as a simple proxy for depth
        avg_length = sum(len(msg.content) for msg in conversation.messages)
        avg_length /= len(conversation.messages)

        # Normalize to 0-1 range (assuming 500 chars is "deep" interaction)
        return min(avg_length / 500.0, 1.0)

    def _calculate_user_participation(self, conversation: Conversation) -> float:
        """Calculate user participation score."""
        if not conversation.messages:
            return 0.0

        user_messages = sum(1 for msg in conversation.messages 
                          if msg.role == "user")
        return user_messages / len(conversation.messages)

    def _is_topic_change(self, prev_message: Message, curr_message: Message) -> bool:
        """Detect topic change between messages."""
        # Simple implementation - could be enhanced with NLP
        # Consider messages with less than 50% word overlap as topic changes
        prev_words = set(prev_message.content.lower().split())
        curr_words = set(curr_message.content.lower().split())
        
        if not prev_words or not curr_words:
            return False
            
        overlap = len(prev_words.intersection(curr_words))
        smaller_set = min(len(prev_words), len(curr_words))
        
        return overlap / smaller_set < 0.5

    def _calculate_message_context_score(self,
                                       prev_message: Message,
                                       curr_message: Message) -> float:
        """Calculate context adherence score between messages."""
        # Simple implementation - could be enhanced with NLP
        # Consider word overlap as a measure of context adherence
        prev_words = set(prev_message.content.lower().split())
        curr_words = set(curr_message.content.lower().split())
        
        if not prev_words or not curr_words:
            return 1.0
            
        overlap = len(prev_words.intersection(curr_words))
        smaller_set = min(len(prev_words), len(curr_words))
        
        return overlap / smaller_set

    def _calculate_transition_smoothness(self,
                                       prev_message: Message,
                                       curr_message: Message) -> float:
        """Calculate transition smoothness between messages."""
        # Simple implementation - could be enhanced with more sophisticated analysis
        # Consider response time and context adherence
        time_diff = (curr_message.timestamp - 
                    prev_message.timestamp).total_seconds()
        context_score = self._calculate_message_context_score(
            prev_message,
            curr_message
        )
        
        # Normalize time difference (assuming 5 seconds is "smooth")
        time_score = max(0, 1 - (time_diff / 5.0))
        
        return (time_score + context_score) / 2.0

    def get_metrics(self, conversation_id: UUID) -> List[FlowMetrics]:
        """Get flow metrics for conversation."""
        return self.flow_metrics.get(conversation_id, [])

    def get_control(self, conversation_id: UUID) -> Optional[FlowControl]:
        """Get flow control settings for conversation."""
        return self.flow_controls.get(conversation_id)

    def update_control(self,
                      conversation_id: UUID,
                      control: FlowControl) -> bool:
        """Update flow control settings."""
        if conversation_id not in self.active_conversations:
            return False
        self.flow_controls[conversation_id] = control
        return True

    def end_conversation(self, conversation_id: UUID) -> bool:
        """End and cleanup conversation."""
        self.active_conversations.pop(conversation_id, None)
        self.flow_controls.pop(conversation_id, None)
        return True