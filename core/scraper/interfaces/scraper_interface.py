"""
Scraper Interface

Defines the contract for all
product scraper implementations.

Project:
AI-Powered Business Risk Analysis
and Recommendation System
"""

from abc import ABC, abstractmethod

from core.scraper.dto.product import Product


class ScraperInterface(ABC):
    """
    Contract for all product scrapers.
    """

    @abstractmethod
    def scrape_product(
        self,
        product_url: str
    ) -> Product:
        """
        Scrape a product and return its
        metadata together with customer reviews.

        Args:
            product_url: Product page URL.

        Returns:
            Product DTO.
        """
        raise NotImplementedError