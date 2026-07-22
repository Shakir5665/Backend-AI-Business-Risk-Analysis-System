import skfuzzy.control as ctrl

from business_risk.fuzzy.fuzzy_variables import (
    create_input_variable,
    create_output_variable,
)


def build_trust_control_system() -> ctrl.ControlSystem:
    """
    Build the fuzzy control system for Trust Risk Assessment.
    """

    trust_mention_ratio = create_input_variable(
        "trust_mention_ratio"
    )

    trust_negative_strength = create_input_variable(
        "trust_negative_strength"
    )

    trust_risk = create_output_variable(
        "trust_risk"
    )

    rules = [

        ctrl.Rule(
            trust_mention_ratio["LOW"] &
            trust_negative_strength["LOW"],
            trust_risk["VERY_LOW"]
        ),

        ctrl.Rule(
            trust_mention_ratio["LOW"] &
            trust_negative_strength["MEDIUM"],
            trust_risk["LOW"]
        ),

        ctrl.Rule(
            trust_mention_ratio["LOW"] &
            trust_negative_strength["HIGH"],
            trust_risk["MEDIUM"]
        ),

        ctrl.Rule(
            trust_mention_ratio["MEDIUM"] &
            trust_negative_strength["LOW"],
            trust_risk["LOW"]
        ),

        ctrl.Rule(
            trust_mention_ratio["MEDIUM"] &
            trust_negative_strength["MEDIUM"],
            trust_risk["MEDIUM"]
        ),

        ctrl.Rule(
            trust_mention_ratio["MEDIUM"] &
            trust_negative_strength["HIGH"],
            trust_risk["HIGH"]
        ),

        ctrl.Rule(
            trust_mention_ratio["HIGH"] &
            trust_negative_strength["LOW"],
            trust_risk["MEDIUM"]
        ),

        ctrl.Rule(
            trust_mention_ratio["HIGH"] &
            trust_negative_strength["MEDIUM"],
            trust_risk["HIGH"]
        ),

        ctrl.Rule(
            trust_mention_ratio["HIGH"] &
            trust_negative_strength["HIGH"],
            trust_risk["CRITICAL"]
        ),
    ]

    return ctrl.ControlSystem(rules)