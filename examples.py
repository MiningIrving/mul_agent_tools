"""
Example usage of the Multi-Agent Financial Analysis Framework.

This script demonstrates how to use the framework for various types of financial queries.
"""

import sys
import os
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.graph import FinancialAnalysisGraph
from core.state import GraphState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_simple_query():
    """Example of a simple query that goes directly to execution."""
    print("\n" + "="*60)
    print("Example 1: Simple Query")
    print("="*60)
    
    graph = FinancialAnalysisGraph(enable_persistence=False)
    
    query = "苹果公司的股价是多少？"
    session_id = f"simple_query_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"Query: {query}")
    print(f"Session ID: {session_id}")
    
    try:
        # Note: This will fail without actual LLM API keys, but shows the structure
        result = graph.invoke(query, session_id)
        print(f"Result: {result.final_answer}")
    except Exception as e:
        print(f"Error (expected without API keys): {e}")
        
        # Show what would happen by creating a mock state
        mock_state = GraphState(
            original_query=query,
            session_id=session_id,
            query_complexity="SIMPLE",
            final_answer="苹果公司(AAPL)当前股价: $185.25，涨幅: +2.3%"
        )
        print(f"Mock Result: {mock_state.final_answer}")


def example_complex_query():
    """Example of a complex query that requires planning and multiple agents."""
    print("\n" + "="*60)
    print("Example 2: Complex Query")
    print("="*60)
    
    graph = FinancialAnalysisGraph(enable_persistence=False)
    
    query = "比较比亚迪和特斯拉的财务表现，并分析它们的投资价值"
    session_id = f"complex_query_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"Query: {query}")
    print(f"Session ID: {session_id}")
    
    try:
        result = graph.invoke(query, session_id)
        print(f"Result: {result.final_answer}")
    except Exception as e:
        print(f"Error (expected without API keys): {e}")
        
        # Show the expected workflow
        print("\nExpected Workflow:")
        print("1. Router: Classifies as COMPLEX")
        print("2. Planner: Creates task plan:")
        print("   - Task 1: 选股agent - 个股信息查询 (比亚迪)")
        print("   - Task 2: 选股agent - 个股信息查询 (特斯拉)")  
        print("   - Task 3: 新闻agent - 新闻查询 (比亚迪)")
        print("   - Task 4: 新闻agent - 新闻查询 (特斯拉)")
        print("   - Task 5: 荐股agent - 综合分析")
        print("3. Agent Executor: Executes tasks sequentially")
        print("4. Answer Generator: Synthesizes final comparison report")


def example_knowledge_query():
    """Example of a knowledge query."""
    print("\n" + "="*60)
    print("Example 3: Knowledge Query")
    print("="*60)
    
    # Demonstrate knowledge tool directly
    from tools.knowledge_query import KnowledgeQueryTool
    
    tool = KnowledgeQueryTool("金融知识查询")
    
    queries = [
        "什么是市盈率？",
        "价值投资的原理是什么？",
        "如何进行风险管理？"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        try:
            result = tool.execute(query=query)
            print(f"Concept: {result.get('concept', 'N/A')}")
            print(f"Definition: {result.get('definition', 'N/A')[:100]}...")
            if result.get('related_concepts'):
                print(f"Related: {', '.join(result['related_concepts'])}")
        except Exception as e:
            print(f"Error: {e}")


def example_stock_screening():
    """Example of stock screening."""
    print("\n" + "="*60)
    print("Example 4: Stock Screening")
    print("="*60)
    
    from tools.stock_selection import StockSelectionTool
    
    tool = StockSelectionTool("条件选股")
    
    # Screen for value stocks
    criteria = {
        "pe_ratio_max": 20,
        "market_cap_min": 100,  # 100亿以上
        "roe_min": 0.15,  # ROE > 15%
        "industry": "科技",
        "limit": 5
    }
    
    print("Screening criteria:")
    for key, value in criteria.items():
        print(f"  {key}: {value}")
    
    try:
        results = tool.execute(**criteria)
        print(f"\nFound {len(results)} stocks:")
        for i, stock in enumerate(results, 1):
            name = stock.get('stock_name', stock.get('company_name', 'Unknown'))
            pe = stock.get('pe_ratio', 'N/A')
            roe = stock.get('roe', 'N/A')
            print(f"  {i}. {name} - PE: {pe}, ROE: {roe}")
    except Exception as e:
        print(f"Error: {e}")


def example_news_search():
    """Example of news search."""
    print("\n" + "="*60)
    print("Example 5: News Search") 
    print("="*60)
    
    from tools.news_query import NewsQueryTool
    
    tool = NewsQueryTool("新闻查询")
    
    queries = [
        {"company": "比亚迪", "limit": 3},
        {"keywords": ["新能源", "汽车"], "limit": 2}
    ]
    
    for query_params in queries:
        print(f"\nNews query: {query_params}")
        try:
            results = tool.execute(**query_params)
            print(f"Found {len(results)} news articles:")
            for i, article in enumerate(results, 1):
                title = article.get('title', 'No title')
                source = article.get('source', 'Unknown')
                print(f"  {i}. {title[:50]}... ({source})")
        except Exception as e:
            print(f"Error: {e}")


def demonstrate_graph_structure():
    """Demonstrate the graph structure."""
    print("\n" + "="*60)
    print("Graph Structure Visualization")
    print("="*60)
    
    graph = FinancialAnalysisGraph(enable_persistence=False)
    
    try:
        print("Graph structure:")
        print(graph.get_graph_visualization())
    except Exception as e:
        print(f"Error getting visualization: {e}")
        
        # Show the conceptual structure
        print("Conceptual Graph Structure:")
        print("""
        START
          ↓
        Router (query classification)
          ↓
        ┌─────────────────────────────┐
        │ SIMPLE    │ COMPLEX  │ OOS │
        ↓           ↓          ↓
        Agent       Planner    Fallback
        Executor    ↓          Agent
        ↓           Agent      ↓
        Answer      Executor   END
        Generator   ↓
        ↓           Remediation
        END         ↓
                    Answer
                    Generator
                    ↓
                    END
        """)


def main():
    """Main function to run all examples."""
    print("Multi-Agent Financial Analysis Framework Examples")
    print("================================================")
    
    # Run examples
    example_simple_query()
    example_complex_query()
    example_knowledge_query()
    example_stock_screening()
    example_news_search()
    demonstrate_graph_structure()
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60)
    print("\nNote: Some examples may show errors due to missing API keys.")
    print("To run with actual LLM integration, set:")
    print("  export OPENAI_API_KEY='your_api_key'")
    print("  export LANGFUSE_PUBLIC_KEY='your_public_key'")
    print("  export LANGFUSE_SECRET_KEY='your_secret_key'")


if __name__ == "__main__":
    main()