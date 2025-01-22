#!/usr/bin/env python3
# ai_agent/agents/crew_agent.py

import logging
from typing import List, Dict, Any, Optional, Set
from datetime import datetime

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

# Try to import CrewAI dependencies
try:
    from crewai import Agent, Task, Crew, Process
    CREWAI_AVAILABLE = True
    logger.debug("CrewAI dependencies loaded successfully")
except ImportError:
    CREWAI_AVAILABLE = False
    logger.warning("CrewAI not available, crew agent will run in limited mode")
    # Create dummy classes for type hints
    class Agent:
        def __init__(self, *args, **kwargs): pass
    class Task:
        def __init__(self, *args, **kwargs): pass
    class Crew:
        def __init__(self, *args, **kwargs): pass
        def kickoff(self): return "CrewAI not available - operation not supported"
    class Process:
        sequential = "sequential"
        parallel = "parallel"

class CrewAgentError(Exception):
    """Base exception class for crew agent errors"""
    pass

class WorkflowError(CrewAgentError):
    """Raised when there are workflow-related errors"""
    pass

class AgentInitializationError(CrewAgentError):
    """Raised when agent initialization fails"""
    pass

class DeveloperCrewAgent(BaseAgent):
    """
    Advanced developer agent implementation that manages software development workflows
    using a specialized team of AI agents.
    """
    
    def __init__(self, config: Dict[str, Any], model: Optional[Any] = None):
        """Initialize the developer crew agent."""
        if not CREWAI_AVAILABLE:
            logger.warning("Initializing CrewAgent without CrewAI support")
            
        super().__init__(config, model)
        self.name = "Developer Crew"
        self.description = "Multi-agent system for advanced software development"
        self.current_workflow: Optional[str] = None
        self.agents: Dict[str, Agent] = {}
        self.initialization_time: Optional[datetime] = None
        self.last_workflow_execution: Optional[datetime] = None
        self.execution_count: int = 0
        self.success_count: int = 0
        
        self._initialize_crew()

    def _initialize_crew(self) -> None:
        """Initialize the development crew with specialized roles."""
        if not CREWAI_AVAILABLE:
            logger.warning("Crew initialization skipped - CrewAI not available")
            return

        try:
            self._create_architect_agent()
            self._create_developer_agent()
            self._create_analyst_agent()
            self._create_integrator_agent()
            
            self.initialization_time = datetime.now()
            logger.info("Development crew initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing development crew: {e}")
            raise AgentInitializationError(f"Failed to initialize crew: {str(e)}")

    def _create_architect_agent(self) -> None:
        """Create the system architect agent."""
        self.agents['architect'] = Agent(
            role='System Architect',
            goal='Design and manage system architecture and dependencies',
            backstory="""Expert system architect with deep understanding of 
            architecture, design patterns, and system integration.""",
            verbose=True,
            allow_delegation=True,
            llm=self.model
        )

    def _create_developer_agent(self) -> None:
        """Create the senior developer agent."""
        self.agents['developer'] = Agent(
            role='Senior Developer',
            goal='Implement solutions and manage code quality',
            backstory="""Skilled senior developer with expertise in development,
            debugging, and optimization.""",
            verbose=True,
            allow_delegation=True,
            llm=self.model
        )

    def _create_analyst_agent(self) -> None:
        """Create the technical analyst agent."""
        self.agents['analyst'] = Agent(
            role='Technical Analyst',
            goal='Analyze code and create documentation',
            backstory="""Detail-oriented analyst specializing in code analysis,
            pattern recognition, and technical documentation.""",
            verbose=True,
            allow_delegation=True,
            llm=self.model
        )

    def _create_integrator_agent(self) -> None:
        """Create the system integrator agent."""
        self.agents['integrator'] = Agent(
            role='System Integrator',
            goal='Manage system integration and dependencies',
            backstory="""Experienced integrator managing dependencies,
            compatibility, and system consistency.""",
            verbose=True,
            allow_delegation=True,
            llm=self.model
        )

    def set_workflow(self, workflow_name: str) -> bool:
        """Set the current workflow."""
        if not CREWAI_AVAILABLE:
            logger.warning("Cannot set workflow - CrewAI not available")
            return False

        try:
            workflows = self.config.get_workflow_config(workflow_name)
            if not workflows:
                raise WorkflowError(f"Workflow '{workflow_name}' not found in configuration")
            
            if not workflows.get('enabled', True):
                raise WorkflowError(f"Workflow '{workflow_name}' is disabled")
            
            self.current_workflow = workflow_name
            logger.info(f"Workflow set to: {workflow_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting workflow: {e}")
            return False

    def process_message(self, messages: List[Dict[str, str]]) -> str:
        """Process a message using the current workflow."""
        if not CREWAI_AVAILABLE:
            return "Crew agent features are not available - CrewAI is required"

        if not self.initialization_time:
            return "Development crew not properly initialized"

        if not self.current_workflow:
            return "Please select a workflow first (troubleshoot/improve/develop/document)"

        try:
            start_time = datetime.now()
            user_message = messages[-1]['content']
            workflow_config = self._get_workflow_config()
            
            # Create and validate tasks
            tasks = self._create_workflow_tasks(
                workflow_config['steps'],
                user_message,
                workflow_config.get('roles', {})
            )
            
            if not tasks:
                raise WorkflowError("No valid tasks created for the workflow")

            # Get required agents
            active_agents = self._get_workflow_agents(workflow_config.get('roles', {}))
            if not active_agents:
                raise WorkflowError("No valid agents available for the workflow")

            # Execute workflow
            result = self._execute_workflow(active_agents, tasks)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_execution_stats(True, execution_time)
            
            return result

        except Exception as e:
            self._update_execution_stats(False)
            error_msg = f"Error in workflow processing: {str(e)}"
            logger.error(error_msg)
            return f"Workflow execution failed: {str(e)}"

    def _get_workflow_config(self) -> Dict[str, Any]:
        """Get and validate workflow configuration."""
        try:
            workflow_config = self.config.get_workflow_config(self.current_workflow)
            if not workflow_config:
                raise WorkflowError(f"Configuration not found for workflow: {self.current_workflow}")
            return workflow_config
        except Exception as e:
            logger.error(f"Error getting workflow configuration: {e}")
            raise

    def _execute_workflow(self, agents: List[Agent], tasks: List[Task]) -> str:
        """Execute the workflow with the given agents and tasks."""
        try:
            crew = Crew(
                agents=agents,
                tasks=tasks,
                verbose=True,
                process=Process.sequential
            )

            result = crew.kickoff()
            logger.info(f"Workflow {self.current_workflow} completed successfully")
            return result

        except Exception as e:
            logger.error(f"Error during workflow execution: {e}")
            raise WorkflowError(f"Workflow execution failed: {str(e)}")

    def _update_execution_stats(self, success: bool, execution_time: Optional[float] = None) -> None:
        """Update workflow execution statistics."""
        self.execution_count += 1
        if success:
            self.success_count += 1
        self.last_workflow_execution = datetime.now()
        
        if execution_time:
            logger.info(
                f"Workflow execution completed - Success: {success}, "
                f"Time: {execution_time:.2f}s, "
                f"Success rate: {(self.success_count/self.execution_count)*100:.1f}%"
            )

    def get_agent_info(self) -> Dict[str, Any]:
        """Return detailed agent information."""
        workflows = self.config.get_active_workflows() if CREWAI_AVAILABLE else {}
        
        return {
            "name": self.name,
            "description": self.description,
            "type": "developer",
            "capabilities": [
                "troubleshooting",
                "code-improvement",
                "feature-development",
                "documentation"
            ],
            "workflows": workflows,
            "is_active": self.is_active,
            "current_workflow": self.current_workflow,
            "team_members": list(self.agents.keys()),
            "crewai_available": CREWAI_AVAILABLE,
            "initialization_time": self.initialization_time,
            "last_execution": self.last_workflow_execution,
            "execution_stats": {
                "total_executions": self.execution_count,
                "successful_executions": self.success_count,
                "success_rate": (self.success_count/self.execution_count)*100 if self.execution_count > 0 else 0
            },
            "status": self.status
        }

    def reset(self) -> bool:
        """Reset the crew agent to initial state."""
        try:
            super().reset()
            self.current_workflow = None
            self.execution_count = 0
            self.success_count = 0
            self.last_workflow_execution = None
            return True
        except Exception as e:
            logger.error(f"Failed to reset crew agent: {e}")
            return False