"""
Knowledge agent implementation.

This agent specializes in financial knowledge and educational content.
"""

from typing import Any, List
from ..tools import get_tool
from .base import BaseAgent
from ..core.state import GraphState, TaskDefinition


class KnowledgeAgent(BaseAgent):
    """
    Agent specialized in financial knowledge and education.
    
    This agent provides explanations of financial concepts, investment strategies,
    and educational content to help users understand financial markets.
    """
    
    def __init__(self, name: str):
        """Initialize the knowledge agent."""
        super().__init__(name)
        self.available_tools = ["金融知识查询"]
    
    def execute_task(self, state: GraphState, task: TaskDefinition) -> Any:
        """
        Execute a knowledge-related task.
        
        Args:
            state: Current graph state
            task: Task definition
            
        Returns:
            Knowledge or educational content
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
            
            # Enhance knowledge results with context
            enhanced_result = self._enhance_knowledge_response(result, inputs, state)
            
            # Log execution
            self.log_execution(task, enhanced_result)
            
            return enhanced_result
            
        except Exception as e:
            self.logger.error(f"Tool execution failed: {str(e)}")
            raise
    
    def get_available_tools(self) -> List[str]:
        """Get list of tools this agent can use."""
        return self.available_tools.copy()
    
    def _enhance_knowledge_response(self, result: Any, inputs: dict, state: GraphState) -> dict:
        """
        Enhance knowledge responses with additional context and structure.
        
        Args:
            result: Raw knowledge result
            inputs: Original inputs
            state: Current graph state for context
            
        Returns:
            Enhanced knowledge response
        """
        if isinstance(result, dict):
            return result
        
        # Structure the knowledge response
        enhanced_response = {
            "query": inputs.get("query", ""),
            "knowledge_content": result,
            "type": self._classify_knowledge_type(inputs.get("query", "")),
            "related_concepts": self._suggest_related_concepts(inputs.get("query", "")),
            "practical_examples": self._generate_examples(inputs.get("query", ""))
        }
        
        return enhanced_response
    
    def _classify_knowledge_type(self, query: str) -> str:
        """
        Classify the type of knowledge query.
        
        Args:
            query: User's knowledge query
            
        Returns:
            Knowledge type classification
        """
        query_lower = query.lower()
        
        if any(term in query_lower for term in ["市盈率", "pe", "ratio", "指标"]):
            return "financial_metrics"
        
        if any(term in query_lower for term in ["投资", "策略", "方法", "技巧"]):
            return "investment_strategy"
        
        if any(term in query_lower for term in ["风险", "管理", "控制"]):
            return "risk_management"
        
        if any(term in query_lower for term in ["分析", "评估", "判断"]):
            return "financial_analysis"
        
        if any(term in query_lower for term in ["市场", "行业", "宏观"]):
            return "market_knowledge"
        
        return "general_knowledge"
    
    def _suggest_related_concepts(self, query: str) -> List[str]:
        """
        Suggest related financial concepts.
        
        Args:
            query: Original query
            
        Returns:
            List of related concepts
        """
        knowledge_type = self._classify_knowledge_type(query)
        
        related_concepts = {
            "financial_metrics": ["市净率", "ROE", "毛利率", "净利率", "负债率"],
            "investment_strategy": ["价值投资", "成长投资", "指数投资", "分散投资"],
            "risk_management": ["止损", "仓位管理", "资产配置", "Beta系数"],
            "financial_analysis": ["基本面分析", "技术分析", "财务报表分析", "行业分析"],
            "market_knowledge": ["牛市", "熊市", "经济周期", "货币政策", "通胀"],
            "general_knowledge": ["股票", "债券", "基金", "ETF", "期权"]
        }
        
        return related_concepts.get(knowledge_type, [])
    
    def _generate_examples(self, query: str) -> List[str]:
        """
        Generate practical examples for the knowledge topic.
        
        Args:
            query: Original query
            
        Returns:
            List of practical examples
        """
        knowledge_type = self._classify_knowledge_type(query)
        
        examples = {
            "financial_metrics": [
                "苹果公司的市盈率为28倍，表示当前股价是每股收益的28倍",
                "市盈率低于15通常被认为是价值股的标准之一"
            ],
            "investment_strategy": [
                "巴菲特的价值投资法：寻找被低估的优质公司长期持有",
                "定投策略：每月固定时间投入固定金额，降低市场波动风险"
            ],
            "risk_management": [
                "设置止损点：当股价下跌10%时自动卖出以控制损失",
                "资产配置：60%股票 + 30%债券 + 10%现金的经典配置"
            ],
            "financial_analysis": [
                "分析苹果公司：查看其营收增长、利润率、现金流等指标",
                "行业对比：比较同行业公司的估值水平和增长前景"
            ],
            "market_knowledge": [
                "2008年金融危机时，股市大幅下跌，但优质公司最终恢复并创新高",
                "美联储加息通常会对科技股产生负面影响"
            ],
            "general_knowledge": [
                "购买股票就是购买公司的一部分所有权",
                "ETF是跟踪指数的基金，可以一次性投资多只股票"
            ]
        }
        
        return examples.get(knowledge_type, [])
    
    def _get_educational_resources(self, knowledge_type: str) -> List[str]:
        """
        Get relevant educational resources for the knowledge type.
        
        Args:
            knowledge_type: Type of knowledge
            
        Returns:
            List of educational resources
        """
        resources = {
            "financial_metrics": [
                "学习如何阅读财务报表",
                "理解各种估值指标的含义和应用",
                "掌握财务比率分析方法"
            ],
            "investment_strategy": [
                "研究成功投资者的投资理念",
                "学习不同市场环境下的投资策略",
                "了解资产配置的重要性"
            ],
            "risk_management": [
                "学习投资风险的类型和管理方法",
                "掌握仓位管理和止损技巧",
                "了解分散投资的原理"
            ]
        }
        
        return resources.get(knowledge_type, [])