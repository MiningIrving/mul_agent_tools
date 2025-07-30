"""
Prediction agent implementation.

This agent specializes in stock price prediction and trend analysis.
"""

from typing import Any, List, Dict
from ..tools import get_tool
from .base import BaseAgent
from ..core.state import GraphState, TaskDefinition


class PredictionAgent(BaseAgent):
    """
    Agent specialized in stock price prediction and trend analysis.
    
    This agent combines stock data and research reports to provide
    price predictions and trend analysis.
    """
    
    def __init__(self, name: str):
        """Initialize the prediction agent."""
        super().__init__(name)
        self.available_tools = ["个股信息查询", "研报查询"]
    
    def execute_task(self, state: GraphState, task: TaskDefinition) -> Any:
        """
        Execute a prediction task.
        
        Args:
            state: Current graph state
            task: Task definition
            
        Returns:
            Prediction analysis results
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
            
            # Perform prediction-specific analysis
            if task.tool == "个股信息查询":
                result = self._analyze_price_trends(result, inputs, state)
            elif task.tool == "研报查询":
                result = self._analyze_analyst_predictions(result, inputs)
            
            # Log execution
            self.log_execution(task, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Tool execution failed: {str(e)}")
            raise
    
    def get_available_tools(self) -> List[str]:
        """Get list of tools this agent can use."""
        return self.available_tools.copy()
    
    def _analyze_price_trends(self, stock_data: Any, inputs: dict, state: GraphState) -> dict:
        """
        Analyze price trends and generate predictions.
        
        Args:
            stock_data: Stock data
            inputs: Original inputs
            state: Graph state for additional context
            
        Returns:
            Price trend analysis with predictions
        """
        analysis = {
            "stock_data": stock_data,
            "trend_analysis": self._perform_trend_analysis(stock_data),
            "price_prediction": self._generate_price_prediction(stock_data),
            "risk_factors": self._identify_prediction_risks(stock_data),
            "confidence_level": self._calculate_confidence(stock_data),
            "timeframe": "短期(1-3个月)"
        }
        
        return analysis
    
    def _analyze_analyst_predictions(self, research_data: Any, inputs: dict) -> dict:
        """
        Analyze analyst predictions from research reports.
        
        Args:
            research_data: Research report data
            inputs: Original inputs
            
        Returns:
            Analyst prediction analysis
        """
        analysis = {
            "research_data": research_data,
            "analyst_consensus": self._extract_consensus(research_data),
            "target_prices": self._extract_target_prices(research_data),
            "rating_distribution": self._analyze_ratings(research_data),
            "key_assumptions": self._extract_assumptions(research_data)
        }
        
        return analysis
    
    def _perform_trend_analysis(self, stock_data: dict) -> dict:
        """
        Perform technical trend analysis.
        
        Args:
            stock_data: Stock data
            
        Returns:
            Trend analysis results
        """
        trend_analysis = {
            "short_term_trend": "Unknown",
            "medium_term_trend": "Unknown",
            "momentum_indicators": {},
            "support_resistance": {}
        }
        
        # Simple trend analysis based on available data
        if "current_price" in stock_data and "price_change" in stock_data:
            price_change = stock_data.get("price_change", 0)
            
            if isinstance(price_change, (int, float)):
                if price_change > 5:
                    trend_analysis["short_term_trend"] = "强烈上涨"
                elif price_change > 2:
                    trend_analysis["short_term_trend"] = "上涨"
                elif price_change > -2:
                    trend_analysis["short_term_trend"] = "震荡"
                elif price_change > -5:
                    trend_analysis["short_term_trend"] = "下跌"
                else:
                    trend_analysis["short_term_trend"] = "强烈下跌"
        
        # Add momentum indicators if available
        momentum_indicators = ["rsi", "macd", "moving_average"]
        for indicator in momentum_indicators:
            if indicator in stock_data:
                trend_analysis["momentum_indicators"][indicator] = stock_data[indicator]
        
        return trend_analysis
    
    def _generate_price_prediction(self, stock_data: dict) -> dict:
        """
        Generate price prediction based on available data.
        
        Args:
            stock_data: Stock data
            
        Returns:
            Price prediction
        """
        prediction = {
            "predicted_direction": "Unknown",
            "target_price_range": "N/A",
            "probability": "N/A",
            "methodology": "基于基本面和技术分析的简化预测"
        }
        
        # Simple prediction logic based on available metrics
        positive_indicators = 0
        negative_indicators = 0
        
        # Check valuation
        if "pe_ratio" in stock_data and isinstance(stock_data["pe_ratio"], (int, float)):
            pe = stock_data["pe_ratio"]
            if pe < 15:
                positive_indicators += 1
            elif pe > 30:
                negative_indicators += 1
        
        # Check growth
        if "revenue_growth" in stock_data and isinstance(stock_data["revenue_growth"], (int, float)):
            growth = stock_data["revenue_growth"]
            if growth > 10:
                positive_indicators += 1
            elif growth < 0:
                negative_indicators += 1
        
        # Check recent performance
        if "price_change" in stock_data and isinstance(stock_data["price_change"], (int, float)):
            change = stock_data["price_change"]
            if change > 0:
                positive_indicators += 0.5
            else:
                negative_indicators += 0.5
        
        # Generate prediction
        if positive_indicators > negative_indicators:
            prediction["predicted_direction"] = "上涨"
            if "current_price" in stock_data:
                try:
                    current_price = float(stock_data["current_price"])
                    target_low = current_price * 1.05
                    target_high = current_price * 1.15
                    prediction["target_price_range"] = f"{target_low:.2f} - {target_high:.2f}"
                except (ValueError, TypeError):
                    pass
        elif negative_indicators > positive_indicators:
            prediction["predicted_direction"] = "下跌"
            if "current_price" in stock_data:
                try:
                    current_price = float(stock_data["current_price"])
                    target_low = current_price * 0.85
                    target_high = current_price * 0.95
                    prediction["target_price_range"] = f"{target_low:.2f} - {target_high:.2f}"
                except (ValueError, TypeError):
                    pass
        else:
            prediction["predicted_direction"] = "震荡"
        
        return prediction
    
    def _identify_prediction_risks(self, stock_data: dict) -> List[str]:
        """
        Identify risks that could affect predictions.
        
        Args:
            stock_data: Stock data
            
        Returns:
            List of prediction risks
        """
        risks = []
        
        # Market risks
        if "beta" in stock_data and isinstance(stock_data["beta"], (int, float)):
            beta = stock_data["beta"]
            if beta > 1.5:
                risks.append("高市场波动性风险")
        
        # Fundamental risks
        if "debt_ratio" in stock_data and isinstance(stock_data["debt_ratio"], (int, float)):
            debt = stock_data["debt_ratio"]
            if debt > 0.6:
                risks.append("高负债风险")
        
        # Valuation risks
        if "pe_ratio" in stock_data and isinstance(stock_data["pe_ratio"], (int, float)):
            pe = stock_data["pe_ratio"]
            if pe > 40:
                risks.append("估值过高风险")
        
        # Add general market risks
        risks.extend([
            "宏观经济风险",
            "行业政策风险",
            "市场情绪风险"
        ])
        
        return risks
    
    def _calculate_confidence(self, stock_data: dict) -> str:
        """
        Calculate prediction confidence level.
        
        Args:
            stock_data: Stock data
            
        Returns:
            Confidence level
        """
        data_completeness = len([k for k, v in stock_data.items() if v is not None])
        
        if data_completeness >= 8:
            return "高"
        elif data_completeness >= 5:
            return "中"
        else:
            return "低"
    
    def _extract_consensus(self, research_data: Any) -> dict:
        """Extract analyst consensus from research data."""
        # Simplified consensus extraction
        return {
            "average_rating": "Unknown",
            "buy_recommendations": 0,
            "hold_recommendations": 0,
            "sell_recommendations": 0
        }
    
    def _extract_target_prices(self, research_data: Any) -> dict:
        """Extract target prices from research data."""
        return {
            "average_target": "N/A",
            "highest_target": "N/A",
            "lowest_target": "N/A",
            "price_range": "N/A"
        }
    
    def _analyze_ratings(self, research_data: Any) -> dict:
        """Analyze rating distribution."""
        return {
            "buy_percentage": 0,
            "hold_percentage": 0,
            "sell_percentage": 0,
            "total_analysts": 0
        }
    
    def _extract_assumptions(self, research_data: Any) -> List[str]:
        """Extract key assumptions from research reports."""
        # Simplified assumption extraction
        return [
            "基于当前市场环境的假设",
            "假设行业政策保持稳定",
            "假设公司基本面无重大变化"
        ]