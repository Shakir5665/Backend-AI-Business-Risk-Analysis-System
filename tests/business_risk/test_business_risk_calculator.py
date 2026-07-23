import pytest
from core.business_risk.aggregation.aggregation_result import AggregationResult
from core.business_risk.calculator.business_risk_calculator import BusinessRiskCalculator
from core.business_risk.models.aspect_risk import AspectRisk
from core.business_risk.models.risk_level import RiskLevel


calculator = BusinessRiskCalculator()

def aggregation() -> AggregationResult:
    """
    Creates an empty aggregation result for testing.
    """
    return AggregationResult()


def aspect(score: float, level: RiskLevel, name: str) -> AspectRisk:
    return AspectRisk(
        aspect=name,
        score=score,
        level=level,
    )

def test_all_very_low():

    result = calculator.calculate(
        aggregation=aggregation(),
        quality=aspect(10, RiskLevel.VERY_LOW, "quality"),
        delivery=aspect(12, RiskLevel.VERY_LOW, "delivery"),
        trust=aspect(15, RiskLevel.VERY_LOW, "trust"),
    )

    assert result.business_risk_level == RiskLevel.VERY_LOW


def test_all_low():

    result = calculator.calculate(
        aggregation=aggregation(),
        quality=aspect(25, RiskLevel.LOW, "quality"),
        delivery=aspect(22, RiskLevel.LOW, "delivery"),
        trust=aspect(18, RiskLevel.LOW, "trust"),
    )

    assert result.business_risk_level == RiskLevel.LOW

def test_all_medium():

    result = calculator.calculate(
        aggregation=aggregation(),
        quality=aspect(45, RiskLevel.MEDIUM, "quality"),
        delivery=aspect(50, RiskLevel.MEDIUM, "delivery"),
        trust=aspect(55, RiskLevel.MEDIUM, "trust"),
    )

    assert result.business_risk_level == RiskLevel.MEDIUM

def test_trust_critical_override():

    result = calculator.calculate(
        aggregation=aggregation(),
        quality=aspect(40, RiskLevel.MEDIUM, "quality"),
        delivery=aspect(35, RiskLevel.LOW, "delivery"),
        trust=aspect(95, RiskLevel.CRITICAL, "trust"),
    )

    assert result.business_risk_level == RiskLevel.CRITICAL

def test_quality_critical_override():

    result = calculator.calculate(
        aggregation=aggregation(),
        quality=aspect(95, RiskLevel.CRITICAL, "quality"),
        delivery=aspect(35, RiskLevel.LOW, "delivery"),
        trust=aspect(30, RiskLevel.LOW, "trust"),
    )

    assert result.business_risk_level == RiskLevel.HIGH

def test_delivery_critical_override():

    result = calculator.calculate(
        aggregation=aggregation(),
        quality=aspect(30, RiskLevel.LOW, "quality"),
        delivery=aspect(90, RiskLevel.CRITICAL, "delivery"),
        trust=aspect(40, RiskLevel.MEDIUM, "trust"),
    )

    assert result.business_risk_level == RiskLevel.HIGH


def test_multiple_high_rule():

    result = calculator.calculate(
        aggregation=aggregation(),
        quality=aspect(75, RiskLevel.HIGH, "quality"),
        delivery=aspect(80, RiskLevel.HIGH, "delivery"),
        trust=aspect(30, RiskLevel.LOW, "trust"),
    )

    assert result.business_risk_level == RiskLevel.CRITICAL

def test_baseline_result():

    result = calculator.calculate(
        aggregation=aggregation(),
        quality=aspect(72, RiskLevel.HIGH, "quality"),
        delivery=aspect(45, RiskLevel.MEDIUM, "delivery"),
        trust=aspect(35, RiskLevel.LOW, "trust"),
    )

    assert result.business_risk_level == RiskLevel.HIGH

def test_baseline_medium():

    result = calculator.calculate(
        aggregation=aggregation(),
        quality=aspect(48, RiskLevel.MEDIUM, "quality"),
        delivery=aspect(25, RiskLevel.LOW, "delivery"),
        trust=aspect(30, RiskLevel.LOW, "trust"),
    )

    assert result.business_risk_level == RiskLevel.MEDIUM

def test_baseline_score():

    result = calculator.calculate(
        aggregation=aggregation(),
        quality=aspect(82.4, RiskLevel.HIGH, "quality"),
        delivery=aspect(30, RiskLevel.LOW, "delivery"),
        trust=aspect(25, RiskLevel.LOW, "trust"),
    )

    assert result.business_risk_index == pytest.approx(82.4)

