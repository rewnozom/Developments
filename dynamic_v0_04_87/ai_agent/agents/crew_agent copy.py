# ai_agent/agents/crew_agent.py

from typing import List, Dict, Any
from crewai import Agent, Task, Crew, Process

from .base_agent import BaseAgent
import logging
import os

logger = logging.getLogger(__name__)

class DeveloperCrewAgent(BaseAgent):
    """
    Advanced developer agent implementation that manages software development workflows
    using a specialized team of AI agents.
    """
    
    def __init__(self, config: Dict[str, Any], model: Any = None):
        super().__init__(config, model)
        self.name = "Developer Crew"
        self.description = "Multi-agent system for advanced software development"
        self.current_workflow = None
        self.agents = {}
        self.initialize_crew()

    def initialize_crew(self):
        """Initialize the development crew with specialized roles"""
        try:
            # System Architect
            self.agents['architect'] = Agent(
                role='System Architect',
                goal='Design and manage system architecture and dependencies',
                backstory="""You are an expert system architect with deep understanding of 
                software architecture, design patterns, and system integration. You excel at 
                analyzing complex systems and making high-level design decisions.""",
                verbose=True,
                allow_delegation=True,
                llm=self.model
            )

            # Senior Developer
            self.agents['developer'] = Agent(
                role='Senior Developer',
                goal='Implement solutions and manage code quality',
                backstory="""You are a skilled senior developer with extensive experience in 
                software development, debugging, and optimization. You write clean, efficient, 
                and maintainable code while following best practices.""",
                verbose=True,
                allow_delegation=True,
                llm=self.model
            )

            # Technical Analyst
            self.agents['analyst'] = Agent(
                role='Technical Analyst',
                goal='Analyze code and create documentation',
                backstory="""You are a detail-oriented technical analyst specializing in 
                code analysis, pattern recognition, and technical documentation. You have 
                a strong ability to understand complex systems and explain them clearly.""",
                verbose=True,
                allow_delegation=True,
                llm=self.model
            )

            # System Integrator
            self.agents['integrator'] = Agent(
                role='System Integrator',
                goal='Manage system integration and dependencies',
                backstory="""You are an experienced system integrator with expertise in 
                managing dependencies, ensuring compatibility, and maintaining system 
                consistency across different components.""",
                verbose=True,
                allow_delegation=True,
                llm=self.model
            )

            logger.info("Development crew initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing development crew: {e}")
            raise

    def set_workflow(self, workflow_name: str) -> bool:
        """
        Set the current workflow
        
        Args:
            workflow_name (str): Name of the workflow to set
            
        Returns:
            bool: True if workflow was set successfully, False otherwise
        """
        try:
            workflows = self.config.get_workflow_config(workflow_name)
            if workflows and workflows.get('enabled', True):
                self.current_workflow = workflow_name
                logger.info(f"Workflow set to: {workflow_name}")
                return True
            logger.warning(f"Invalid or disabled workflow: {workflow_name}")
            return False
        except Exception as e:
            logger.error(f"Error setting workflow: {e}")
            return False

    def process_message(self, messages: List[Dict[str, str]]) -> str:
        """
        Process a message using the current workflow
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries
            
        Returns:
            str: The crew's response
        """
        try:
            if not self.current_workflow:
                return "Please select a workflow first (troubleshoot/improve/develop/document)."

            # Extract the latest user message
            user_message = messages[-1]['content']
            workflow_config = self.config.get_workflow_config(self.current_workflow)
            
            # Create tasks based on workflow
            tasks = self._create_workflow_tasks(
                workflow_config['steps'],
                user_message,
                workflow_config.get('roles', {})
            )

            # Select the appropriate agents for this workflow
            active_agents = self._get_workflow_agents(workflow_config.get('roles', {}))

            # Create and run the crew
            crew = Crew(
                agents=active_agents,
                tasks=tasks,
                verbose=True,
                process=Process.sequential  # or Process.parallel depending on workflow
            )

            # Execute the workflow
            result = crew.kickoff()
            logger.info(f"Workflow {self.current_workflow} completed successfully")
            return result

        except Exception as e:
            error_msg = f"Error in workflow processing: {e}"
            logger.error(error_msg)
            return f"I apologize, but I encountered an error: {str(e)}"

    def _create_workflow_tasks(self, steps: List[str], context: str, roles: Dict[str, str]) -> List[Task]:
        """Create tasks for the specified workflow steps"""
        tasks = []
        
        # Task configurations for each workflow type
        task_configs = {
            # Troubleshooting workflow tasks
            'problem_analysis': {
                'agent': self.agents['analyst'],
                'description': f"Analyze the reported issue and gather relevant information: {context}"
            },
            'context_gathering': {
                'agent': self.agents['analyst'],
                'description': f"Gather all relevant context and code related to the issue: {context}"
            },
            'error_diagnosis': {
                'agent': self.agents['developer'],
                'description': f"Diagnose the root cause of the issue: {context}"
            },
            'solution_design': {
                'agent': self.agents['architect'],
                'description': f"Design a comprehensive solution for the issue: {context}"
            },
            
            # Code improvement workflow tasks
            'code_review': {
                'agent': self.agents['analyst'],
                'description': f"Review the existing code and identify areas for improvement: {context}"
            },
            'quality_analysis': {
                'agent': self.agents['analyst'],
                'description': f"Analyze code quality and identify potential improvements: {context}"
            },
            'pattern_recognition': {
                'agent': self.agents['architect'],
                'description': f"Identify patterns and opportunities for better design: {context}"
            },
            'reusability_check': {
                'agent': self.agents['architect'],
                'description': f"Identify components that could be made more reusable: {context}"
            },
            
            # Development workflow tasks
            'requirement_analysis': {
                'agent': self.agents['analyst'],
                'description': f"Analyze the requirements and their implications: {context}"
            },
            'dependency_check': {
                'agent': self.agents['integrator'],
                'description': f"Check and analyze all system dependencies: {context}"
            },
            'impact_analysis': {
                'agent': self.agents['architect'],
                'description': f"Analyze the impact of changes on the system: {context}"
            },
            'design_planning': {
                'agent': self.agents['architect'],
                'description': f"Create a detailed design plan: {context}"
            },
            
            # Documentation workflow tasks
            'scope_analysis': {
                'agent': self.agents['analyst'],
                'description': f"Analyze the scope and requirements for documentation: {context}"
            },
            'content_assessment': {
                'agent': self.agents['analyst'],
                'description': f"Assess existing documentation and identify gaps: {context}"
            },
            'structure_planning': {
                'agent': self.agents['architect'],
                'description': f"Plan the documentation structure and organization: {context}"
            },
            'content_creation': {
                'agent': self.agents['analyst'],
                'description': f"Create clear and comprehensive documentation: {context}"
            },
            
            # Common tasks
            'implementation': {
                'agent': self.agents['developer'],
                'description': f"Implement the solution: {context}"
            },
            'testing': {
                'agent': self.agents['developer'],
                'description': f"Test the implementation thoroughly: {context}"
            },
            'validation': {
                'agent': self.agents['analyst'],
                'description': f"Validate the changes and ensure quality: {context}"
            },
            'integration': {
                'agent': self.agents['integrator'],
                'description': f"Handle integration of changes: {context}"
            }
        }

        # Create tasks for each step
        for step in steps:
            if step in task_configs:
                config = task_configs[step]
                tasks.append(Task(
                    description=config['description'],
                    agent=config['agent']
                ))
            else:
                logger.warning(f"Unknown workflow step: {step}")

        return tasks

    def _get_workflow_agents(self, roles: Dict[str, str]) -> List[Agent]:
        """Get the agents needed for the current workflow"""
        needed_agents = set()
        for role in roles.keys():
            if role in self.agents:
                needed_agents.add(self.agents[role])
        return list(needed_agents)

    def get_agent_info(self) -> Dict[str, Any]:
        """Return agent information"""
        workflows = self.config.get_active_workflows()
        
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
            "team_members": [
                "System Architect",
                "Senior Developer",
                "Technical Analyst",
                "System Integrator"
            ]
        }