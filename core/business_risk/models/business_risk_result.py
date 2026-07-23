from dataclasses import dataclass, field

from .aspect_risk import AspectRisk
from .risk_level import RiskLevel


@dataclass
class BusinessRiskResult:
    """
    Final output of the Business Risk Engine.
    """

    quality: AspectRisk
    delivery: AspectRisk
    trust: AspectRisk

    business_risk_index: float
    business_risk_level: RiskLevel

    recommendations: list[str] = field(default_factory=list)