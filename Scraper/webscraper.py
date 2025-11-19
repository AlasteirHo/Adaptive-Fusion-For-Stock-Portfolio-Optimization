"""
INVESTING.COM NEWS SCRAPER - ESSENTIAL VERSION
One CSV file per ticker, anti-detection, auto-resume

Usage:
    python investing_scraper.py
"""

import time
import random
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os

class InvestingComScraper:
    """Scrape Investing.com news with one CSV per ticker"""
    
    def __init__(self, ticker, investing_url, cutoff_date='2024-10-10', max_pages=500):
        """
        Args:
            ticker: Stock symbol (e.g., 'NVDA')
            investing_url: Investing.com news URL
            cutoff_date: Stop scraping when articles older than this date (YYYY-MM-DD)
            max_pages: Safety limit to prevent infinite scraping
        """
        self.ticker = ticker.upper()
        self.base_url = investing_url
        self.cutoff_date = pd.to_datetime(cutoff_date)
        self.max_pages = max_pages
        
        # Create output directory
        self.output_dir = f'news_data/{self.ticker}'
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.articles = []
        self.driver = None
        
        print(f"\n{'='*70}")
        print(f"SCRAPING: {self.ticker}")
        print(f"{'='*70}")
        print(f"Output: {self.output_dir}/{self.ticker}_news.csv")
        print(f"Cutoff date: {self.cutoff_date.date()}")
        print(f"Will stop when articles older than {self.cutoff_date.date()} are found")
        print(f"{'='*70}\n")
    
    def setup_driver(self):
        """Initialize Chrome with anti-detection"""
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        # Comment out to see browser (helpful for debugging)
        # options.add_argument('--headless=new')
        
        self.driver = uc.Chrome(options=options)
        print("[READY] Browser ready\n")
    
    def get_page_url(self, page_num):
        """Get URL for specific page"""
        return self.base_url if page_num == 1 else f"{self.base_url}/{page_num}"
    
    def extract_articles(self):
        """Extract articles from current page"""
        articles = []
        
        try:
            # Wait for articles
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='article-title-link']"))
            )
            
            time.sleep(random.uniform(2, 4))
            
            # Scroll to load content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Find all article links
            links = self.driver.find_elements(By.CSS_SELECTOR, "[data-test='article-title-link']")
            print(f"  Found {len(links)} articles")
            
            for idx, link in enumerate(links, 1):
                try:
                    title = link.text.strip()
                    url = link.get_attribute('href')
                    
                    if not title or not url:
                        continue
                    
                    # Find parent container
                    parent = None
                    for _ in range(5):
                        try:
                            parent = link.find_element(By.XPATH, "./ancestor::*[.//time[@data-test='article-publish-date']]")
                            break
                        except:
                            continue
                    
                    if not parent:
                        parent = link.find_element(By.XPATH, "./../..")
                    
                    # Get publish date
                    publish_date = None
                    relative_time = None
                    try:
                        time_elem = parent.find_element(By.CSS_SELECTOR, "time[data-test='article-publish-date']")
                        publish_date = time_elem.get_attribute('datetime')
                        relative_time = time_elem.text.strip()
                    except:
                        try:
                            all_times = self.driver.find_elements(By.CSS_SELECTOR, "time[data-test='article-publish-date']")
                            if idx <= len(all_times):
                                publish_date = all_times[idx-1].get_attribute('datetime')
                                relative_time = all_times[idx-1].text.strip()
                        except:
                            pass
                    
                    # Get publisher
                    publisher = "Unknown"
                    publisher_url = None
                    try:
                        pub_elem = parent.find_element(By.CSS_SELECTOR, "[data-test='article-provider-link']")
                        publisher = pub_elem.text.strip()
                        publisher_url = pub_elem.get_attribute('href')
                    except:
                        try:
                            pub_elem = parent.find_element(By.CSS_SELECTOR, "a[href*='/members/contributors/']")
                            publisher = pub_elem.text.strip()
                            publisher_url = pub_elem.get_attribute('href')
                        except:
                            pass
                    
                    articles.append({
                        'ticker': self.ticker,
                        'title': title,
                        'url': url,
                        'publish_date': publish_date,
                        'relative_time': relative_time,
                        'publisher': publisher,
                        'publisher_url': publisher_url
                    })
                    
                except Exception as e:
                    continue
            
            print(f"  [OK] Extracted {len(articles)} articles")
            
        except TimeoutException:
            print(f"  [TIMEOUT]")
        except Exception as e:
            print(f"  [ERROR]: {e}")
        
        return articles
    
    def save_progress(self, page_num):
        """Save simple progress marker"""
        progress_file = f'{self.output_dir}/.last_page'
        with open(progress_file, 'w') as f:
            f.write(str(page_num))
        print(f"  [SAVED] Progress saved (page {page_num}, {len(self.articles)} articles)")
    
    def load_progress(self):
        """Load last completed page"""
        progress_file = f'{self.output_dir}/.last_page'
        
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                last_page = int(f.read().strip())
            
            print(f"[FOUND] Found previous progress:")
            print(f"   Last page: {last_page}")
            print(f"   Resume from page {last_page + 1}? (y/n): ", end='')
            
            resume = input().strip().lower()
            if resume == 'y':
                return last_page + 1
        
        return 1
    
    def scrape(self, start_page=None):
        """Main scraping method - stops when articles older than cutoff_date are found"""
        
        if start_page is None:
            start_page = self.load_progress()
        
        try:
            self.setup_driver()
            
            page = start_page
            reached_cutoff = False
            
            while page <= self.max_pages and not reached_cutoff:
                print(f"\n[Page {page}]")
                
                url = self.get_page_url(page)
                
                try:
                    self.driver.get(url)
                    print(f"  Loaded: {url}")
                    
                    time.sleep(random.uniform(3, 6))
                    
                    page_articles = self.extract_articles()
                    
                    if not page_articles:
                        print(f"  [WARNING] No articles, retrying...")
                        time.sleep(5)
                        page_articles = self.extract_articles()
                        
                        if not page_articles:
                            print(f"  [STOP] No more articles")
                            break
                    
                    # Check dates and filter articles
                    articles_to_add = []
                    for article in page_articles:
                        if article['publish_date']:
                            try:
                                article_date = pd.to_datetime(article['publish_date'])
                                
                                if article_date < self.cutoff_date:
                                    print(f"  [CUTOFF] Found article before cutoff: {article_date.date()}")
                                    reached_cutoff = True
                                    break
                                else:
                                    articles_to_add.append(article)
                            except:
                                # If date parsing fails, include the article
                                articles_to_add.append(article)
                        else:
                            # If no date, include the article
                            articles_to_add.append(article)
                    
                    self.articles.extend(articles_to_add)
                    
                    if reached_cutoff:
                        print(f"  [COMPLETE] Reached cutoff date ({self.cutoff_date.date()})")
                        print(f"  [TOTAL] Stopping scrape. Total: {len(self.articles)} articles")
                        break
                    
                    # Save progress every 10 pages
                    if page % 10 == 0:
                        self.save_progress(page)
                        # Also save CSV periodically
                        self.export_csv()
                    
                    print(f"  [TOTAL] Total: {len(self.articles)} articles")
                    
                    # Longer break every 20 pages
                    if page % 20 == 0:
                        print(f"  [BREAK] Taking a break...")
                        time.sleep(random.uniform(10, 15))
                    
                    page += 1
                    
                except Exception as e:
                    print(f"  [ERROR]: {e}")
                    page += 1
                    continue
            
            # Final save
            self.save_progress(page - 1)
            
            print(f"\n{'='*70}")
            print(f"[COMPLETE] {self.ticker}")
            print(f"{'='*70}")
            print(f"Total articles: {len(self.articles)}")
            if self.articles:
                dates = [pd.to_datetime(a['publish_date']) for a in self.articles if a['publish_date']]
                if dates:
                    print(f"Date range: {min(dates).date()} to {max(dates).date()}")
            print(f"{'='*70}\n")
            
        except KeyboardInterrupt:
            print(f"\n\n[INTERRUPTED]")
            self.save_progress(page if 'page' in locals() else start_page)
            print(f"Progress saved")
            
        finally:
            if self.driver:
                self.driver.quit()
    
    def export_csv(self):
        """Export to CSV"""
        csv_file = f'{self.output_dir}/{self.ticker}_news.csv'
        
        df = pd.DataFrame(self.articles)
        df = df.drop_duplicates(subset=['url'], keep='first')
        
        if 'publish_date' in df.columns:
            df['publish_date'] = pd.to_datetime(df['publish_date'])
            df = df.sort_values('publish_date', ascending=False)
        
        df.to_csv(csv_file, index=False, encoding='utf-8')
        
        print(f"\n[SAVED] CSV saved: {csv_file}")
        print(f"   Articles: {len(df)}")
        
        if not df.empty and df['publish_date'].notna().any():
            print(f"   Date range: {df['publish_date'].min().date()} to {df['publish_date'].max().date()}")
        
        return df


