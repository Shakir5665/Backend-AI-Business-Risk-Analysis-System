from core.ai.inference.inference_engine import InferenceEngine

engine = InferenceEngine()

outputs = engine.predict(

    "Delivery was very late but product quality is excellent."

)

print(outputs.keys())

print(outputs["sentiment_logits"].shape)

print(outputs["aspect_logits"].shape)