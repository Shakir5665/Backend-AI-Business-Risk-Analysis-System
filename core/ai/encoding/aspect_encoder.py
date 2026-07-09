"""
Aspect Encoder

Encodes and decodes business aspects into
multi-hot vectors for multi-label classification.

Project:
AI-Powered Business Risk Analysis
and Recommendation System
"""

from pathlib import Path
from typing import List

import joblib

from configs.model_labels import ASPECT_LABELS
from core.common.logger import logger


class AspectEncoder:
    """
    Custom multi-label encoder for business aspects.

    Aspect Order
    ------------

    quality  -> index 0
    trust    -> index 1
    delivery -> index 2

    Example
    -------

    ["quality", "delivery"]

    ↓

    [1,0,1]
    """

    def __init__(self):

        self.labels = ASPECT_LABELS

        self.label_to_index = {

            label: index

            for index, label in enumerate(self.labels)

        }

        self.index_to_label = {

            index: label

            for index, label in enumerate(self.labels)

        }

        logger.info(
            "AspectEncoder initialized."
        )

    # --------------------------------------------------

    @property
    def classes(self):

        return self.labels

    # --------------------------------------------------

    def encode(
        self,
        aspects: List[str]
    ) -> List[int]:

        vector = [

            0

            for _ in self.labels

        ]

        for aspect in aspects:

            if aspect not in self.label_to_index:

                raise ValueError(

                    f"Unknown aspect: {aspect}"

                )

            index = self.label_to_index[aspect]

            vector[index] = 1

        return vector

    # --------------------------------------------------

    def decode(
        self,
        vector: List[int]
    ) -> List[str]:

        if len(vector) != len(self.labels):

            raise ValueError(

                f"Invalid vector length."

                f" Expected {len(self.labels)},"

                f" got {len(vector)}."

            )

        decoded = []

        for index, value in enumerate(vector):

            if value == 1:

                decoded.append(

                    self.index_to_label[index]

                )

        return decoded

    # --------------------------------------------------

    def encode_batch(
        self,
        batch: List[List[str]]
    ) -> List[List[int]]:

        return [

            self.encode(aspects)

            for aspects in batch

        ]

    # --------------------------------------------------

    def decode_batch(
        self,
        batch: List[List[int]]
    ) -> List[List[str]]:

        return [

            self.decode(vector)

            for vector in batch

        ]

    # --------------------------------------------------

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

            {

                "labels": self.labels

            },

            path

        )

        logger.info(

            f"Aspect encoder saved to {path}"

        )

    # --------------------------------------------------

    def load(
        self,
        path: str | Path
    ):

        data = joblib.load(path)

        self.labels = data["labels"]

        self.label_to_index = {

            label: index

            for index, label in enumerate(self.labels)

        }

        self.index_to_label = {

            index: label

            for index, label in enumerate(self.labels)

        }

        logger.info(

            f"Aspect encoder loaded from {path}"

        )