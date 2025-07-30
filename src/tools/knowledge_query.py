"""
Knowledge query tool implementation.

This tool provides financial knowledge and educational content.
"""

from typing import Dict, Any
import random
from .base import BaseTool


class KnowledgeQueryTool(BaseTool):
    """
    Tool for querying financial knowledge and educational content.
    
    This tool can provide explanations of financial concepts,
    investment strategies, and market analysis methods.
    """
    
    def __init__(self, name: str):
        """Initialize the knowledge query tool."""
        super().__init__(name)
        self.knowledge_base = self._initialize_knowledge_base()
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute knowledge query.
        
        Args:
            **kwargs: Query parameters
            
        Returns:
            Knowledge content and explanations
            
        Raises:
            ValueError: If required parameters are missing
        """
        # Validate inputs
        if not self.validate_inputs(kwargs):
            raise ValueError("Invalid inputs for knowledge query")
        
        # Extract query
        query = kwargs.get("query", "").strip()
        if not query:
            raise ValueError("Query parameter is required")
        
        try:
            # Search knowledge base
            knowledge_result = self._search_knowledge(query)
            
            self.log_execution(kwargs, knowledge_result)
            
            return knowledge_result
            
        except Exception as e:
            self.logger.error(f"Failed to query knowledge: {str(e)}")
            raise
    
    def get_schema(self) -> Dict[str, Any]:
        """Get input schema for knowledge query."""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Financial knowledge query or concept to explain"
                },
                "category": {
                    "type": "string",
                    "enum": ["基础概念", "投资策略", "技术分析", "基本面分析", "风险管理", "市场知识"],
                    "description": "Knowledge category filter"
                },
                "detail_level": {
                    "type": "string",
                    "enum": ["基础", "中级", "高级"],
                    "description": "Detail level of explanation",
                    "default": "中级"
                }
            },
            "required": ["query"]
        }
    
    def get_description(self) -> str:
        """Get tool description."""
        return "查询金融知识和投资概念，提供专业解释、实例分析和学习建议"
    
    def _initialize_knowledge_base(self) -> Dict[str, Dict[str, Any]]:
        """Initialize the financial knowledge base."""
        return {
            # 基础概念
            "市盈率": {
                "category": "基础概念",
                "definition": "市盈率(P/E)是指股票价格与每股收益的比率，反映投资者愿意为每单位收益支付的价格。",
                "formula": "市盈率 = 股价 / 每股收益(EPS)",
                "interpretation": {
                    "低市盈率": "通常表示股票被低估或公司增长缓慢",
                    "高市盈率": "可能表示市场对公司增长预期较高或股票被高估"
                },
                "typical_ranges": {
                    "价值股": "8-15倍",
                    "成长股": "20-40倍",
                    "科技股": "30-80倍"
                },
                "examples": [
                    "银行股市盈率通常在5-10倍之间",
                    "科技成长股市盈率可能达到50倍以上"
                ],
                "related_concepts": ["市净率", "PEG", "每股收益", "估值"]
            },
            
            "市净率": {
                "category": "基础概念", 
                "definition": "市净率(P/B)是指股票市价与每股净资产的比率，反映股票相对于公司净资产的估值水平。",
                "formula": "市净率 = 股价 / 每股净资产",
                "interpretation": {
                    "P/B < 1": "股价低于净资产，可能被低估",
                    "P/B > 3": "股价较净资产有较大溢价"
                },
                "applications": [
                    "适用于资产密集型行业分析",
                    "银行、地产等重资产行业常用指标"
                ],
                "limitations": [
                    "对轻资产公司意义有限",
                    "无形资产价值难以体现"
                ]
            },
            
            "ROE": {
                "category": "基础概念",
                "definition": "净资产收益率(ROE)衡量公司运用股东权益创造利润的能力，是重要的盈利能力指标。",
                "formula": "ROE = 净利润 / 股东权益 × 100%",
                "significance": "ROE是巴菲特最重视的财务指标之一",
                "benchmark": {
                    "优秀": "> 20%",
                    "良好": "15%-20%", 
                    "一般": "10%-15%",
                    "较差": "< 10%"
                },
                "dupont_analysis": {
                    "公式": "ROE = 净利率 × 资产周转率 × 权益乘数",
                    "含义": "从盈利能力、营运能力、财务杠杆三个维度分析"
                }
            },
            
            # 投资策略
            "价值投资": {
                "category": "投资策略",
                "definition": "价值投资是寻找被市场低估的优质公司，以低于内在价值的价格买入并长期持有的投资策略。",
                "core_principles": [
                    "买入被低估的优质公司",
                    "关注公司内在价值而非短期股价波动",
                    "长期持有，让复利发挥作用",
                    "安全边际：以足够低的价格买入"
                ],
                "selection_criteria": [
                    "稳定且可预测的盈利能力",
                    "强大的护城河（竞争优势）",
                    "优秀的管理团队",
                    "合理的财务杠杆",
                    "良好的现金流"
                ],
                "famous_practitioners": [
                    "沃伦·巴菲特 - 伯克希尔哈撒韦",
                    "本杰明·格雷厄姆 - 价值投资之父",
                    "彼得·林奇 - 富达基金"
                ],
                "typical_metrics": [
                    "低市盈率(P/E)",
                    "低市净率(P/B)", 
                    "高股息收益率",
                    "高净资产收益率(ROE)"
                ]
            },
            
            "成长投资": {
                "category": "投资策略",
                "definition": "成长投资专注于投资收入和利润增长速度超过市场平均水平的公司。",
                "key_characteristics": [
                    "高收入增长率",
                    "高利润增长率", 
                    "强劲的市场需求",
                    "创新能力和技术优势"
                ],
                "evaluation_metrics": [
                    "PEG比率（市盈率相对盈利增长比率）",
                    "收入增长率",
                    "净利润增长率",
                    "市场份额增长"
                ],
                "risks": [
                    "估值风险 - 高估值容易回调",
                    "增长放缓风险",
                    "市场竞争加剧",
                    "技术迭代风险"
                ]
            },
            
            # 技术分析
            "技术分析": {
                "category": "技术分析",
                "definition": "技术分析是通过研究股价走势图表、交易量等市场数据来预测未来价格变动的方法。",
                "basic_assumptions": [
                    "市场行为包含一切信息",
                    "价格以趋势方式演变",
                    "历史会重演"
                ],
                "main_tools": [
                    "趋势线和支撑阻力位",
                    "移动平均线",
                    "技术指标(RSI、MACD、KDJ)",
                    "K线图形态分析"
                ],
                "common_patterns": [
                    "头肩顶/底",
                    "双顶/底",
                    "三角形整理",
                    "旗形和楔形"
                ]
            },
            
            # 风险管理
            "风险管理": {
                "category": "风险管理",
                "definition": "风险管理是识别、评估和控制投资风险的过程，目标是在可接受的风险水平下最大化收益。",
                "main_types": [
                    "市场风险 - 整体市场下跌",
                    "信用风险 - 发行人违约",
                    "流动性风险 - 无法及时变现",
                    "操作风险 - 人为错误或系统故障"
                ],
                "management_techniques": [
                    "分散投资 - 不要把鸡蛋放在一个篮子里",
                    "止损设置 - 控制单笔损失",
                    "仓位管理 - 合理配置资金",
                    "对冲策略 - 使用衍生品降低风险"
                ],
                "position_sizing": {
                    "原则": "单个股票仓位不超过总资产的10%",
                    "方法": "根据风险承受能力确定仓位大小"
                }
            },
            
            # 市场知识
            "牛市": {
                "category": "市场知识",
                "definition": "牛市是指股票市场长期上涨的趋势，投资者情绪乐观，交易活跃。",
                "characteristics": [
                    "股价持续上涨",
                    "交易量放大",
                    "投资者信心增强",
                    "新股发行活跃"
                ],
                "typical_duration": "通常持续1-3年",
                "driving_factors": [
                    "经济增长强劲",
                    "企业盈利改善",
                    "货币政策宽松",
                    "投资者风险偏好提升"
                ]
            },
            
            "熊市": {
                "category": "市场知识", 
                "definition": "熊市是指股票市场长期下跌的趋势，投资者情绪悲观，市场萎靡。",
                "characteristics": [
                    "股价持续下跌",
                    "交易量萎缩",
                    "投资者恐慌情绪",
                    "估值回归合理区间"
                ],
                "survival_strategies": [
                    "保持冷静，避免恐慌性抛售",
                    "寻找优质公司的投资机会",
                    "分批建仓，平均成本",
                    "保持充足现金流"
                ]
            }
        }
    
    def _search_knowledge(self, query: str) -> Dict[str, Any]:
        """Search the knowledge base for relevant information."""
        query_lower = query.lower()
        
        # Direct match
        for concept, content in self.knowledge_base.items():
            if concept.lower() in query_lower or query_lower in concept.lower():
                return self._format_knowledge_response(concept, content, query)
        
        # Keyword matching
        matches = []
        for concept, content in self.knowledge_base.items():
            # Check if query contains related concepts
            if hasattr(content, 'get') and content.get('related_concepts'):
                for related in content['related_concepts']:
                    if related.lower() in query_lower:
                        matches.append((concept, content))
                        break
        
        if matches:
            concept, content = matches[0]  # Return first match
            return self._format_knowledge_response(concept, content, query)
        
        # Category-based search
        categories = ["基础概念", "投资策略", "技术分析", "基本面分析", "风险管理", "市场知识"]
        for category in categories:
            if category in query:
                return self._format_category_response(category, query)
        
        # Fuzzy matching for common financial terms
        return self._generate_general_response(query)
    
    def _format_knowledge_response(self, concept: str, content: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Format a specific knowledge response."""
        response = {
            "concept": concept,
            "category": content.get("category", "金融知识"),
            "query": query,
            "definition": content.get("definition", ""),
            "main_content": content,
            "practical_examples": self._get_practical_examples(concept, content),
            "related_concepts": content.get("related_concepts", []),
            "learning_suggestions": self._generate_learning_suggestions(concept),
            "additional_resources": self._get_additional_resources(content.get("category", ""))
        }
        
        return response
    
    def _format_category_response(self, category: str, query: str) -> Dict[str, Any]:
        """Format a category-based response."""
        category_concepts = {k: v for k, v in self.knowledge_base.items() 
                           if v.get("category") == category}
        
        response = {
            "category": category,
            "query": query,
            "overview": self._get_category_overview(category),
            "key_concepts": list(category_concepts.keys()),
            "concept_details": category_concepts,
            "learning_path": self._get_learning_path(category),
            "recommended_order": self._get_recommended_learning_order(category)
        }
        
        return response
    
    def _generate_general_response(self, query: str) -> Dict[str, Any]:
        """Generate a general response for unknown queries."""
        response = {
            "query": query,
            "status": "partial_match",
            "message": "未找到完全匹配的知识内容，以下是相关建议：",
            "suggestions": [
                "尝试使用更具体的金融术语",
                "查询基础概念如：市盈率、ROE、市净率",
                "了解投资策略如：价值投资、成长投资",
                "学习技术分析方法和工具"
            ],
            "popular_topics": list(self.knowledge_base.keys())[:6],
            "categories": ["基础概念", "投资策略", "技术分析", "风险管理", "市场知识"],
            "sample_queries": [
                "什么是市盈率？",
                "价值投资的原理是什么？",
                "如何进行风险管理？",
                "牛市和熊市的特征是什么？"
            ]
        }
        
        return response
    
    def _get_practical_examples(self, concept: str, content: Dict[str, Any]) -> list:
        """Get practical examples for a concept."""
        if "examples" in content:
            return content["examples"]
        
        # Generate examples based on concept type
        examples_map = {
            "市盈率": [
                "贵州茅台市盈率30倍，说明投资者愿意为其每元收益支付30元",
                "银行股市盈率通常在5-8倍，反映其稳定但增长有限的特征"
            ],
            "价值投资": [
                "巴菲特投资可口可乐，看中其强大的品牌护城河",
                "在2008年金融危机时买入优质银行股，获得丰厚回报"
            ],
            "风险管理": [
                "设置10%的止损点，避免单笔投资损失过大",
                "将资金分散投资于不同行业，降低集中风险"
            ]
        }
        
        return examples_map.get(concept, [f"关于{concept}的实际应用案例"])
    
    def _generate_learning_suggestions(self, concept: str) -> list:
        """Generate learning suggestions for a concept."""
        general_suggestions = [
            f"深入学习{concept}的计算方法和应用场景",
            f"比较{concept}在不同行业中的表现差异",
            f"关注{concept}的历史变化趋势",
            "结合实际案例加深理解"
        ]
        
        return general_suggestions
    
    def _get_additional_resources(self, category: str) -> list:
        """Get additional learning resources by category."""
        resources_map = {
            "基础概念": [
                "《聪明的投资者》- 本杰明·格雷厄姆",
                "《证券分析》- 格雷厄姆&多德",
                "财务报表分析教程"
            ],
            "投资策略": [
                "《巴菲特致股东的信》",
                "《彼得·林奇的成功投资》",
                "《投资最重要的事》- 霍华德·马克斯"
            ],
            "技术分析": [
                "《日本蜡烛图技术》",
                "《技术分析实战》",
                "TradingView技术分析工具"
            ],
            "风险管理": [
                "《风险管理与金融机构》",
                "《黑天鹅》- 纳西姆·塔勒布",
                "投资组合理论学习"
            ]
        }
        
        return resources_map.get(category, ["相关金融教育资源"])
    
    def _get_category_overview(self, category: str) -> str:
        """Get overview description for a category."""
        overviews = {
            "基础概念": "金融基础概念是投资分析的基石，包括各种财务指标和市场术语。",
            "投资策略": "投资策略是指导投资决策的系统性方法，不同策略适用于不同的市场环境。",
            "技术分析": "技术分析通过图表和指标分析价格走势，帮助判断买卖时机。",
            "风险管理": "风险管理是投资成功的关键，通过识别和控制风险来保护投资资本。",
            "市场知识": "市场知识涵盖市场周期、市场情绪等影响投资的宏观因素。"
        }
        
        return overviews.get(category, "重要的金融知识领域")
    
    def _get_learning_path(self, category: str) -> list:
        """Get recommended learning path for a category."""
        paths = {
            "基础概念": [
                "1. 学习基本财务指标（市盈率、市净率、ROE）",
                "2. 理解财务报表三张表",
                "3. 掌握估值方法",
                "4. 了解宏观经济指标"
            ],
            "投资策略": [
                "1. 了解不同投资流派的特点",
                "2. 学习价值投资的核心原理",
                "3. 掌握成长投资的判断标准",
                "4. 制定个人投资策略"
            ],
            "风险管理": [
                "1. 识别各类投资风险",
                "2. 学习分散投资原理",
                "3. 掌握仓位管理技巧",
                "4. 建立止损机制"
            ]
        }
        
        return paths.get(category, ["系统性学习该领域知识"])
    
    def _get_recommended_learning_order(self, category: str) -> list:
        """Get recommended learning order for concepts in a category."""
        orders = {
            "基础概念": ["市盈率", "市净率", "ROE"],
            "投资策略": ["价值投资", "成长投资"],
            "市场知识": ["牛市", "熊市"]
        }
        
        return orders.get(category, [])