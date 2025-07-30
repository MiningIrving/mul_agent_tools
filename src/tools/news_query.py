"""
News query tool implementation.

This tool provides financial news and market information.
"""

from typing import Dict, Any, List
import random
from datetime import datetime, timedelta
from .base import BaseTool


class NewsQueryTool(BaseTool):
    """
    Tool for querying financial news and market information.
    
    This tool can search for news related to specific companies,
    sectors, or general market conditions.
    """
    
    def __init__(self, name: str):
        """Initialize the news query tool."""
        super().__init__(name)
    
    def execute(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Execute news query.
        
        Args:
            **kwargs: Query parameters
            
        Returns:
            List of news articles
            
        Raises:
            ValueError: If required parameters are missing
        """
        # Validate inputs
        if not self.validate_inputs(kwargs):
            raise ValueError("Invalid inputs for news query")
        
        # Extract query parameters
        query_params = self._extract_query_params(kwargs)
        
        try:
            # Fetch news data
            news_results = self._fetch_news(query_params)
            
            self.log_execution(kwargs, news_results)
            
            return news_results
            
        except Exception as e:
            self.logger.error(f"Failed to fetch news: {str(e)}")
            raise
    
    def get_schema(self) -> Dict[str, Any]:
        """Get input schema for news query."""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for news"
                },
                "company": {
                    "type": "string",
                    "description": "Company name or stock code"
                },
                "industry": {
                    "type": "string",
                    "description": "Industry sector"
                },
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Keywords to search for"
                },
                "date_from": {
                    "type": "string",
                    "description": "Start date (YYYY-MM-DD)"
                },
                "date_to": {
                    "type": "string", 
                    "description": "End date (YYYY-MM-DD)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of news items",
                    "default": 10
                },
                "language": {
                    "type": "string",
                    "enum": ["zh", "en"],
                    "description": "Language preference",
                    "default": "zh"
                }
            },
            "anyOf": [
                {"required": ["query"]},
                {"required": ["company"]},
                {"required": ["keywords"]}
            ]
        }
    
    def get_description(self) -> str:
        """Get tool description."""
        return "查询金融新闻和市场资讯，支持公司、行业、关键词等多种搜索方式"
    
    def _extract_query_params(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize query parameters."""
        params = {}
        
        # Primary search terms
        if "query" in kwargs:
            params["query"] = kwargs["query"]
        elif "company" in kwargs:
            params["query"] = kwargs["company"]
        elif "keywords" in kwargs:
            params["query"] = " ".join(kwargs["keywords"])
        
        # Additional filters
        for key in ["company", "industry", "keywords"]:
            if key in kwargs:
                params[key] = kwargs[key]
        
        # Date range
        if "date_from" in kwargs:
            params["date_from"] = kwargs["date_from"]
        if "date_to" in kwargs:
            params["date_to"] = kwargs["date_to"]
        
        # Limit and language
        params["limit"] = kwargs.get("limit", 10)
        params["language"] = kwargs.get("language", "zh")
        
        return params
    
    def _fetch_news(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch news based on query parameters.
        
        In a real implementation, this would integrate with:
        - Financial news APIs (Alpha Vantage, NewsAPI)
        - Chinese financial news sources (新浪财经, 东方财富)
        - RSS feeds from financial publications
        - Web scraping from news websites
        """
        # Simulate news fetching
        return self._generate_simulated_news(params)
    
    def _generate_simulated_news(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate simulated news data for demonstration."""
        query = params.get("query", "")
        language = params.get("language", "zh")
        limit = params.get("limit", 10)
        
        # Determine if this is about a specific company
        company_keywords = {
            "比亚迪": "BYD",
            "特斯拉": "Tesla", 
            "苹果": "Apple",
            "腾讯": "Tencent",
            "阿里巴巴": "Alibaba",
            "茅台": "Moutai"
        }
        
        company = None
        for cn_name, en_name in company_keywords.items():
            if cn_name in query or en_name.lower() in query.lower():
                company = cn_name
                break
        
        # Generate news based on context
        if company:
            news_articles = self._generate_company_news(company, language, limit)
        else:
            news_articles = self._generate_general_market_news(language, limit)
        
        return news_articles[:limit]
    
    def _generate_company_news(self, company: str, language: str, limit: int) -> List[Dict[str, Any]]:
        """Generate company-specific news."""
        news_templates = {
            "比亚迪": [
                "比亚迪Q4交付量创新高，新能源汽车销量同比增长85%",
                "比亚迪海外市场拓展提速，获得欧洲大型订单",
                "比亚迪发布最新财报，营收和净利润双双超预期",
                "比亚迪推出新一代刀片电池技术，安全性能大幅提升",
                "机构看好比亚迪长期发展，上调目标价至280元"
            ],
            "特斯拉": [
                "特斯拉上海工厂产能再度提升，月产量突破8万辆",
                "马斯克透露特斯拉将在中国推出更多车型",
                "特斯拉FSD功能在华测试进展顺利，有望年内落地",
                "特斯拉降价策略效果显著，订单量大幅增长",
                "分析师上调特斯拉评级，认为估值仍有上升空间"
            ],
            "苹果": [
                "苹果iPhone 15系列销量超预期，Pro版本最受欢迎",
                "苹果Vision Pro头显设备即将量产，预计明年发布",
                "苹果服务业务收入创新高，成为增长新引擎",
                "苹果计划在印度扩大生产规模，减少对中国依赖",
                "巴菲特增持苹果股票，称其为最佳投资之一"
            ]
        }
        
        base_templates = news_templates.get(company, [
            f"{company}发布最新业绩报告，业绩表现超出市场预期",
            f"{company}宣布重大战略调整，加大研发投入",
            f"机构调研密集，{company}受到市场广泛关注",
            f"{company}高管接受采访，详解未来发展规划"
        ])
        
        news_articles = []
        for i in range(min(limit, len(base_templates) * 2)):
            template = base_templates[i % len(base_templates)]
            
            # Generate article details
            publish_time = datetime.now() - timedelta(days=random.randint(0, 30))
            
            article = {
                "title": template,
                "summary": f"这是关于{company}的重要新闻摘要。{template[:50]}...",
                "content": f"根据最新消息，{template} 这一消息引起了市场的广泛关注，分析师认为这将对公司未来发展产生积极影响。",
                "source": random.choice(["新浪财经", "东方财富", "财联社", "证券时报", "第一财经"]),
                "publish_time": publish_time.strftime("%Y-%m-%d %H:%M:%S"),
                "url": f"https://finance.sina.com.cn/stock/s/{random.randint(100000, 999999)}.shtml",
                "sentiment": random.choice(["positive", "neutral", "negative"]),
                "relevance_score": round(random.uniform(0.7, 1.0), 2),
                "tags": [company, "财报", "业绩", "股价"],
                "read_count": random.randint(1000, 50000)
            }
            
            news_articles.append(article)
        
        return news_articles
    
    def _generate_general_market_news(self, language: str, limit: int) -> List[Dict[str, Any]]:
        """Generate general market news."""
        market_templates = [
            "A股三大指数集体收涨，科技股表现强劲",
            "央行宣布降准，释放流动性支持实体经济",
            "北向资金连续净流入，外资看好A股长期价值",
            "新能源汽车板块大涨，政策利好持续释放",
            "房地产板块反弹，多地政策边际放松",
            "医药生物板块走强，创新药获得重大突破",
            "消费板块分化明显，白酒股领涨",
            "银行股集体上涨，净息差改善预期增强",
            "芯片概念股活跃，国产化替代加速推进",
            "新基建概念受关注，5G建设持续推进"
        ]
        
        news_articles = []
        for i in range(limit):
            template = market_templates[i % len(market_templates)]
            publish_time = datetime.now() - timedelta(days=random.randint(0, 7))
            
            article = {
                "title": template,
                "summary": f"市场动态摘要：{template[:30]}...",
                "content": f"市场分析显示，{template} 投资者对后市走势保持谨慎乐观态度，建议关注相关投资机会。",
                "source": random.choice(["证券日报", "中国证券报", "上海证券报", "财经网", "金融界"]),
                "publish_time": publish_time.strftime("%Y-%m-%d %H:%M:%S"),
                "url": f"https://finance.163.com/stock/{random.randint(100000, 999999)}.html",
                "sentiment": random.choice(["positive", "neutral"]),
                "relevance_score": round(random.uniform(0.6, 0.9), 2),
                "tags": ["市场", "股市", "投资", "分析"],
                "read_count": random.randint(5000, 100000)
            }
            
            news_articles.append(article)
        
        return news_articles
    
    def _filter_by_date_range(self, articles: List[Dict[str, Any]], date_from: str, date_to: str) -> List[Dict[str, Any]]:
        """Filter articles by date range."""
        if not date_from and not date_to:
            return articles
        
        filtered_articles = []
        
        for article in articles:
            try:
                article_date = datetime.strptime(article["publish_time"], "%Y-%m-%d %H:%M:%S").date()
                
                if date_from:
                    from_date = datetime.strptime(date_from, "%Y-%m-%d").date()
                    if article_date < from_date:
                        continue
                
                if date_to:
                    to_date = datetime.strptime(date_to, "%Y-%m-%d").date()
                    if article_date > to_date:
                        continue
                
                filtered_articles.append(article)
                
            except (ValueError, KeyError):
                # If date parsing fails, include the article
                filtered_articles.append(article)
        
        return filtered_articles
    
    def _score_relevance(self, article: Dict[str, Any], query: str) -> float:
        """Score article relevance to query."""
        query_words = set(query.lower().split())
        title_words = set(article["title"].lower().split())
        
        # Simple relevance scoring based on word overlap
        overlap = len(query_words.intersection(title_words))
        max_words = max(len(query_words), len(title_words), 1)
        
        return overlap / max_words