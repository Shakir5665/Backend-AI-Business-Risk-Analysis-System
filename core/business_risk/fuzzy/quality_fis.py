from core.business_risk.fuzzy.base_fis import BaseFIS
from core.business_risk.fuzzy.rules.quality_rules import (
    build_quality_control_system,
)


class QualityFIS(BaseFIS):
    """
    Quality Risk Fuzzy Inference System.
    """

    def __init__(self):

        super().__init__(
            aspect_name="Quality",

            control_system=build_quality_control_system(),

            input_mapping={
                "mention_ratio": "quality_mention_ratio",
                "average_negative_strength": "quality_negative_strength",
            },

            output_variable="quality_risk",
        )