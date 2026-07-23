from core.analysis.engine.product_analysis_engine import ProductAnalysisEngine

from core.business_risk.calculator.business_risk_calculator import (
    BusinessRiskCalculator,
)

from core.business_risk.fuzzy.quality_fis import QualityFIS
from core.business_risk.fuzzy.delivery_fis import DeliveryFIS
from core.business_risk.fuzzy.trust_fis import TrustFIS

from core.business_risk.reporting.pipeline_report_printer import (
    PipelineReportPrinter,
)


PRODUCT_URL = (
    "https://www.daraz.lk/products/"
    "p9-headphones-bluetooth-51-wireless-headband-over-ear-noise-cancelling-"
    "earpieces-stereo-sound-sports-music-earphones-with-mic-hands-free-"
    "gaming-headset-with-mftf-android-samsung-ios-apple-iphone-p47-p47m-"
    "cat-ears-solo-xb450-i402134382-s2181403040.html"
)


def main():

    # ---------------------------------------------------------
    # Step 1 - Run Product Analysis
    # ---------------------------------------------------------

    engine = ProductAnalysisEngine()

    result = engine.analyze(PRODUCT_URL)

    aggregation = result.aggregation_result

    stats = aggregation.aspect_statistics

    # ---------------------------------------------------------
    # Step 2 - Quality Risk
    # ---------------------------------------------------------

    quality = QualityFIS().evaluate(
        mention_ratio=stats["quality"]["mention_ratio"],
        average_negative_strength=stats["quality"][
            "average_negative_strength"
        ],
    )

    # ---------------------------------------------------------
    # Step 3 - Delivery Risk
    # ---------------------------------------------------------

    delivery = DeliveryFIS().evaluate(
        mention_ratio=stats["delivery"]["mention_ratio"],
        average_negative_strength=stats["delivery"][
            "average_negative_strength"
        ],
    )

    # ---------------------------------------------------------
    # Step 4 - Trust Risk
    # ---------------------------------------------------------

    trust = TrustFIS().evaluate(
        mention_ratio=stats["trust"]["mention_ratio"],
        average_negative_strength=stats["trust"][
            "average_negative_strength"
        ],
    )

    # ---------------------------------------------------------
    # Step 5 - Business Risk
    # ---------------------------------------------------------

    business = BusinessRiskCalculator().calculate(
        aggregation=aggregation,
        quality=quality,
        delivery=delivery,
        trust=trust,
    )

    # ---------------------------------------------------------
    # Step 6 - Print Report
    # ---------------------------------------------------------

    PipelineReportPrinter.print_report(
        product=result.product,
        aggregation=aggregation,
        quality=quality,
        delivery=delivery,
        trust=trust,
        business=business,
    )

    # ---------------------------------------------------------
    # Step 7 - Assertions
    # ---------------------------------------------------------

    assert 0 <= business.business_risk_index <= 100


if __name__ == "__main__":
    main()