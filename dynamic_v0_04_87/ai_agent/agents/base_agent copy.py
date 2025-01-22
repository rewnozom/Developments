# ai_agent/agents/base_agent.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    """
    def __init__(self, config: Dict[str, Any], model: Any = None):
        self.config = config
        self.model = model
        self.is_active = False

    @abstractmethod
    def process_message(self, messages: List[Dict[str, str]]) -> str:
        """
        Process a message using the agent's logic.
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries with 'role' and 'content'
            
        Returns:
            str: The agent's response
        """
        pass

    def activate(self):
        """Activate the agent"""
        self.is_active = True

    def deactivate(self):
        """Deactivate the agent"""
        self.is_active = False

    @property
    def is_running(self) -> bool:
        """Check if the agent is currently active"""
        return self.is_active

    @abstractmethod
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about the agent for display purposes.
        
        Returns:
            Dict[str, Any]: Dictionary containing agent information
        """
        pass