# ai_agent/agents/agent_factory.py

from typing import Dict, Type, Any
from .base_agent import BaseAgent
from .chat_agent import ChatAgent

class AgentFactory:
    """
    Factory class for creating and managing different types of agents
    """
    _agents: Dict[str, Type[BaseAgent]] = {
        "chat": ChatAgent
    }

    @classmethod
    def register_agent(cls, name: str, agent_class: Type[BaseAgent]):
        """
        Register a new agent type
        
        Args:
            name (str): Name identifier for the agent type
            agent_class (Type[BaseAgent]): The agent class to register
        """
        cls._agents[name] = agent_class

    @classmethod
    def create_agent(cls, agent_type: str, config: Dict[str, Any], model: Any = None) -> BaseAgent:
        """
        Create an instance of the specified agent type
        
        Args:
            agent_type (str): Type of agent to create
            config (Dict[str, Any]): Configuration for the agent
            model (Any, optional): Model instance to use with the agent
            
        Returns:
            BaseAgent: An instance of the requested agent type
            
        Raises:
            ValueError: If the agent type is not registered
        """
        if agent_type not in cls._agents:
            raise ValueError(f"Unknown agent type: {agent_type}")
            
        return cls._agents[agent_type](config, model)

    @classmethod
    def get_available_agents(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all registered agent types
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping agent names to their info
        """
        return {
            name: agent_class(config={}, model=None).get_agent_info()
            for name, agent_class in cls._agents.items()
        }