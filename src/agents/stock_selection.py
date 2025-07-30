"""
Stock selection agent implementation.

This agent specializes in stock screening and selection based on various criteria.
"""

from typing import Any, List
from ..tools import get_tool
from .base import BaseAgent
from ..core.state import GraphState, TaskDefinition


class StockSelectionAgent(BaseAgent):
    """
    Agent specialized in stock selection and screening.
    
    This agent can perform individual stock queries and conditional stock screening
    to help users find stocks that match specific criteria.
    """
    
    def __init__(self, name: str):
        """Initialize the stock selection agent."""
        super().__init__(name)
        self.available_tools = ["个股信息查询", "条件选股"]
    
    def execute_task(self, state: GraphState, task: TaskDefinition) -> Any:
        """
        Execute a stock selection task.
        
        Args:
            state: Current graph state
            task: Task definition
            
        Returns:
            Stock selection results
        """
        if not self.validate_task(task):
            raise ValueError(f"Agent {self.name} cannot execute tool {task.tool}")
        
        # Prepare inputs
        inputs = self.prepare_inputs(state, task)
        
        # Get the appropriate tool
        tool = get_tool(task.tool)
        if not tool:
            raise ValueError(f"Tool {task.tool} not found")
        
        try:
            # Execute the tool
            result = tool.execute(**inputs)
            
            # Log execution
            self.log_execution(task, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Tool execution failed: {str(e)}")
            raise
    
    def get_available_tools(self) -> List[str]:
        """Get list of tools this agent can use."""
        return self.available_tools.copy()
    
    def _validate_stock_inputs(self, inputs: dict) -> bool:
        """
        Validate inputs for stock-related operations.
        
        Args:
            inputs: Input parameters
            
        Returns:
            True if inputs are valid
        """
        # For individual stock queries, we need stock code or name
        if "stock_code" in inputs or "stock_name" in inputs:
            return True
        
        # For conditional selection, we need selection criteria
        if any(key in inputs for key in ["pe_ratio_max", "market_cap_min", "industry"]):
            return True
        
        return False