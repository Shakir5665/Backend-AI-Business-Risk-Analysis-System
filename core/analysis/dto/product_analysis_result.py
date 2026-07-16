"""
Product Analysis Result

Represents the complete analysis
of a single product.

Project:
AI-Powered Business Risk Analysis
and Recommendation System
"""

from dataclasses import dataclass
from typing import Any

from core.scraper.dto.product import Product
from core.business_risk.aggregation.aggregation_result import AggregationResult


@dataclass(slots=True)
class ProductAnalysisResult:
    """
    Final result returned by the
    Product Analysis Engine.
    """

    product: Product

    analysis: AggregationResult

    business_risk: dict[str, Any] | None = None

    assessment_reliability: dict[str, Any] | None = None

    recommendations: list[str] | None = None