"""
Review Preprocessor

Single entry point for preprocessing.

Project:
AI-Powered Business Risk Analysis and Recommendation System
"""

from typing import List

from core.common.logger import logger

from core.ai.preprocessing.cleaner import TextCleaner
from core.ai.preprocessing.repeat_normalizer import RepeatNormalizer
from core.ai.preprocessing.srilankan_normalizer import SriLankanNormalizer


class ReviewPreprocessor:

    def __init__(self):

        logger.info("Initializing ReviewPreprocessor...")

        self.cleaner = TextCleaner()

        self.repeat = RepeatNormalizer()

        self.srilankan = SriLankanNormalizer()

        logger.info("ReviewPreprocessor initialized successfully.")

    # ---------------------------------------------------------

    def preprocess(self, text: str) -> str:

        if text is None:
            return ""

        text = self.cleaner.clean(text)

        text = self.repeat.normalize(text)

        text = self.srilankan.normalize(text)

        return text.strip()

    # ---------------------------------------------------------

    def preprocess_batch(
        self,
        texts: List[str]
    ) -> List[str]:

        return [

            self.preprocess(text)

            for text in texts

        ]