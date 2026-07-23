from __future__ import annotations

from abc import ABC, abstractmethod

from core.business_risk.calculator.rules.rule_context import RuleContext
from core.business_risk.models.risk_level import RiskLevel


class BusinessRule(ABC):
    """
    Base class for all Business Risk rules.

    Each rule inspects the RuleContext and decides
    whether it should override the baseline risk.
    """

    @abstractmethod
    def matches(self, context: RuleContext) -> bool:
        """
        Returns True if this rule should be applied.
        """
        raise NotImplementedError

    @abstractmethod
    def apply(self, context: RuleContext) -> RiskLevel:
        """
        Returns the Business Risk Level produced by this rule.
        """
        raise NotImplementedError

    @property
    def name(self) -> str:
        """
        Human-readable rule name.
        """
        return self.__class__.__name__