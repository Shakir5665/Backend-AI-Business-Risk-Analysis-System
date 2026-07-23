from __future__ import annotations

from core.business_risk.aggregation.aggregation_result import AggregationResult
from core.business_risk.calculator.rules.rule_context import RuleContext
from core.business_risk.calculator.rules.rule_registry import RULES
from core.business_risk.calculator.utils import (
    calculate_baseline_score,
    determine_baseline_level,
)
from core.business_risk.models.aspect_risk import AspectRisk
from core.business_risk.models.business_risk_result import BusinessRiskResult


class BusinessRiskCalculator:
    """
    Executes the Business Rule Engine to determine
    the overall Business Risk Level.
    """

    def calculate(
        self,
        aggregation: AggregationResult,
        quality: AspectRisk,
        delivery: AspectRisk,
        trust: AspectRisk,
    ) -> BusinessRiskResult:

        # -----------------------------------------------------
        # Calculate baseline
        # -----------------------------------------------------

        baseline_score = calculate_baseline_score(
            quality,
            delivery,
            trust,
        )

        baseline_level = determine_baseline_level(
            quality,
            delivery,
            trust,
        )

        # -----------------------------------------------------
        # Create rule context
        # -----------------------------------------------------

        context = RuleContext(
            aggregation=aggregation,

            quality=quality,
            delivery=delivery,
            trust=trust,
            baseline_score=baseline_score,
            baseline_level=baseline_level,
        )

        # -----------------------------------------------------
        # Execute business rules
        # -----------------------------------------------------

        final_level = baseline_level

        for rule in RULES:

            if rule.matches(context):
                final_level = rule.apply(context)
                break

        # -----------------------------------------------------
        # Build result
        # -----------------------------------------------------

        return BusinessRiskResult(
            quality=quality,
            delivery=delivery,
            trust=trust,
            business_risk_index=baseline_score,
            business_risk_level=final_level,
            recommendations=[],
        )