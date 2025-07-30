"""
News agent implementation.

This agent specializes in financial news gathering and analysis.
"""

from typing import Any, List
from ..tools import get_tool
from .base import BaseAgent
from ..core.state import GraphState, TaskDefinition


class NewsAgent(BaseAgent):
    """
    Agent specialized in financial news and information gathering.
    
    This agent can query news, announcements, and research reports
    related to companies and financial markets.
    """
    
    def __init__(self, name: str):
        """Initialize the news agent."""
        super().__init__(name)
        self.available_tools = ["新闻查询", "公告查询", "研报查询"]
    
    def execute_task(self, state: GraphState, task: TaskDefinition) -> Any:
        """
        Execute a news-related task.
        
        Args:
            state: Current graph state
            task: Task definition
            
        Returns:
            News or information results
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
            
            # Post-process news results if needed
            if task.tool == "新闻查询":
                result = self._process_news_results(result, inputs)
            
            # Log execution
            self.log_execution(task, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Tool execution failed: {str(e)}")
            raise
    
    def get_available_tools(self) -> List[str]:
        """Get list of tools this agent can use."""
        return self.available_tools.copy()
    
    def _process_news_results(self, results: Any, inputs: dict) -> dict:
        """
        Process and structure news results.
        
        Args:
            results: Raw news results
            inputs: Original inputs for context
            
        Returns:
            Processed news results
        """
        if not results:
            return {"news": [], "summary": "No relevant news found"}
        
        # If results is already structured, return as-is
        if isinstance(results, dict):
            return results
        
        # Structure the results
        structured_results = {
            "query_params": inputs,
            "news_count": len(results) if isinstance(results, list) else 1,
            "news_items": results if isinstance(results, list) else [results],
            "timestamp": inputs.get("timestamp", "N/A")
        }
        
        return structured_results
    
    def _filter_relevant_news(self, news_items: list, keywords: list) -> list:
        """
        Filter news items for relevance based on keywords.
        
        Args:
            news_items: List of news items
            keywords: Keywords to filter by
            
        Returns:
            Filtered news items
        """
        if not keywords:
            return news_items
        
        filtered_items = []
        for item in news_items:
            item_text = str(item).lower()
            if any(keyword.lower() in item_text for keyword in keywords):
                filtered_items.append(item)
        
        return filtered_items