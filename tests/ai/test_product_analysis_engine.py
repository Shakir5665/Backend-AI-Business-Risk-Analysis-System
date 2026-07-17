
from core.analysis.engine.product_analysis_engine import ProductAnalysisEngine

url = "https://www.daraz.lk/products/m10-tws-wireless-earbuds-bluetooth-earphone-hifi-touch-control-led-digital-display-with-microphone-and-power-bank-i189252843-s1203427915.html?c=&channelLpJumpArgs=&clickTrackInfo=query%253Aear%252Bbuds%253Bnid%253A189252843%253Bsrc%253ALazadaMainSrp%253Brn%253A3ad72d8b58c43b44e577ca2a5f47a7d0%253Bregion%253Alk%253Bsku%253A189252843_LK%253Bprice%253A969%253Bclient%253Adesktop%253Bsupplier_id%253A1000122366101%253Bsession_id%253A%253Bbiz_source%253Ahttps%253A%252F%252Fwww.daraz.lk%252F%253Bslot%253A5%253Butlog_bucket_id%253A470687%253Basc_category_id%253A9708%253Bitem_id%253A189252843%253Bsku_id%253A1203427915%253Bshop_id%253A54780%253BtemplateInfo%253A&freeshipping=0&fs_ab=1&fuse_fs=&lang=en&location=Western&price=969&priceCompare=skuId%3A1203427915%3Bsource%3Alazada-search-voucher%3Bsn%3A3ad72d8b58c43b44e577ca2a5f47a7d0%3BoriginPrice%3A96900%3BdisplayPrice%3A96900%3BisGray%3Afalse%3BsinglePromotionId%3A50000034767003%3BsingleToolCode%3ApromPrice%3BvoucherPricePlugin%3A0%3Btimestamp%3A1782231321749&qSellingPoint=p--ear%20buds&ratingscore=4.360776088096487&request_id=3ad72d8b58c43b44e577ca2a5f47a7d0&review=3814&sale=17723&search=1&source=search&spm=a2a0e.searchlist.list.5&stock=1"

engine = ProductAnalysisEngine()

result = engine.analyze(url)

print("=" * 80)
print("PRODUCT")
print("=" * 80)

print(f"Product ID      : {result.product.product_id}")
print(f"Product Name    : {result.product.product_name}")
print(f"Category        : {result.product.category}")
print(f"Review Count    : {len(result.product.reviews)}")
print(f"Product URL     : {result.product.product_url}")

print("\nReview Statistics")
print(result.aggregation_result.review_statistics)

print("\nSentiment Statistics")
print(result.aggregation_result.sentiment_statistics)

print("\nAspect Statistics")
print(result.aggregation_result.aspect_statistics)

print("\nConfidence Statistics")
print(result.aggregation_result.confidence_statistics)
