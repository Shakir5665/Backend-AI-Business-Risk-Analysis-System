"""
Professional Daraz Review Scraper Engine - Manual Filter Mode
- Let's you manually apply the star filter
- Then scraper takes over and scrapes all pages
- Press 'Q' to stop gracefully
- Saves to CSV in real-time
"""

import time
import csv
import re
from datetime import datetime
from typing import List
import logging

# For browser automation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from core.scraper.interfaces.scraper_interface import ScraperInterface
from core.scraper.dto.product import Product
from core.scraper.dto.scraped_review import ScrapedReview

# For keyboard detection
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    import msvcrt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ScraperEngine(ScraperInterface):
    """Daraz scraper with manual filter mode"""
    
    def __init__(self):

        """
        Initialize the scraper engine.

        Browser resources are created only
        when scraping starts.
        """

        self._driver = None

        self.csv_filename = None

        
    def _init_csv(self):
        """Initialize CSV file with headers"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_filename = f"product_reviews_{timestamp}.csv"
        
        with open(self.csv_filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            # writer.writerow(['Review Number', 'Review'])
        
        logger.info(f"CSV file created: {self.csv_filename}")
        
    def _save_review_to_csv(self, review_text: str, index: int):
        """Save a single review to CSV"""
        try:
            with open(self.csv_filename, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([index, review_text])
        except Exception as e:
            logger.error(f"Error saving review: {e}")
        
    def _setup_browser(self, headless: bool):
        """Setup Chrome browser"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless")
            
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self._driver = webdriver.Chrome(options=chrome_options)
        self._driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def _check_stop(self) -> bool:
        """Check if user pressed 'Q' to stop"""
        if KEYBOARD_AVAILABLE:
            if keyboard.is_pressed('q') or keyboard.is_pressed('Q'):
                logger.info("User pressed 'Q'. Stopping...")
                return True
        else:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key in [b'q', b'Q']:
                    logger.info("User pressed 'Q'. Stopping...")
                    return True
        return False
    
    def _wait_for_manual_filter(self):
        """
        Wait for user to manually apply the star filter
        User should click the filter in the browser
        """
        print("\n" + "=" * 80)
        print("MANUAL FILTER MODE")
        print("=" * 80)
        print("\nThe browser is now open with your product page.")
        print("\nPlease follow these steps:")
        print("1. Find the 'Reviews' section")
        print("2. Click on the star filter (e.g., '1 Star' or 'All Stars')")
        print("3. Wait for the page to refresh with filtered reviews")
        print("4. Make sure you can see the filtered reviews")
        print("\nIMPORTANT: Click on the filter you want to scrape")
        print("   - For 1-star reviews: Click '1 Star'")
        print("   - For 2-star reviews: Click '2 Star'")
        print("   - For all reviews: Click 'All Stars' or don't click any filter")
        print("\nWhen you're ready, type 'start' in the console and press Enter")
        print("   OR type 'quit' to exit")
        print("=" * 80)
        
        while True:
            user_input = input("\nEnter command (start/quit): ").strip().lower()
            if user_input == 'start':
                print("\nContinuing with scraping...")
                time.sleep(2)
                return True
            elif user_input == 'quit':
                print("\nExiting scraper...")
                return False
            else:
                print("Invalid command. Please type 'start' or 'quit'")
    
    def _get_total_pages(self) -> int:
        """Get total number of review pages"""
        try:
            # Wait for pagination to load
            time.sleep(3)
            
            # Try to find total pages from pagination
            pagination_selectors = [
                '.next-pagination-item',
                '.pagination-item',
                'button[class*="pagination-item"]',
                '.next-pagination-list button'
            ]
            
            max_page = 1
            
            for selector in pagination_selectors:
                try:
                    items = self._driver.find_elements(By.CSS_SELECTOR, selector)
                    for item in items:
                        try:
                            text = item.text.strip()
                            if text.isdigit():
                                page_num = int(text)
                                if page_num > max_page:
                                    max_page = page_num
                        except:
                            continue
                    
                    if max_page > 1:
                        logger.info(f"Found {max_page} total pages")
                        return max_page
                except:
                    continue
            
            # Alternative: Try to find total from text
            try:
                page_source = self._driver.page_source
                # Look for patterns like "Page 1 of 138" or "1-20 of 4978"
                patterns = [
                    r'Page\s+(\d+)\s+of\s+(\d+)',
                    r'(\d+)-(\d+)\s+of\s+(\d+)',
                    r'of\s+(\d+)\s+pages?',
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, page_source, re.IGNORECASE)
                    if match:
                        # Get the last number (total pages)
                        total = int(match.group(-1))
                        if total > 1:
                            logger.info(f"Found {total} total pages")
                        return total
            except:
                pass
            
            return 1
            
        except Exception as e:
            logger.error(f"Error getting total pages: {e}")
            return 1
    
    def _extract_reviews_from_page(self) -> List[str]:
        """Extract reviews from current page"""
        comments = []
        
        try:
            # Wait for content to load
            time.sleep(2)
            
            # Try multiple selectors for review content
            selectors = [
                '.review-content',
                '.item-content .content',
                '.pdp-review-item .review-content',
                '.content .content',
                'div.content',
                '.review-item .content',
                '.pdp-review-item .content',
                '.item-review .content',
                '.review-text',
                '.comment-text'
            ]
            
            for selector in selectors:
                try:
                    elements = self._driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and len(text) > 3:
                            # Clean the text
                            text = ' '.join(text.split())
                            # Skip if it's just metadata
                            skip_words = ['stars', 'star', 'rating', 'verified', 'purchase']
                            if not any(word in text.lower() for word in skip_words):
                                comments.append(text)
                    if comments:
                        logger.info(f"Found {len(comments)} comments with selector: {selector}")
                        break
                except:
                    continue
            
            return comments
            
        except Exception as e:
            logger.error(f"Error extracting comments: {e}")
            return []
    
    def _go_to_page(self, page_num: int) -> bool:
        """Navigate to a specific page using JavaScript"""
        try:
            # Try to find and click the page number
            page_buttons = self._driver.find_elements(By.CSS_SELECTOR, 
                '.next-pagination-item, .pagination-item, button[class*="pagination-item"]')
            
            for button in page_buttons:
                try:
                    if button.text.strip() == str(page_num):
                        if button.is_displayed() and button.is_enabled():
                            # Use JavaScript to click (bypasses interception)
                            self._driver.execute_script("arguments[0].scrollIntoView(true);", button)
                            time.sleep(0.5)
                            self._driver.execute_script("arguments[0].click();", button)
                            time.sleep(3)
                            logger.info(f"Navigated to page {page_num}")
                            return True
                except:
                    continue
            
            # Alternative: Try to use next button
            try:
                next_buttons = self._driver.find_elements(By.CSS_SELECTOR, 
                    '.next-pagination-item.next, .pagination-next, button[class*="next"]:not([disabled])')
                
                for btn in next_buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        self._driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                        time.sleep(0.5)
                        self._driver.execute_script("arguments[0].click();", btn)
                        time.sleep(3)
                        logger.info(f"Clicked next button")
                        return True
            except:
                pass
            
            return False
            
        except Exception as e:
            logger.error(f"Error navigating to page {page_num}: {e}")
            return False
    
    def scrape_product(self, product_url: str) -> Product:

        self._init_csv()
        self._setup_browser(headless=False)

        unique_review_texts: set[str] = set()
        review_count = 0
        consecutive_empty_pages = 0
        reviews: list[ScrapedReview] = []
        
        try:
            # Open product page
            logger.info(f"Opening product page: {product_url}")
            self._driver.get(product_url)
            time.sleep(5)
            
            # Wait for user to apply filter manually
            if not self._wait_for_manual_filter():
                self._driver.quit()
                self._driver = None
                return Product(
                    product_id="",
                    product_name="",
                    product_url=product_url,
                    category=None,
                    reviews=reviews
                )
            
            # Get total pages
            total_pages = self._get_total_pages()
            logger.info(f"Total pages to scrape: {total_pages}")
            
            if total_pages <= 1:
                logger.warning("Only 1 page found or couldn't detect pagination")
            
            print("\n" + "=" * 70)
            print("Scraping in progress... Press 'Q' to stop")
            print(f"Total pages: {total_pages}")
            print("=" * 70 + "\n")
            
            current_page = 1
            
            while current_page <= total_pages:
                # Check if user wants to stop
                if self._check_stop():
                    break
                
                # If not on the right page, navigate
                if current_page > 1:
                    if not self._go_to_page(current_page):
                        logger.warning(f"Could not navigate to page {current_page}")
                        consecutive_empty_pages += 1
                        if consecutive_empty_pages >= 3:
                            logger.info("Stopping: Too many navigation failures")
                            break
                        current_page += 1
                        continue
                    else:
                        consecutive_empty_pages = 0
                
                # Extract reviews from current page
                page_review_texts = self._extract_reviews_from_page()
                
                if page_review_texts:
                    new_count = 0
                    for review_text in page_review_texts:
                        if review_text not in unique_review_texts:
                            unique_review_texts.add(review_text)
                            review_count += 1
                            new_count += 1
                            review = ScrapedReview(
                                review_text=review_text,
                                rating=None,
                                reviewer=None,
                                review_date=None
                            )
                            reviews.append(review)
                            self._save_review_to_csv(
                                review_text,
                                review_count
                            )
                    
                    logger.info(f"Created {new_count} ScrapedReview objects.")
                    consecutive_empty_pages = 0
                    
                    # Show progress every 10 pages
                    if current_page % 10 == 0:
                        print(f"Progress: Page {current_page}/{total_pages}, {review_count} reviews scraped")
                else:
                    logger.warning(f"No reviews found on page {current_page}")
                    consecutive_empty_pages += 1
                    
                    # If we hit 5 consecutive empty pages, stop
                    if consecutive_empty_pages >= 5:
                        logger.info(f"Stopping: No reviews for {consecutive_empty_pages} consecutive pages")
                        break
                
                current_page += 1
                
                # Small delay between pages
                time.sleep(2)
            
            logger.info(f"Scraping complete! Total reviews: {review_count}")
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            
        finally:
            if self._driver:
                self._driver.quit()
                self._driver = None
                
        logger.info("Scraping completed successfully.")
        return Product(
            product_id="",
            product_name="",
            product_url=product_url,
            category=None,
            reviews=reviews
        )