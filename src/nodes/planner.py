"""
Planner node for complex query decomposition.

This module implements the "Planner" that breaks down complex queries into
structured, executable task plans using LLM function calling.
"""

from typing import Dict, Any, List
import logging
import json
from langchain.schema import HumanMessage
from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel

from ..core.state import GraphState, TaskDefinition

logger = logging.getLogger(__name__)


class ExecutionPlan(BaseModel):
    """Pydantic model for structured task planning."""
    tasks: List[Dict[str, Any]]
    reasoning: str


def planner_node(state: GraphState) -> Dict[str, Any]:
    """
    Planner node that decomposes complex queries into executable task plans.
    
    This node uses LLM function calling to break down complex user queries
    into a series of structured, ordered tasks that can be executed by
    specialized agents.
    
    Args:
        state: Current graph state containing the complex query
        
    Returns:
        Updated state with task_plan field populated
    """
    logger.info(f"Planner processing complex query: {state.original_query}")
    
    try:
        # Initialize the LLM for planning
        llm = ChatOpenAI(
            model="gpt-4",  # Use GPT-4 for better planning capabilities
            temperature=0.1,
            max_tokens=1000
        )
        
        # Define the function schema for task planning
        planning_function = {
            "name": "create_execution_plan",
            "description": "Create a structured execution plan for complex financial queries",
            "parameters": {
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "description": "List of tasks to execute",
                        "items": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "string",
                                    "description": "Unique identifier for the task"
                                },
                                "agent": {
                                    "type": "string", 
                                    "description": "Agent to execute this task",
                                    "enum": ["选股agent", "新闻agent", "知识库agent", "诊股agent", "预测agent", "荐股agent"]
                                },
                                "tool": {
                                    "type": "string",
                                    "description": "Tool to be used",
                                    "enum": ["个股信息查询", "条件选股", "新闻查询", "公告查询", "研报查询", "金融知识查询"]
                                },
                                "inputs": {
                                    "type": "object",
                                    "description": "Input parameters for the tool"
                                },
                                "depends_on": {
                                    "type": "string",
                                    "description": "Task ID this task depends on (optional)"
                                }
                            },
                            "required": ["task_id", "agent", "tool", "inputs"]
                        }
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Explanation of the planning logic"
                    }
                },
                "required": ["tasks", "reasoning"]
            }
        }
        
        # Create the planning prompt
        planning_prompt = _create_planning_prompt(state.original_query)
        
        # Get the plan from LLM using function calling
        message = HumanMessage(content=planning_prompt)
        response = llm([message], functions=[planning_function], function_call={"name": "create_execution_plan"})
        
        # Parse the function call response
        if response.additional_kwargs.get("function_call"):
            function_args = json.loads(response.additional_kwargs["function_call"]["arguments"])
            
            # Convert to TaskDefinition objects
            task_plan = []
            for task_data in function_args["tasks"]:
                task = TaskDefinition(
                    task_id=task_data["task_id"],
                    agent=task_data["agent"],
                    tool=task_data["tool"],
                    inputs=task_data["inputs"],
                    depends_on=task_data.get("depends_on")
                )
                task_plan.append(task)
            
            logger.info(f"Generated plan with {len(task_plan)} tasks: {function_args['reasoning']}")
            
            # Update state with the task plan
            state.task_plan = task_plan
            state.update_timestamp()
            
            return {"task_plan": task_plan}
        else:
            raise Exception("LLM did not return a valid function call")
            
    except Exception as e:
        logger.error(f"Error in planner node: {str(e)}")
        
        # Create a fallback simple plan
        fallback_plan = _create_fallback_plan(state.original_query)
        state.task_plan = fallback_plan
        state.add_error(
            task_id="planning",
            agent="planner",
            tool="llm_planning",
            error_type="PLANNING_ERROR",
            error_message=str(e)
        )
        
        return {"task_plan": fallback_plan}


def _create_planning_prompt(query: str) -> str:
    """
    Create a detailed planning prompt for the LLM.
    
    Args:
        query: The complex user query to plan for
        
    Returns:
        Formatted planning prompt
    """
    prompt = f"""You are an expert financial analysis planner. Break down the following complex query into a series of specific, executable tasks.

Available Agents and Their Capabilities:
- 选股agent: Can use 个股信息查询, 条件选股 
- 新闻agent: Can use 新闻查询, 公告查询, 研报查询
- 知识库agent: Can use 金融知识查询
- 诊股agent: Can use 个股信息查询, 新闻查询, 公告查询, 研报查询
- 预测agent: Can use 个股信息查询, 研报查询
- 荐股agent: Can use all tools

Query to plan: "{query}"

Guidelines:
1. Break the query into logical, sequential steps
2. Each task should have a clear, specific purpose
3. Use appropriate agents based on their capabilities
4. Consider dependencies between tasks (use depends_on field)
5. Be specific with input parameters
6. Aim for 2-6 tasks for most complex queries

Create a structured execution plan that will comprehensively address the user's query."""

    return prompt


def _create_fallback_plan(query: str) -> List[TaskDefinition]:
    """
    Create a simple fallback plan when planning fails.
    
    Args:
        query: The original user query
        
    Returns:
        Simple fallback task plan
    """
    fallback_task = TaskDefinition(
        task_id="fallback_task_1",
        agent="知识库agent",
        tool="金融知识查询",
        inputs={"query": query}
    )
    
    return [fallback_task]


def _validate_task_plan(tasks: List[TaskDefinition]) -> bool:
    """
    Validate the generated task plan for logical consistency.
    
    Args:
        tasks: List of tasks to validate
        
    Returns:
        True if plan is valid, False otherwise
    """
    # Check for duplicate task IDs
    task_ids = [task.task_id for task in tasks]
    if len(task_ids) != len(set(task_ids)):
        return False
    
    # Check dependency references
    for task in tasks:
        if task.depends_on and task.depends_on not in task_ids:
            return False
    
    # Check for circular dependencies (simplified check)
    for task in tasks:
        if task.depends_on == task.task_id:
            return False
    
    return True