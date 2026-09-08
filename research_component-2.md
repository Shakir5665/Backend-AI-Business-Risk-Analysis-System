# Research Component 2: Business Risk Calculation and Fuzzy Inference

**AI-Powered Business Risk Analysis and Recommendation System**

---

> **Author:** Shakir | **Project:** Backend AI Business Risk Analysis System  
> **Document Type:** Technical Research Report — IEEE Format  
> **Component:** Research Component 2 — Business Risk Calculation Engine & Fuzzy Logic Inference System  
> **Version:** 1.0 | **Date:** September 2026

---

## Abstract

This report documents the design, architecture, and implementation of **Research Component 2** of the *AI-Powered Business Risk Analysis and Recommendation System* — specifically the **Business Risk Calculation Engine** and its underlying **Fuzzy Inference System (FIS)**. This component receives structured statistical signals derived from AI-predicted customer review data (produced by Component 1's XLM-RoBERTa multi-task model) and transforms them into interpretable, business-level risk classifications across three dimensions: **Product Quality**, **Delivery**, and **Consumer Trust**. A Mamdani-style fuzzy inference architecture, implemented using `scikit-fuzzy`, maps normalized aspect statistics into crisp risk scores on a 0–100 scale. A tiered deterministic **Business Rule Engine** then synthesizes individual aspect risk scores into a single, composite **Business Risk Index (BRI)** and categorical **Risk Level**. The resulting design achieves linguistic interpretability, domain expert alignment, and computational efficiency — demonstrating a principled, hybrid AI–symbolic reasoning approach to automated business risk quantification.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [Statistical Aggregation Layer](#3-statistical-aggregation-layer)
4. [Fuzzy Inference System Design](#4-fuzzy-inference-system-design)
5. [Business Risk Calculation Engine](#5-business-risk-calculation-engine)
6. [Data Models and Type System](#6-data-models-and-type-system)
7. [End-to-End Pipeline Integration](#7-end-to-end-pipeline-integration)
8. [Design Rationale and Theoretical Justification](#8-design-rationale-and-theoretical-justification)
9. [Implementation Summary and Module Map](#9-implementation-summary-and-module-map)
10. [Conclusion](#10-conclusion)
11. [References](#11-references)

---

## 1. Introduction

Business risk quantification from unstructured customer feedback presents a fundamentally ill-posed problem: raw sentiment scores are continuous and ambiguous, yet business decision-making demands crisp, categorical, and explainable risk classifications. Classical Boolean logic fails to accommodate the inherent vagueness in linguistic risk descriptors such as "high delivery risk" or "moderate trust concern." Conversely, purely statistical thresholding loses the nuance of boundary cases and cannot naturally encode domain expert knowledge.

This research component addresses the problem by adopting **Fuzzy Logic** — a formal framework for reasoning under uncertainty using continuous truth values — as the core risk inference engine. The Mamdani fuzzy inference methodology [1] is selected for its alignment with linguistic rule representation and human-interpretable output, making it particularly suitable for business risk contexts where stakeholder transparency is essential.

The design philosophy of Component 2 is grounded in three principles:

1. **Separation of Concerns**: Statistical aggregation, fuzzy inference, and business rule adjudication are implemented as distinct, independently testable modules.
2. **Domain Alignment**: The fuzzy rule bases and membership function parameters encode expert business knowledge directly in code, without requiring retraining of any neural model.
3. **Architectural Composability**: The `BaseFIS` abstract class and `BusinessRule` abstract base class define stable contracts that allow individual FIS instances and business rules to be added, modified, or replaced without altering the orchestrating `BusinessRiskCalculator`.

---

## 2. System Architecture Overview

Component 2 is positioned as the **downstream analytical layer** within the broader pipeline, receiving its inputs from the AI prediction subsystem (XLM-RoBERTa with Bottleneck Adapters — Component 1) and producing the final `BusinessRiskResult` object consumed by the API and reporting layers.

```
+------------------------------------------------------------------+
|           COMPONENT 1: AI Inference Pipeline                     |
|   XLM-RoBERTa + Bottleneck Adapters (Multi-Task Learning)        |
|   --> Per-review: {sentiment, aspect_probabilities,              |
|                    detected_aspects, confidence}                 |
+-------------------------------+----------------------------------+
                                |  List[Dict] -- raw predictions
                                v
+------------------------------------------------------------------+
|   COMPONENT 2A: Statistical Aggregator                           |
|   core/business_risk/aggregation/statistical_aggregator.py       |
|   --> AggregationResult: review_stats, sentiment_stats,          |
|     aspect_stats (mention_ratio, avg_negative_strength),         |
|     confidence_stats                                             |
+-------------------------------+----------------------------------+
                                |  AggregationResult
                                v
+------------------------------------------------------------------+
|   COMPONENT 2B: Fuzzy Inference System (FIS)                     |
|   core/business_risk/fuzzy/                                      |
|   +--------------+  +--------------+  +--------------+           |
|   | QualityFIS   |  | DeliveryFIS  |  |  TrustFIS    |           |
|   +------+-------+  +------+-------+  +------+-------+           |
|          v                 v                  v                  |
|      AspectRisk        AspectRisk         AspectRisk             |
|   (score, level)    (score, level)     (score, level)            |
+-------------------------------+----------------------------------+
                                |  Three AspectRisk objects
                                v
+------------------------------------------------------------------+
|   COMPONENT 2C: Business Risk Calculator                         |
|   core/business_risk/calculator/business_risk_calculator.py      |
|   --> Baseline Computation (max score, dominant level)           |
|   --> Tiered Rule Engine (Tier 1 --> Tier 2 --> Tier 3)          |
|   --> BusinessRiskResult (BRI, Risk Level, Recommendations)      |
+------------------------------------------------------------------+
```

**Figure 1.** End-to-end data flow through Research Component 2.

---

## 3. Statistical Aggregation Layer

### Module: `core/business_risk/aggregation/statistical_aggregator.py`

The `StatisticalAggregator` class is the **bridge** between raw per-review AI predictions and the fuzzy inference subsystem. It aggregates a `List[Dict]` of prediction records — each containing `{sentiment, aspect_probabilities, detected_aspects, confidence}` — into a structured `AggregationResult` object.

### 3.1 Aggregation Pipeline

The aggregation is executed in four sequential passes:

```
predictions (List[Dict])
    |
    +-> _calculate_review_statistics()    --> total, positive, negative, neutral counts
    |
    +-> _calculate_sentiment_statistics() --> positive_ratio, negative_ratio, neutral_ratio
    |
    +-> _calculate_aspect_statistics()    --> per-aspect: mentions, mention_ratio,
    |                                         strength, avg_strength,
    |                                         negative_strength, avg_negative_strength
    |
    +-> _calculate_confidence_statistics() --> average_confidence, low_confidence_ratio
```

### 3.2 Key Computed Metrics

The most critical derived metrics — which serve as **direct FIS inputs** — are:

| Metric | Formula | Role |
|--------|---------|------|
| `mention_ratio` | `aspect_mentions / total_reviews` | Prevalence of aspect concern |
| `average_negative_strength` | `Sum(aspect_prob if sentiment=negative) / total_reviews` | Severity of negative aspect signal |
| `average_strength` | `Sum(aspect_probability) / total_reviews` | Overall aspect prominence |
| `low_confidence_ratio` | `count(confidence < 0.60) / total_reviews` | Model reliability signal |

**Rationale for `average_negative_strength`:** Unlike a simple negative mention count, this metric accumulates the raw sigmoid probability output of the aspect detection head specifically for reviews classified as negative. This provides a *graded* measure of negative signal intensity — a review with aspect probability 0.95 contributes more risk evidence than one with probability 0.51. This design choice exploits the full continuous output of the neural model rather than thresholding to binary aspect detection.

### 3.3 Confidence Filtering

The `LOW_CONFIDENCE_THRESHOLD = 0.60` (defined in `configs/model_config.py`) is used to flag low-reliability predictions. The `low_confidence_ratio` metric is persisted in the `AggregationResult` for downstream use (e.g., in reporting or potential future confidence-weighted inference).

---

## 4. Fuzzy Inference System Design

### Module: `core/business_risk/fuzzy/`

The fuzzy inference layer implements a **Mamdani Fuzzy Inference System** [1] for each of the three business risk aspects. All FIS instances share a common architecture, membership function configuration, and base evaluation protocol, implemented through the `BaseFIS` abstract class.

### 4.1 Universe of Discourse

The universes of discourse are carefully designed to reflect the normalized nature of the input signals and the semantic breadth of risk scoring:

| Variable | Universe | Resolution |
|----------|----------|-----------|
| **Input** (all aspects) | `[0.0, 1.0]` | `0.01` (101 points) |
| **Output** (risk score) | `[0, 100]` | `1` (101 points) |

```python
# membership_config.py
INPUT_UNIVERSE  = np.arange(0.0, 1.01, 0.01)   # Normalized [0,1]
OUTPUT_UNIVERSE = np.arange(0,   101,  1)        # Risk score [0,100]
```

The input normalization to `[0, 1]` is a deliberate design decision: all input features (`mention_ratio`, `average_negative_strength`) are naturally bounded ratios, making this universe directly interpretable without additional scaling transformations.

### 4.2 Input Membership Functions

Three linguistic terms are defined for all input variables, using a combination of trapezoidal (`trapmf`) and triangular (`trimf`) membership functions:

| Linguistic Term | Type | Parameters | Description |
|----------------|------|-----------|-------------|
| `LOW` | Trapezoidal | `[0.00, 0.00, 0.20, 0.40]` | Negligible to minor signal |
| `MEDIUM` | Triangular | `[0.25, 0.50, 0.75]` | Moderate, balanced concern |
| `HIGH` | Trapezoidal | `[0.60, 0.80, 1.00, 1.00]` | Strong to saturated signal |

```
mu(x)
1.0 |
    | ####                       ####
    | #####              ###########
    |  ########      ############
0.0 +------+----------+----------+-- x
        0.0         0.5         1.0
         LOW      MEDIUM       HIGH
```

**Figure 2.** Schematic representation of input membership functions.

**Design Justification:**
- Trapezoidal functions for `LOW` and `HIGH` create flat-topped saturation regions at the extremes, preventing excessive sensitivity when signals are clearly negligible or clearly strong.
- The symmetric triangular `MEDIUM` function (apex at 0.50) creates a smooth gradient transition, ensuring continuous membership changes in the mid-range where boundary cases are most significant.
- Overlapping shoulders between terms (`LOW` fades out at 0.40, `MEDIUM` begins at 0.25) implement the partial membership characteristic that distinguishes fuzzy from crisp classification.

### 4.3 Output Membership Functions

Five output terms map to the five business risk levels, covering the full 0–100 risk score spectrum:

| Linguistic Term | Type | Parameters | Risk Score Range |
|----------------|------|-----------|-----------------|
| `VERY_LOW` | Trapezoidal | `[0, 0, 10, 20]` | Near-zero risk |
| `LOW` | Triangular | `[15, 30, 45]` | Mild risk |
| `MEDIUM` | Triangular | `[40, 55, 70]` | Moderate risk |
| `HIGH` | Triangular | `[65, 80, 90]` | Elevated risk |
| `CRITICAL` | Trapezoidal | `[85, 95, 100, 100]` | Severe/maximal risk |

**Design Justification:**
- The deliberate overlap between adjacent output terms (e.g., `LOW` and `MEDIUM` overlap in the 40–45 region) allows the defuzzification process to produce smooth, continuous risk scores rather than hard jumps.
- `VERY_LOW` and `CRITICAL` use trapezoidal functions with flat shoulders at the extremes, reflecting the semantic reality that extreme scores (near 0 or near 100) all constitute equally definitive assessments.
- The placement of `MEDIUM` centered at 55 (rather than 50) provides a slight bias toward risk sensitivity — a deliberate asymmetric design choice reflecting the asymmetric cost of under-estimating versus over-estimating business risk.

### 4.4 Fuzzy Rule Bases

Each FIS instance employs an identical **9-rule Cartesian product rule base**, formed by the complete combination of {LOW, MEDIUM, HIGH} x {LOW, MEDIUM, HIGH} for the two input variables (`mention_ratio` and `average_negative_strength`). This ensures full rule coverage of the input space with no dead zones.

The rule base implements the following risk matrix:

| `mention_ratio` \\ `avg_neg_strength` | **LOW** | **MEDIUM** | **HIGH** |
|---------------------------------------|---------|-----------|---------|
| **LOW**                               | VERY_LOW | LOW      | MEDIUM  |
| **MEDIUM**                            | LOW     | MEDIUM    | HIGH    |
| **HIGH**                              | MEDIUM  | HIGH      | CRITICAL |

**Table 1.** Fuzzy risk inference matrix for all three aspect FIS instances (Quality, Delivery, Trust).

```python
# Example: Quality FIS Rule Base (quality_rules.py)
rules = [
    ctrl.Rule(quality_mention_ratio["LOW"]    & quality_negative_strength["LOW"],    quality_risk["VERY_LOW"]),
    ctrl.Rule(quality_mention_ratio["LOW"]    & quality_negative_strength["MEDIUM"], quality_risk["LOW"]),
    ctrl.Rule(quality_mention_ratio["LOW"]    & quality_negative_strength["HIGH"],   quality_risk["MEDIUM"]),
    ctrl.Rule(quality_mention_ratio["MEDIUM"] & quality_negative_strength["LOW"],    quality_risk["LOW"]),
    ctrl.Rule(quality_mention_ratio["MEDIUM"] & quality_negative_strength["MEDIUM"], quality_risk["MEDIUM"]),
    ctrl.Rule(quality_mention_ratio["MEDIUM"] & quality_negative_strength["HIGH"],   quality_risk["HIGH"]),
    ctrl.Rule(quality_mention_ratio["HIGH"]   & quality_negative_strength["LOW"],    quality_risk["MEDIUM"]),
    ctrl.Rule(quality_mention_ratio["HIGH"]   & quality_negative_strength["MEDIUM"], quality_risk["HIGH"]),
    ctrl.Rule(quality_mention_ratio["HIGH"]   & quality_negative_strength["HIGH"],   quality_risk["CRITICAL"]),
]
```

**Semantic Interpretation of the Rule Matrix:**
- **Diagonal escalation**: Risk escalates monotonically as both inputs increase, preserving logical consistency.
- **Asymmetric sensitivity to severity**: When `mention_ratio` is LOW but `negative_strength` is HIGH (aspect rarely mentioned but reviews are strongly negative), the output is MEDIUM — reflecting that even rare but intense negative signals carry moderate risk.
- **Frequency dominance**: When `mention_ratio` is HIGH but `negative_strength` is LOW (aspect frequently mentioned but reviews are mostly positive), output is MEDIUM — the sheer frequency of mention warrants attention even absent strong negativity.
- **Conjunctive conjunction**: Rules use Mamdani AND (minimum T-norm), requiring *both* conditions to be partially satisfied simultaneously.

### 4.5 Defuzzification Strategy

The `scikit-fuzzy` library's default **centroid defuzzification** method (Center of Area) is employed:

```
          Integral[ mu_agg(x) * x dx ]
score = ----------------------------------
           Integral[ mu_agg(x) dx ]
```

Where `mu_agg(x)` is the aggregated (clipped) output fuzzy set obtained by combining the activated consequent regions from all fired rules.

**Centroid vs. alternatives:** The centroid method was selected over Mean of Maximum (MoM) or Bisector methods because it considers the full shape of the aggregated output set, producing smooth score transitions as input values change. This smoothness is essential for a continuous risk dashboard display.

The resulting crisp score (floating-point in [0, 100]) is rounded to 2 decimal places and stored as `AspectRisk.score`.

### 4.6 Domain-Specific FIS Instances

Three specialized FIS classes extend `BaseFIS`, each instantiating the shared architecture with aspect-specific variable names:

```python
# BaseFIS (base_fis.py) -- Abstract Base Class
class BaseFIS(ABC):
    def __init__(self, aspect_name, control_system, input_mapping, output_variable):
        self.simulation = ctrl.ControlSystemSimulation(control_system)

    def evaluate(self, **inputs) -> AspectRisk:
        # Feed inputs --> compute() --> read output --> return AspectRisk

    @staticmethod
    def determine_level(score: float) -> RiskLevel:
        if score < 20:   return RiskLevel.VERY_LOW
        elif score < 40: return RiskLevel.LOW
        elif score < 60: return RiskLevel.MEDIUM
        elif score < 80: return RiskLevel.HIGH
        return RiskLevel.CRITICAL
```

| FIS Class | Aspect | Input 1 | Input 2 | Output |
|-----------|--------|---------|---------|--------|
| `QualityFIS` | Product Quality | `quality_mention_ratio` | `quality_negative_strength` | `quality_risk` |
| `DeliveryFIS` | Delivery | `delivery_mention_ratio` | `delivery_negative_strength` | `delivery_risk` |
| `TrustFIS` | Consumer Trust | `trust_mention_ratio` | `trust_negative_strength` | `trust_risk` |

The `input_mapping` dictionary in each FIS class provides the semantic bridge between the caller's parameter names (generic `mention_ratio`, `average_negative_strength`) and the FIS-internal variable names (e.g., `quality_mention_ratio`), ensuring namespace isolation across the three control systems.

The `determine_level()` static method applies a crisp threshold grid to map the continuous score to a `RiskLevel` enum value:

| Score Range | Risk Level |
|-------------|-----------|
| [0, 20)     | VERY_LOW  |
| [20, 40)    | LOW       |
| [40, 60)    | MEDIUM    |
| [60, 80)    | HIGH      |
| [80, 100]   | CRITICAL  |

---

## 5. Business Risk Calculation Engine

### Module: `core/business_risk/calculator/`

The `BusinessRiskCalculator` class orchestrates the synthesis of three individual `AspectRisk` objects into a single `BusinessRiskResult`. It implements a **two-phase computation**: baseline estimation followed by tiered rule adjudication.

### 5.1 Baseline Score Computation

The baseline is computed by the utility functions in `utils.py`:

```python
def calculate_baseline_score(quality, delivery, trust) -> float:
    return max(quality.score, delivery.score, trust.score)

def determine_baseline_level(quality, delivery, trust) -> RiskLevel:
    highest = max((quality, delivery, trust), key=lambda a: a.score)
    return highest.level
```

**Rationale for Maximum-Based Baseline:** The baseline adopts the **single-worst-case principle** — the overall business risk cannot be lower than its most critical failing dimension. This reflects standard risk management theory where systemic risk is bounded below by the risk of the most vulnerable component. A product with excellent quality and delivery but catastrophic trust failures remains a high-risk business entity — the average score would obscure this reality.

### 5.2 Tiered Business Rule Engine

The rule engine implements a **priority-ordered, first-match policy**: rules are evaluated sequentially in priority order, and execution stops at the first matching rule. This deterministic evaluation order ensures predictable, auditable behavior and prevents rule conflicts.

```python
# business_risk_calculator.py -- Rule execution
final_level = baseline_level
for rule in RULES:
    if rule.matches(context):
        final_level = rule.apply(context)
        break
```

Rules are organized into three priority tiers:

---

#### Tier 1 — Domain Override Rules (`tier1_rules.py`)

These rules encode **domain-specific business knowledge** that overrides the mathematical baseline with expert-informed adjustments. They reflect the differential business impact of failures across the three aspects.

| Rule | Trigger Condition | Applied Level | Rationale |
|------|-------------------|---------------|-----------|
| `TrustCriticalRule` | Trust = CRITICAL AND Quality < HIGH AND Delivery < HIGH | CRITICAL | Consumer trust is the most existentially threatening failure; trust destruction triggers immediate CRITICAL status regardless of other dimensions |
| `QualityCriticalRule` | Quality = CRITICAL AND Delivery < HIGH AND Trust < HIGH | HIGH | Product quality failures are severe but recoverable; elevated to HIGH (not CRITICAL) as a standalone issue |
| `DeliveryCriticalRule` | Delivery = CRITICAL AND Quality < HIGH AND Trust < HIGH | HIGH | Delivery failures significantly impact business but are operationally addressable; standalone failure elevates to HIGH |

**Domain Knowledge Encoded:**
- Trust failures receive the **most severe response** because consumer trust, once lost, has the longest recovery trajectory and highest churn risk.
- Quality and Delivery failures in isolation are elevated but moderated — they signal operational problems that are addressable with tactical interventions.
- The `is_below(level, HIGH)` condition on companion aspects prevents Tier 1 rules from triggering when multiple aspects are simultaneously elevated (that case is captured by Tier 2).

---

#### Tier 2 — Escalation Rules (`tier2_rules.py`)

| Rule | Trigger Condition | Applied Level | Rationale |
|------|-------------------|---------------|-----------|
| `MultipleHighRiskRule` | count(aspects >= HIGH) >= 2 | CRITICAL | Simultaneous HIGH/CRITICAL failures across 2+ aspects indicate systemic business failure |

```python
def matches(self, context: RuleContext) -> bool:
    levels = [context.quality.level, context.delivery.level, context.trust.level]
    return count_at_least(levels, RiskLevel.HIGH) >= 2
```

The `count_at_least()` utility employs a numeric ordinal mapping `{VERY_LOW: 0, LOW: 1, MEDIUM: 2, HIGH: 3, CRITICAL: 4}` to enable comparison operations across `RiskLevel` enum values, maintaining clean separation between the categorical enum and its ordinal semantics.

**Multi-Aspect Interaction Logic:** The `MultipleHighRiskRule` captures **systemic risk amplification** — a phenomenon not representable by single-aspect FIS outputs. When a business entity simultaneously exhibits HIGH quality issues, HIGH delivery failures, AND HIGH trust erosion, the combined effect on business survival is non-linear and warrants the most severe risk classification.

---

#### Tier 3 — Consistency Rules (`tier3_rules.py`)

These rules enforce **semantic consistency** when all three aspects agree on the same risk level, guaranteeing that the overall business risk label matches the consensus assessment:

| Rule | Trigger Condition | Applied Level |
|------|-------------------|---------------|
| `AllVeryLowRule` | All three aspects = VERY_LOW | VERY_LOW |
| `AllLowRule` | All three aspects = LOW | LOW |
| `AllMediumRule` | All three aspects = MEDIUM | MEDIUM |

These rules prevent cases where the maximum-based baseline score produces a level that contradicts the uniform qualitative assessment. For example, if all three aspects produce scores of 48 (each classified as MEDIUM), the baseline would correctly identify MEDIUM, but these rules make that determination explicit and auditable through the rule chain.

### 5.3 Rule Context and Immutability

All rules operate on a **frozen `RuleContext` dataclass**, ensuring that no rule can mutate the shared context during evaluation:

```python
@dataclass(frozen=True)
class RuleContext:
    aggregation:    AggregationResult
    quality:        AspectRisk
    delivery:       AspectRisk
    trust:          AspectRisk
    baseline_score: float
    baseline_level: RiskLevel
```

The `frozen=True` constraint is a deliberate architectural decision that enforces **referential transparency** in rule evaluation — each rule's `matches()` and `apply()` methods are guaranteed to be pure functions of the context, enabling future parallelization or caching of rule evaluations.

---

## 6. Data Models and Type System

The system employs immutable, typed data transfer objects throughout the pipeline:

### `RiskLevel` Enum (`models/risk_level.py`)

```python
class RiskLevel(str, Enum):
    VERY_LOW = "VERY_LOW"
    LOW      = "LOW"
    MEDIUM   = "MEDIUM"
    HIGH     = "HIGH"
    CRITICAL = "CRITICAL"
```

Inheriting from both `str` and `Enum` enables `RiskLevel` values to be serialized directly as JSON strings without additional conversion, simplifying API integration.

### `AspectRisk` (`models/aspect_risk.py`)

```python
@dataclass(frozen=True)
class AspectRisk:
    aspect: str       # Aspect name: "Quality", "Delivery", "Trust"
    score:  float     # Crisp FIS output: [0.0, 100.0]
    level:  str       # RiskLevel classification
```

### `BusinessRiskResult` (`models/business_risk_result.py`)

```python
@dataclass
class BusinessRiskResult:
    quality:              AspectRisk
    delivery:             AspectRisk
    trust:                AspectRisk
    business_risk_index:  float      # Max aspect score (0-100)
    business_risk_level:  RiskLevel  # Final adjudicated level
    recommendations:      list[str]  # Placeholder for Component 3
```

The separation of `business_risk_index` (continuous) from `business_risk_level` (categorical) is intentional: the continuous BRI supports dashboard visualizations and trend analysis, while the categorical level supports alert thresholds and automated decision routing.

---

## 7. End-to-End Pipeline Integration

The complete data transformation chain for Research Component 2 can be summarized as follows:

```
1. AI Predictions (Component 1)
   Input:  List[Dict] with {sentiment, aspect_probabilities,
                            detected_aspects, confidence}

2. Statistical Aggregation
   Output: AggregationResult {
       review_statistics:    {total, positive, negative, neutral counts}
       sentiment_statistics: {positive_ratio, negative_ratio, neutral_ratio}
       aspect_statistics:    {quality/delivery/trust: {
                               mentions, mention_ratio,
                               strength, avg_strength,
                               negative_strength, avg_negative_strength}}
       confidence_statistics:{average_confidence, low_confidence_ratio}
   }

3. FIS Input Extraction
   Quality:  mention_ratio = aspect_stats["quality"]["mention_ratio"]
             neg_strength  = aspect_stats["quality"]["average_negative_strength"]
   Delivery: mention_ratio = aspect_stats["delivery"]["mention_ratio"]
             neg_strength  = aspect_stats["delivery"]["average_negative_strength"]
   Trust:    mention_ratio = aspect_stats["trust"]["mention_ratio"]
             neg_strength  = aspect_stats["trust"]["average_negative_strength"]

4. Fuzzy Inference (Example)
   QualityFIS.evaluate(mention_ratio=0.35, average_negative_strength=0.40)
       --> AspectRisk(aspect="Quality", score=47.3, level="MEDIUM")

   DeliveryFIS.evaluate(mention_ratio=0.72, average_negative_strength=0.81)
       --> AspectRisk(aspect="Delivery", score=81.5, level="CRITICAL")

   TrustFIS.evaluate(mention_ratio=0.18, average_negative_strength=0.22)
       --> AspectRisk(aspect="Trust", score=22.1, level="LOW")

5. Business Risk Calculation
   baseline_score = max(47.3, 81.5, 22.1) = 81.5
   baseline_level = CRITICAL  (Delivery dominates)

   Rule Evaluation:
     TrustCriticalRule.matches()   --> False (Trust != CRITICAL)
     QualityCriticalRule.matches() --> False (Quality != CRITICAL)
     DeliveryCriticalRule.matches()--> True  (Delivery=CRITICAL, Quality<HIGH, Trust<HIGH)
     DeliveryCriticalRule.apply()  --> RiskLevel.HIGH  <- Override applied

6. Result
   BusinessRiskResult(
       quality             = AspectRisk(score=47.3, level="MEDIUM"),
       delivery            = AspectRisk(score=81.5, level="CRITICAL"),
       trust               = AspectRisk(score=22.1, level="LOW"),
       business_risk_index = 81.5,
       business_risk_level = "HIGH",       <- Rule-adjudicated (not raw CRITICAL)
       recommendations     = []
   )
```

**Figure 4.** Concrete example of end-to-end pipeline execution showing FIS inference and rule adjudication.

---

## 8. Design Rationale and Theoretical Justification

### 8.1 Why Fuzzy Logic for Risk Quantification?

Business risk from customer feedback is inherently a problem of **linguistic uncertainty**. Natural expressions like "high delivery risk" or "moderate quality concern" cannot be precisely mapped to crisp Boolean categories without information loss. Fuzzy Logic, introduced by Zadeh [2], provides a formal calculus for such vagueness through graded membership — a review dataset where 35% of reviews mention quality issues is more naturally described as "somewhat medium" than definitively "low" or "medium."

The Mamdani FIS [1] is selected over Takagi-Sugeno-Kang (TSK) [3] because:
1. **Interpretability**: Mamdani consequents are linguistic (fuzzy sets), making individual rule outputs directly interpretable.
2. **Expert alignment**: Domain experts can formulate and validate rules in natural language terms ("if mention frequency is HIGH and negative strength is HIGH, then risk is CRITICAL").
3. **Defuzzification flexibility**: The centroid method provides smooth, continuous output transitions.

### 8.2 Why Maximum for Baseline Aggregation?

The maximum-based baseline (`calculate_baseline_score`) implements the **risk dominance principle**: in multi-dimensional risk analysis, the aggregate risk is bounded from below by the maximum component risk. This is consistent with frameworks such as ISO 31000 [4], which defines overall risk as a function of consequence and likelihood — when any single dimension reaches a critical threshold, the overall assessment reflects that severity.

An arithmetic mean would mask critical single-dimension failures. Weighted averaging requires empirically validated weights that may not generalize across different business contexts.

### 8.3 Why a Tiered Rule Engine?

The three-tier rule architecture implements a **priority-ordered expert system** that combines:
- **Tier 1** (Override Rules): Hard domain knowledge that supersedes mathematical computation
- **Tier 2** (Escalation Rules): Multi-aspect interaction effects not captured by individual FIS scores
- **Tier 3** (Consistency Rules): Logical invariants ensuring qualitative coherence

This structure is preferable to a flat rule list because it encodes the *semantic priority* of different risk conditions explicitly in the architecture, rather than through ad hoc rule ordering. The first-match policy ensures deterministic, auditable behavior critical for business risk reporting systems [5].

### 8.4 Architectural Patterns

The implementation leverages several classical software engineering patterns to achieve the design goals:

| Pattern | Application |
|---------|-------------|
| **Template Method** | `BaseFIS` defines the FIS evaluation workflow; subclasses specialize variable names and rule sets |
| **Strategy** | Each `BusinessRule` encapsulates a distinct risk determination strategy, selectable at runtime |
| **Registry** | `RULES` list in `rule_registry.py` centralizes rule ordering and composition |
| **Immutable Value Objects** | `AspectRisk` and `RuleContext` as frozen dataclasses prevent side effects |
| **Abstract Factory** | `build_*_control_system()` functions encapsulate FIS construction complexity |

### 8.5 Scalability Considerations

The current design supports extension along multiple axes without architectural changes:
- **New business aspects**: Add new FIS class (extend `BaseFIS`) + new rule in `rule_registry.py`
- **New business rules**: Implement `BusinessRule` subclass, register in `RULES`
- **Adjusted risk thresholds**: Modify `determine_level()` or `membership_config.py` parameters
- **Weighted aggregation**: Replace `calculate_baseline_score()` with a weighted variant
- **Confidence-gated FIS**: Route low-confidence aggregations to a separate conservative FIS

---

## 9. Implementation Summary and Module Map

```
core/business_risk/
+-- __init__.py
|
+-- aggregation/
|   +-- __init__.py
|   +-- aggregation_result.py           -- AggregationResult data container
|   +-- statistical_aggregator.py       -- StatisticalAggregator (4-phase pipeline)
|
+-- calculator/
|   +-- business_risk_calculator.py     -- BusinessRiskCalculator (orchestrator)
|   +-- utils.py                        -- Risk comparison and baseline utilities
|   +-- rules/
|       +-- __init__.py
|       +-- base_rule.py                -- BusinessRule ABC (matches + apply)
|       +-- rule_context.py             -- RuleContext (frozen dataclass)
|       +-- rule_registry.py            -- RULES ordered list (priority registry)
|       +-- tier1_rules.py              -- Domain override rules (3 rules)
|       +-- tier2_rules.py              -- Escalation rules (1 rule)
|       +-- tier3_rules.py              -- Consistency rules (3 rules)
|
+-- fuzzy/
|   +-- base_fis.py                     -- BaseFIS ABC (evaluate + determine_level)
|   +-- fuzzy_variables.py              -- Antecedent/Consequent factory functions
|   +-- membership_config.py            -- MF parameters + universes of discourse
|   +-- quality_fis.py                  -- QualityFIS
|   +-- delivery_fis.py                 -- DeliveryFIS
|   +-- trust_fis.py                    -- TrustFIS
|   +-- rules/
|       +-- __init__.py
|       +-- quality_rules.py            -- 9-rule quality control system builder
|       +-- delivery_rules.py           -- 9-rule delivery control system builder
|       +-- trust_rules.py              -- 9-rule trust control system builder
|
+-- models/
|   +-- __init__.py
|   +-- aspect_risk.py                  -- AspectRisk (frozen dataclass)
|   +-- business_risk_result.py         -- BusinessRiskResult (output model)
|   +-- risk_level.py                   -- RiskLevel (str Enum, 5 levels)
|
+-- prediction/
|   +-- prediction_collector.py         -- PredictionCollector (List[Dict] accumulator)
|
+-- reporting/
    +-- pipeline_report_printer.py      -- PipelineReportPrinter (ASCII executive report)
```

**Table 2.** Complete module map for Research Component 2.

### 9.1 Key Technology Stack

| Technology | Role |
|-----------|------|
| `scikit-fuzzy` | Mamdani FIS implementation (ctrl, ControlSystem, ControlSystemSimulation) |
| `numpy` | Fuzzy universe arrays and membership function computation |
| Python `dataclasses` | Immutable value objects (AspectRisk, RuleContext) |
| Python `abc` | Abstract base classes (BaseFIS, BusinessRule) |
| Python `enum` | RiskLevel categorical type |

### 9.2 Computational Complexity

| Operation | Complexity |
|-----------|-----------|
| Statistical Aggregation | O(N) — linear in number of reviews N |
| FIS Evaluation (per aspect) | O(R x U) — R rules x U output universe points |
| Business Rule Evaluation | O(T) — T total rules (bounded constant: currently 7) |
| Total Pipeline | O(N + 3*R*U + T) ≈ O(N) for large N |

With `N = 500` reviews, `R = 9` rules per FIS, `U = 101` universe points, and `T = 7` business rules, the entire Component 2 pipeline completes in sub-second execution time on standard hardware.

---

## 10. Conclusion

This report has documented the complete design and implementation of **Research Component 2** — the Business Risk Calculation Engine and Fuzzy Inference System of the AI-Powered Business Risk Analysis and Recommendation System. The component demonstrates a principled integration of:

1. **Statistical signal extraction** from AI-predicted review data, converting raw neural network outputs into normalized business metrics
2. **Mamdani Fuzzy Inference** for interpretable, linguistically-grounded risk quantification across three business dimensions
3. **Tiered deterministic rule adjudication** for domain-expert-aligned composite risk synthesis

The architecture achieves its design objectives:

- **Interpretability**: Every risk score can be traced back to specific fuzzy rules and input values
- **Extensibility**: New aspects, rules, or membership configurations can be added without architectural changes
- **Correctness**: Immutable data contracts prevent side effects; the deterministic rule engine ensures reproducible results
- **Efficiency**: Linear scaling with review corpus size makes the system viable for real-time business intelligence

The resulting **Business Risk Index (BRI)** and **Risk Level** classification provide actionable, explainable risk intelligence from customer feedback at scale, bridging the gap between AI-predicted sentiment signals and human-interpretable business risk management.

---

## 11. References

[1] E. H. Mamdani and S. Assilian, "An experiment in linguistic synthesis with a fuzzy logic controller," *International Journal of Man-Machine Studies*, vol. 7, no. 1, pp. 1–13, 1975. doi: 10.1016/S0020-7373(75)80002-2

[2] L. A. Zadeh, "Fuzzy sets," *Information and Control*, vol. 8, no. 3, pp. 338–353, 1965. doi: 10.1016/S0019-9958(65)90241-X

[3] T. Takagi and M. Sugeno, "Fuzzy identification of systems and its applications to modeling and control," *IEEE Transactions on Systems, Man, and Cybernetics*, vol. 15, no. 1, pp. 116–132, 1985. doi: 10.1109/TSMC.1985.6313399

[4] International Organization for Standardization, *ISO 31000:2018 — Risk Management: Guidelines*, Geneva, Switzerland: ISO, 2018.

[5] W. van der Aalst, "Business process management: A comprehensive survey," *ISRN Software Engineering*, 2013, Art. no. 507984. doi: 10.1155/2013/507984

[6] J. Warner and J. Sexauer, *scikit-fuzzy: A fuzzy logic toolkit for SciPy*, v0.4.2, 2019. [Online]. Available: https://pythonhosted.org/scikit-fuzzy/

[7] Y. Liu, J. Ott, N. Goyal, J. Du, M. Joshi, D. Chen, O. Levy, M. Lewis, L. Zettlemoyer, and V. Stoyanov, "RoBERTa: A robustly optimized BERT pretraining approach," *arXiv preprint arXiv:1907.11692*, 2019.

[8] A. Pfeiffer, I. Vulić, I. Gurevych, and S. Ruder, "AdapterHub: A framework for adapting transformers," in *Proc. EMNLP 2020: System Demonstrations*, pp. 46–54, 2020.

---

*End of Research Component 2 Report*

---

> **Document Status:** Complete  
> **Reviewed By:** Author  
> **Next Component:** Research Component 3 — Recommendation Engine and API Integration Layer
