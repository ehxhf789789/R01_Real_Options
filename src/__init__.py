"""
BIM Real Options Valuation Model

A Python-based valuation framework for BIM design service bidding decisions
using Real Options Analysis (ROA).
"""

from .valuation_engine import ValuationEngine
from .tier_system import Tier0Input, Tier1Derivation, Tier2Sampler

__version__ = "1.0.1"
__author__ = "Hanbin Lee"
__all__ = [
    "ValuationEngine",
    "Tier0Input",
    "Tier1Derivation",
    "Tier2Sampler",
]
