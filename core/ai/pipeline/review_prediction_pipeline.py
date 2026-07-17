"""
Review Prediction Pipeline

Coordinates AI prediction for an entire collection of reviews.

Responsibilities
----------------
- Accept multiple scraped reviews
- Invoke Predictor for each review
- Return all formatted predictions

Project:
AI-Powered Business Risk Analysis
and Recommendation System
"""

from typing import List, Dict

from core.ai.predictor import Predictor
from core.scraper.dto.scraped_review import ScrapedReview

from core.common.logger import logger


class ReviewPredictionPipeline:
    """
    Executes AI prediction for a collection of reviews.
    """

    def __init__(self):

        logger.info(
            "Initializing ReviewPredictionPipeline..."
        )

        self._predictor = Predictor()

        logger.info(
            "ReviewPredictionPipeline initialized successfully."
        )

    # --------------------------------------------------

    def predict_reviews(
        self,
        reviews: List[ScrapedReview]
    ) -> List[Dict]:
        """
        Predict all reviews of a product.

        Parameters
        ----------
        reviews : List[ScrapedReview]

        Returns
        -------
        List[Dict]
        """

        logger.info(
            f"Predicting {len(reviews)} reviews..."
        )

        predictions = []

        for review in reviews:

            prediction = self._predictor.predict(
                review.review_text
            )

            predictions.append(
                prediction
            )

        logger.info(
            f"Finished predicting {len(predictions)} reviews."
        )

        return predictions