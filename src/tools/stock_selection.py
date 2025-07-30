"""
Stock selection tool implementation.

This tool provides conditional stock screening and selection
based on various financial criteria.
"""

from typing import Dict, Any, List
import random
from .base import BaseTool


class StockSelectionTool(BaseTool):
    """
    Tool for conditional stock screening and selection.
    
    This tool can filter stocks based on various criteria such as
    valuation metrics, financial ratios, market cap, and industry.
    """
    
    def __init__(self, name: str):
        """Initialize the stock selection tool."""
        super().__init__(name)
    
    def execute(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Execute stock selection based on criteria.
        
        Args:
            **kwargs: Selection criteria
            
        Returns:
            List of stocks matching the criteria
            
        Raises:
            ValueError: If no valid criteria are provided
        """
        # Validate inputs
        if not self.validate_inputs(kwargs):
            raise ValueError("Invalid inputs for stock selection")
        
        # Extract selection criteria
        criteria = self._extract_criteria(kwargs)
        
        if not criteria:
            raise ValueError("At least one selection criterion is required")
        
        try:
            # Perform stock screening
            selected_stocks = self._screen_stocks(criteria)
            
            self.log_execution(kwargs, selected_stocks)
            
            return selected_stocks
            
        except Exception as e:
            self.logger.error(f"Failed to screen stocks: {str(e)}")
            raise
    
    def get_schema(self) -> Dict[str, Any]:
        """Get input schema for stock selection."""
        return {
            "type": "object",
            "properties": {
                "pe_ratio_max": {
                    "type": "number",
                    "description": "Maximum P/E ratio"
                },
                "pe_ratio_min": {
                    "type": "number", 
                    "description": "Minimum P/E ratio"
                },
                "pb_ratio_max": {
                    "type": "number",
                    "description": "Maximum P/B ratio"
                },
                "pb_ratio_min": {
                    "type": "number",
                    "description": "Minimum P/B ratio"
                },
                "market_cap_min": {
                    "type": "number",
                    "description": "Minimum market capitalization"
                },
                "market_cap_max": {
                    "type": "number",
                    "description": "Maximum market capitalization"
                },
                "roe_min": {
                    "type": "number",
                    "description": "Minimum return on equity"
                },
                "debt_ratio_max": {
                    "type": "number",
                    "description": "Maximum debt ratio"
                },
                "revenue_growth_min": {
                    "type": "number",
                    "description": "Minimum revenue growth rate (%)"
                },
                "dividend_yield_min": {
                    "type": "number",
                    "description": "Minimum dividend yield (%)"
                },
                "industry": {
                    "type": "string",
                    "description": "Industry filter"
                },
                "sector": {
                    "type": "string",
                    "description": "Sector filter"
                },
                "exchange": {
                    "type": "string",
                    "description": "Exchange filter (e.g., SZ, SH, NASDAQ)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 20
                }
            },
            "additionalProperties": False
        }
    
    def get_description(self) -> str:
        """Get tool description."""
        return "根据财务指标和市场条件筛选股票，支持市盈率、市净率、市值、ROE等多种条件"
    
    def _extract_criteria(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract valid screening criteria from inputs."""
        valid_criteria = {}
        
        # Numerical criteria
        numerical_fields = [
            "pe_ratio_max", "pe_ratio_min", "pb_ratio_max", "pb_ratio_min",
            "market_cap_min", "market_cap_max", "roe_min", "debt_ratio_max",
            "revenue_growth_min", "dividend_yield_min"
        ]
        
        for field in numerical_fields:
            if field in kwargs and kwargs[field] is not None:
                try:
                    valid_criteria[field] = float(kwargs[field])
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid numerical value for {field}: {kwargs[field]}")
        
        # String criteria
        string_fields = ["industry", "sector", "exchange"]
        for field in string_fields:
            if field in kwargs and kwargs[field]:
                valid_criteria[field] = str(kwargs[field]).strip()
        
        # Limit
        if "limit" in kwargs:
            try:
                valid_criteria["limit"] = int(kwargs["limit"])
            except (ValueError, TypeError):
                valid_criteria["limit"] = 20
        else:
            valid_criteria["limit"] = 20
        
        return valid_criteria
    
    def _screen_stocks(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Perform stock screening based on criteria.
        
        In a real implementation, this would query actual stock databases.
        For now, we'll simulate the screening process.
        """
        # Generate a pool of simulated stocks
        stock_pool = self._generate_stock_pool()
        
        # Apply filters
        filtered_stocks = []
        
        for stock in stock_pool:
            if self._stock_matches_criteria(stock, criteria):
                filtered_stocks.append(stock)
        
        # Limit results
        limit = criteria.get("limit", 20)
        return filtered_stocks[:limit]
    
    def _generate_stock_pool(self) -> List[Dict[str, Any]]:
        """Generate a simulated pool of stocks for screening."""
        chinese_stocks = [
            {"code": "000001.SZ", "name": "平安银行", "industry": "金融"},
            {"code": "000002.SZ", "name": "万科A", "industry": "房地产"},
            {"code": "000858.SZ", "name": "五粮液", "industry": "白酒"},
            {"code": "002594.SZ", "name": "比亚迪", "industry": "汽车"},
            {"code": "600519.SH", "name": "贵州茅台", "industry": "白酒"},
            {"code": "600036.SH", "name": "招商银行", "industry": "金融"},
            {"code": "000776.SZ", "name": "广发证券", "industry": "金融"},
            {"code": "002415.SZ", "name": "海康威视", "industry": "科技"},
            {"code": "000063.SZ", "name": "中兴通讯", "industry": "科技"},
            {"code": "002371.SZ", "name": "北方华创", "industry": "科技"}
        ]
        
        us_stocks = [
            {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
            {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Discretionary"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology"},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Discretionary"},
            {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial"},
            {"symbol": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare"},
            {"symbol": "V", "name": "Visa Inc.", "sector": "Financial"},
            {"symbol": "PG", "name": "Procter & Gamble Co.", "sector": "Consumer Staples"},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology"}
        ]
        
        stock_pool = []
        
        # Generate Chinese stocks with random metrics
        for stock in chinese_stocks:
            stock_data = {
                "stock_code": stock["code"],
                "stock_name": stock["name"],
                "industry": stock["industry"],
                "exchange": stock["code"].split(".")[-1],
                "current_price": round(random.uniform(10, 300), 2),
                "pe_ratio": round(random.uniform(5, 50), 2),
                "pb_ratio": round(random.uniform(0.5, 10), 2),
                "market_cap": round(random.uniform(50, 5000), 2),  # 亿元
                "roe": round(random.uniform(0.02, 0.30), 4),
                "debt_ratio": round(random.uniform(0.1, 0.8), 4),
                "revenue_growth": round(random.uniform(-10, 40), 2),
                "dividend_yield": round(random.uniform(0, 8), 2),
                "currency": "CNY"
            }
            stock_pool.append(stock_data)
        
        # Generate US stocks with random metrics
        for stock in us_stocks:
            stock_data = {
                "symbol": stock["symbol"],
                "company_name": stock["name"],
                "sector": stock["sector"],
                "exchange": "NASDAQ",
                "current_price": round(random.uniform(20, 500), 2),
                "pe_ratio": round(random.uniform(8, 80), 2),
                "pb_ratio": round(random.uniform(1, 20), 2),
                "market_cap": round(random.uniform(100, 3000), 2),  # 十亿美元
                "roe": round(random.uniform(0.05, 0.40), 4),
                "debt_ratio": round(random.uniform(0.0, 0.7), 4),
                "revenue_growth": round(random.uniform(-5, 50), 2),
                "dividend_yield": round(random.uniform(0, 5), 2),
                "currency": "USD"
            }
            stock_pool.append(stock_data)
        
        return stock_pool
    
    def _stock_matches_criteria(self, stock: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if a stock matches the screening criteria."""
        
        # P/E ratio filters
        if "pe_ratio_max" in criteria:
            if stock.get("pe_ratio", float('inf')) > criteria["pe_ratio_max"]:
                return False
        
        if "pe_ratio_min" in criteria:
            if stock.get("pe_ratio", 0) < criteria["pe_ratio_min"]:
                return False
        
        # P/B ratio filters
        if "pb_ratio_max" in criteria:
            if stock.get("pb_ratio", float('inf')) > criteria["pb_ratio_max"]:
                return False
        
        if "pb_ratio_min" in criteria:
            if stock.get("pb_ratio", 0) < criteria["pb_ratio_min"]:
                return False
        
        # Market cap filters
        if "market_cap_min" in criteria:
            if stock.get("market_cap", 0) < criteria["market_cap_min"]:
                return False
        
        if "market_cap_max" in criteria:
            if stock.get("market_cap", float('inf')) > criteria["market_cap_max"]:
                return False
        
        # ROE filter
        if "roe_min" in criteria:
            if stock.get("roe", 0) < criteria["roe_min"]:
                return False
        
        # Debt ratio filter
        if "debt_ratio_max" in criteria:
            if stock.get("debt_ratio", float('inf')) > criteria["debt_ratio_max"]:
                return False
        
        # Revenue growth filter
        if "revenue_growth_min" in criteria:
            if stock.get("revenue_growth", float('-inf')) < criteria["revenue_growth_min"]:
                return False
        
        # Dividend yield filter
        if "dividend_yield_min" in criteria:
            if stock.get("dividend_yield", 0) < criteria["dividend_yield_min"]:
                return False
        
        # Industry filter
        if "industry" in criteria:
            if stock.get("industry", "").lower() != criteria["industry"].lower():
                return False
        
        # Sector filter
        if "sector" in criteria:
            if stock.get("sector", "").lower() != criteria["sector"].lower():
                return False
        
        # Exchange filter
        if "exchange" in criteria:
            if stock.get("exchange", "").upper() != criteria["exchange"].upper():
                return False
        
        return True
    
    def _sort_results(self, stocks: List[Dict[str, Any]], sort_by: str = "pe_ratio") -> List[Dict[str, Any]]:
        """Sort screening results by specified criteria."""
        if not stocks:
            return stocks
        
        try:
            return sorted(stocks, key=lambda x: x.get(sort_by, float('inf')))
        except (TypeError, KeyError):
            return stocks
    
    def _add_ranking_scores(self, stocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add ranking scores to help users prioritize results."""
        for i, stock in enumerate(stocks):
            # Simple ranking score based on common value investing criteria
            score = 0
            
            # Lower P/E is better
            pe = stock.get("pe_ratio", 50)
            if pe < 15:
                score += 3
            elif pe < 25:
                score += 1
            
            # Higher ROE is better
            roe = stock.get("roe", 0)
            if roe > 0.15:
                score += 3
            elif roe > 0.10:
                score += 1
            
            # Lower debt is better
            debt = stock.get("debt_ratio", 1)
            if debt < 0.3:
                score += 2
            elif debt < 0.5:
                score += 1
            
            # Higher revenue growth is better
            growth = stock.get("revenue_growth", 0)
            if growth > 15:
                score += 2
            elif growth > 5:
                score += 1
            
            stock["ranking_score"] = score
            stock["rank"] = i + 1
        
        return stocks