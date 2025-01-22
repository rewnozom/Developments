# ai_agent/agents/chat_agent.py

from typing import List, Dict, Any
from .base_agent import BaseAgent

class ChatAgent(BaseAgent):
    """
    Standard chat agent implementation - wraps the existing chat functionality
    """
    def __init__(self, config: Dict[str, Any], model: Any = None):
        super().__init__(config, model)
        self.name = "Standard Chat"
        self.description = "Standard chat interface with direct model interaction"

    def process_message(self, messages: List[Dict[str, str]]) -> str:
        """Process message using standard chat logic"""
        if not self.model:
            raise ValueError("No model configured for chat agent")
            
        # Use existing chat logic from AIService
        accepts_messages = self.model.__class__.__name__ in ['OpenAIChat', 'AzureChatOpenAI', 'ChatOpenAI']
        if accepts_messages:
            response = self.model(messages)
        else:
            concatenated_messages = ' '.join(m['content'] for m in messages)
            response = self.model.invoke(concatenated_messages) if hasattr(self.model, 'invoke') else self.model(concatenated_messages)

        if isinstance(response, str):
            return response
        elif isinstance(response, dict) and 'content' in response:
            return response['content']
        elif hasattr(response, 'content'):
            return response.content
        else:
            return str(response)

    def get_agent_info(self) -> Dict[str, Any]:
        """Return agent information"""
        return {
            "name": self.name,
            "description": self.description,
            "type": "chat",
            "capabilities": ["direct-chat"],
            "is_active": self.is_active
        }