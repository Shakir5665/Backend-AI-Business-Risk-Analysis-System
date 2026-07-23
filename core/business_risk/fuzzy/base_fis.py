from abc import ABC
from typing import Dict

import skfuzzy.control as ctrl

from core.business_risk.models.aspect_risk import AspectRisk
from core.business_risk.models.risk_level import RiskLevel


class BaseFIS(ABC):
    """
    Base class for all fuzzy inference systems.

    Provides common functionality for:
    - running fuzzy inference
    - computing crisp output
    - converting score to RiskLevel
    - returning AspectRisk
    """

    def __init__(
        self,
        aspect_name: str,
        control_system: ctrl.ControlSystem,
        input_mapping: Dict[str, str],
        output_variable: str,
    ):

        self.aspect_name = aspect_name

        self.input_mapping = input_mapping

        self.output_variable = output_variable

        self.simulation = ctrl.ControlSystemSimulation(
            control_system
        )

    def evaluate(self, **inputs) -> AspectRisk:
        """
        Execute fuzzy inference.

        Example:

        evaluate(
            mention_ratio=0.62,
            average_negative_strength=0.73
        )
        """

        # Assign inputs
        for parameter, variable_name in self.input_mapping.items():

            if parameter not in inputs:
                raise ValueError(
                    f"Missing input parameter: {parameter}"
                )

            self.simulation.input[variable_name] = inputs[parameter]

        # Run inference
        self.simulation.compute()

        # Read output
        score = self.simulation.output[self.output_variable]

        return AspectRisk(
            aspect=self.aspect_name,
            score=round(score, 2),
            level=self.determine_level(score)
        )

    @staticmethod
    def determine_level(score: float) -> RiskLevel:

        if score < 20:
            return RiskLevel.VERY_LOW

        elif score < 40:
            return RiskLevel.LOW

        elif score < 60:
            return RiskLevel.MEDIUM

        elif score < 80:
            return RiskLevel.HIGH

        return RiskLevel.CRITICAL