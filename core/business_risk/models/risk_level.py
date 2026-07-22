from enum import Enum


class RiskLevel(str, Enum):
    """
    Standard business risk levels.
    """

    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"