"""
Sentiment Label Encoder

Encodes sentiment labels into numerical values
required for model training.

Also supports decoding predictions back to labels.

Project:
AI-Powered Business Risk Analysis and Recommendation System
"""

from pathlib import Path
from typing import List

import joblib
from sklearn.preprocessing import LabelEncoder

from configs.model_labels import SENTIMENT_LABELS
from core.common.logger import logger


class SentimentEncoder:

    def __init__(self):

        self.encoder = LabelEncoder()

        self.encoder.fit(SENTIMENT_LABELS)

        logger.info(
            "SentimentEncoder initialized."
        )

    # ------------------------------------------------------

    def encode(self, label: str) -> int:

        return int(

            self.encoder.transform(

                [label]

            )[0]

        )

    # ------------------------------------------------------

    def decode(self, value: int) -> str:

        return str(

            self.encoder.inverse_transform(

                [value]

            )[0]

        )

    # ------------------------------------------------------

    def encode_batch(

        self,

        labels: List[str]

    ) -> List[int]:

        return list(

            self.encoder.transform(labels)

        )

    # ------------------------------------------------------

    def decode_batch(

        self,

        values: List[int]

    ) -> List[str]:

        return list(

            self.encoder.inverse_transform(values)

        )

    # ------------------------------------------------------

    def save(

        self,

        path: str | Path

    ):

        path = Path(path)

        path.parent.mkdir(

            parents=True,

            exist_ok=True

        )

        joblib.dump(

            self.encoder,

            path

        )

        logger.info(

            f"Sentiment encoder saved to {path}"

        )

    # ------------------------------------------------------

    def load(

        self,

        path: str | Path

    ):

        self.encoder = joblib.load(path)

        logger.info(

            f"Sentiment encoder loaded from {path}"

        )

    # ------------------------------------------------------

    @property

    def classes(self):

        return list(

            self.encoder.classes_

        )