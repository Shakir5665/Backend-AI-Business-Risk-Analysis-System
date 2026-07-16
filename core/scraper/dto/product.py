"""
Product DTO

Represents a scraped product together
with its customer reviews.

Project:
AI-Powered Business Risk Analysis
and Recommendation System
"""

from dataclasses import dataclass, field
from typing import Optional

from core.scraper.dto.scraped_review import ScrapedReview


@dataclass(slots=True)
class Product:
    """
    Represents one product and its reviews.
    """

    product_id: str

    product_name: str

    product_url: str

    category: Optional[str] = None

    reviews: list[ScrapedReview] = field(default_factory=list)