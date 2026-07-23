from core.analysis.dto.product_analysis_result import ProductAnalysisResult
from core.scraper.engines.scraper_engine import ScraperEngine
from core.ai.pipeline import ReviewPredictionPipeline
from core.business_risk.prediction.prediction_collector import PredictionCollector
from core.scraper.dto.product import Product

from core.business_risk.aggregation.statistical_aggregator import (
    StatisticalAggregator
)


class ProductAnalysisEngine:
    """
    Coordinates the complete product analysis workflow.
    """

    def __init__(self):

        self._scraper = ScraperEngine()
        self._pipeline = ReviewPredictionPipeline()
        self._collector = PredictionCollector()
        self._aggregator = StatisticalAggregator()

    
    def analyze(self, product_url: str):


        product = self._scraper.scrape_product(
            product_url
        )

    
        predictions = self._pipeline.predict_reviews(
            product.reviews
        )

        
        self._collector.clear()
        

        self._collector.add_many(
            predictions
        )

        aggregation_result = self._aggregator.aggregate(
             self._collector.get_all()
        )

        return ProductAnalysisResult(
            product=product,
            aggregation_result=aggregation_result
        )
    