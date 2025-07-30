"""
Base agent class and agent registry.

This module defines the base agent interface and provides a registry
for dynamically loading agents by name.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

from ..core.state import GraphState, TaskDefinition

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all agents in the financial analysis framework.
    
    All agents must implement the execute_task method and define their
    available tools through the get_available_tools method.
    """
    
    def __init__(self, name: str):
        """
        Initialize the base agent.
        
        Args:
            name: Human-readable name of the agent
        """
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")
    
    @abstractmethod
    def execute_task(self, state: GraphState, task: TaskDefinition) -> Any:
        """
        Execute a specific task using the agent's capabilities.
        
        Args:
            state: Current graph state for context
            task: Task definition with tool and inputs
            
        Returns:
            Result of the task execution
            
        Raises:
            Exception: If task execution fails
        """
        pass
    
    @abstractmethod
    def get_available_tools(self) -> list:
        """
        Get list of tools this agent can use.
        
        Returns:
            List of tool names this agent has access to
        """
        pass
    
    def validate_task(self, task: TaskDefinition) -> bool:
        """
        Validate that this agent can execute the given task.
        
        Args:
            task: Task to validate
            
        Returns:
            True if agent can execute task, False otherwise
        """
        available_tools = self.get_available_tools()
        return task.tool in available_tools
    
    def prepare_inputs(self, state: GraphState, task: TaskDefinition) -> Dict[str, Any]:
        """
        Prepare inputs for task execution, including dependency resolution.
        
        Args:
            state: Current graph state
            task: Task to prepare inputs for
            
        Returns:
            Prepared inputs dictionary
        """
        inputs = task.inputs.copy()
        
        # Add dependency results if available
        if task.depends_on and task.depends_on in state.agent_results:
            inputs["dependency_result"] = state.agent_results[task.depends_on]
        
        # Add session context
        inputs["session_id"] = state.session_id
        
        return inputs
    
    def log_execution(self, task: TaskDefinition, result: Any):
        """
        Log task execution for debugging and monitoring.
        
        Args:
            task: Executed task
            result: Execution result
        """
        self.logger.info(
            f"Executed task {task.task_id} with tool {task.tool}. "
            f"Result type: {type(result).__name__}"
        )


# Agent registry for dynamic loading
_AGENT_REGISTRY = {}


def register_agent(name: str, agent_class: type):
    """
    Register an agent class in the global registry.
    
    Args:
        name: Agent name (should match names used in task planning)
        agent_class: Agent class to register
    """
    _AGENT_REGISTRY[name] = agent_class
    logger.info(f"Registered agent: {name}")


def get_agent(name: str) -> Optional[BaseAgent]:
    """
    Get an agent instance by name.
    
    Args:
        name: Name of the agent to retrieve
        
    Returns:
        Agent instance or None if not found
    """
    if name in _AGENT_REGISTRY:
        agent_class = _AGENT_REGISTRY[name]
        return agent_class(name)
    
    logger.error(f"Agent '{name}' not found in registry")
    return None


def list_available_agents() -> list:
    """
    Get list of all registered agent names.
    
    Returns:
        List of registered agent names
    """
    return list(_AGENT_REGISTRY.keys())


def get_agent_capabilities() -> Dict[str, list]:
    """
    Get capabilities matrix for all registered agents.
    
    Returns:
        Dictionary mapping agent names to their available tools
    """
    capabilities = {}
    
    for name, agent_class in _AGENT_REGISTRY.items():
        # Create temporary instance to get capabilities
        temp_agent = agent_class(name)
        capabilities[name] = temp_agent.get_available_tools()
    
    return capabilities


# Initialize registry with all agent classes
def _initialize_registry():
    """Initialize the agent registry with all available agents."""
    # Import here to avoid circular imports
    from .stock_selection import StockSelectionAgent
    from .news import NewsAgent
    from .knowledge import KnowledgeAgent
    from .diagnosis import DiagnosisAgent
    from .prediction import PredictionAgent
    from .recommendation import RecommendationAgent
    
    # Register all agents with their Chinese names as used in the README
    register_agent("选股agent", StockSelectionAgent)
    register_agent("新闻agent", NewsAgent)
    register_agent("知识库agent", KnowledgeAgent)
    register_agent("诊股agent", DiagnosisAgent)
    register_agent("预测agent", PredictionAgent)
    register_agent("荐股agent", RecommendationAgent)


# Initialize registry on module import
_initialize_registry()