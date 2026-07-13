# Backend AI Business Risk Analysis System

## Project Structure

```text
.
├── configs/                  # Configuration files for models, preprocessing, and paths
├── core/                     # Core application logic and AI/business risk modules
│   ├── ai/                   # Model inference, preprocessing, tokenization, and prediction logic
│   ├── business_risk/        # Risk aggregation, dashboard, evidence, and recommendation logic
│   └── common/               # Shared utilities, constants, exceptions, and logging
├── database/                 # Database models, repositories, migrations, and seeders
├── logs/                     # Application runtime logs
├── media/                    # Uploaded or generated media files
├── models/                   # Pretrained model artifacts and tokenizer assets
├── outputs/                  # Generated analysis outputs and logs
├── resources/                # Supporting resource files such as slang dictionaries
├── server/                   # Django backend project and app modules
│   ├── apps/                 # Authentication, analysis, reports, and user-related apps
│   └── config/               # Django settings, URLs, and WSGI/ASGI entrypoints
├── static/                   # Static web assets
├── tests/                    # Unit, integration, and business-risk test suites
├── docker-compose.yml        # Container orchestration configuration
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```
