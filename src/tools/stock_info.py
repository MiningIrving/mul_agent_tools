"""
Stock information query tool implementation.

This tool provides comprehensive stock information including
price, financial metrics, and performance data.
"""

from typing import Dict, Any
import random
from .base import BaseTool


class StockInfoTool(BaseTool):
    """
    Tool for querying individual stock information.
    
    This tool can retrieve current stock prices, financial metrics,
    and performance data for individual stocks.
    """
    
    def __init__(self, name: str):
        """Initialize the stock info tool."""
        super().__init__(name)
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute stock information query.
        
        Args:
            **kwargs: Query parameters including stock_code, stock_name, or symbol
            
        Returns:
            Stock information data
            
        Raises:
            ValueError: If required parameters are missing
        """
        # Validate inputs
        if not self.validate_inputs(kwargs):
            raise ValueError("Invalid inputs for stock info query")
        
        # Extract stock identifier
        stock_identifier = self._extract_stock_identifier(kwargs)
        
        if not stock_identifier:
            raise ValueError("Stock identifier (code, name, or symbol) is required")
        
        try:
            # Simulate stock data retrieval
            # In a real implementation, this would call actual stock APIs
            stock_data = self._fetch_stock_data(stock_identifier)
            
            self.log_execution(kwargs, stock_data)
            
            return stock_data
            
        except Exception as e:
            self.logger.error(f"Failed to fetch stock data: {str(e)}")
            raise
    
    def get_schema(self) -> Dict[str, Any]:
        """Get input schema for stock info query."""
        return {
            "type": "object",
            "properties": {
                "stock_code": {
                    "type": "string",
                    "description": "Stock code (e.g., 000001.SZ, AAPL)"
                },
                "stock_name": {
                    "type": "string", 
                    "description": "Company name (e.g., 苹果公司, Apple Inc.)"
                },
                "symbol": {
                    "type": "string",
                    "description": "Stock symbol (e.g., AAPL, TSLA)"
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to retrieve (optional)"
                }
            },
            "anyOf": [
                {"required": ["stock_code"]},
                {"required": ["stock_name"]},
                {"required": ["symbol"]}
            ]
        }
    
    def get_description(self) -> str:
        """Get tool description."""
        return "查询个股详细信息，包括股价、财务指标、市场表现等数据"
    
    def _extract_stock_identifier(self, kwargs: Dict[str, Any]) -> str:
        """Extract stock identifier from inputs."""
        for key in ["stock_code", "symbol", "stock_name"]:
            if key in kwargs and kwargs[key]:
                return kwargs[key]
        return ""
    
    def _fetch_stock_data(self, identifier: str) -> Dict[str, Any]:
        """
        Simulate fetching stock data from external API.
        
        In a real implementation, this would integrate with:
        - Yahoo Finance API
        - Alpha Vantage
        - Tushare (for Chinese stocks)
        - Wind API
        - etc.
        """
        # Simulate different types of stocks
        if any(cn_code in identifier.upper() for cn_code in ["SZ", "SH", "比亚迪", "茅台"]):
            return self._generate_chinese_stock_data(identifier)
        else:
            return self._generate_us_stock_data(identifier)
    
    def _generate_chinese_stock_data(self, identifier: str) -> Dict[str, Any]:
        """Generate simulated Chinese stock data."""
        # Map known Chinese stocks
        stock_mapping = {
            "比亚迪": "002594.SZ",
            "贵州茅台": "600519.SH", 
            "腾讯": "00700.HK",
            "阿里巴巴": "09988.HK"
        }
        
        stock_code = stock_mapping.get(identifier, identifier)
        
        # Simulate realistic Chinese stock data
        base_price = random.uniform(50, 500)
        
        return {
            "stock_code": stock_code,
            "stock_name": identifier if identifier in stock_mapping else "示例公司",
            "current_price": round(base_price, 2),
            "price_change": round(random.uniform(-5, 5), 2),
            "price_change_percent": round(random.uniform(-10, 10), 2),
            "volume": random.randint(1000000, 50000000),
            "market_cap": round(base_price * random.uniform(100, 1000), 2),  # 亿元
            "pe_ratio": round(random.uniform(8, 45), 2),
            "pb_ratio": round(random.uniform(0.8, 8), 2),
            "roe": round(random.uniform(0.05, 0.25), 4),
            "debt_ratio": round(random.uniform(0.2, 0.7), 4),
            "revenue_growth": round(random.uniform(-10, 30), 2),
            "net_profit_growth": round(random.uniform(-15, 40), 2),
            "dividend_yield": round(random.uniform(0, 5), 2),
            "beta": round(random.uniform(0.5, 2.0), 2),
            "52_week_high": round(base_price * random.uniform(1.1, 1.5), 2),
            "52_week_low": round(base_price * random.uniform(0.6, 0.9), 2),
            "industry": random.choice(["汽车", "白酒", "科技", "金融", "医药", "房地产"]),
            "exchange": stock_code.split(".")[-1] if "." in stock_code else "SZ",
            "currency": "CNY",
            "last_updated": "2024-01-15 15:00:00"
        }
    
    def _generate_us_stock_data(self, identifier: str) -> Dict[str, Any]:
        """Generate simulated US stock data."""
        # Map known US stocks
        stock_mapping = {
            "AAPL": "Apple Inc.",
            "TSLA": "Tesla Inc.",
            "MSFT": "Microsoft Corporation",
            "GOOGL": "Alphabet Inc.",
            "AMZN": "Amazon.com Inc."
        }
        
        symbol = identifier.upper()
        company_name = stock_mapping.get(symbol, f"{symbol} Corporation")
        
        # Simulate realistic US stock data
        base_price = random.uniform(20, 400)
        
        return {
            "symbol": symbol,
            "company_name": company_name,
            "current_price": round(base_price, 2),
            "price_change": round(random.uniform(-10, 10), 2),
            "price_change_percent": round(random.uniform(-8, 8), 2),
            "volume": random.randint(5000000, 100000000),
            "market_cap": round(base_price * random.uniform(500, 3000), 2),  # 百万美元
            "pe_ratio": round(random.uniform(12, 60), 2),
            "pb_ratio": round(random.uniform(1, 15), 2),
            "roe": round(random.uniform(0.08, 0.35), 4),
            "debt_ratio": round(random.uniform(0.1, 0.6), 4),
            "revenue_growth": round(random.uniform(-5, 25), 2),
            "net_profit_growth": round(random.uniform(-20, 50), 2),
            "dividend_yield": round(random.uniform(0, 4), 2),
            "beta": round(random.uniform(0.7, 2.5), 2),
            "52_week_high": round(base_price * random.uniform(1.2, 1.8), 2),
            "52_week_low": round(base_price * random.uniform(0.5, 0.8), 2),
            "sector": random.choice(["Technology", "Consumer Discretionary", "Healthcare", "Financial", "Energy"]),
            "exchange": "NASDAQ",
            "currency": "USD",
            "last_updated": "2024-01-15 16:00:00 EST"
        }
    
    def _normalize_stock_identifier(self, identifier: str) -> str:
        """
        Normalize stock identifier for consistent processing.
        
        Args:
            identifier: Raw stock identifier
            
        Returns:
            Normalized identifier
        """
        # Remove extra spaces and convert to uppercase for symbols
        identifier = identifier.strip()
        
        # If it looks like a US symbol, convert to uppercase
        if len(identifier) <= 5 and identifier.isalpha():
            return identifier.upper()
        
        # If it looks like a Chinese stock code, keep as-is
        if "." in identifier or any(char.isdigit() for char in identifier):
            return identifier.upper()
        
        # For company names, keep original case
        return identifier