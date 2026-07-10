"""
Aggregation Result

Stores the aggregated business
statistics generated from AI
predictions.

Project:
AI-Powered Business Risk Analysis
and Recommendation System
"""

from typing import Dict

from core.common.logger import logger


class AggregationResult:
    """
    Standard aggregation output.
    """

    def __init__(self):

        self.review_statistics = {}

        self.sentiment_statistics = {}

        self.aspect_statistics = {}

        self.confidence_statistics = {}

        #self.weighted_statistics = {}

        self.fuzzy_inputs = {}

        logger.info(
            "AggregationResult initialized."
        )

    # ---------------------------------------------

    def to_dict(self) -> Dict:

        return {

            "review_statistics": self.review_statistics,

            "sentiment_statistics": self.sentiment_statistics,

            "aspect_statistics": self.aspect_statistics,

            "confidence_statistics": self.confidence_statistics,

            #"weighted_statistics": self.weighted_statistics,

            "fuzzy_inputs": self.fuzzy_inputs

        }