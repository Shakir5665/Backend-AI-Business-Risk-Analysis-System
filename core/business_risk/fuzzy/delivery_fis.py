from core.business_risk.fuzzy.base_fis import BaseFIS
from core.business_risk.fuzzy.rules.delivery_rules import (
    build_delivery_control_system,
)


class DeliveryFIS(BaseFIS):
    """
    Delivery Risk Fuzzy Inference System.
    """

    def __init__(self):

        super().__init__(
            aspect_name="Delivery",

            control_system=build_delivery_control_system(),

            input_mapping={
                "mention_ratio": "delivery_mention_ratio",
                "average_negative_strength": "delivery_negative_strength",
            },

            output_variable="delivery_risk",
        )