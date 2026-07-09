"""
Repeated Character Normalizer

Reduces excessive repeated characters while preserving meaning.

Examples:
    goooood      -> good
    niyaaaamai   -> niyamai
    brooooo      -> bro
    suuuuper     -> suuper

Project:
AI-Powered Business Risk Analysis and Recommendation System
"""

import re
from typing import Optional

from configs.preprocessing_config import MAX_REPEATED_CHARACTERS
from core.common.logger import logger


class RepeatNormalizer:

    def __init__(self):

        self.pattern = re.compile(r"(.)\1{2,}")

        logger.info("RepeatNormalizer initialized")

    def normalize(self, text: Optional[str]) -> str:

        if not text:
            return ""

        return self.pattern.sub(self._replace, text)

    def _replace(self, match):

        character = match.group(1)

        return character * MAX_REPEATED_CHARACTERS

    def normalize_batch(self, texts):

        return [
            self.normalize(text)
            for text in texts
        ]