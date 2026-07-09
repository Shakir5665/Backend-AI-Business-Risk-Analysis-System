"""
Prediction Formatter

Converts raw model outputs into
business-friendly prediction results.

Responsibilities
----------------
- Decode sentiment
- Calculate confidence
- Convert logits to probabilities
- Decode aspects

Project:
AI-Powered Business Risk Analysis
and Recommendation System
"""

from typing import Dict

import torch
import torch.nn.functional as F

from core.ai.encoding.sentiment_encoder import SentimentEncoder
from core.ai.encoding.aspect_encoder import AspectEncoder

from core.common.logger import logger

ASPECT_THRESHOLD = 0.5


class PredictionFormatter:
    """
    Formats raw model predictions.
    """

    def __init__(self, loader):

        self.loader = loader

        self.sentiment_encoder = loader.sentiment_encoder_instance

        self.aspect_encoder = loader.aspect_encoder_instance

        logger.info(
            "PredictionFormatter initialized."
        )

    # --------------------------------------------------

    def format(
        self,
        review: str,
        outputs: Dict[str, torch.Tensor]
    ) -> Dict:

        # ----------------------------------------
        # Sentiment
        # ----------------------------------------

        sentiment_logits = outputs["sentiment_logits"]

        sentiment_probs = F.softmax(

            sentiment_logits,

            dim=1

        )[0]

        sentiment_index = torch.argmax(

            sentiment_probs

        ).item()

        sentiment_label = self.sentiment_encoder.decode(

            sentiment_index

        )

        confidence = sentiment_probs[

            sentiment_index

        ].item()


        # ----------------------------------------
        # Aspect
        # ----------------------------------------

        aspect_logits = outputs["aspect_logits"]

        aspect_probs = torch.sigmoid(
            aspect_logits
        )[0]

        aspect_probabilities = {}

        detected_aspects = []

        for index, aspect_name in enumerate(
            self.aspect_encoder.classes
        ):

            probability = round(
                aspect_probs[index].item(),
                4
            )

            aspect_name = str(aspect_name)

            aspect_probabilities[aspect_name] = probability

            if probability >= ASPECT_THRESHOLD:

                detected_aspects.append(
                    aspect_name
                )

        # ----------------------------------------
        # Sentiment Probabilities
        # ----------------------------------------

        sentiment_probabilities = {}

        for index, label in enumerate(

            self.sentiment_encoder.classes

        ):

            sentiment_probabilities[str(label)] = round(

                sentiment_probs[index].item(),

                4

            )

        # ----------------------------------------

        return {

            "review": review,

            "sentiment": str(sentiment_label),

            "confidence": round(
                confidence,
                4
            ),

            "sentiment_probabilities": sentiment_probabilities,

            "aspect_probabilities": aspect_probabilities,

            "detected_aspects": detected_aspects

    }