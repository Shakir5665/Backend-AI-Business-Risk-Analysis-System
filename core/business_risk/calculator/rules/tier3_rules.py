from __future__ import annotations

from core.business_risk.calculator.rules.base_rule import BusinessRule
from core.business_risk.calculator.rules.rule_context import RuleContext
from core.business_risk.models.risk_level import RiskLevel


class AllVeryLowRule(BusinessRule):
    """
    All aspects indicate VERY_LOW risk.
    """

    def matches(self, context: RuleContext) -> bool:
        return (
            context.quality.level == RiskLevel.VERY_LOW
            and context.delivery.level == RiskLevel.VERY_LOW
            and context.trust.level == RiskLevel.VERY_LOW
        )

    def apply(self, context: RuleContext) -> RiskLevel:
        return RiskLevel.VERY_LOW


class AllLowRule(BusinessRule):
    """
    All aspects indicate LOW risk.
    """

    def matches(self, context: RuleContext) -> bool:
        return (
            context.quality.level == RiskLevel.LOW
            and context.delivery.level == RiskLevel.LOW
            and context.trust.level == RiskLevel.LOW
        )

    def apply(self, context: RuleContext) -> RiskLevel:
        return RiskLevel.LOW


class AllMediumRule(BusinessRule):
    """
    All aspects indicate MEDIUM risk.
    """

    def matches(self, context: RuleContext) -> bool:
        return (
            context.quality.level == RiskLevel.MEDIUM
            and context.delivery.level == RiskLevel.MEDIUM
            and context.trust.level == RiskLevel.MEDIUM
        )

    def apply(self, context: RuleContext) -> RiskLevel:
        return RiskLevel.MEDIUM