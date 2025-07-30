"""
Fallback node for out-of-scope queries.

This module implements the "Fallback Agent" that provides graceful responses
for queries that are outside the system's financial analysis capabilities.
"""

from typing import Dict, Any
import logging

from ..core.state import GraphState

logger = logging.getLogger(__name__)


def fallback_node(state: GraphState) -> Dict[str, Any]:
    """
    Fallback node that handles out-of-scope queries.
    
    This node provides polite, helpful responses for queries that are:
    1. Classified as OOS (Out-of-Scope) by the router
    2. Have encountered critical failures during processing
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with appropriate fallback response
    """
    logger.info(f"Fallback node handling query: {state.original_query}")
    
    # Determine the type of fallback response needed
    if state.query_complexity == "OOS":
        fallback_answer = _create_oos_response(state.original_query)
        logger.info("Created out-of-scope response")
    else:
        fallback_answer = _create_failure_response(state)
        logger.info("Created failure recovery response")
    
    # Update state with fallback answer
    state.final_answer = fallback_answer
    state.update_timestamp()
    
    return {"final_answer": fallback_answer}


def _create_oos_response(query: str) -> str:
    """
    Create a helpful response for out-of-scope queries.
    
    Args:
        query: The original user query
        
    Returns:
        Polite and helpful OOS response
    """
    response = f"""# 查询响应

您好！感谢您的咨询。

## 关于您的问题
您询问的是："{query}"

## 我的专业领域
我是一个专注于**金融分析**的AI助手，我的核心能力包括：

### 📊 股票分析
- 个股信息查询（股价、市盈率、市值等）
- 条件选股和股票筛选
- 股票诊断和技术分析
- 股票投资建议

### 📰 金融资讯
- 金融新闻查询和分析
- 公司公告信息
- 研究报告摘要
- 市场动态追踪

### 💡 金融知识
- 金融概念解释
- 投资策略分析
- 风险评估指导
- 财务指标解读

## 建议
为了更好地为您服务，您可以尝试询问以下类型的问题：

- "比亚迪的股价是多少？"
- "市盈率低于20的科技股有哪些？"
- "特斯拉最近有什么重要新闻？"
- "如何分析一只股票的投资价值？"

如果您有任何**金融或投资相关**的问题，我很乐意为您提供专业的分析和建议！

---
*如有金融投资问题，请随时咨询！*"""
    
    return response


def _create_failure_response(state: GraphState) -> str:
    """
    Create a response for queries that failed during processing.
    
    Args:
        state: Graph state with error information
        
    Returns:
        Apologetic but helpful failure response
    """
    response = f"""# 分析报告

## 您的查询
{state.original_query}

## 分析状态
很抱歉，在处理您的查询时遇到了一些技术问题，无法完成完整的分析。

## 遇到的问题
"""
    
    # Summarize the main issues
    if state.error_log:
        error_types = set([error.error_type for error in state.error_log])
        
        if "NETWORK_ERROR" in error_types or "API_TIMEOUT" in error_types:
            response += "- 网络连接或数据服务暂时不稳定\n"
        
        if "INVALID_INPUT" in error_types:
            response += "- 部分查询参数可能需要调整\n"
        
        if "AUTH_ERROR" in error_types:
            response += "- 数据服务认证问题\n"
        
        if "RATE_LIMIT_ERROR" in error_types:
            response += "- 数据请求频率限制\n"
    
    response += """
## 建议措施
1. **稍后重试**：某些问题可能是暂时性的
2. **简化查询**：尝试将复杂问题分解为多个简单问题
3. **检查输入**：确认股票代码、公司名称等信息准确

## 我仍能帮助您
即使遇到了这些技术问题，我仍然可以为您提供：
- 金融概念和投资知识解答
- 市场分析方法指导
- 投资策略建议
- 风险管理建议

## 示例问题
您可以尝试这样的问题：
- "什么是市盈率？如何使用它评估股票？"
- "价值投资的核心原则是什么？"
- "如何进行基本面分析？"

感谢您的理解，请随时提出其他金融相关问题！

---
*技术问题通常是暂时的，建议稍后重试您的原始查询*"""
    
    return response


def _detect_query_intent(query: str) -> str:
    """
    Analyze the query to better understand user intent for more helpful responses.
    
    Args:
        query: User's original query
        
    Returns:
        Detected intent category
    """
    query_lower = query.lower()
    
    # Weather related
    if any(word in query_lower for word in ["天气", "weather", "温度", "下雨"]):
        return "weather"
    
    # Cooking/recipes
    if any(word in query_lower for word in ["做饭", "食谱", "烹饪", "cooking", "recipe"]):
        return "cooking"
    
    # General knowledge
    if any(word in query_lower for word in ["什么是", "how to", "怎么", "为什么"]):
        return "general_knowledge"
    
    # Entertainment
    if any(word in query_lower for word in ["电影", "音乐", "游戏", "娱乐", "movie", "music"]):
        return "entertainment"
    
    # Technology (non-financial)
    if any(word in query_lower for word in ["编程", "代码", "软件", "programming", "code"]):
        return "technology"
    
    return "other"


def _create_contextual_suggestion(intent: str) -> str:
    """
    Create contextual suggestions based on detected intent.
    
    Args:
        intent: Detected query intent
        
    Returns:
        Contextual suggestion text
    """
    suggestions = {
        "weather": "对于天气信息，建议您使用专门的天气应用或网站。",
        "cooking": "对于烹饪问题，建议您查阅专业的美食网站或烹饪应用。",
        "entertainment": "对于娱乐资讯，建议您使用专门的娱乐或影音平台。",
        "technology": "对于技术问题，建议您查阅技术文档或专业的开发者社区。",
        "general_knowledge": "对于一般知识问题，建议您使用通用的搜索引擎或百科全书。"
    }
    
    return suggestions.get(intent, "建议您使用专门针对该领域的工具或服务。")


def _get_sample_financial_queries() -> list:
    """
    Get sample financial queries to help users understand capabilities.
    
    Returns:
        List of sample queries
    """
    return [
        "苹果公司(AAPL)的当前股价和市盈率是多少？",
        "帮我找出市盈率低于15的科技股",
        "特斯拉最近有什么重要新闻和公告？",
        "比较比亚迪和蔚来汽车的财务表现",
        "什么是价值投资？如何选择价值股？",
        "如何分析一家公司的财务健康状况？"
    ]