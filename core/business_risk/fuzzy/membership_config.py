"""
Membership function configuration for the Business Risk Engine.
"""

import numpy as np
import skfuzzy as fuzz


# ==========================================================
# Universe of Discourse
# ==========================================================

# Input variables (normalized to 0.0 - 1.0)
INPUT_UNIVERSE = np.arange(0.0, 1.01, 0.01)

# Output variables (risk score 0 - 100)
OUTPUT_UNIVERSE = np.arange(0, 101, 1)


# ==========================================================
# Input Membership Functions
# ==========================================================

INPUT_MEMBERSHIPS = {

    "LOW": lambda x: fuzz.trapmf(x, [0.00, 0.00, 0.20, 0.40]),

    "MEDIUM": lambda x: fuzz.trimf(x, [0.25, 0.50, 0.75]),

    "HIGH": lambda x: fuzz.trapmf(x, [0.60, 0.80, 1.00, 1.00]),
}


# ==========================================================
# Output Membership Functions
# ==========================================================

OUTPUT_MEMBERSHIPS = {

    "VERY_LOW": lambda x: fuzz.trapmf(x, [0, 0, 10, 20]),

    "LOW": lambda x: fuzz.trimf(x, [15, 30, 45]),

    "MEDIUM": lambda x: fuzz.trimf(x, [40, 55, 70]),

    "HIGH": lambda x: fuzz.trimf(x, [65, 80, 90]),

    "CRITICAL": lambda x: fuzz.trapmf(x, [85, 95, 100, 100]),
}