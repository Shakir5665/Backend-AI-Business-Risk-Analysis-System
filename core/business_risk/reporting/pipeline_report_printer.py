from datetime import datetime


class PipelineReportPrinter:

    WIDTH = 100

    @staticmethod
    def line():
        print("=" * PipelineReportPrinter.WIDTH)

    @staticmethod
    def section(title: str):
        print()
        print("-" * PipelineReportPrinter.WIDTH)
        print(title.upper())
        print("-" * PipelineReportPrinter.WIDTH)

    @staticmethod
    def print_report(
            product,
            aggregation,
            quality,
            delivery,
            trust,
            business,
    ):

        printer = PipelineReportPrinter

        printer.line()
        print("AI BUSINESS RISK ANALYSIS REPORT".center(printer.WIDTH))
        printer.line()

        print(f"Generated : {datetime.now():%Y-%m-%d %H:%M:%S}")

        printer.section("Product Information")

        print(f"Product ID           : {product.product_id}")
        print(f"Product Name         : {product.product_name}")
        print(f"Category             : {product.category}")
        print(f"Review Count         : {len(product.reviews)}")
        print(f"Product URL          : {product.product_url}")

        printer.section("Review Statistics")

        for key, value in aggregation.review_statistics.items():
            print(f"{key:<25}: {value}")

        printer.section("Sentiment Statistics")

        for key, value in aggregation.sentiment_statistics.items():
            print(f"{key:<25}: {value}")

        printer.section("Aspect Statistics")

        for key, value in aggregation.aspect_statistics.items():
            print(f"{key:<25}: {value}")

        printer.section("Confidence Statistics")

        for key, value in aggregation.confidence_statistics.items():
            print(f"{key:<25}: {value}")

        printer.section("Fuzzy Risk Analysis")

        print(f"Quality Risk Score   : {quality.score:.2f}")
        print(f"Quality Risk Level   : {quality.level}")

        print()

        print(f"Delivery Risk Score  : {delivery.score:.2f}")
        print(f"Delivery Risk Level  : {delivery.level}")

        print()

        print(f"Trust Risk Score     : {trust.score:.2f}")
        print(f"Trust Risk Level     : {trust.level}")

        printer.section("Business Risk")

        print(f"Business Risk Index  : {business.business_risk_index:.2f}")
        print(f"Business Risk Level  : {business.business_risk_level}")

        printer.line()
        print("PIPELINE EXECUTED SUCCESSFULLY".center(printer.WIDTH))
        printer.line()