# ============================================================================
# CONFIGURATION - EDIT YOUR STOCKS HERE
# ============================================================================

STOCKS = {
    'NVDA': 'https://www.investing.com/equities/nvidia-corp-news',
    'AAPL': 'https://www.investing.com/equities/apple-computer-inc-news',
    'TSLA': 'https://www.investing.com/equities/tesla-motors-news',
    'MSFT': 'https://www.investing.com/equities/microsoft-corp-news',
    'GOOGL': 'https://www.investing.com/equities/google-inc-news',
    'META': 'https://www.investing.com/equities/facebook-inc-news',
    'AMD': 'https://www.investing.com/equities/advanced-micro-device-news',
    'JPM': 'https://www.investing.com/equities/jp-morgan-chase-news',
    'BAC': 'https://www.investing.com/equities/bank-of-america-news',
    'JNJ': 'https://www.investing.com/equities/johnson-johnson-news',
    
}


# ============================================================================
# MAIN PROGRAM
# ============================================================================

def scrape_single(ticker, url, cutoff_date='2024-10-10'):
    """Scrape a single ticker until cutoff date"""
    scraper = InvestingComScraper(ticker, url, cutoff_date)
    scraper.scrape()
    df = scraper.export_csv()
    return df


def scrape_multiple(stocks, cutoff_date='2024-10-10'):
    """Scrape multiple tickers until cutoff date"""
    results = {}
    total = len(stocks)
    
    print(f"\n{'='*70}")
    print(f"BATCH SCRAPING {total} TICKERS")
    print(f"Cutoff date: {cutoff_date}")
    print(f"{'='*70}\n")
    
    for idx, (ticker, url) in enumerate(stocks.items(), 1):
        print(f"\n{'#'*70}")
        print(f"# [{idx}/{total}] {ticker}")
        print(f"{'#'*70}\n")
        
        try:
            df = scrape_single(ticker, url, cutoff_date)
            results[ticker] = df
            print(f"[SUCCESS] {ticker}: {len(df)} articles")
        except Exception as e:
            print(f"[FAILED] {ticker} failed: {e}")
            results[ticker] = None
        
        if idx < total:
            print(f"\n{'-'*70}")
            print(f"[BREAK] 10 second break...")
            print(f"{'-'*70}")
            time.sleep(10)
    
    # Summary
    print(f"\n{'='*70}")
    print("BATCH COMPLETE")
    print(f"{'='*70}")
    successful = sum(1 for df in results.values() if df is not None)
    print(f"Successful: {successful}/{total}")
    
    for ticker, df in results.items():
        if df is not None:
            print(f"  [OK] news_data/{ticker}/{ticker}_news.csv ({len(df)} articles)")
    
    print(f"{'='*70}\n")
    
    return results


