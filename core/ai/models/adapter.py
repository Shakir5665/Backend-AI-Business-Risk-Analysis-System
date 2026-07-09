"""
Adapter Layer

Implements a bottleneck adapter for
parameter-efficient fine-tuning.

Project:
AI-Powered Business Risk Analysis
and Recommendation System
"""

import torch
import torch.nn as nn

from configs.model_config import (
    HIDDEN_SIZE,
    ADAPTER_DIM,
    ADAPTER_DROPOUT
)

from core.common.logger import logger


class Adapter(nn.Module):
    """
    Bottleneck Adapter

    Architecture

        Input (768)

            │

            ▼

      Linear (768 → 64)

            │

            ▼

          ReLU

            │

            ▼

        Dropout

            │

            ▼

      Linear (64 → 768)

            │

            ▼

      Residual Connection

            │

            ▼

        Output (768)
    """

    def __init__(self):

        super().__init__()

        self.down_projection = nn.Linear(
            HIDDEN_SIZE,
            ADAPTER_DIM
        )

        self.activation = nn.ReLU()

        self.dropout = nn.Dropout(
            ADAPTER_DROPOUT
        )

        self.up_projection = nn.Linear(
            ADAPTER_DIM,
            HIDDEN_SIZE
        )

        logger.info("Adapter initialized.")

    def forward(
        self,
        x: torch.Tensor
    ) -> torch.Tensor:

        residual = x

        x = self.down_projection(x)

        x = self.activation(x)

        x = self.dropout(x)

        x = self.up_projection(x)

        x = x + residual

        return x