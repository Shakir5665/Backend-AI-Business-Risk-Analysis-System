import skfuzzy.control as ctrl

from .membership_config import (
    INPUT_UNIVERSE,
    OUTPUT_UNIVERSE,
    INPUT_MEMBERSHIPS,
    OUTPUT_MEMBERSHIPS,
)


def create_input_variable(name: str) -> ctrl.Antecedent:
    """
    Create a standardized fuzzy input variable.
    """

    variable = ctrl.Antecedent(INPUT_UNIVERSE, name)

    for label, mf in INPUT_MEMBERSHIPS.items():
        variable[label] = mf(INPUT_UNIVERSE)

    return variable


def create_output_variable(name: str) -> ctrl.Consequent:
    """
    Create a standardized fuzzy output variable.
    """

    variable = ctrl.Consequent(OUTPUT_UNIVERSE, name)

    for label, mf in OUTPUT_MEMBERSHIPS.items():
        variable[label] = mf(OUTPUT_UNIVERSE)

    return variable