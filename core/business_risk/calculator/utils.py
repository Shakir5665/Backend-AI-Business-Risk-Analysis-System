from __future__ import annotations

from core.business_risk.models.aspect_risk import AspectRisk
from core.business_risk.models.risk_level import RiskLevel


# ----------------------------------------------------------------------
# Risk Level Ordering
# ----------------------------------------------------------------------

RISK_LEVEL_ORDER = {
    RiskLevel.VERY_LOW: 0,
    RiskLevel.LOW: 1,
    RiskLevel.MEDIUM: 2,
    RiskLevel.HIGH: 3,
    RiskLevel.CRITICAL: 4,
}


# ----------------------------------------------------------------------
# Comparisons
# ----------------------------------------------------------------------

def is_at_least(level: RiskLevel, minimum: RiskLevel) -> bool:
    """
    Returns True if 'level' is greater than or equal to 'minimum'.
    """
    return RISK_LEVEL_ORDER[level] >= RISK_LEVEL_ORDER[minimum]


def is_below(level: RiskLevel, maximum: RiskLevel) -> bool:
    """
    Returns True if 'level' is lower than 'maximum'.
    """
    return RISK_LEVEL_ORDER[level] < RISK_LEVEL_ORDER[maximum]


# ----------------------------------------------------------------------
# Counting
# ----------------------------------------------------------------------

def count_at_least(levels: list[RiskLevel], minimum: RiskLevel) -> int:
    """
    Counts how many risk levels are greater than or equal to 'minimum'.
    """
    return sum(is_at_least(level, minimum) for level in levels)


# ----------------------------------------------------------------------
# Baseline
# ----------------------------------------------------------------------

def calculate_baseline_score(
    quality: AspectRisk,
    delivery: AspectRisk,
    trust: AspectRisk,
) -> float:
    """
    Returns the highest aspect risk score.
    """
    return max(
        quality.score,
        delivery.score,
        trust.score,
    )


def determine_baseline_level(
    quality: AspectRisk,
    delivery: AspectRisk,
    trust: AspectRisk,
) -> RiskLevel:
    """
    Returns the level of the aspect with the highest score.
    """
    highest = max(
        (quality, delivery, trust),
        key=lambda aspect: aspect.score,
    )

    return highest.level