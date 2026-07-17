"""
Prediction Collector

Stores AI predictions for business
risk analysis.

Project:
AI-Powered Business Risk Analysis
and Recommendation System
"""

from typing import Dict, List

from core.common.logger import logger


class PredictionCollector:
    """
    Collects prediction results from
    the AI predictor.
    """

    def __init__(self):

        self._predictions: List[Dict] = []

        logger.info(
            "PredictionCollector initialized."
        )

    # --------------------------------------------------

    def add(
        self,
        prediction: Dict
    ):

        self._predictions.append(
            prediction
        )

    # --------------------------------------------------

    def add_many(
        self,
        predictions: List[Dict]
    ):

        self._predictions.extend(
            predictions
        )

    # --------------------------------------------------

    def get_all(
        self
    ) -> List[Dict]:

        return self._predictions.copy()

    # --------------------------------------------------

    def clear(
        self
    ):

        self._predictions.clear()

    # --------------------------------------------------

    def size(
        self
    ) -> int:

        return len(
            self._predictions
        )