from core.ai.predictor import Predictor
from core.business_risk.prediction.prediction_collector import PredictionCollector

predictor = Predictor()

collector = PredictionCollector()

reviews = [

    "Delivery was very late.",

    "Excellent quality product.",

    "wow Super ඕන.❤️❤️❤️❤️ such a good product.nice ඕන thnk you darazz❤️🔥🔥"

]

for review in reviews:

    prediction = predictor.predict(review)

    collector.add(prediction)

print(f"Total Predictions : {collector.size()}")

print()

for prediction in collector.get_all():

    print(prediction)

    print("-" * 80)