if __name__ == "__main__":
    print("\n" + "="*70)
    print("INVESTING.COM NEWS SCRAPER")
    print("="*70)
    
    # Show available tickers
    print("\nAvailable tickers in configuration:")
    for ticker in STOCKS.keys():
        print(f"  - {ticker}")
    
    print("\n" + "-"*70)
    
    # Get ticker list
    ticker_input = input("\nEnter tickers (comma-separated, e.g. NVDA,AAPL,TSLA): ").strip()
    
    if not ticker_input:
        print("Error: No tickers entered")
        exit(1)
    
    # Parse tickers
    requested_tickers = [t.strip().upper() for t in ticker_input.split(',')]
    
    # Validate tickers
    invalid_tickers = [t for t in requested_tickers if t not in STOCKS]
    if invalid_tickers:
        print(f"\nError: Unknown tickers: {', '.join(invalid_tickers)}")
        print(f"Available tickers: {', '.join(STOCKS.keys())}")
        exit(1)
    
    # Get cutoff date
    cutoff = input("\nCutoff date (YYYY-MM-DD, default 2024-10-10): ").strip()
    cutoff_date = cutoff if cutoff else '2024-10-10'
    
    # Validate date format
    try:
        pd.to_datetime(cutoff_date)
    except:
        print(f"Error: Invalid date format: {cutoff_date}")
        print("Use format: YYYY-MM-DD")
        exit(1)
    
    # Create stocks dict with requested tickers only
    stocks_to_scrape = {ticker: STOCKS[ticker] for ticker in requested_tickers}
    
    # Confirmation
    print("\n" + "="*70)
    print("SCRAPING CONFIGURATION")
    print("="*70)
    print(f"Tickers: {', '.join(requested_tickers)} ({len(requested_tickers)} total)")
    print(f"Cutoff date: {cutoff_date}")
    print(f"Will scrape articles from {cutoff_date} to present")
    print("="*70)
    
    confirm = input("\nContinue? (y/n): ").strip().lower()
    
    if confirm == 'y':
        scrape_multiple(stocks_to_scrape, cutoff_date)
    else:
        print("Cancelled")