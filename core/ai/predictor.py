 
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
        self.loader = ModelLoader()

        # AI Pipeline
        self.engine = InferenceEngine(
            self.loader
        )

        self.formatter = PredictionFormatter(
            self.loader
        )

        logger.info(
            "Predictor initialized successfully."
        )

    # --------------------------------------------------

    def predict(
        self,
        review: str
    ) -> Dict:

        outputs = self.engine.predict(
            review
        )

        result = self.formatter.format(
            review,
            outputs
        )

        return result