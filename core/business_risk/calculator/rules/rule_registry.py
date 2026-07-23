from core.business_risk.calculator.rules.base_rule import BusinessRule
from core.business_risk.calculator.rules.tier1_rules import (
    DeliveryCriticalRule,
    QualityCriticalRule,
    TrustCriticalRule,
)
from core.business_risk.calculator.rules.tier2_rules import (
    MultipleHighRiskRule,
)
from core.business_risk.calculator.rules.tier3_rules import (
    AllLowRule,
    AllMediumRule,
    AllVeryLowRule,
)

RULES: list[BusinessRule] = [

    # ---------------------------------------------------------
    # Tier 1 - Override Rules
    # ---------------------------------------------------------
    TrustCriticalRule(),
    QualityCriticalRule(),
    DeliveryCriticalRule(),

    # ---------------------------------------------------------
    # Tier 2 - Escalation Rules
    # ---------------------------------------------------------
    MultipleHighRiskRule(),

    # ---------------------------------------------------------
    # Tier 3 - Consistency Rules
    # ---------------------------------------------------------
    AllVeryLowRule(),
    AllLowRule(),
    AllMediumRule(),
]
