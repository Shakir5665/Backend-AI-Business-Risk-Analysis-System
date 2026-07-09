"""
Inference Engine

Runs the complete AI inference pipeline.

Responsibilities
----------------
- Preprocess review
- Tokenize review
- Run model inference
- Return raw logits

Project:
AI-Powered Business Risk Analysis
and Recommendation System
"""

from typing import Dict

import torch

from core.ai.preprocessing.preprocessor import ReviewPreprocessor
from core.ai.inference.model_loader import ModelLoader

from core.common.logger import logger


class InferenceEngine:
    """
    Executes AI inference.
    """

    def __init__(self, loader):

        self.loader = loader

        self.preprocessor = ReviewPreprocessor()

    # --------------------------------------------------

    def predict(
        self,
        review: str
    ) -> Dict[str, torch.Tensor]:

        # -----------------------------
        # Preprocess
        # -----------------------------

        review = self.preprocessor.preprocess(

            review

        )

        # -----------------------------
        # Tokenize
        # -----------------------------

        tokens = self.loader.tokenizer_instance.tokenize(

            review

        )

        input_ids = tokens["input_ids"].unsqueeze(0).to(

            self.loader.device

        )

        attention_mask = tokens["attention_mask"].unsqueeze(0).to(

            self.loader.device

        )

        # -----------------------------
        # Model Inference
        # -----------------------------

        with torch.no_grad():

            outputs = self.loader.model_instance(

                input_ids=input_ids,

                attention_mask=attention_mask

            )

        return outputs