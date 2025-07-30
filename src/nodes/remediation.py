"""
Remediation node for error handling and recovery.

This module implements the "Remediation" node that acts as the system's
immune system, making intelligent decisions about error recovery.
"""

from typing import Dict, Any
import logging

from ..core.state import GraphState

logger = logging.getLogger(__name__)


def remediation_node(state: GraphState) -> Dict[str, Any]:
    """
    Remediation node that handles errors and decides on recovery actions.
    
    This node analyzes the latest error in the error log and makes intelligent
    decisions about how to proceed: retry, replan, continue, or complete.
    
    Args:
        state: Current graph state containing error log
        
    Returns:
        Updated state with remediation decisions
    """
    logger.info("Remediation node processing errors")
    
    if not state.error_log:
        logger.info("No errors to remediate")
        return {}
    
    latest_error = state.error_log[-1]
    logger.info(f"Remediating error: {latest_error.error_type} for task {latest_error.task_id}")
    
    # Apply remediation logic based on error type and conditions
    remediation_action = _determine_remediation_action(state, latest_error)
    
    logger.info(f"Remediation action: {remediation_action}")
    
    # Execute the remediation action
    if remediation_action == "retry":
        return _handle_retry(state, latest_error)
    elif remediation_action == "replan":
        return _handle_replan(state, latest_error)
    elif remediation_action == "continue":
        return _handle_continue(state, latest_error)
    else:  # complete
        return _handle_complete(state, latest_error)


def _determine_remediation_action(state: GraphState, error) -> str:
    """
    Determine the appropriate remediation action based on error analysis.
    
    Args:
        state: Current graph state
        error: The error record to analyze
        
    Returns:
        Remediation action: 'retry', 'replan', 'continue', or 'complete'
    """
    # Check for critical errors that should stop execution
    if state.has_critical_errors():
        return "complete"
    
    # Retry logic for transient errors
    if error.error_type in ["API_TIMEOUT", "NETWORK_ERROR"] and error.retry_count < 3:
        return "retry"
    
    # Replan for invalid inputs that might need a different approach
    if error.error_type == "INVALID_STOCK_CODE" and len(state.task_plan) > 1:
        return "replan"
    
    # Retry with stricter prompts for LLM errors
    if error.error_type in ["AGENT_HALLUCINATION", "LLM_ERROR"] and error.retry_count < 2:
        return "retry"
    
    # Continue with other tasks for unrecoverable errors
    pending_tasks = state.get_pending_tasks()
    if pending_tasks:
        return "continue"
    
    # All tasks processed or no more retries
    return "complete"


def _handle_retry(state: GraphState, error) -> Dict[str, Any]:
    """
    Handle retry remediation action.
    
    Args:
        state: Current graph state
        error: The error record
        
    Returns:
        Updated state for retry
    """
    logger.info(f"Retrying task {error.task_id}")
    
    # Find the task and reset its status
    task = state.get_task_by_id(error.task_id)
    if task:
        task.status = "pending"
        
        # Increment retry count in error log
        error.retry_count += 1
        
        # Add retry note
        state.add_error(
            task_id=error.task_id,
            agent=error.agent,
            tool=error.tool,
            error_type="RETRY_ATTEMPT",
            error_message=f"Retrying task due to {error.error_type}",
            retry_count=error.retry_count
        )
    
    return {"task_plan": state.task_plan, "error_log": state.error_log}


def _handle_replan(state: GraphState, error) -> Dict[str, Any]:
    """
    Handle replan remediation action.
    
    Args:
        state: Current graph state
        error: The error record
        
    Returns:
        Updated state for replanning
    """
    logger.info(f"Replanning due to error in task {error.task_id}")
    
    # Mark current task as permanently failed
    task = state.get_task_by_id(error.task_id)
    if task:
        task.status = "failed"
    
    # Clear task plan to trigger replanning
    # The planner will be invoked again with context from errors
    state.task_plan = []
    
    # Add replan note
    state.add_error(
        task_id="replanning",
        agent="remediation",
        tool="replan",
        error_type="REPLAN_TRIGGERED",
        error_message=f"Replanning triggered by {error.error_type} in task {error.task_id}"
    )
    
    return {"task_plan": state.task_plan, "error_log": state.error_log}


def _handle_continue(state: GraphState, error) -> Dict[str, Any]:
    """
    Handle continue remediation action.
    
    Args:
        state: Current graph state
        error: The error record
        
    Returns:
        Updated state to continue with other tasks
    """
    logger.info(f"Continuing with other tasks, skipping failed task {error.task_id}")
    
    # Mark the failed task as permanently failed
    task = state.get_task_by_id(error.task_id)
    if task:
        task.status = "failed"
    
    # Add continuation note
    state.add_error(
        task_id=error.task_id,
        agent="remediation", 
        tool="continue",
        error_type="TASK_SKIPPED",
        error_message=f"Skipping task {error.task_id} due to unrecoverable {error.error_type}"
    )
    
    return {"task_plan": state.task_plan, "error_log": state.error_log}


def _handle_complete(state: GraphState, error) -> Dict[str, Any]:
    """
    Handle complete remediation action.
    
    Args:
        state: Current graph state
        error: The error record
        
    Returns:
        Updated state to complete processing
    """
    logger.info(f"Completing processing despite errors")
    
    # Mark any remaining tasks as failed
    for task in state.task_plan:
        if task.status == "pending":
            task.status = "failed"
    
    # Add completion note
    state.add_error(
        task_id="completion",
        agent="remediation",
        tool="complete",
        error_type="FORCED_COMPLETION",
        error_message="Completing processing due to critical errors or max retries reached"
    )
    
    return {"task_plan": state.task_plan, "error_log": state.error_log}


def _analyze_error_patterns(state: GraphState) -> Dict[str, Any]:
    """
    Analyze error patterns to improve remediation decisions.
    
    Args:
        state: Current graph state
        
    Returns:
        Error pattern analysis
    """
    error_types = [error.error_type for error in state.error_log]
    error_agents = [error.agent for error in state.error_log]
    
    analysis = {
        "total_errors": len(state.error_log),
        "error_types": list(set(error_types)),
        "most_common_error": max(set(error_types), key=error_types.count) if error_types else None,
        "problematic_agents": list(set(error_agents)),
        "critical_errors_count": len([e for e in state.error_log if e.error_type in ["UNRECOVERABLE_ERROR", "AUTH_FAILURE"]])
    }
    
    return analysis