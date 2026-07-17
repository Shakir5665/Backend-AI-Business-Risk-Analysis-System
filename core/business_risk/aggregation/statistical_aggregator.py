"""
Statistical Aggregator

Aggregates AI prediction results
into business statistics.

Project:
AI-Powered Business Risk Analysis
and Recommendation System
"""

from typing import Dict, List

from configs.model_config import LOW_CONFIDENCE_THRESHOLD

from core.business_risk.aggregation.aggregation_result import AggregationResult
from core.common.logger import logger


class StatisticalAggregator:
    """
    Aggregates prediction results.
    """

    def __init__(self):

        logger.info(
            "StatisticalAggregator initialized."
        )

    # ------------------------------------------------
    # Aggregate
    # ------------------------------------------------

    def aggregate(
        self,
        predictions: List[Dict]
    ) -> AggregationResult:

        result = AggregationResult()

        self._calculate_review_statistics(
            predictions,
            result
        )

        self._calculate_sentiment_statistics(
            result
        )

        self._calculate_aspect_statistics(
            predictions,
            result
        )

        self._calculate_confidence_statistics(
            predictions,
            result
        )

        return result

    # ------------------------------------------------
    # Review Statistics
    # ------------------------------------------------

    def _calculate_review_statistics(
        self,
        predictions: List[Dict],
        result: AggregationResult
    ) -> None:

        total_reviews = len(predictions)

        positive_reviews = 0
        negative_reviews = 0
        neutral_reviews = 0

        for prediction in predictions:

            sentiment = prediction["sentiment"]

            if sentiment == "positive":
                positive_reviews += 1

            elif sentiment == "negative":
                negative_reviews += 1

            elif sentiment == "neutral":
                neutral_reviews += 1

        result.review_statistics = {

            "total_reviews": total_reviews,

            "positive_reviews": positive_reviews,

            "negative_reviews": negative_reviews,

            "neutral_reviews": neutral_reviews

        }

    # ------------------------------------------------
    # Sentiment Statistics
    # ------------------------------------------------

    def _calculate_sentiment_statistics(
        self,
        result
    ):

        total_reviews = result.review_statistics["total_reviews"]

        positive_reviews = result.review_statistics["positive_reviews"]

        negative_reviews = result.review_statistics["negative_reviews"]

        neutral_reviews = result.review_statistics["neutral_reviews"]

        if total_reviews > 0:

            positive_ratio = round(
                positive_reviews / total_reviews,
                4
            )

            negative_ratio = round(
                negative_reviews / total_reviews,
                4
            )

            neutral_ratio = round(
                neutral_reviews / total_reviews,
                4
            )

        else:

            positive_ratio = 0.0
            negative_ratio = 0.0
            neutral_ratio = 0.0

        result.sentiment_statistics = {

            "positive_ratio": positive_ratio,

            "negative_ratio": negative_ratio,

            "neutral_ratio": neutral_ratio

        }

    # ------------------------------------------------
    # Aspect Statistics
    # ------------------------------------------------

    def _calculate_aspect_statistics(
        self,
        predictions,
        result
    ):

        total_reviews = result.review_statistics["total_reviews"]

        aspect_statistics = {

            "quality": {

                "mentions": 0,
                "mention_ratio": 0.0,

                "strength": 0.0,
                "average_strength": 0.0 ,

                "negative_strength":0.0,

                "average_negative_strength":0.0

            },

            "delivery": {

                "mentions": 0,
                "mention_ratio": 0.0,

                "strength": 0.0,
                "average_strength": 0.0,

                "negative_strength":0.0,

                "average_negative_strength":0.0



            },

            "trust": {

                "mentions": 0,
                "mention_ratio": 0.0,

                "strength": 0.0,
                "average_strength": 0.0 ,

                "negative_strength":0.0,

                "average_negative_strength":0.0

            }

        }

        for prediction in predictions:

            # Count mentions
            for aspect in prediction["detected_aspects"]:

                aspect_statistics[aspect]["mentions"] += 1

            # Accumulate strengths
            for aspect, probability in prediction["aspect_probabilities"].items():

                aspect_statistics[aspect]["strength"] += probability

                if prediction["sentiment"] == "negative":

                    aspect_statistics[aspect]["negative_strength"] += probability

        for aspect in aspect_statistics.values():

            if total_reviews > 0:

                aspect["mention_ratio"] = round(

                    aspect["mentions"] / total_reviews,

                    4

                )

                aspect["average_strength"] = round(

                    aspect["strength"] / total_reviews,

                    4

                )

                aspect["average_negative_strength"] = round(

                    aspect["negative_strength"] / total_reviews,

                    4

                )

            aspect["strength"] = round(

                aspect["strength"],

                4

            )

            aspect["negative_strength"] = round(

                aspect["negative_strength"],

                4

            )

            

        result.aspect_statistics = aspect_statistics

    # ------------------------------------------------
    # Confidence Statistics
    # ------------------------------------------------

    def _calculate_confidence_statistics(
        self,
        predictions,
        result
    ):

        total_reviews = result.review_statistics["total_reviews"]

        total_confidence = 0.0

        low_confidence_reviews = 0

        for prediction in predictions:

            confidence = prediction["confidence"]

            total_confidence += confidence

            if confidence < LOW_CONFIDENCE_THRESHOLD:

                low_confidence_reviews += 1

        if total_reviews > 0:

            average_confidence = round(

                total_confidence / total_reviews,

                4

            )

            low_confidence_ratio = round(

                low_confidence_reviews / total_reviews,

                4

            )

        else:

            average_confidence = 0.0

            low_confidence_ratio = 0.0

        result.confidence_statistics = {

            "average_confidence": average_confidence,

            "low_confidence_ratio": low_confidence_ratio

        }