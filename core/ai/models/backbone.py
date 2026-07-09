"""
XLM-R Backbone

Loads the pretrained XLM-R model and
returns the CLS embedding.

Project:
AI-Powered Business Risk Analysis
and Recommendation System
"""

import torch
import torch.nn as nn

from transformers import AutoModel

from configs.model_config import (
    MODEL_NAME,
    FREEZE_BACKBONE
)

from core.common.logger import logger


class XLMRBackbone(nn.Module):
    """
    Wrapper around pretrained XLM-R.

    Input
    -----
    input_ids        : (batch_size, sequence_length)

    attention_mask   : (batch_size, sequence_length)

    Output
    ------
    CLS embedding    : (batch_size, hidden_size)
    """

    def __init__(self):

        super().__init__()

        self.backbone = AutoModel.from_pretrained(
            MODEL_NAME
        )

        if FREEZE_BACKBONE:

            for parameter in self.backbone.parameters():

                parameter.requires_grad = False

        logger.info(
            f"Loaded pretrained backbone: {MODEL_NAME}"
        )

    # --------------------------------------------------

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor
    ) -> torch.Tensor:

        outputs = self.backbone(

            input_ids=input_ids,

            attention_mask=attention_mask

        )

        cls_embedding = outputs.last_hidden_state[:, 0, :]

        return cls_embedding