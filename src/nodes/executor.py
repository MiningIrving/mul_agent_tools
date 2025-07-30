"""
Agent executor node for task execution.

This module implements the "Agent Executor" that dynamically dispatches
tasks to appropriate agents and manages the execution loop.
"""

from typing import Dict, Any, Optional
import logging

from ..core.state import GraphState, TaskDefinition
from ..agents import get_agent

logger = logging.getLogger(__name__)


def agent_executor_node(state: GraphState) -> Dict[str, Any]:
    """
    Agent executor node that executes tasks from the task plan.
    
    This node serves as a dynamic dispatcher that:
    1. Gets the next pending task from the task plan
    2. Identifies and calls the appropriate agent
    3. Handles the execution result or error
    4. Updates the state accordingly
    
    Args:
        state: Current graph state containing task plan and results
        
    Returns:
        Updated state with new agent results or error records
    """
    logger.info("Agent executor processing tasks")
    
    # Get the next pending task
    pending_tasks = state.get_pending_tasks()
    
    if not pending_tasks:
        logger.info("No pending tasks found")
        return {}
    
    # Get the first available task (considering dependencies)
    current_task = _get_next_executable_task(state, pending_tasks)
    
    if not current_task:
        logger.warning("No executable tasks found (possibly waiting for dependencies)")
        return {}
    
    logger.info(f"Executing task: {current_task.task_id} with agent: {current_task.agent}")
    
    try:
        # Mark task as running
        current_task.status = "running"
        state.update_timestamp()
        
        # Get the appropriate agent
        agent = get_agent(current_task.agent)
        
        if not agent:
            raise Exception(f"Agent '{current_task.agent}' not found")
        
        # Execute the task
        result = agent.execute_task(state, current_task)
        
        # Mark task as completed and store result
        state.mark_task_completed(current_task.task_id, result)
        
        logger.info(f"Task {current_task.task_id} completed successfully")
        
        return {
            "agent_results": state.agent_results,
            "task_plan": state.task_plan
        }
        
    except Exception as e:
        logger.error(f"Error executing task {current_task.task_id}: {str(e)}")
        
        # Mark task as failed and log error
        state.mark_task_failed(current_task.task_id)
        
        # Determine error type for better remediation
        error_type = _classify_error(e)
        
        state.add_error(
            task_id=current_task.task_id,
            agent=current_task.agent,
            tool=current_task.tool,
            error_type=error_type,
            error_message=str(e)
        )
        
        return {
            "error_log": state.error_log,
            "task_plan": state.task_plan
        }


def _get_next_executable_task(state: GraphState, pending_tasks: list) -> Optional[TaskDefinition]:
    """
    Get the next task that can be executed (dependencies satisfied).
    
    Args:
        state: Current graph state
        pending_tasks: List of pending tasks
        
    Returns:
        Next executable task or None if no tasks are ready
    """
    completed_task_ids = set(state.agent_results.keys())
    
    for task in pending_tasks:
        # Check if dependencies are satisfied
        if not task.depends_on or task.depends_on in completed_task_ids:
            return task
    
    return None


def _classify_error(error: Exception) -> str:
    """
    Classify error type for better remediation decisions.
    
    Args:
        error: The exception that occurred
        
    Returns:
        Error type classification
    """
    error_message = str(error).lower()
    
    # Network and API related errors
    if any(keyword in error_message for keyword in ["timeout", "connection", "network"]):
        return "NETWORK_ERROR"
    
    if any(keyword in error_message for keyword in ["rate limit", "quota", "too many requests"]):
        return "RATE_LIMIT_ERROR"
    
    if any(keyword in error_message for keyword in ["unauthorized", "authentication", "api key"]):
        return "AUTH_ERROR"
    
    # Data validation errors
    if any(keyword in error_message for keyword in ["invalid", "not found", "does not exist"]):
        return "INVALID_INPUT"
    
    # Agent/tool specific errors
    if any(keyword in error_message for keyword in ["agent", "tool"]):
        return "AGENT_ERROR"
    
    # LLM related errors
    if any(keyword in error_message for keyword in ["hallucination", "format", "parsing"]):
        return "LLM_ERROR"
    
    # Default to generic error
    return "UNKNOWN_ERROR"


def _prepare_task_inputs(state: GraphState, task: TaskDefinition) -> Dict[str, Any]:
    """
    Prepare inputs for task execution, resolving any dependencies.
    
    Args:
        state: Current graph state
        task: Task to prepare inputs for
        
    Returns:
        Prepared inputs with resolved dependencies
    """
    inputs = task.inputs.copy()
    
    # If task depends on another task, include its results
    if task.depends_on and task.depends_on in state.agent_results:
        dependency_result = state.agent_results[task.depends_on]
        inputs["dependency_result"] = dependency_result
    
    return inputs


def _validate_agent_result(result: Any) -> bool:
    """
    Validate that the agent returned a proper result.
    
    Args:
        result: Result from agent execution
        
    Returns:
        True if result is valid, False otherwise
    """
    # Basic validation - result should not be None or empty
    if result is None:
        return False
    
    # If result is a dict, it should have some content
    if isinstance(result, dict) and not result:
        return False
    
    # If result is a string, it should not be empty
    if isinstance(result, str) and not result.strip():
        return False
    
    return True


def _should_retry_task(state: GraphState, task_id: str) -> bool:
    """
    Determine if a failed task should be retried.
    
    Args:
        state: Current graph state
        task_id: ID of the failed task
        
    Returns:
        True if task should be retried, False otherwise
    """
    # Find error records for this task
    task_errors = [error for error in state.error_log if error.task_id == task_id]
    
    if not task_errors:
        return False
    
    latest_error = task_errors[-1]
    
    # Don't retry if already retried too many times
    if latest_error.retry_count >= 3:
        return False
    
    # Retry for transient errors
    retryable_errors = ["NETWORK_ERROR", "RATE_LIMIT_ERROR", "TIMEOUT_ERROR"]
    
    return latest_error.error_type in retryable_errors