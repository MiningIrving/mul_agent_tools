"""
Main graph implementation for the financial analysis framework.

This module defines the LangGraph workflow that orchestrates the entire
multi-agent financial analysis process.
"""

from typing import Literal, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import GraphState
from ..nodes.router import router_node
from ..nodes.planner import planner_node
from ..nodes.executor import agent_executor_node
from ..nodes.remediation import remediation_node
from ..nodes.answer import answer_generator_node
from ..nodes.fallback import fallback_node


class FinancialAnalysisGraph:
    """
    Main graph class that orchestrates the financial analysis workflow.
    
    This class builds and manages the LangGraph workflow, defining how
    different nodes are connected and how control flows between them.
    """
    
    def __init__(self, enable_persistence: bool = True):
        """
        Initialize the financial analysis graph.
        
        Args:
            enable_persistence: Whether to enable graph state persistence
        """
        self.enable_persistence = enable_persistence
        self.workflow = self._build_graph()
        self.app = self._compile_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow definition."""
        workflow = StateGraph(GraphState)
        
        # Add all nodes
        workflow.add_node("router", router_node)
        workflow.add_node("planner", planner_node)
        workflow.add_node("agent_executor", agent_executor_node)
        workflow.add_node("remediation", remediation_node)
        workflow.add_node("answer_generator", answer_generator_node)
        workflow.add_node("fallback", fallback_node)
        
        # Set entry point
        workflow.set_entry_point("router")
        
        # Add conditional edges from router
        workflow.add_conditional_edges(
            "router",
            self._route_after_classification,
            {
                "simple": "agent_executor",
                "complex": "planner", 
                "oos": "fallback"
            }
        )
        
        # From planner, always go to agent_executor
        workflow.add_edge("planner", "agent_executor")
        
        # Add conditional edges from agent_executor
        workflow.add_conditional_edges(
            "agent_executor",
            self._route_after_execution,
            {
                "continue": "agent_executor",  # Loop back for more tasks
                "error": "remediation",        # Handle errors
                "complete": "answer_generator" # All tasks done
            }
        )
        
        # Add conditional edges from remediation
        workflow.add_conditional_edges(
            "remediation",
            self._route_after_remediation,
            {
                "retry": "agent_executor",     # Retry the task
                "replan": "planner",          # Go back to planning
                "continue": "agent_executor", # Continue with next task
                "complete": "answer_generator" # All tasks done despite errors
            }
        )
        
        # Terminal nodes
        workflow.add_edge("answer_generator", END)
        workflow.add_edge("fallback", END)
        
        return workflow
    
    def _compile_graph(self):
        """Compile the graph with optional persistence."""
        if self.enable_persistence:
            memory = MemorySaver()
            return self.workflow.compile(checkpointer=memory)
        else:
            return self.workflow.compile()
    
    @staticmethod
    def _route_after_classification(state: GraphState) -> Literal["simple", "complex", "oos"]:
        """
        Routing logic after query classification.
        
        Args:
            state: Current graph state
            
        Returns:
            Next node to execute based on query complexity
        """
        complexity = state.query_complexity
        
        if complexity == "SIMPLE":
            return "simple"
        elif complexity == "COMPLEX":
            return "complex"
        else:  # OOS or None
            return "oos"
    
    @staticmethod
    def _route_after_execution(state: GraphState) -> Literal["continue", "error", "complete"]:
        """
        Routing logic after agent execution.
        
        Args:
            state: Current graph state
            
        Returns:
            Next action based on execution status
        """
        # Check if there are new errors
        if state.error_log and state.error_log[-1].retry_count == 0:
            return "error"
        
        # Check if there are pending tasks
        pending_tasks = state.get_pending_tasks()
        if pending_tasks:
            return "continue"
        
        # All tasks completed
        return "complete"
    
    @staticmethod
    def _route_after_remediation(state: GraphState) -> Literal["retry", "replan", "continue", "complete"]:
        """
        Routing logic after error remediation.
        
        Args:
            state: Current graph state
            
        Returns:
            Next action based on remediation decision
        """
        if not state.error_log:
            return "complete"
        
        latest_error = state.error_log[-1]
        
        # Check for critical errors
        if state.has_critical_errors():
            return "complete"
        
        # Retry logic for common recoverable errors
        if latest_error.error_type in ["API_TIMEOUT", "NETWORK_ERROR"] and latest_error.retry_count < 3:
            return "retry"
        
        # Replan for invalid inputs that might need different approach
        if latest_error.error_type == "INVALID_STOCK_CODE" and len(state.task_plan) > 1:
            return "replan"
        
        # Continue with remaining tasks for other errors
        pending_tasks = state.get_pending_tasks()
        if pending_tasks:
            return "continue"
        
        return "complete"
    
    def invoke(self, query: str, session_id: str, config: Dict[str, Any] = None) -> GraphState:
        """
        Invoke the graph with a user query.
        
        Args:
            query: User's financial analysis query
            session_id: Unique session identifier
            config: Optional configuration for the graph execution
            
        Returns:
            Final state after processing the query
        """
        initial_state = GraphState(
            original_query=query,
            session_id=session_id
        )
        
        # Set up configuration for persistence if enabled
        if config is None:
            config = {}
        
        if self.enable_persistence:
            config.setdefault("configurable", {})["thread_id"] = session_id
        
        # Execute the graph
        final_state = self.app.invoke(initial_state, config=config)
        
        return final_state
    
    def stream(self, query: str, session_id: str, config: Dict[str, Any] = None):
        """
        Stream the graph execution for real-time monitoring.
        
        Args:
            query: User's financial analysis query
            session_id: Unique session identifier
            config: Optional configuration for the graph execution
            
        Yields:
            State updates during graph execution
        """
        initial_state = GraphState(
            original_query=query,
            session_id=session_id
        )
        
        # Set up configuration for persistence if enabled
        if config is None:
            config = {}
        
        if self.enable_persistence:
            config.setdefault("configurable", {})["thread_id"] = session_id
        
        # Stream the graph execution
        for update in self.app.stream(initial_state, config=config):
            yield update
    
    def get_graph_visualization(self) -> str:
        """
        Get a text representation of the graph structure.
        
        Returns:
            String representation of the graph
        """
        return self.app.get_graph().draw_ascii()
    
    def get_state_schema(self) -> Dict[str, Any]:
        """
        Get the schema of the graph state.
        
        Returns:
            JSON schema of the GraphState
        """
        return GraphState.schema()