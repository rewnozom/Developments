# ai_agent/agents/developer_agent.py

from typing import List, Dict, Any
from crewai import Agent, Task, Crew, Process

from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class DeveloperAgent(BaseAgent):
    """
    Developer agent implementation that manages software development workflows
    using a team of specialized agents.
    """
    
    def __init__(self, config: Dict[str, Any], model: Any = None):
        super().__init__(config, model)
        self.name = "Developer Agent"
        self.description = "Multi-agent system for software development"
        self.current_workflow = None
        self.initialize_team()

    def initialize_team(self):
        """Initialize the development team with specialized roles"""
        try:
            # Architect Agent
            self.architect = Agent(
                role='Software Architect',
                goal='Design and maintain system architecture',
                backstory="""You are an experienced software architect with deep 
                knowledge of design patterns, system architecture, and best practices.""",
                verbose=True,
                allow_delegation=True,
                llm=self.model
            )

            # Developer Agent
            self.developer = Agent(
                role='Developer',
                goal='Implement features and fix bugs',
                backstory="""You are a skilled developer with expertise in writing 
                clean, efficient, and maintainable code.""",
                verbose=True,
                allow_delegation=True,
                llm=self.model
            )

            # Code Reviewer Agent
            self.reviewer = Agent(
                role='Code Reviewer',
                goal='Review code and ensure quality',
                backstory="""You are a meticulous code reviewer with a strong focus 
                on code quality, performance, and security.""",
                verbose=True,
                allow_delegation=True,
                llm=self.model
            )

            logger.info("Development team initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing development team: {e}")
            raise

    def set_workflow(self, workflow_name: str):
        """Set the current workflow"""
        try:
            workflows = self.config.get_agent_config()['profile']['config']['workflows']
            if workflow_name in workflows and workflows[workflow_name]['enabled']:
                self.current_workflow = workflow_name
                logger.info(f"Workflow set to: {workflow_name}")
                return True
            else:
                logger.warning(f"Invalid or disabled workflow: {workflow_name}")
                return False
        except Exception as e:
            logger.error(f"Error setting workflow: {e}")
            return False

    def process_message(self, messages: List[Dict[str, str]]) -> str:
        """
        Process a message using the current workflow
        """
        try:
            if not self.current_workflow:
                return "Please select a workflow first using set_workflow()."

            # Extract the latest user message
            user_message = messages[-1]['content']
            workflow_config = self.config.get_workflow_config(self.current_workflow)
            
            # Create tasks based on workflow steps
            tasks = []
            for step in workflow_config['steps']:
                task = self._create_task_for_step(step, user_message)
                if task:
                    tasks.append(task)

            # Create and run the development crew
            crew = Crew(
                agents=[self.architect, self.developer, self.reviewer],
                tasks=tasks,
                verbose=2
            )

            # Execute the workflow
            result = crew.kickoff()
            logger.info(f"Workflow {self.current_workflow} completed successfully")
            return result

        except Exception as e:
            error_msg = f"Error in workflow processing: {e}"
            logger.error(error_msg)
            return f"I apologize, but I encountered an error: {str(e)}"

    def _create_task_for_step(self, step: str, context: str) -> Task:
        """Create a specific task based on the workflow step"""
        task_configs = {
            'analysis': {
                'agent': self.architect,
                'description': f"Analyze the following request and provide architectural insights: {context}"
            },
            'planning': {
                'agent': self.architect,
                'description': f"Create a detailed implementation plan for: {context}"
            },
            'implementation': {
                'agent': self.developer,
                'description': f"Implement the solution based on the planning: {context}"
            },
            'review': {
                'agent': self.reviewer,
                'description': f"Review the implementation and provide feedback: {context}"
            },
            'testing': {
                'agent': self.developer,
                'description': f"Create and execute tests for: {context}"
            },
            'documentation': {
                'agent': self.developer,
                'description': f"Create documentation for: {context}"
            },
            'suggestions': {
                'agent': self.reviewer,
                'description': f"Provide improvement suggestions for: {context}"
            },
            'reproduction': {
                'agent': self.developer,
                'description': f"Reproduce and analyze the bug: {context}"
            },
            'fixing': {
                'agent': self.developer,
                'description': f"Implement bug fix for: {context}"
            }
        }

        if step in task_configs:
            config = task_configs[step]
            return Task(
                description=config['description'],
                agent=config['agent']
            )
        else:
            logger.warning(f"Unknown workflow step: {step}")
            return None

    def get_agent_info(self) -> Dict[str, Any]:
        """Return agent information"""
        return {
            "name": self.name,
            "description": self.description,
            "type": "developer",
            "capabilities": [
                "code-review",
                "feature-development",
                "bug-fixing",
                "refactoring"
            ],
            "is_active": self.is_active,
            "current_workflow": self.current_workflow,
            "team_members": [
                "Software Architect",
                "Developer",
                "Code Reviewer"
            ]
        }