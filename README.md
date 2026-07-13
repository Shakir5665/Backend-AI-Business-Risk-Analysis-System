# Backend AI Business Risk Analysis System

## Project Structure

```text
.
├── .env
├── .gitignore
├── docker-compose.yml
├── README.md
├── requirements.txt
├── test.py
├── configs/
│   ├── model_config.py
│   ├── model_labels.py
│   ├── paths.py
│   └── preprocessing_config.py
├── core/
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── predictor.py
│   │   ├── encoding/
│   │   │   ├── __init__.py
│   │   │   ├── aspect_encoder.py
│   │   │   └── sentiment_encoder.py
│   │   ├── inference/
│   │   │   ├── __init__.py
│   │   │   ├── inference_engine.py
│   │   │   ├── model_loader.py
│   │   │   └── prediction_formatter.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── adapter.py
│   │   │   ├── backbone.py
│   │   │   ├── business_risk_model.py
│   │   │   └── classification_heads.py
│   │   ├── preprocessing/
│   │   │   ├── __init__.py
│   │   │   ├── cleaner.py
│   │   │   ├── preprocessor.py
│   │   │   ├── repeat_normalizer.py
│   │   │   └── srilankan_normalizer.py
│   │   └── tokenization/
│   │       ├── __init__.py
│   │       └── tokenizer.py
│   ├── business_risk/
│   │   ├── __init__.py
│   │   ├── aggregation/
│   │   │   ├── __init__.py
│   │   │   ├── aggregation_result.py
│   │   │   └── statistical_aggregator.py
│   │   ├── dashboard/
│   │   ├── evidence/
│   │   ├── fuzzy/
│   │   ├── health/
│   │   └── prediction/
│   │       └── prediction_collector.py
│   ├── common/
│   │   ├── __init__.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── helpers.py
│   │   ├── logger.py
│   │   └── validators.py
│   └── scraper/
│       ├── __init__.py
│       ├── scraper.py
│       ├── collectors/
│       ├── extractors/
│       ├── normalizers/
│       ├── parsers/
│       └── validators/
├── database/
│   ├── __init__.py
│   ├── migrations/
│   ├── repositories/
│   └── seeders/
├── logs/
├── media/
├── models/
│   ├── README.md
│   └── v1/
│       ├── best_model.pt
│       ├── labels.json
│       ├── model_info.json
│       └── tokenizer/
│           ├── sentencepiece.bpe.model
│           ├── special_tokens_map.json
│           ├── tokenizer_config.json
│           └── tokenizer.json
├── outputs/
│   └── logs/
├── resources/
│   └── slang_dictionary.json
├── server/
│   ├── manage.py
│   ├── apps/
│   │   ├── analysis/
│   │   │   ├── __init__.py
│   │   │   ├── migrations/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── services.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   ├── authentication/
│   │   │   ├── __init__.py
│   │   │   ├── migrations/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── services.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   ├── reports/
│   │   │   ├── __init__.py
│   │   │   ├── migrations/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── services.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   └── users/
│   │       ├── __init__.py
│   │       ├── models.py
│   │       ├── serializers.py
│   │       ├── services.py
│   │       ├── urls.py
│   │       └── views.py
│   └── config/
│       ├── __init__.py
│       ├── asgi.py
│       ├── settings.py
│       ├── urls.py
│       └── wsgi.py
├── static/
├── tests/
│   ├── ai/
│   │   ├── agregation_test.py
│   │   ├── inference_test.py
│   │   └── prediction_collector_test.py
│   ├── api/
│   ├── business_risk/
│   ├── integration/
│   └── scraper/
└── venv/
```
