"""
Diagnosis agent implementation.

This agent specializes in comprehensive stock analysis and diagnosis.
"""

from typing import Any, List, Dict
from ..tools import get_tool
from .base import BaseAgent
from ..core.state import GraphState, TaskDefinition


class DiagnosisAgent(BaseAgent):
    """
    Agent specialized in comprehensive stock diagnosis and analysis.
    
    This agent can perform deep analysis of individual stocks by combining
    multiple data sources including stock info, news, announcements, and research reports.
    """
    
    def __init__(self, name: str):
        """Initialize the diagnosis agent."""
        super().__init__(name)
        self.available_tools = ["个股信息查询", "新闻查询", "公告查询", "研报查询"]
    
    def execute_task(self, state: GraphState, task: TaskDefinition) -> Any:
        """
        Execute a stock diagnosis task.
        
        Args:
            state: Current graph state
            task: Task definition
            
        Returns:
            Comprehensive stock diagnosis results
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
            
            # Perform diagnosis-specific processing
            if task.tool == "个股信息查询":
                result = self._analyze_stock_metrics(result, inputs)
            elif task.tool in ["新闻查询", "公告查询", "研报查询"]:
                result = self._analyze_information_impact(result, inputs)
            
            # Log execution
            self.log_execution(task, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Tool execution failed: {str(e)}")
            raise
    
    def get_available_tools(self) -> List[str]:
        """Get list of tools this agent can use."""
        return self.available_tools.copy()
    
    def _analyze_stock_metrics(self, stock_data: Any, inputs: dict) -> dict:
        """
        Analyze stock metrics and provide diagnostic insights.
        
        Args:
            stock_data: Raw stock data
            inputs: Original inputs
            
        Returns:
            Enhanced stock analysis with diagnostic insights
        """
        if not isinstance(stock_data, dict):
            return {"raw_data": stock_data, "analysis": "Unable to analyze non-structured data"}
        
        analysis = {
            "stock_data": stock_data,
            "financial_health": self._assess_financial_health(stock_data),
            "valuation_analysis": self._analyze_valuation(stock_data),
            "risk_assessment": self._assess_risks(stock_data),
            "investment_recommendation": self._generate_recommendation(stock_data)
        }
        
        return analysis
    
    def _analyze_information_impact(self, info_data: Any, inputs: dict) -> dict:
        """
        Analyze the potential impact of news/announcements on stock performance.
        
        Args:
            info_data: News or announcement data
            inputs: Original inputs
            
        Returns:
            Information impact analysis
        """
        analysis = {
            "information": info_data,
            "sentiment_analysis": self._analyze_sentiment(info_data),
            "impact_assessment": self._assess_market_impact(info_data),
            "key_themes": self._extract_key_themes(info_data),
            "timeline_relevance": self._assess_timeline_relevance(info_data)
        }
        
        return analysis
    
    def _assess_financial_health(self, stock_data: dict) -> dict:
        """
        Assess the financial health of a company.
        
        Args:
            stock_data: Stock financial data
            
        Returns:
            Financial health assessment
        """
        health_score = {"score": "N/A", "factors": [], "concerns": []}
        
        # Analyze key financial metrics if available
        if "pe_ratio" in stock_data:
            pe = stock_data["pe_ratio"]
            if isinstance(pe, (int, float)):
                if pe < 15:
                    health_score["factors"].append("Attractive valuation (low P/E)")
                elif pe > 30:
                    health_score["concerns"].append("High valuation (high P/E)")
        
        if "debt_ratio" in stock_data:
            debt = stock_data["debt_ratio"]
            if isinstance(debt, (int, float)):
                if debt < 0.3:
                    health_score["factors"].append("Low debt levels")
                elif debt > 0.6:
                    health_score["concerns"].append("High debt levels")
        
        if "roe" in stock_data:
            roe = stock_data["roe"]
            if isinstance(roe, (int, float)):
                if roe > 0.15:
                    health_score["factors"].append("Strong return on equity")
                elif roe < 0.05:
                    health_score["concerns"].append("Low profitability")
        
        # Calculate overall health score
        if len(health_score["factors"]) > len(health_score["concerns"]):
            health_score["score"] = "Good"
        elif len(health_score["concerns"]) > len(health_score["factors"]):
            health_score["score"] = "Concerning"
        else:
            health_score["score"] = "Neutral"
        
        return health_score
    
    def _analyze_valuation(self, stock_data: dict) -> dict:
        """
        Analyze stock valuation metrics.
        
        Args:
            stock_data: Stock data
            
        Returns:
            Valuation analysis
        """
        valuation = {
            "assessment": "N/A",
            "metrics": {},
            "comparison": "Industry comparison not available"
        }
        
        # Extract valuation metrics
        valuation_metrics = ["pe_ratio", "pb_ratio", "ps_ratio", "peg_ratio"]
        for metric in valuation_metrics:
            if metric in stock_data:
                valuation["metrics"][metric] = stock_data[metric]
        
        # Simple valuation assessment
        if "pe_ratio" in stock_data and isinstance(stock_data["pe_ratio"], (int, float)):
            pe = stock_data["pe_ratio"]
            if pe < 15:
                valuation["assessment"] = "Undervalued"
            elif pe > 25:
                valuation["assessment"] = "Overvalued"
            else:
                valuation["assessment"] = "Fairly valued"
        
        return valuation
    
    def _assess_risks(self, stock_data: dict) -> dict:
        """
        Assess investment risks based on available data.
        
        Args:
            stock_data: Stock data
            
        Returns:
            Risk assessment
        """
        risks = {
            "risk_level": "Unknown",
            "risk_factors": [],
            "volatility": "N/A"
        }
        
        # Assess risks based on available metrics
        if "beta" in stock_data and isinstance(stock_data["beta"], (int, float)):
            beta = stock_data["beta"]
            if beta > 1.5:
                risks["risk_factors"].append("High volatility (Beta > 1.5)")
                risks["risk_level"] = "High"
            elif beta < 0.8:
                risks["risk_factors"].append("Low volatility (Beta < 0.8)")
                risks["risk_level"] = "Low"
            else:
                risks["risk_level"] = "Moderate"
        
        if "debt_ratio" in stock_data and isinstance(stock_data["debt_ratio"], (int, float)):
            debt = stock_data["debt_ratio"]
            if debt > 0.6:
                risks["risk_factors"].append("High debt levels")
        
        return risks
    
    def _generate_recommendation(self, stock_data: dict) -> dict:
        """
        Generate investment recommendation based on analysis.
        
        Args:
            stock_data: Stock data
            
        Returns:
            Investment recommendation
        """
        recommendation = {
            "action": "Hold",
            "confidence": "Low",
            "reasoning": [],
            "target_price": "N/A"
        }
        
        # This is a simplified recommendation logic
        # In a real implementation, this would be much more sophisticated
        
        positive_factors = 0
        negative_factors = 0
        
        # Check valuation
        if "pe_ratio" in stock_data and isinstance(stock_data["pe_ratio"], (int, float)):
            pe = stock_data["pe_ratio"]
            if pe < 15:
                positive_factors += 1
                recommendation["reasoning"].append("Attractive valuation")
            elif pe > 30:
                negative_factors += 1
                recommendation["reasoning"].append("High valuation concerns")
        
        # Generate recommendation
        if positive_factors > negative_factors:
            recommendation["action"] = "Buy"
            recommendation["confidence"] = "Medium" if positive_factors >= 2 else "Low"
        elif negative_factors > positive_factors:
            recommendation["action"] = "Sell"
            recommendation["confidence"] = "Medium" if negative_factors >= 2 else "Low"
        
        return recommendation
    
    def _analyze_sentiment(self, info_data: Any) -> str:
        """Analyze sentiment of information."""
        # Simplified sentiment analysis
        if isinstance(info_data, str):
            text = info_data.lower()
            positive_words = ["增长", "上涨", "利好", "增加", "提升", "超预期"]
            negative_words = ["下跌", "亏损", "风险", "担忧", "下降", "利空"]
            
            pos_count = sum(1 for word in positive_words if word in text)
            neg_count = sum(1 for word in negative_words if word in text)
            
            if pos_count > neg_count:
                return "Positive"
            elif neg_count > pos_count:
                return "Negative"
        
        return "Neutral"
    
    def _assess_market_impact(self, info_data: Any) -> str:
        """Assess potential market impact of information."""
        # Simplified impact assessment
        if isinstance(info_data, str):
            text = info_data.lower()
            high_impact_words = ["重大", "突破", "收购", "合并", "财报", "业绩"]
            
            if any(word in text for word in high_impact_words):
                return "High"
        
        return "Low"
    
    def _extract_key_themes(self, info_data: Any) -> List[str]:
        """Extract key themes from information."""
        # Simplified theme extraction
        themes = []
        if isinstance(info_data, str):
            text = info_data.lower()
            theme_keywords = {
                "业绩": ["业绩", "财报", "收入", "利润"],
                "产品": ["产品", "技术", "创新", "研发"],
                "市场": ["市场", "行业", "竞争", "份额"],
                "监管": ["监管", "政策", "合规", "法规"]
            }
            
            for theme, keywords in theme_keywords.items():
                if any(keyword in text for keyword in keywords):
                    themes.append(theme)
        
        return themes
    
    def _assess_timeline_relevance(self, info_data: Any) -> str:
        """Assess the timeline relevance of information."""
        # Simplified timeline assessment
        return "Recent" if info_data else "Unknown"