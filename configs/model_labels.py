"""
Model Label Configuration

Defines the fixed label order used across the
entire machine learning pipeline.

This file must NEVER be changed after model training,
otherwise saved models become incompatible.

Project:
AI-Powered Business Risk Analysis and Recommendation System
"""

# ----------------------------------------------------------
# Sentiment Labels
# ----------------------------------------------------------

SENTIMENT_LABELS = [

    "negative",

    "neutral",

    "positive"

]

# ----------------------------------------------------------
# Aspect Labels
# ----------------------------------------------------------

ASPECT_LABELS = [

    "quality",

    "trust",

    "delivery"

]