from dataclasses import dataclass


@dataclass(frozen=True)
class AspectRisk:
    """
    Represents the fuzzy risk assessment for a single business aspect.
    """

    aspect: str
    score: float          # Crisp risk score (0–100)
    level: str            # VERY_LOW, LOW, MEDIUM, HIGH, CRITICAL