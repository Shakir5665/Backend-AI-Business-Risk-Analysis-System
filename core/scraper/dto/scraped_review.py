"""
Scraped Review DTO

Represents a single customer review
scraped from an e-commerce platform.

Project:
AI-Powered Business Risk Analysis
and Recommendation System
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class ScrapedReview:
    """
    Represents one scraped customer review.
    """

    review_text: str

    rating: Optional[int] = None

    reviewer: Optional[str] = None

    review_date: Optional[str] = None