"""
Base tool class and tool registry.

This module defines the base tool interface and provides a registry
for dynamically loading tools by name.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """
    Base class for all tools in the financial analysis framework.
    
    All tools must implement the execute method and provide metadata
    about their capabilities and requirements.
    """
    
    def __init__(self, name: str):
        """
        Initialize the base tool.
        
        Args:
            name: Human-readable name of the tool
        """
        self.name = name
        self.logger = logging.getLogger(f"tool.{name}")
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        Execute the tool with given parameters.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            Tool execution result
            
        Raises:
            Exception: If tool execution fails
        """
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the input schema for this tool.
        
        Returns:
            JSON schema describing expected inputs
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get a human-readable description of the tool.
        
        Returns:
            Tool description
        """
        pass
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """
        Validate that the provided inputs match the tool's schema.
        
        Args:
            inputs: Input parameters to validate
            
        Returns:
            True if inputs are valid, False otherwise
        """
        schema = self.get_schema()
        required_fields = schema.get("required", [])
        
        # Check required fields are present
        for field in required_fields:
            if field not in inputs:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        return True
    
    def log_execution(self, inputs: Dict[str, Any], result: Any):
        """
        Log tool execution for debugging and monitoring.
        
        Args:
            inputs: Tool inputs
            result: Tool result
        """
        self.logger.info(
            f"Executed with inputs: {list(inputs.keys())}. "
            f"Result type: {type(result).__name__}"
        )


# Tool registry for dynamic loading
_TOOL_REGISTRY = {}


def register_tool(name: str, tool_class: type):
    """
    Register a tool class in the global registry.
    
    Args:
        name: Tool name (should match names used in task planning)
        tool_class: Tool class to register
    """
    _TOOL_REGISTRY[name] = tool_class
    logger.info(f"Registered tool: {name}")


def get_tool(name: str) -> Optional[BaseTool]:
    """
    Get a tool instance by name.
    
    Args:
        name: Name of the tool to retrieve
        
    Returns:
        Tool instance or None if not found
    """
    if name in _TOOL_REGISTRY:
        tool_class = _TOOL_REGISTRY[name]
        return tool_class(name)
    
    logger.error(f"Tool '{name}' not found in registry")
    return None


def list_available_tools() -> List[str]:
    """
    Get list of all registered tool names.
    
    Returns:
        List of registered tool names
    """
    return list(_TOOL_REGISTRY.keys())


def get_tool_schemas() -> Dict[str, Dict[str, Any]]:
    """
    Get schemas for all registered tools.
    
    Returns:
        Dictionary mapping tool names to their schemas
    """
    schemas = {}
    
    for name, tool_class in _TOOL_REGISTRY.items():
        # Create temporary instance to get schema
        temp_tool = tool_class(name)
        schemas[name] = temp_tool.get_schema()
    
    return schemas


def get_tool_descriptions() -> Dict[str, str]:
    """
    Get descriptions for all registered tools.
    
    Returns:
        Dictionary mapping tool names to their descriptions
    """
    descriptions = {}
    
    for name, tool_class in _TOOL_REGISTRY.items():
        # Create temporary instance to get description
        temp_tool = tool_class(name)
        descriptions[name] = temp_tool.get_description()
    
    return descriptions


# Initialize registry with all tool classes
def _initialize_registry():
    """Initialize the tool registry with all available tools."""
    # Import here to avoid circular imports
    from .stock_info import StockInfoTool
    from .stock_selection import StockSelectionTool
    from .news_query import NewsQueryTool
    from .announcement import AnnouncementTool
    from .research_report import ResearchReportTool
    from .knowledge_query import KnowledgeQueryTool
    
    # Register all tools with their Chinese names as used in the README
    register_tool("个股信息查询", StockInfoTool)
    register_tool("条件选股", StockSelectionTool)
    register_tool("新闻查询", NewsQueryTool)
    register_tool("公告查询", AnnouncementTool)
    register_tool("研报查询", ResearchReportTool)
    register_tool("金融知识查询", KnowledgeQueryTool)


# Initialize registry on module import
_initialize_registry()