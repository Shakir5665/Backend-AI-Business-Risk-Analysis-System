from core.business_risk.fuzzy.quality_fis import QualityFIS


def main():

    fis = QualityFIS()

    test_cases = [

        # mention_ratio, average_negative_strength
        (0.10, 0.10),

        (0.20, 0.80),

        (0.50, 0.50),

        (0.80, 0.70),

        (0.90, 0.90),
    ]

    print("=" * 60)
    print("QUALITY FUZZY SYSTEM TEST")
    print("=" * 60)

    for mention_ratio, strength in test_cases:

        result = fis.evaluate(
            mention_ratio=mention_ratio,
            average_negative_strength=strength,
        )

        print(
            f"Mention={mention_ratio:.2f} "
            f"Strength={strength:.2f} "
            f"-> Score={result.score:.2f} "
            f"Level={result.level.value}"
        )


if __name__ == "__main__":
    main()