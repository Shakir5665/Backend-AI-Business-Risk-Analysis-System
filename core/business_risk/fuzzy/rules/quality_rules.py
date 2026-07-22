import skfuzzy.control as ctrl

from core.business_risk.fuzzy.fuzzy_variables import (
    create_input_variable,
    create_output_variable,
)


def build_quality_control_system() -> ctrl.ControlSystem:
    """
    Build the fuzzy control system for Quality Risk Assessment.
    """

    # ==========================================================
    # Input Variables
    # ==========================================================

    quality_mention_ratio = create_input_variable(
        "quality_mention_ratio"
    )

    quality_negative_strength = create_input_variable(
        "quality_negative_strength"
    )

    # ==========================================================
    # Output Variable
    # ==========================================================

    quality_risk = create_output_variable(
        "quality_risk"
    )

    # ==========================================================
    # Rule Base
    # ==========================================================

    rules = [

        ctrl.Rule(
            quality_mention_ratio["LOW"] &
            quality_negative_strength["LOW"],
            quality_risk["VERY_LOW"]
        ),

        ctrl.Rule(
            quality_mention_ratio["LOW"] &
            quality_negative_strength["MEDIUM"],
            quality_risk["LOW"]
        ),

        ctrl.Rule(
            quality_mention_ratio["LOW"] &
            quality_negative_strength["HIGH"],
            quality_risk["MEDIUM"]
        ),

        ctrl.Rule(
            quality_mention_ratio["MEDIUM"] &
            quality_negative_strength["LOW"],
            quality_risk["LOW"]
        ),

        ctrl.Rule(
            quality_mention_ratio["MEDIUM"] &
            quality_negative_strength["MEDIUM"],
            quality_risk["MEDIUM"]
        ),

        ctrl.Rule(
            quality_mention_ratio["MEDIUM"] &
            quality_negative_strength["HIGH"],
            quality_risk["HIGH"]
        ),

        ctrl.Rule(
            quality_mention_ratio["HIGH"] &
            quality_negative_strength["LOW"],
            quality_risk["MEDIUM"]
        ),

        ctrl.Rule(
            quality_mention_ratio["HIGH"] &
            quality_negative_strength["MEDIUM"],
            quality_risk["HIGH"]
        ),

        ctrl.Rule(
            quality_mention_ratio["HIGH"] &
            quality_negative_strength["HIGH"],
            quality_risk["CRITICAL"]
        ),
    ]

    return ctrl.ControlSystem(rules)