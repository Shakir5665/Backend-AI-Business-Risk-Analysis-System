from __future__ import annotations

from core.business_risk.calculator.rules.base_rule import BusinessRule
from core.business_risk.calculator.rules.rule_context import RuleContext
from core.business_risk.calculator.utils import count_at_least
from core.business_risk.models.risk_level import RiskLevel


class MultipleHighRiskRule(BusinessRule):
    """
    If two or more business aspects are HIGH or CRITICAL,
    the overall business risk becomes CRITICAL.
    """

    def matches(self, context: RuleContext) -> bool:

        levels = [
            context.quality.level,
            context.delivery.level,
            context.trust.level,
        ]

        return count_at_least(levels, RiskLevel.HIGH) >= 2

    def apply(self, context: RuleContext) -> RiskLevel:
        return RiskLevel.CRITICAL