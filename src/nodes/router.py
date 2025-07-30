"""
Router node for query classification.

This module implements the "Master Router" that serves as the first line of defense,
classifying incoming queries by complexity and domain relevance.
"""

from typing import Dict, Any
import logging
from langchain.schema import HumanMessage
from langchain.chat_models import ChatOpenAI

from ..core.state import GraphState

logger = logging.getLogger(__name__)


def router_node(state: GraphState) -> Dict[str, Any]:
    """
    Router node that classifies queries into SIMPLE, COMPLEX, or OOS categories.
    
    This node analyzes the user's original query and determines its complexity
    and domain relevance to route it to the appropriate processing path.
    
    Args:
        state: Current graph state containing the original query
        
    Returns:
        Updated state with query_complexity field set
    """
    logger.info(f"Router processing query: {state.original_query}")
    
    try:
        # Initialize the LLM for classification
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            max_tokens=50
        )
        
        # Classification prompt with clear instructions and examples
        classification_prompt = """You are a query classifier for a financial analysis system. 
Classify the following user query into exactly one of these categories:

SIMPLE: Single-step queries that can be answered by one tool/agent directly
- Examples: "What is AAPL's current stock price?", "What's Tesla's P/E ratio?"

COMPLEX: Multi-step queries requiring multiple agents and data sources  
- Examples: "Compare Apple and Microsoft's financial performance", "Analyze Tesla's recent performance and find related news"

OOS: Out-of-scope queries unrelated to financial analysis
- Examples: "What's the weather today?", "How do I cook pasta?"

Query: "{query}"

Respond with only one word: SIMPLE, COMPLEX, or OOS"""
        
        # Format the prompt with the actual query
        formatted_prompt = classification_prompt.format(query=state.original_query)
        
        # Get classification from LLM
        message = HumanMessage(content=formatted_prompt)
        response = llm([message])
        
        # Extract and validate the classification
        classification = response.content.strip().upper()
        
        if classification not in ["SIMPLE", "COMPLEX", "OOS"]:
            logger.warning(f"Invalid classification '{classification}', defaulting to COMPLEX")
            classification = "COMPLEX"
        
        logger.info(f"Query classified as: {classification}")
        
        # Update state with classification
        state.query_complexity = classification
        state.update_timestamp()
        
        return {"query_complexity": classification}
        
    except Exception as e:
        logger.error(f"Error in router node: {str(e)}")
        
        # Default to COMPLEX on error to ensure the query gets processed
        state.query_complexity = "COMPLEX" 
        state.add_error(
            task_id="router_classification",
            agent="router",
            tool="llm_classification",
            error_type="CLASSIFICATION_ERROR",
            error_message=str(e)
        )
        
        return {"query_complexity": "COMPLEX"}


def _get_classification_examples() -> str:
    """
    Get few-shot examples for better classification accuracy.
    
    Returns:
        String containing classification examples
    """
    examples = """
Examples of each category:

SIMPLE:
- "What is Apple's current stock price?"
- "Show me Tesla's P/E ratio"
- "What's the market cap of Microsoft?"
- "Get the latest price of BYD stock"

COMPLEX:
- "Compare Apple and Microsoft's financial performance over the last year"
- "Analyze Tesla's recent stock performance and find related news"
- "Find undervalued tech stocks with P/E ratio below 20"
- "Compare BYD and NIO's valuation and find recent research reports"

OOS:
- "What's the weather like today?"
- "How do I cook pasta?"
- "What time is it in New York?"
- "Tell me a joke"
"""
    return examples