from business_risk.fuzzy.base_fis import BaseFIS
from business_risk.fuzzy.rules.trust_rules import (
    build_trust_control_system,
)


class TrustFIS(BaseFIS):
    """
    Trust Risk Fuzzy Inference System.
    """

    def __init__(self):

        super().__init__(
            aspect_name="Trust",

            control_system=build_trust_control_system(),

            input_mapping={
                "mention_ratio": "trust_mention_ratio",
                "average_negative_strength": "trust_negative_strength",
            },

            output_variable="trust_risk",
        )
        