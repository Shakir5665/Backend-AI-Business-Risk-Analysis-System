import skfuzzy.control as ctrl

from core.business_risk.fuzzy.fuzzy_variables import (
    create_input_variable,
    create_output_variable,
)


def build_delivery_control_system() -> ctrl.ControlSystem:
    """
    Build the fuzzy control system for Delivery Risk Assessment.
    """

    delivery_mention_ratio = create_input_variable(
        "delivery_mention_ratio"
    )

    delivery_negative_strength = create_input_variable(
        "delivery_negative_strength"
    )

    delivery_risk = create_output_variable(
        "delivery_risk"
    )

    rules = [

        ctrl.Rule(
            delivery_mention_ratio["LOW"] &
            delivery_negative_strength["LOW"],
            delivery_risk["VERY_LOW"]
        ),

        ctrl.Rule(
            delivery_mention_ratio["LOW"] &
            delivery_negative_strength["MEDIUM"],
            delivery_risk["LOW"]
        ),

        ctrl.Rule(
            delivery_mention_ratio["LOW"] &
            delivery_negative_strength["HIGH"],
            delivery_risk["MEDIUM"]
        ),

        ctrl.Rule(
            delivery_mention_ratio["MEDIUM"] &
            delivery_negative_strength["LOW"],
            delivery_risk["LOW"]
        ),

        ctrl.Rule(
            delivery_mention_ratio["MEDIUM"] &
            delivery_negative_strength["MEDIUM"],
            delivery_risk["MEDIUM"]
        ),

        ctrl.Rule(
            delivery_mention_ratio["MEDIUM"] &
            delivery_negative_strength["HIGH"],
            delivery_risk["HIGH"]
        ),

        ctrl.Rule(
            delivery_mention_ratio["HIGH"] &
            delivery_negative_strength["LOW"],
            delivery_risk["MEDIUM"]
        ),

        ctrl.Rule(
            delivery_mention_ratio["HIGH"] &
            delivery_negative_strength["MEDIUM"],
            delivery_risk["HIGH"]
        ),

        ctrl.Rule(
            delivery_mention_ratio["HIGH"] &
            delivery_negative_strength["HIGH"],
            delivery_risk["CRITICAL"]
        ),
    ]

    return ctrl.ControlSystem(rules)
