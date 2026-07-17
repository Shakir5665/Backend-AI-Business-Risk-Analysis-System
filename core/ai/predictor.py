 
"""
Predictor

Public AI prediction interface.

Responsibilities
----------------
- Coordinate inference pipeline
- Return formatted prediction

Project:
AI-Powered Business Risk Analysis
and Recommendation System
"""

from typing import Dict

from core.ai.inference.model_loader import ModelLoader
from core.ai.inference.inference_engine import InferenceEngine
from core.ai.inference.prediction_formatter import PredictionFormatter

from core.common.logger import logger


class Predictor:
    """
    Public AI prediction service.
    """

    def __init__(self):

        logger.info(
            "Initializing Predictor..."
        )

        # Load all shared AI resources once
        self._loader = ModelLoader()

        # AI Pipeline
        self._engine = InferenceEngine(
            self._loader
        )

        self._formatter = PredictionFormatter(
            self._loader
        )

        logger.info(
            "Predictor initialized successfully."
        )

    # --------------------------------------------------

    def predict(
        self,
        review: str
    ) -> Dict:

        outputs = self._engine.predict(
            review
        )

        result = self._formatter.format(
            review,
            outputs
        )

        return result