from __future__ import annotations

from core.business_risk.calculator.rules.base_rule import BusinessRule
from core.business_risk.calculator.rules.rule_context import RuleContext
from core.business_risk.calculator.utils import is_below
from core.business_risk.models.risk_level import RiskLevel


class TrustCriticalRule(BusinessRule):
    """
    Trust is the most sensitive business aspect.

    If Trust is CRITICAL while the other aspects are
    below HIGH, the overall business risk becomes CRITICAL.
    """

    def matches(self, context: RuleContext) -> bool:
        return (
            context.trust.level == RiskLevel.CRITICAL
            and is_below(context.quality.level, RiskLevel.HIGH)
            and is_below(context.delivery.level, RiskLevel.HIGH)
        )

    def apply(self, context: RuleContext) -> RiskLevel:
        return RiskLevel.CRITICAL


class QualityCriticalRule(BusinessRule):
    """
    Product quality is critical but less severe than trust.
    """

    def matches(self, context: RuleContext) -> bool:
        return (
            context.quality.level == RiskLevel.CRITICAL
            and is_below(context.delivery.level, RiskLevel.HIGH)
            and is_below(context.trust.level, RiskLevel.HIGH)
        )

    def apply(self, context: RuleContext) -> RiskLevel:
        return RiskLevel.HIGH


class DeliveryCriticalRule(BusinessRule):
    """
    Delivery failures can significantly impact the business,
    but are generally less severe than trust failures.
    """

    def matches(self, context: RuleContext) -> bool:
        return (
            context.delivery.level == RiskLevel.CRITICAL
            and is_below(context.quality.level, RiskLevel.HIGH)
            and is_below(context.trust.level, RiskLevel.HIGH)
        )

    def apply(self, context: RuleContext) -> RiskLevel:
        return RiskLevel.HIGH