"""
Answer generator node for synthesizing final responses.

This module implements the "Answer Generator" that combines all collected
information into a high-quality, structured response for the user.
"""

from typing import Dict, Any
import logging
try:
    from langchain.schema import HumanMessage
    from langchain.chat_models import ChatOpenAI
except ImportError:
    # Fallback for different langchain versions
    from langchain_core.messages import HumanMessage
    from langchain_openai import ChatOpenAI

from ..core.state import GraphState

logger = logging.getLogger(__name__)


def answer_generator_node(state: GraphState) -> Dict[str, Any]:
    """
    Answer generator node that synthesizes the final response.
    
    This node takes the complete final state and generates a comprehensive,
    structured answer that combines all successful results and acknowledges
    any limitations or failures.
    
    Args:
        state: Final graph state with all agent results and errors
        
    Returns:
        Updated state with final_answer field populated
    """
    logger.info("Answer generator synthesizing final response")
    
    try:
        # Initialize the LLM for answer synthesis
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.2,  # Slight creativity for better narrative
            max_tokens=2000
        )
        
        # Create comprehensive synthesis prompt
        synthesis_prompt = _create_synthesis_prompt(state)
        
        # Generate the final answer
        message = HumanMessage(content=synthesis_prompt)
        response = llm([message])
        
        final_answer = response.content.strip()
        
        logger.info("Final answer generated successfully")
        
        # Update state with final answer
        state.final_answer = final_answer
        state.update_timestamp()
        
        return {"final_answer": final_answer}
        
    except Exception as e:
        logger.error(f"Error in answer generator: {str(e)}")
        
        # Create fallback answer
        fallback_answer = _create_fallback_answer(state)
        state.final_answer = fallback_answer
        
        state.add_error(
            task_id="answer_generation",
            agent="answer_generator",
            tool="llm_synthesis",
            error_type="SYNTHESIS_ERROR",
            error_message=str(e)
        )
        
        return {"final_answer": fallback_answer}


def _create_synthesis_prompt(state: GraphState) -> str:
    """
    Create a comprehensive prompt for answer synthesis.
    
    Args:
        state: Complete graph state
        
    Returns:
        Formatted synthesis prompt
    """
    # Prepare data sections
    successful_results = _format_successful_results(state)
    error_summary = _format_error_summary(state)
    execution_summary = _format_execution_summary(state)
    
    prompt = f"""You are a senior financial analyst from a top-tier investment firm. Your task is to synthesize the results of a comprehensive financial analysis into a clear, professional report.

## Original User Query
{state.original_query}

## Execution Summary
{execution_summary}

## Analysis Results
{successful_results}

## Limitations and Issues
{error_summary}

## Instructions
Please create a professional financial analysis report with the following structure:

1. **Executive Summary (TL;DR)**: A brief overview of key findings
2. **Detailed Analysis**: Comprehensive analysis organized by topic
3. **Data Sources**: Clear attribution of information sources
4. **Limitations**: Honest acknowledgment of any missing information
5. **Conclusion**: Synthesized insights and recommendations

### Guidelines:
- Adopt the persona of an experienced financial analyst
- Use clear, professional language with proper financial terminology
- Structure the response using Markdown formatting for clarity
- Synthesize information rather than just listing data points
- Connect related information from different sources
- Be transparent about any limitations or missing data
- Provide actionable insights when possible

### Style Requirements:
- Use bullet points and numbered lists for clarity
- Include relevant financial metrics and data
- Cite sources when referencing specific data
- Maintain objectivity while being insightful
- Use appropriate financial analysis frameworks

Generate a comprehensive, professional financial analysis report based on the available information."""
    
    return prompt


def _format_successful_results(state: GraphState) -> str:
    """
    Format successful agent results for synthesis.
    
    Args:
        state: Graph state with agent results
        
    Returns:
        Formatted results string
    """
    if not state.agent_results:
        return "No successful data retrievals were completed."
    
    formatted_results = []
    
    for task_id, result in state.agent_results.items():
        # Find the corresponding task
        task = state.get_task_by_id(task_id)
        if task:
            agent_name = task.agent
            tool_name = task.tool
            
            formatted_results.append(f"**{agent_name} - {tool_name}**:")
            
            # Format the result based on its type
            if isinstance(result, dict):
                for key, value in result.items():
                    formatted_results.append(f"  - {key}: {value}")
            elif isinstance(result, list):
                for item in result:
                    formatted_results.append(f"  - {item}")
            else:
                formatted_results.append(f"  - {result}")
            
            formatted_results.append("")  # Add spacing
    
    return "\n".join(formatted_results) if formatted_results else "No results available."


def _format_error_summary(state: GraphState) -> str:
    """
    Format error summary for transparency.
    
    Args:
        state: Graph state with error log
        
    Returns:
        Formatted error summary
    """
    if not state.error_log:
        return "All requested information was successfully retrieved."
    
    # Group errors by type
    error_groups = {}
    for error in state.error_log:
        if error.error_type not in error_groups:
            error_groups[error.error_type] = []
        error_groups[error.error_type].append(error)
    
    formatted_errors = []
    
    for error_type, errors in error_groups.items():
        if error_type in ["RETRY_ATTEMPT", "REPLAN_TRIGGERED", "TASK_SKIPPED"]:
            continue  # Skip internal remediation messages
        
        formatted_errors.append(f"**{error_type}**:")
        for error in errors:
            formatted_errors.append(f"  - {error.agent} ({error.tool}): {error.error_message}")
        formatted_errors.append("")
    
    return "\n".join(formatted_errors) if formatted_errors else "No significant issues encountered."


def _format_execution_summary(state: GraphState) -> str:
    """
    Format execution summary showing what was attempted.
    
    Args:
        state: Graph state with task plan
        
    Returns:
        Formatted execution summary
    """
    if not state.task_plan:
        return "Simple query processed directly."
    
    total_tasks = len(state.task_plan)
    completed_tasks = len([task for task in state.task_plan if task.status == "completed"])
    failed_tasks = len([task for task in state.task_plan if task.status == "failed"])
    
    summary = [
        f"Complex query decomposed into {total_tasks} tasks:",
        f"- Successfully completed: {completed_tasks}",
        f"- Failed: {failed_tasks}",
        ""
    ]
    
    # List all attempted tasks
    for task in state.task_plan:
        status_emoji = "✅" if task.status == "completed" else "❌" if task.status == "failed" else "⏳"
        summary.append(f"{status_emoji} {task.agent} - {task.tool}")
    
    return "\n".join(summary)


def _create_fallback_answer(state: GraphState) -> str:
    """
    Create a fallback answer when synthesis fails.
    
    Args:
        state: Graph state
        
    Returns:
        Fallback answer string
    """
    fallback = f"""# Financial Analysis Report

## Query
{state.original_query}

## Status
I apologize, but I encountered technical difficulties while synthesizing the final analysis report. However, I was able to gather some information:

"""
    
    # Add any available results
    if state.agent_results:
        fallback += "## Available Data\n"
        for task_id, result in state.agent_results.items():
            task = state.get_task_by_id(task_id)
            if task:
                fallback += f"- **{task.agent}**: {result}\n"
    
    # Add error acknowledgment
    if state.error_log:
        fallback += f"\n## Issues Encountered\n"
        fallback += f"- {len(state.error_log)} technical issues occurred during analysis\n"
    
    fallback += "\nPlease try your query again, or consider simplifying it for better results."
    
    return fallback