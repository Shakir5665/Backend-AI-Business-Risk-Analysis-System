from core.ai.predictor import Predictor
from core.business_risk.prediction.prediction_collector import PredictionCollector
from core.business_risk.aggregation.statistical_aggregator import StatisticalAggregator

predictor = Predictor()

collector = PredictionCollector()

reviews = [

    "Delivery was very late.",

    "Excellent quality product.",

    "Highly recommended seller."

]

for review in reviews:

    collector.add(
        predictor.predict(review)
    )

aggregator = StatisticalAggregator()

result = aggregator.aggregate(
    collector.get_all()
)

print(result)