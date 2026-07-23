from dataclasses import dataclass

from core.business_risk.aggregation.aggregation_result import AggregationResult
from core.business_risk.models.aspect_risk import AspectRisk
from core.business_risk.models.risk_level import RiskLevel


@dataclass(frozen=True)
class RuleContext:
    """
    Shared context for all business rules.
    """

    aggregation: AggregationResult

    quality: AspectRisk
    delivery: AspectRisk
    trust: AspectRisk

    baseline_score: float
    baseline_level: RiskLevel