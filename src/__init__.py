"""
Multi-Agent Financial Analysis Framework

A state-driven multi-agent system for financial analysis using LangGraph.
"""

__version__ = "0.1.0"
__author__ = "MiningIrving"
__description__ = "Multi-Agent Financial Analysis Framework"

from .core import GraphState
from .core.graph import FinancialAnalysisGraph

__all__ = ["GraphState", "FinancialAnalysisGraph"]