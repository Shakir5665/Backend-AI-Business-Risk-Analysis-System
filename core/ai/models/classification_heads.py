"""
Classification Heads

Contains task-specific classification heads
for Sentiment Analysis and Aspect Detection.

Project:
AI-Powered Business Risk Analysis
and Recommendation System
"""

import torch
import torch.nn as nn

from configs.model_config import (
    HIDDEN_SIZE,
    CLASSIFIER_DROPOUT,
    NUM_SENTIMENT_CLASSES
)

from core.common.logger import logger


# ==========================================================
# Sentiment Classification Head
# ==========================================================

class SentimentHead(nn.Module):
    """
    Sentiment Classification Head

    Architecture

    768
      │
      ▼
    Dropout
      │
      ▼
    Linear 768 → 256
      │
      ▼
      ReLU
      │
      ▼
    Dropout
      │
      ▼
    Linear 256 → 3
    """

    def __init__(self):

        super().__init__()

        self.classifier = nn.Sequential(

            nn.Dropout(CLASSIFIER_DROPOUT),

            nn.Linear(
                HIDDEN_SIZE,
                256
            ),

            nn.ReLU(),

            nn.Dropout(CLASSIFIER_DROPOUT),

            nn.Linear(
                256,
                NUM_SENTIMENT_CLASSES
            )

        )

        logger.info(
            "Sentiment Head initialized."
        )

    def forward(
        self,
        x: torch.Tensor
    ) -> torch.Tensor:

        return self.classifier(x)


# ==========================================================
# Aspect Classification Head
# ==========================================================

class AspectHead(nn.Module):
    """
    Aspect Classification Head

    Multi-label Classification

    768
      │
      ▼
    Dropout
      │
      ▼
    Linear 768 → 256
      │
      ▼
      ReLU
      │
      ▼
    Dropout
      │
      ▼
    Linear 256 → Number of Aspects
    """

    def __init__(
        self,
        num_aspect_classes: int
    ):

        super().__init__()

        self.classifier = nn.Sequential(

            nn.Dropout(CLASSIFIER_DROPOUT),

            nn.Linear(
                HIDDEN_SIZE,
                256
            ),

            nn.ReLU(),

            nn.Dropout(CLASSIFIER_DROPOUT),

            nn.Linear(
                256,
                num_aspect_classes
            )

        )

        logger.info(
            "Aspect Head initialized."
        )

    def forward(
        self,
        x: torch.Tensor
    ) -> torch.Tensor:

        return self.classifier(x)