"""
Business Risk Model

Multi-task learning model for:

1. Sentiment Classification
2. Aspect Classification

Architecture

Input
  │
  ▼
XLM-R Backbone
  │
  ▼
CLS Embedding
  │
 ┌──────────────┐
 ▼              ▼
Sentiment    Aspect
 Adapter     Adapter
 ▼              ▼
Head         Head
 ▼              ▼
Sentiment    Aspect
 Logits      Logits

Project:
AI-Powered Business Risk Analysis
and Recommendation System
"""

from typing import Dict

import torch
import torch.nn as nn

from core.ai.models.backbone import XLMRBackbone
from core.ai.models.adapter import Adapter
from core.ai.models.classification_heads import (
    SentimentHead,
    AspectHead
)

from configs.model_config import (
    HIDDEN_SIZE,
    ADAPTER_DIM
)

from core.common.logger import logger


class BusinessRiskModel(nn.Module):
    """
    Multi-task Business Risk Model.
    """

    def __init__(
        self,
        num_aspect_classes: int
    ):

        super().__init__()

        # -----------------------------
        # Backbone
        # -----------------------------

        self.backbone = XLMRBackbone()

        # -----------------------------
        # Adapters
        # -----------------------------

        self.sentiment_adapter = Adapter()
    

        self.aspect_adapter = Adapter()

        # -----------------------------
        # Classification Heads
        # -----------------------------

        self.sentiment_head = SentimentHead()

        self.aspect_head = AspectHead(

            num_aspect_classes=num_aspect_classes

        )

        logger.info(
            "BusinessRiskModel initialized."
        )

    # -------------------------------------------------

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor
    ) -> Dict[str, torch.Tensor]:

        # -----------------------------
        # XLM-R
        # -----------------------------

        cls_embedding = self.backbone(

            input_ids=input_ids,

            attention_mask=attention_mask

        )

        # -----------------------------
        # Sentiment Branch
        # -----------------------------

        sentiment_features = self.sentiment_adapter(

            cls_embedding

        )

        sentiment_logits = self.sentiment_head(

            sentiment_features

        )

        # -----------------------------
        # Aspect Branch
        # -----------------------------

        aspect_features = self.aspect_adapter(

            cls_embedding

        )

        aspect_logits = self.aspect_head(

            aspect_features

        )

        # -----------------------------
        # Output
        # -----------------------------

        return {

            "sentiment_logits": sentiment_logits,

            "aspect_logits": aspect_logits

        }