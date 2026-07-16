"""
Test script for the ScraperEngine
"""

import traceback
from core.scraper.engines.scraper_engine import ScraperEngine

def main():
    """Main function to test the scraper engine"""
    print("=" * 80)
    print("REVIEW SCRAPER TEST - MANUAL FILTER MODE")
    print("=" * 80)
    print("\n💡 Press 'Q' at any time to stop scraping gracefully")
    print("💡 All reviews are saved to CSV in real-time")
    print("💡 You manually apply the star filter in the browser")
    print("=" * 80)
    
    # Product URL
    product_url = "https://www.daraz.lk/products/p47-headset-bluetooth-wireless-earphones-with-mic-gaming-headset-50-foldable-ear-over-p47-50-earphone-hifi-noise-cancelling-headphone-bass-super-microphone-new-f-m-tf-card-support-i167209228-s1116070917.html?c=&channelLpJumpArgs=&clickTrackInfo=query%253AHeadphones%253Bnid%253A167209228%253Bsrc%253ALazadaMainSrp%253Brn%253A743870dd2d9929c55e523f098575365e%253Bregion%253Alk%253Bsku%253A167209228_LK%253Bprice%253A898%253Bclient%253Adesktop%253Bsupplier_id%253A1000123656061%253Bsession_id%253A%253Bbiz_source%253Ah5_external%253Bslot%253A7%253Utlog_bucket_id%253A470687%253Basc_category_id%253A156%253Bitem_id%253A167209228%253Bsku_id%253A1116070917%253Bshop_id%253A98345%253BtemplateInfo%253A&freeshipping=0&fs_ab=1&fuse_fs=&lang=en&location=Western&price=898&priceCompare=skuId%3A1116070917%3Bsource%3Alazada-search-voucher%3Bsn%3A743870dd2d9929c55e523f098575365e%3BoriginPrice%3A89800%3BdisplayPrice%3A89800%3BisGray%3Afalse%3BsinglePromotionId%3A50000034767003%3BsingleToolCode%3ApromPrice%3BvoucherPricePlugin%3A0%3Btimestamp%3A1782238194684&ratingscore=4.440511307767945&request_id=743870dd2d9929c55e523f098575365e%3Breview=2034&sale=10246&search=1&source=search&spm=a2a0e.searchlist.list.7&stock=1"

    scraper = ScraperEngine()
    
    try:
        # Scrape all reviews
        product = scraper.scrape_product(product_url)
        
        if product.reviews:
            print(f"\n✅ Found {len(product.reviews)} total reviews!")
            
            # Print sample
            print("\n📝 Sample Reviews (First 5):")
            print("-" * 70)
            for review in product.reviews[:5]:
                print(review.review_text)
            print("-" * 70)
            
            print(f"\n📁 All reviews saved to: {scraper.csv_filename}")
        else:
            print("\n❌ No reviews were scraped!")
            
    except KeyboardInterrupt:
        print("\n🛑 Scraping interrupted by user!")
        print(f"✅ Saved reviews to CSV so far")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        traceback.print_exc()
        
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
