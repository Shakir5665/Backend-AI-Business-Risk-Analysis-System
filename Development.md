# Development Report

**AI-Powered Business Risk Analysis and Recommendation System**

---

> **Author:** Shakir | **Project:** Backend AI Business Risk Analysis System
> **Document Type:** Development Documentation Report
> **Section:** 2.4 — System Development, Components, and Integration
> **Version:** 1.0 | **Date:** September 2026

---
 
## Abstract

This document provides a comprehensive development report for the AI-Powered Business Risk Analysis and Recommendation System. It covers the complete lifecycle of software development across nine subsystems: the overall system architecture, the Daraz web scraping engine, multilingual text preprocessing, the multi-task XLM-RoBERTa NLP model, the Fuzzy Logic risk analysis engine, the Business Risk Index (BRI) calculation engine, the knowledge-base-driven recommendation engine, the FastAPI backend and REST API integration, and the dashboard frontend integration. Each subsection describes the technical implementation approach, key design decisions, components developed, and integration points between subsystems.

---

## Table of Contents

1. [2.4.1 System Development](#241-system-development)
2. [2.4.2 Web Scraping](#242-web-scraping)
3. [2.4.3 Multilingual Preprocessing](#243-multilingual-preprocessing)
4. [2.4.4 NLP Model](#244-nlp-model)
5. [2.4.5 Risk Analysis Engine](#245-risk-analysis-engine)
6. [2.4.6 BRI Engine](#246-bri-engine)
7. [2.4.7 Recommendation Engine](#247-recommendation-engine)
8. [2.4.8 Backend/API Integration](#248-backendapi-integration)
9. [2.4.9 Dashboard Integration](#249-dashboard-integration)

---

## 2.4.1 System Development

### Overview

The system was developed as a full-stack, production-ready backend application using a **modular, layered architecture**. The design separates concerns across distinct components that can be developed, tested, and replaced independently. The technology stack is centered around Python as the primary language, with FastAPI as the web framework and PyTorch as the deep learning runtime.

### Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Web Framework | FastAPI + Uvicorn | 0.104+ |
| Deep Learning | PyTorch + Transformers (HuggingFace) | 2.x |
| Fuzzy Inference | scikit-fuzzy + NumPy | 0.4.x |
| Database ORM | SQLAlchemy | 2.x |
| Database | PostgreSQL 15 / SQLite (dev) | 15 |
| Schema Migration | Alembic | 1.x |
| Web Scraping | Selenium + ChromeDriver | 4.x |
| Data Validation | Pydantic v2 | 2.x |
| Authentication | PyJWT + bcrypt | Latest |
| SMTP Email | smtplib + MIMEText | stdlib |
| Configuration | pydantic-settings | 2.x |

### System Architecture

The overall system is structured into three major tiers:

```
+----------------------------------------------------------+
|   PRESENTATION TIER                                      |
|   FastAPI REST API (/api/v1/*)                           |
|   Static Dashboard SPA (/static/*)                       |
+-----------------------------+----------------------------+
                              |
+-----------------------------v----------------------------+
|   APPLICATION TIER                                       |
|   AnalysisService   AuthService   HealthService          |
|   AnalysisMapper    Repositories  Middleware             |
+---+------------------+------------------+---------------+
    |                  |                  |
+---v-------+  +-------v-------+  +------v---------+
| SCRAPING  |  |  AI PIPELINE  |  | RISK & RECO.   |
| Selenium  |  |  Preprocessing|  | Fuzzy FIS      |
| Scraper   |  |  XLM-RoBERTa  |  | Rule Engine    |
| Engine    |  |  Inference    |  | Reco. Engine   |
+-----------+  +---------------+  +----------------+
    |                  |                  |
+---v------------------v------------------v--------------+
|   DATA TIER                                            |
|   PostgreSQL 15: users, products, analyses, reviews    |
+--------------------------------------------------------+
```

**Figure 1.** Three-tier system architecture diagram.

### Project Directory Structure

```
Backend-AI-Business-Risk-Analysis-System/
├── app/                        # FastAPI Application Layer
│   ├── api/                    # Routes, Schemas, Dependencies
│   ├── config/                 # Settings & environment config
│   ├── database/               # Session management, Base entity
│   ├── models/                 # SQLAlchemy ORM models
│   ├── repositories/           # Data access layer
│   ├── security/               # JWT + bcrypt
│   ├── services/               # Business logic services
│   ├── middleware/             # Request ID + Logging middleware
│   ├── startup.py              # AI engine startup sequence
│   └── main.py                 # FastAPI app entry point
│
├── core/                       # Core AI & Business Logic Modules
│   ├── scraper/                # Selenium web scraping engine
│   ├── ai/                     # Preprocessing + NLP model + inference
│   │   ├── preprocessing/      # Text cleaning, normalization
│   │   ├── models/             # XLM-R + Adapters + Classification heads
│   │   ├── inference/          # InferenceEngine, PredictionFormatter
│   │   └── pipeline/           # End-to-end AI pipeline
│   ├── business_risk/          # Fuzzy FIS + Business Rule Engine
│   │   ├── fuzzy/              # Mamdani FIS instances
│   │   ├── calculator/         # BusinessRiskCalculator + rules
│   │   ├── aggregation/        # StatisticalAggregator
│   │   └── models/             # AspectRisk, BusinessRiskResult
│   ├── recommendation/         # Recommendation engine
│   │   ├── knowledge/          # Knowledge base + JSON rules
│   │   ├── engine/             # RecommendationEngine
│   │   └── interpreter/        # RiskInterpreter
│   └── analysis/               # ProductAnalysisEngine orchestrator
│
├── configs/                    # Global configuration constants
│   ├── model_config.py         # XLM-R parameters
│   ├── model_labels.py         # ASPECT_LABELS, SENTIMENT_LABELS
│   └── preprocessing_config.py # Cleaner flags & patterns
│
├── database/                   # Alembic migrations
├── resources/                  # slang_dictionary.json
├── static/                     # Dashboard SPA (HTML/CSS/JS)
└── models/                     # Pretrained checkpoint files
```

### Startup Sequence

The system follows a deterministic startup sequence on application launch:

```
1. FastAPI Lifespan Context Manager starts
2. startup_ai_engine() executes:
   a. Base.metadata.create_all() -> creates missing DB tables
   b. ensure_schema_migrations() -> additive column migration
   c. ProductAnalysisEngine instantiated (loads XLM-R)
   d. app_state.set_ai_healthy(engine) -> marks system READY
   e. resume_scraped_jobs() -> restarts any incomplete analyses
3. FastAPI begins accepting HTTP requests
```

If any step fails, `app_state.set_ai_unhealthy(error_msg)` is called and the `/api/v1/health` endpoint reflects the degraded state, enabling liveness probe integration.

---

## 2.4.2 Web Scraping

### Overview

The web scraping subsystem is responsible for extracting product metadata and customer review texts from the **Daraz e-commerce platform** (the primary platform in Sri Lanka and South Asia). It is implemented as a Selenium-based automated browser system (`ScraperEngine`) capable of both supervised CLI mode and fully automated API-driven headless mode.

### Implementation

**Module:** `core/scraper/engines/scraper_engine.py`

The `ScraperEngine` class (948 lines) implements the `ScraperInterface` contract and handles the full scraping lifecycle:

```python
class ScraperEngine(ScraperInterface):
    def __init__(self, job_state=None, auto_start: bool = True):
        self._driver = None          # Chrome WebDriver (lazy init)
        self.job_state = job_state   # API job state reference
        self.auto_start = auto_start # Headless vs. manual mode
```

### Browser Automation Strategy

Chrome is launched with a carefully crafted set of anti-detection options:

```python
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--user-agent=Mozilla/5.0 Chrome/120.0.0.0")
driver.execute_script(
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
)
```

These options suppress `navigator.webdriver = true` fingerprinting, masquerade as a legitimate Chrome 120 browser, and disable automation telemetry, collectively defeating most bot detection systems employed by Daraz.

### Progressive Lazy-Load Scroll

Daraz renders review sections using JavaScript-driven lazy loading. The scraper implements `_progressive_scroll_to_content()` which:

1. Scrolls the page in 700px increments with 1.0-second intervals
2. After each scroll, polls 10 CSS selectors targeting review containers: `#module_product_review`, `.pdp-mod-review`, `.pdp-review-summary`, `.mod-reviews`, `.pdp-review-item`, `.review-item`, `.review-content`, `.item-content`, `.next-pagination`, `.pagination`
3. On detection, `scrollIntoView({behavior: 'smooth', block: 'center'})` brings the container into viewport
4. Falls back gracefully with a warning if no container detected after `max_scrolls` iterations

### Pagination Handling

The scraper implements robust multi-page review traversal using Daraz's pagination structure:
- Detects "Next" pagination buttons via CSS selectors
- Tracks page number synchronization to detect stale pagination state
- Handles `StaleElementReferenceException` with retry logic
- Supports **graceful stop**: both API-triggered (`job_state.stop_requested`) and keyboard-triggered (Q key press or `msvcrt.getch()`)

### Real-Time CSV Persistence

Reviews are written to a timestamped CSV file in real-time during scraping:

```python
def _init_csv(self):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    self.csv_filename = f"product_reviews_{timestamp}.csv"

def _save_review_to_csv(self, review_text: str, index: int):
    with open(self.csv_filename, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([index, review_text])
```

Real-time CSV writing ensures no review data is lost if the scraper is interrupted mid-session.

### Data Transfer Objects

```python
# core/scraper/dto/product.py
@dataclass
class Product:
    title: str
    seller: str
    rating: float
    total_reviews: int
    category: str
    image_url: str
    external_product_id: str
    current_price: str

# core/scraper/dto/scraped_review.py
@dataclass
class ScrapedReview:
    text: str
    index: int
```

### Dual Operation Modes

| Mode | Trigger | Browser | User Interaction |
|------|---------|---------|-----------------|
| **API Mode** | `job_state != None` | Headless | None — fully automated |
| **CLI Mode** | `job_state == None` | Headful | Manual star filter selection, `start`/`quit` commands |

---

## 2.4.3 Multilingual Preprocessing

### Overview

Customer reviews on Daraz (Sri Lanka) exhibit significant linguistic diversity: English, Sinhala (Romanized), Tamil (Romanized), code-mixed English-Sinhala, and emoji-heavy informal text. The preprocessing pipeline is designed to normalize this heterogeneous input into clean, model-ready text while preserving linguistic signals important for sentiment and aspect classification.

The pipeline is composed of three sequential stages, all orchestrated by `ReviewPreprocessor`.

### Pipeline Architecture

```
Raw Review Text
      |
      v
+----------------+
|  TextCleaner   |  Stage 1: Structural cleaning
+----------------+
      |
      v
+-------------------+
|  RepeatNormalizer |  Stage 2: Expressive character reduction
+-------------------+
      |
      v
+---------------------+
|  SriLankanNormalizer|  Stage 3: Domain slang normalization
+---------------------+
      |
      v
Clean Preprocessed Text
```

### Stage 1: TextCleaner

**Module:** `core/ai/preprocessing/cleaner.py`

`TextCleaner` performs 12 distinct cleaning operations, each independently configurable via `configs/preprocessing_config.py` flags:

| Operation | Config Flag | Effect |
|-----------|------------|--------|
| Unicode normalization | `NORMALIZE_UNICODE` | `unicodedata.normalize("NFC", text)` — canonical form |
| HTML entity decode | Always on | `html.unescape(text)` |
| Lowercasing | `LOWERCASE` | Case normalization for vocabulary consistency |
| HTML tag removal | `REMOVE_HTML` | Strip `<b>`, `<br>`, `<span>` etc. from scraped text |
| URL removal | `REMOVE_URLS` | Remove `http://...` and `www...` links |
| Email removal | `REMOVE_EMAILS` | Remove embedded email addresses |
| Mention removal | `REMOVE_MENTIONS` | Remove `@username` references |
| Hashtag normalization | `NORMALIZE_HASHTAGS` | `#delivery` becomes `delivery` |
| Control character removal | `REMOVE_CONTROL_CHARACTERS` | Strip non-printable chars |
| Punctuation normalization | Always on | `...` becomes `.`, `!!!` becomes `!` |
| Whitespace normalization | `REMOVE_EXTRA_WHITESPACE` | Collapse multiple spaces to single |
| Dataset-specific cleaning | `REMOVE_BACKSLASHES`, etc. | Strip training dataset artifacts |

### Stage 2: RepeatNormalizer

**Module:** `core/ai/preprocessing/repeat_normalizer.py`

Handles informal expressive writing where characters are repeated for emphasis, a common pattern in Sri Lankan colloquial text:

```python
self.pattern = re.compile(r"(.)\1{2,}")  # Match any char repeated 3+ times

# Examples:
# "goooood"    -> "good"
# "niyaaaamai" -> "niyamai"   (Sinhala: "great")
# "brooooo"    -> "bro"
# "suuuuper"   -> "suuper"
```

The `MAX_REPEATED_CHARACTERS` constant controls the preserved repetition ceiling (defaulting to 2). This preserves intentional 2-character repetition while eliminating extreme exaggerations.

### Stage 3: SriLankanNormalizer

**Module:** `core/ai/preprocessing/srilankan_normalizer.py`

This normalizer addresses the core linguistic challenge of the domain: **Romanized Sinhala slang and colloquial expressions** that are not present in standard NLP vocabularies.

The normalizer loads a custom `slang_dictionary.json` from `resources/`, which maps standard words to a list of Sri Lankan variations:

```json
{
  "good": ["niyamai", "niyame", "niyama", "hodai", "hoda"],
  "bad": ["naraka", "narakui", "baadu"],
  "fast": ["wega", "wegi", "issara"],
  "delivery": ["deliver", "deliv", "deliveri"]
}
```

The normalizer builds a reverse lookup map at initialization:

```
"niyamai" --> "good"
"hodai"   --> "good"
"naraka"  --> "bad"
```

During normalization, each word is looked up in the map (case-insensitive), with punctuation prefix/suffix preserved. This normalization dramatically improves the XLM-R model's ability to recognize sentiment polarity in Romanized Sinhala reviews.

### ReviewPreprocessor: Unified Pipeline

```python
class ReviewPreprocessor:
    def preprocess(self, text: str) -> str:
        text = self.cleaner.clean(text)       # Stage 1
        text = self.repeat.normalize(text)    # Stage 2
        text = self.srilankan.normalize(text) # Stage 3
        return text.strip()
```

Both single-text (`preprocess()`) and batch (`preprocess_batch()`) modes are supported for efficient bulk processing.

---

## 2.4.4 NLP Model

### Overview

The NLP model is the core intelligence of the system: a **multi-task, fine-tuned XLM-RoBERTa-base** model that simultaneously classifies review sentiment (3-class) and detects business risk aspects (multi-label). The model employs **Bottleneck Adapters** for parameter-efficient fine-tuning, allowing task-specific learning without full retraining of the 270M-parameter XLM-R backbone.

### Model Architecture

**Module:** `core/ai/models/business_risk_model.py`

```
Input (tokenized review text)
      |
      v
XLMRBackbone (FacebookAI/xlm-roberta-base, 270M params, FROZEN)
      |
      v
CLS Token Embedding [batch_size, 768]
      |
  +---+----------------+
  |                    |
  v                    v
SentimentAdapter    AspectAdapter
(Bottleneck)        (Bottleneck)
  |                    |
  v                    v
SentimentHead       AspectHead
  |                    |
  v                    v
Sentiment Logits    Aspect Logits
[batch_size, 3]     [batch_size, N_aspects]
```

**Figure 2.** BusinessRiskModel multi-task architecture.

### XLM-RoBERTa Backbone

**Module:** `core/ai/models/backbone.py`

```python
class XLMRBackbone(nn.Module):
    def __init__(self):
        self.backbone = AutoModel.from_pretrained("FacebookAI/xlm-roberta-base")
        if FREEZE_BACKBONE:
            for parameter in self.backbone.parameters():
                parameter.requires_grad = False

    def forward(self, input_ids, attention_mask) -> torch.Tensor:
        outputs = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
        return outputs.last_hidden_state[:, 0, :]  # CLS embedding
```

| Configuration | Value |
|--------------|-------|
| `MODEL_NAME` | `"FacebookAI/xlm-roberta-base"` |
| `HIDDEN_SIZE` | `768` |
| `MAX_SEQUENCE_LENGTH` | `512` tokens |
| `FREEZE_BACKBONE` | `True` (all 270M params frozen) |
| `INFERENCE_BATCH_SIZE` | `64` |

The backbone is **fully frozen** during inference — only adapter and head parameters are active. This reduces GPU memory requirements and eliminates catastrophic forgetting risk while preserving XLM-R's multilingual capabilities across 100 languages, critically including English, Sinhala script representation, and Tamil.

The CLS token embedding (`outputs.last_hidden_state[:, 0, :]`) provides a sentence-level contextual representation of the input review, leveraging XLM-R's cross-lingual alignment for effective Romanized Sinhala processing.

### Bottleneck Adapter

**Module:** `core/ai/models/adapter.py`

```
Input (768)
    |
    v
Linear: 768 -> 128     (down-projection, compression ratio 6:1)
    |
    v
ReLU
    |
    v
Dropout (p=0.1)
    |
    v
Linear: 128 -> 768     (up-projection, restores original dimensionality)
    |
    v
+ residual connection  (x + adapter_output, preserves pre-adapter features)
    |
    v
Output (768)
```

| Configuration | Value |
|--------------|-------|
| `ADAPTER_DIM` | `128` |
| `ADAPTER_DROPOUT` | `0.1` |
| Trainable params per adapter | ~197,376 (`768x128 + 128 + 128x768 + 768`) |

Two separate adapter instances are instantiated: `sentiment_adapter` and `aspect_adapter`, providing task-specific feature transformations while sharing the same frozen XLM-R backbone. The residual connection ensures gradient stability during fine-tuning by preserving the original CLS representation.

### Sentiment Classification Head

**Module:** `core/ai/models/classification_heads.py`

```
Adapter Output (768)
      |
  Dropout (p=0.1)
      |
  Linear: 768 -> 256
      |
    ReLU
      |
  Dropout (p=0.1)
      |
  Linear: 256 -> 3
      |
  Sentiment Logits [batch, 3]
```

Output classes: `{positive, negative, neutral}` (3 classes, `NUM_SENTIMENT_CLASSES = 3`)

### Aspect Detection Head

```
Adapter Output (768)
      |
  Dropout (p=0.1)
      |
  Linear: 768 -> 256
      |
    ReLU
      |
  Dropout (p=0.1)
      |
  Linear: 256 -> N_aspects
      |
  Aspect Logits [batch, N_aspects]
```

Output: Multi-label classification. Logits are passed through `sigmoid()` during inference to produce independent probability scores per aspect. Aspects are defined in `configs/model_labels.py` (`ASPECT_LABELS`): currently **3 aspects** — `quality`, `delivery`, `trust`.

### Inference Pipeline

**Module:** `core/ai/inference/inference_engine.py`

The `InferenceEngine` handles batched prediction:

1. Tokenize preprocessed texts using XLM-R tokenizer (`max_length=512`, padding, truncation)
2. Run forward pass in `torch.no_grad()` context (inference mode, no gradient computation)
3. Apply `softmax()` to sentiment logits to get sentiment probabilities
4. Apply `sigmoid()` to aspect logits to get independent per-aspect probabilities
5. Select predicted sentiment class via `argmax()`
6. Threshold aspect probabilities at `0.5` for binary aspect detection
7. Compute prediction confidence as `max(sentiment_probabilities)`

Inference runs in batches of `INFERENCE_BATCH_SIZE = 64` reviews, balancing GPU utilization against memory constraints.

---

## 2.4.5 Risk Analysis Engine

### Overview

The Risk Analysis Engine translates raw AI predictions (sentiment + aspect probabilities from the NLP model) into structured, quantifiable business risk scores using a **Mamdani Fuzzy Inference System (FIS)**. This is the core of Research Component 2 documented separately; this section covers the development implementation perspective.

### Development Components

**Module:** `core/business_risk/`

The engine was developed as a cleanly separated module with four sub-packages:

```
core/business_risk/
├── aggregation/     # Statistical signal extraction from predictions
├── fuzzy/           # Mamdani FIS implementation
├── calculator/      # Business Rule Engine and BRI computation
└── models/          # Immutable domain data models
```

### Statistical Aggregation Development

`StatisticalAggregator` was developed to convert `List[Dict]` raw predictions into the normalized numerical signals required by the FIS:

- **`mention_ratio`**: Developed as a prevalence signal — the proportion of reviews mentioning each aspect. Ranges [0.0, 1.0], naturally bounded for FIS input.
- **`average_negative_strength`**: A graded severity metric that accumulates sigmoid probabilities exclusively from negatively-classified reviews. Rather than binary mention detection, this metric leverages the full continuous output of the neural model.
- **`low_confidence_ratio`**: A reliability metric tracking predictions below `LOW_CONFIDENCE_THRESHOLD = 0.60`.

### FIS Development

Three independent FIS instances were developed using `scikit-fuzzy`'s control system API:

```python
# Example: DeliveryFIS initialization
delivery_ctrl = ctrl.ControlSystem(rules=build_delivery_rules())
self.simulation = ctrl.ControlSystemSimulation(delivery_ctrl)
```

Each FIS was developed with:
- **Input variables**: `mention_ratio [0,1]` and `average_negative_strength [0,1]`, each with 3 membership functions (LOW/MEDIUM/HIGH)
- **Output variable**: `risk_score [0,100]`, with 5 membership functions (VERY_LOW/LOW/MEDIUM/HIGH/CRITICAL)
- **Rule base**: 9 rules (3x3 Cartesian product) — complete coverage with no dead zones
- **Defuzzification**: Centroid (Center of Area) method

The `BaseFIS` abstract class was developed to enforce a common `evaluate(**inputs) -> AspectRisk` contract across all three FIS instances, with concrete implementations (`QualityFIS`, `DeliveryFIS`, `TrustFIS`) providing aspect-specific variable namespacing via `input_mapping`.

### Risk Score to Level Mapping

```python
@staticmethod
def determine_level(score: float) -> RiskLevel:
    if score < 20:   return RiskLevel.VERY_LOW
    elif score < 40: return RiskLevel.LOW
    elif score < 60: return RiskLevel.MEDIUM
    elif score < 80: return RiskLevel.HIGH
    return RiskLevel.CRITICAL
```

---

## 2.4.6 BRI Engine

### Overview

The **Business Risk Index (BRI) Engine** synthesizes the three individual aspect risk scores (Quality, Delivery, Trust) from the FIS into a single composite business risk classification using a two-phase computation: maximum-based baseline scoring followed by tiered business rule adjudication.

### Baseline Computation Development

**Module:** `core/business_risk/calculator/utils.py`

```python
def calculate_baseline_score(quality, delivery, trust) -> float:
    return max(quality.score, delivery.score, trust.score)

def determine_baseline_level(quality, delivery, trust) -> RiskLevel:
    return max((quality, delivery, trust), key=lambda a: a.score).level
```

The maximum-based approach was selected after evaluating three alternatives:

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| Maximum | Captures worst-case failure | May overstate risk in mixed scenarios | **Selected** |
| Arithmetic Mean | Balanced representation | Masks critical single-aspect failures | Rejected |
| Weighted Average | Domain-tunable | Requires empirical weight validation | Deferred to future work |

### Business Rule Engine Development

**Module:** `core/business_risk/calculator/rules/`

The rule engine was developed using the **Strategy + Registry** pattern. Seven rules across three tiers were implemented:

**Tier 1 — Domain Override Rules (3 rules):**

| Rule Class | Trigger | Override Level |
|-----------|---------|---------------|
| `TrustCriticalRule` | Trust=CRITICAL + others below HIGH | CRITICAL |
| `QualityCriticalRule` | Quality=CRITICAL + others below HIGH | HIGH |
| `DeliveryCriticalRule` | Delivery=CRITICAL + others below HIGH | HIGH |

**Tier 2 — Escalation Rules (1 rule):**

| Rule Class | Trigger | Override Level |
|-----------|---------|---------------|
| `MultipleHighRiskRule` | 2 or more aspects at HIGH/CRITICAL | CRITICAL |

**Tier 3 — Consistency Rules (3 rules):**

| Rule Class | Trigger | Override Level |
|-----------|---------|---------------|
| `AllVeryLowRule` | All three = VERY_LOW | VERY_LOW |
| `AllLowRule` | All three = LOW | LOW |
| `AllMediumRule` | All three = MEDIUM | MEDIUM |

The execution policy is **first-match, priority-ordered** — rules are evaluated sequentially from Tier 1 to Tier 3, stopping at the first match:

```python
final_level = baseline_level
for rule in RULES:       # Ordered: T1 rules -> T2 rules -> T3 rules
    if rule.matches(context):
        final_level = rule.apply(context)
        break
```

All rules operate on a `frozen=True` `RuleContext` dataclass, ensuring referential transparency and preventing mutation during evaluation.

### BRI Output

The `BusinessRiskCalculator` produces a `BusinessRiskResult`:

```python
@dataclass
class BusinessRiskResult:
    quality:              AspectRisk      # FIS output for quality
    delivery:             AspectRisk      # FIS output for delivery
    trust:                AspectRisk      # FIS output for trust
    business_risk_index:  float           # max(quality, delivery, trust) score
    business_risk_level:  RiskLevel       # Rule-adjudicated final level
    recommendations:      list            # Populated by Recommendation Engine
```

The continuous `business_risk_index` (0-100) is stored in the database as a directly sortable `FLOAT` column, while `business_risk_level` is stored as an indexed `VARCHAR` for categorical filtering.

---

## 2.4.7 Recommendation Engine

### Overview

The Recommendation Engine translates the `BusinessRiskResult` into actionable, human-readable business recommendations. It follows a fully modular, dependency-injected 4-stage pipeline that separates context interpretation, action selection, report building, and response formatting.

### Architecture

**Module:** `core/recommendation/engine/recommendation_engine.py`

```
BusinessRiskResult
      |
      v
[Stage 1] RiskInterpreter.interpret()
      |   -> RecommendationContext
      v
[Stage 2] ActionSelector.select(context)
      |   -> SelectionResult (matched rules from Knowledge Base)
      v
[Stage 3] ReportBuilder.build(selection_result)
      |   -> RecommendationReport (structured, deduplicated)
      v
[Stage 4] ResponseFormatter.format(report, start_time)
      |   -> RecommendationResult (final output)
      v
RecommendationResult
```

### Knowledge Base Development

**Module:** `core/recommendation/knowledge/`

The knowledge base is a JSON-driven rule catalog (`knowledge/data/`) providing aspect-level, risk-level-specific recommendations. It is composed of five sub-components developed independently:

| Component | Class | Responsibility |
|-----------|-------|---------------|
| `KnowledgeLoader` | `loader.py` | Reads and parses all JSON rule files from `data/` directory |
| `KnowledgeValidator` | `validator.py` | Schema validation of loaded rules |
| `KnowledgeRepository` | `repository.py` | Multi-index storage for fast rule lookup |
| `RecommendationKnowledgeBase` | `knowledge_base.py` | Facade combining Loader + Validator + Repository |
| `KnowledgeLoader` | `knowledge_loader.py` | Application-level singleton loader |

Each recommendation rule has the following structure:

```json
{
  "id": "QUAL_HIGH_001",
  "aspect": "QUALITY",
  "risk_level": "HIGH",
  "priority": "HIGH",
  "tags": ["quality_control", "inspection"],
  "recommendation": "Implement a rigorous pre-shipment quality inspection process..."
}
```

**`RecommendationKnowledgeBase` query interface:**

```python
kb.get_rules(aspect="QUALITY", risk_level="HIGH")    # Aspect-specific rules
kb.get_general_rules(risk_level="CRITICAL")           # Cross-aspect rules
kb.get_rule_by_id("QUAL_HIGH_001")                    # Direct ID lookup
kb.get_all_rules()                                    # Full catalog
```

The knowledge base is **lazily initialized** and protected by an `_ensure_initialized()` guard, preventing accidental query before the data directory is loaded.

### RiskInterpreter

**Module:** `core/recommendation/interpreter/risk_interpreter.py`

Converts a `BusinessRiskResult` into a `RecommendationContext`: a structured object that identifies which aspects require recommendations based on their risk levels and what the dominant overall risk scenario is.

### ActionSelector

**Module:** `core/recommendation/selector/`

Queries the `RecommendationKnowledgeBase` with the aspect and risk level from the context, selecting applicable recommendation rules and assembling a `SelectionResult`.

### ReportBuilder

**Module:** `core/recommendation/report/`

Structures and deduplicates the selected recommendation rules into a `RecommendationReport`, ordering recommendations by priority and removing duplicates that match across multiple aspects.

### ResponseFormatter

**Module:** `core/recommendation/formatter/`

Converts the `RecommendationReport` into the final `RecommendationResult` DTO and computes the `execution_time_ms` metric from `start_time`.

### Stateless and Thread-Safe Design

The `RecommendationEngine` is **stateless** — all inputs pass through the 4-stage pipeline without storing any per-request state on the class instance. This makes it inherently thread-safe for concurrent multi-tenant analysis executions without locks.

---

## 2.4.8 Backend/API Integration

### Overview

The backend is implemented as a **FastAPI** application (`app/main.py`) with a structured router hierarchy, global exception handling, custom middleware, dependency injection, and OpenAPI documentation. It serves as the integration layer connecting the AI/business logic core to the external world.

### FastAPI Application Configuration

```python
app = FastAPI(
    title="AI Business Risk Analysis System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)
```

### API Router Hierarchy

All API routes are organized under `/api/v1/` prefix with distinct tags:

```
/api/v1/
├── auth/
│   ├── POST /register          # User registration -> JWT
│   ├── POST /login             # Authentication -> JWT
│   ├── POST /forgot-password   # OTP dispatch via email
│   └── POST /reset-password    # OTP verify + password reset
│
├── analysis/
│   ├── POST /check-product     # Step 1: URL validation + product preview
│   ├── POST /start             # Step 2: Start background analysis job
│   ├── POST /stop              # Step 3: Graceful stop scraping
│   ├── GET  /status/{id}       # Step 4: Poll job status
│   └── GET  /result/{id}       # Step 5: Retrieve completed result
│
├── history/
│   ├── GET  /                  # Paginated analysis history
│   ├── GET  /{id}              # Analysis detail with reviews
│   └── DELETE /{id}            # Delete analysis record
│
├── products/
│   ├── GET  /                  # Paginated monitored products
│   └── GET  /{id}/analyses     # All analyses for a product
│
├── profile/
│   └── GET  /me                # Current user profile
│
└── health/
    └── GET  /health            # System + AI + DB health check
```

### Guided 5-Step Analysis Workflow

The analysis API implements a **guided multi-step job workflow**, enabling the frontend dashboard to display real-time progress:

```
Step 1: POST /check-product   -> Product preview (title, image, rating, reviews)
Step 2: POST /start           -> Job ID issued, scraping begins in background thread
Step 3: POST /stop            -> Graceful stop requested (optional)
Step 4: GET  /status/{id}     -> Poll: "scraping", "processing", "completed", "failed"
Step 5: GET  /result/{id}     -> Full BusinessRiskResult + RecommendationResult
```

### Standardized API Response Envelope

All API endpoints return responses conforming to a unified `ApiResponse[T]` schema:

```json
{
  "success": true,
  "message": "Analysis completed successfully.",
  "data": {},
  "meta": {
    "requestId": "req-abc-123",
    "timestamp": "2026-09-08T15:00:00Z",
    "version": "1.0.0"
  }
}
```

### Middleware Stack

Three middleware layers are applied in order:

| Middleware | Module | Function |
|-----------|--------|----------|
| `RequestIDMiddleware` | `app/middleware/request_id_middleware.py` | Generates UUID `X-Request-ID` header per request for traceability |
| `LoggingMiddleware` | `app/middleware/logging_middleware.py` | Logs request method, path, status code, and duration |
| `CORSMiddleware` | FastAPI built-in | CORS headers for frontend origins (`localhost:3000`, `localhost:5173`) |

### Global Exception Handling

```python
app.add_exception_handler(BaseBusinessException, business_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
```

All exceptions are caught and converted to structured JSON error responses with consistent `success: false` envelopes.

### Dependency Injection

FastAPI's `Depends()` system is used throughout for session and service provisioning:

```python
@router.post("/start")
async def start_analysis(
    body: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
):
```

`get_current_user` decodes the JWT bearer token, resolves the user UUID, and fetches the `User` record from the database, enforcing authentication on every protected endpoint.

`get_analysis_service` provisions a fresh `AnalysisService` instance with a bound `Session`, `ProductRepository`, `AnalysisRepository`, and `ReviewRepository` for the lifetime of the current request.

### Background Job Execution

Analysis jobs are run in a background thread via Python's `asyncio.to_thread()`:

```python
asyncio.create_task(
    asyncio.to_thread(service._run_full_analysis_job, job_id, product_url, user_id)
)
```

The background job:
1. Runs the Selenium scraper (blocking I/O, off main event loop)
2. Preprocesses collected reviews
3. Runs inference batch through XLM-R
4. Aggregates statistics
5. Computes FIS risk scores
6. Runs business rule engine
7. Generates recommendations
8. Persists `Analysis` + `Review` records to database
9. Updates `JobState` to `completed` or `failed`

### OpenAPI Documentation

FastAPI automatically generates interactive Swagger UI (`/docs`) and ReDoc (`/redoc`) documentation from route decorators, Pydantic schemas, and docstrings, enabling easy API testing and frontend integration without manual documentation effort.

---

## 2.4.9 Dashboard Integration

### Overview

The system ships with an integrated **Single-Page Application (SPA) dashboard** served directly by FastAPI's static file server. This eliminates the need for a separate frontend hosting infrastructure and enables a fully self-contained deployable artifact.

### Static File Serving

```python
# app/main.py
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/static/index.html")
```

The root URL (`/`) automatically redirects to the dashboard SPA at `/static/index.html`. The entire `static/` directory is served under the `/static/` prefix.

### Cache Control

Static files are served with aggressive no-cache headers to ensure the dashboard always reflects the latest deployed version:

```python
@app.middleware("http")
async def add_no_cache_header(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static") or request.url.path == "/":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response
```

### CORS Configuration

The API allows cross-origin requests from configured frontend origins, enabling the dashboard to be hosted separately during development:

```python
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",   # React/Next.js dev server
    "http://localhost:5173",   # Vite dev server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]
```

### Dashboard API Integration Points

The dashboard integrates with the backend through the following primary API flows:

**Authentication Flow:**
```
Dashboard --> POST /api/v1/auth/register --> Backend --> JWT Token --> localStorage
Dashboard --> POST /api/v1/auth/login    --> Backend --> JWT Token --> localStorage
```

**Analysis Flow:**
```
Dashboard --> POST /check-product --> Show product preview card
          --> POST /start         --> Receive job_id, show progress spinner
          --> GET  /status/{id}   --> Poll every 3s, update progress bar
          --> GET  /result/{id}   --> Render BRI gauge, aspect cards, recommendations
```

**History Flow:**
```
Dashboard --> GET /api/v1/history?page=1&limit=10&risk_level=HIGH --> History table
          --> GET /api/v1/history/{id}                            --> Analysis detail
          --> DELETE /api/v1/history/{id}                         --> Remove from table
```

**Products Flow:**
```
Dashboard --> GET /api/v1/products?page=1           --> Monitored product cards
          --> GET /api/v1/products/{id}/analyses    --> Product analysis list
```

### Risk Dashboard Display Data

The frontend dashboard renders the following data from the completed analysis result:

| Dashboard Element | Data Source | API Field |
|------------------|------------|-----------|
| Business Risk Index gauge | `business_risk_index` | `0-100` float |
| Risk Level badge | `business_risk_level` | `VERY_LOW / LOW / MEDIUM / HIGH / CRITICAL` |
| Quality Risk card | `quality.score` + `quality.level` | FIS output |
| Delivery Risk card | `delivery.score` + `delivery.level` | FIS output |
| Trust Risk card | `trust.score` + `trust.level` | FIS output |
| Sentiment distribution chart | `total_positive/negative/neutral_reviews` | Aggregation stats |
| Recommendations list | `recommendation_snapshot` | JSON array of strings |
| Negative reviews sample | `risk_breakdown.negative_reviews` | Up to 20 worst reviews |
| Analysis metadata | `execution_duration_ms`, `created_at` | Timing + timestamp |

### Health Monitoring Integration

The dashboard displays real-time system health by polling `/api/v1/health`:

```json
{
  "database": "healthy",
  "ai_engine": "healthy",
  "scraper": "healthy",
  "overall": "healthy"
}
```

This enables the dashboard to proactively display degradation warnings when the AI engine or database is unavailable, preventing users from attempting analyses during downtime.

---

## Summary

This development report has documented the complete implementation of all nine subsystems of the AI-Powered Business Risk Analysis and Recommendation System:

| Subsystem | Key Technology | Approx. Lines of Code |
|-----------|---------------|----------------------|
| System Development | FastAPI, Python, PostgreSQL | ~200 (app layer) |
| Web Scraping | Selenium + Chrome | ~950 |
| Multilingual Preprocessing | regex, unicodedata, JSON slang dict | ~330 |
| NLP Model | PyTorch, XLM-RoBERTa, Adapters | ~400 |
| Risk Analysis Engine (FIS) | scikit-fuzzy, NumPy | ~600 |
| BRI Engine | Business Rule Engine | ~400 |
| Recommendation Engine | Knowledge Base, 4-stage pipeline | ~800 |
| Backend/API Integration | FastAPI, SQLAlchemy, JWT | ~1500 |
| Dashboard Integration | Static SPA + REST integration | ~200 (config) |

The system architecture demonstrates a principled separation of concerns — each subsystem independently testable, independently deployable, and composable into the full analysis pipeline. The combination of neural NLP (XLM-RoBERTa), symbolic reasoning (Fuzzy Logic + Business Rules), and knowledge-driven recommendation represents a hybrid AI architecture well-suited to the multilingual, domain-specific challenge of business risk analysis from Sri Lankan e-commerce reviews.

---

*End of Development Report*

---

> **Document Status:** Complete
> **Reviewed By:** Author
> **Related Documents:**
> - `research_component-2.md` — Business Risk Calculation and Fuzzy Inference
> - `Data_management.md` — Database Architecture, Constraints, and Security
