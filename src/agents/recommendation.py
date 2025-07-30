"""
Recommendation agent implementation.

This agent provides comprehensive investment recommendations.
"""

from typing import Any, List, Dict
from ..tools import get_tool
from .base import BaseAgent
from ..core.state import GraphState, TaskDefinition


class RecommendationAgent(BaseAgent):
    """
    Agent specialized in providing comprehensive investment recommendations.
    
    This agent has access to all tools and can provide holistic investment
    advice by combining data from multiple sources.
    """
    
    def __init__(self, name: str):
        """Initialize the recommendation agent."""
        super().__init__(name)
        self.available_tools = [
            "个股信息查询", "条件选股", "新闻查询", 
            "公告查询", "研报查询", "金融知识查询"
        ]
    
    def execute_task(self, state: GraphState, task: TaskDefinition) -> Any:
        """
        Execute a recommendation task.
        
        Args:
            state: Current graph state
            task: Task definition
            
        Returns:
            Investment recommendation results
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
            
            # Enhance result with recommendation analysis
            enhanced_result = self._enhance_with_recommendation_analysis(
                result, task.tool, inputs, state
            )
            
            # Log execution
            self.log_execution(task, enhanced_result)
            
            return enhanced_result
            
        except Exception as e:
            self.logger.error(f"Tool execution failed: {str(e)}")
            raise
    
    def get_available_tools(self) -> List[str]:
        """Get list of tools this agent can use."""
        return self.available_tools.copy()
    
    def _enhance_with_recommendation_analysis(
        self, result: Any, tool_name: str, inputs: dict, state: GraphState
    ) -> dict:
        """
        Enhance tool results with recommendation analysis.
        
        Args:
            result: Raw tool result
            tool_name: Name of the tool used
            inputs: Original inputs
            state: Current graph state for context
            
        Returns:
            Enhanced result with recommendation insights
        """
        enhanced_result = {
            "tool_result": result,
            "tool_used": tool_name,
            "recommendation_analysis": self._generate_recommendation_analysis(
                result, tool_name, inputs, state
            ),
            "investment_implications": self._analyze_investment_implications(
                result, tool_name
            ),
            "action_items": self._generate_action_items(result, tool_name),
            "risk_considerations": self._identify_risks(result, tool_name)
        }
        
        return enhanced_result
    
    def _generate_recommendation_analysis(
        self, result: Any, tool_name: str, inputs: dict, state: GraphState
    ) -> dict:
        """
        Generate comprehensive recommendation analysis.
        
        Args:
            result: Tool result
            tool_name: Tool used
            inputs: Original inputs
            state: Graph state
            
        Returns:
            Recommendation analysis
        """
        analysis = {
            "overall_assessment": "需要更多信息",
            "key_strengths": [],
            "key_concerns": [],
            "recommendation_level": "中性",
            "confidence": "低"
        }
        
        if tool_name == "个股信息查询":
            analysis = self._analyze_stock_recommendation(result)
        elif tool_name == "条件选股":
            analysis = self._analyze_screening_recommendation(result)
        elif tool_name in ["新闻查询", "公告查询"]:
            analysis = self._analyze_news_recommendation(result)
        elif tool_name == "研报查询":
            analysis = self._analyze_research_recommendation(result)
        elif tool_name == "金融知识查询":
            analysis = self._analyze_knowledge_recommendation(result)
        
        return analysis
    
    def _analyze_stock_recommendation(self, stock_data: Any) -> dict:
        """Analyze stock data for recommendation."""
        if not isinstance(stock_data, dict):
            return {"overall_assessment": "数据格式不支持分析"}
        
        strengths = []
        concerns = []
        
        # Analyze valuation
        if "pe_ratio" in stock_data and isinstance(stock_data["pe_ratio"], (int, float)):
            pe = stock_data["pe_ratio"]
            if pe < 15:
                strengths.append("估值合理 (市盈率 < 15)")
            elif pe > 30:
                concerns.append("估值偏高 (市盈率 > 30)")
        
        # Analyze growth
        if "revenue_growth" in stock_data and isinstance(stock_data["revenue_growth"], (int, float)):
            growth = stock_data["revenue_growth"]
            if growth > 15:
                strengths.append("营收增长强劲")
            elif growth < 0:
                concerns.append("营收增长疲软")
        
        # Analyze profitability
        if "roe" in stock_data and isinstance(stock_data["roe"], (int, float)):
            roe = stock_data["roe"]
            if roe > 0.15:
                strengths.append("盈利能力强 (ROE > 15%)")
            elif roe < 0.05:
                concerns.append("盈利能力弱 (ROE < 5%)")
        
        # Analyze debt
        if "debt_ratio" in stock_data and isinstance(stock_data["debt_ratio"], (int, float)):
            debt = stock_data["debt_ratio"]
            if debt < 0.3:
                strengths.append("债务水平健康")
            elif debt > 0.6:
                concerns.append("债务负担较重")
        
        # Generate overall recommendation
        if len(strengths) > len(concerns) + 1:
            recommendation_level = "推荐买入"
            confidence = "中"
        elif len(concerns) > len(strengths) + 1:
            recommendation_level = "建议卖出"
            confidence = "中"
        else:
            recommendation_level = "持有观望"
            confidence = "低"
        
        return {
            "overall_assessment": f"基于基本面分析，该股票{recommendation_level}",
            "key_strengths": strengths,
            "key_concerns": concerns,
            "recommendation_level": recommendation_level,
            "confidence": confidence
        }
    
    def _analyze_screening_recommendation(self, screening_result: Any) -> dict:
        """Analyze stock screening results."""
        if isinstance(screening_result, list):
            stock_count = len(screening_result)
            if stock_count > 10:
                assessment = f"筛选出{stock_count}只股票，建议进一步细化筛选条件"
                recommendation = "优化筛选"
            elif stock_count > 0:
                assessment = f"筛选出{stock_count}只候选股票，建议逐一深入分析"
                recommendation = "深入研究"
            else:
                assessment = "未找到符合条件的股票，建议放宽筛选条件"
                recommendation = "调整条件"
        else:
            assessment = "筛选结果格式异常"
            recommendation = "重新筛选"
        
        return {
            "overall_assessment": assessment,
            "key_strengths": ["系统化选股方法"],
            "key_concerns": ["需要进一步验证"],
            "recommendation_level": recommendation,
            "confidence": "中"
        }
    
    def _analyze_news_recommendation(self, news_data: Any) -> dict:
        """Analyze news data for investment implications."""
        sentiment = self._analyze_news_sentiment(news_data)
        impact = self._assess_news_impact(news_data)
        
        if sentiment == "positive" and impact == "high":
            recommendation = "积极关注"
            assessment = "正面新闻可能推动股价上涨"
        elif sentiment == "negative" and impact == "high":
            recommendation = "谨慎观望"
            assessment = "负面新闻可能影响股价表现"
        else:
            recommendation = "继续关注"
            assessment = "新闻影响有限，保持关注"
        
        return {
            "overall_assessment": assessment,
            "key_strengths": ["及时的信息更新"],
            "key_concerns": ["新闻真实性需要验证"],
            "recommendation_level": recommendation,
            "confidence": "中"
        }
    
    def _analyze_research_recommendation(self, research_data: Any) -> dict:
        """Analyze research report data."""
        return {
            "overall_assessment": "研报提供专业分析视角",
            "key_strengths": ["专业机构分析", "深度行业洞察"],
            "key_concerns": ["可能存在利益冲突", "时效性"],
            "recommendation_level": "参考借鉴",
            "confidence": "中"
        }
    
    def _analyze_knowledge_recommendation(self, knowledge_data: Any) -> dict:
        """Analyze knowledge query results."""
        return {
            "overall_assessment": "知识学习有助于提升投资决策能力",
            "key_strengths": ["提升投资素养", "理论指导实践"],
            "key_concerns": ["理论与实践存在差距"],
            "recommendation_level": "建议学习",
            "confidence": "高"
        }
    
    def _analyze_investment_implications(self, result: Any, tool_name: str) -> dict:
        """
        Analyze investment implications of the result.
        
        Args:
            result: Tool result
            tool_name: Tool used
            
        Returns:
            Investment implications analysis
        """
        implications = {
            "short_term_impact": "有限",
            "long_term_impact": "待观察",
            "portfolio_implications": "无重大影响",
            "sector_implications": "行业影响不明确"
        }
        
        # Customize based on tool type
        if tool_name == "个股信息查询":
            implications["short_term_impact"] = "可能影响短期交易决策"
            implications["long_term_impact"] = "基本面分析对长期投资有指导意义"
        elif tool_name == "新闻查询":
            implications["short_term_impact"] = "新闻可能引起短期波动"
            implications["sector_implications"] = "可能影响相关行业"
        
        return implications
    
    def _generate_action_items(self, result: Any, tool_name: str) -> List[str]:
        """
        Generate actionable investment recommendations.
        
        Args:
            result: Tool result
            tool_name: Tool used
            
        Returns:
            List of action items
        """
        action_items = []
        
        if tool_name == "个股信息查询":
            action_items = [
                "分析财务指标趋势",
                "比较同行业公司",
                "关注最新公司动态",
                "评估风险收益比"
            ]
        elif tool_name == "条件选股":
            action_items = [
                "对筛选结果进行排序",
                "进行个股深度分析",
                "分散投资降低风险",
                "设定止损点位"
            ]
        elif tool_name in ["新闻查询", "公告查询"]:
            action_items = [
                "验证消息真实性",
                "评估影响持续时间",
                "关注市场反应",
                "调整投资策略"
            ]
        elif tool_name == "研报查询":
            action_items = [
                "交叉验证不同研报观点",
                "关注研报更新",
                "结合自身判断",
                "跟踪分析师准确率"
            ]
        else:
            action_items = [
                "收集更多信息",
                "制定投资计划",
                "控制投资风险",
                "定期回顾调整"
            ]
        
        return action_items
    
    def _identify_risks(self, result: Any, tool_name: str) -> List[str]:
        """
        Identify investment risks based on the result.
        
        Args:
            result: Tool result
            tool_name: Tool used
            
        Returns:
            List of identified risks
        """
        common_risks = [
            "市场风险",
            "流动性风险",
            "信息不对称风险"
        ]
        
        specific_risks = []
        
        if tool_name == "个股信息查询":
            specific_risks = ["个股特有风险", "财务数据滞后风险"]
        elif tool_name == "新闻查询":
            specific_risks = ["信息真实性风险", "市场过度反应风险"]
        elif tool_name == "条件选股":
            specific_risks = ["模型失效风险", "历史数据局限性"]
        
        return common_risks + specific_risks
    
    def _analyze_news_sentiment(self, news_data: Any) -> str:
        """Analyze sentiment of news data."""
        # Simplified sentiment analysis
        if isinstance(news_data, str):
            text = news_data.lower()
            positive_words = ["增长", "上涨", "利好", "突破", "创新"]
            negative_words = ["下跌", "亏损", "风险", "警告", "下滑"]
            
            pos_count = sum(1 for word in positive_words if word in text)
            neg_count = sum(1 for word in negative_words if word in text)
            
            if pos_count > neg_count:
                return "positive"
            elif neg_count > pos_count:
                return "negative"
        
        return "neutral"
    
    def _assess_news_impact(self, news_data: Any) -> str:
        """Assess the potential impact of news."""
        if isinstance(news_data, str):
            text = news_data.lower()
            high_impact_words = ["重大", "突破", "收购", "重组", "业绩"]
            
            if any(word in text for word in high_impact_words):
                return "high"
        
        return "medium"