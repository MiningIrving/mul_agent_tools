"""Agent implementations for the financial analysis framework."""

from .base import BaseAgent, get_agent
from .stock_selection import StockSelectionAgent
from .news import NewsAgent
from .knowledge import KnowledgeAgent
from .diagnosis import DiagnosisAgent
from .prediction import PredictionAgent
from .recommendation import RecommendationAgent

__all__ = [
    "BaseAgent",
    "get_agent",
    "StockSelectionAgent",
    "NewsAgent", 
    "KnowledgeAgent",
    "DiagnosisAgent",
    "PredictionAgent",
    "RecommendationAgent"
]