import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from datetime import datetime
import feedparser
import logging
import os
from urllib.parse import urljoin, urlparse

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Updated cryptocurrency news sources with working RSS feeds and more sites
CRYPTO_SOURCES = {
    'rss_feeds': {
        # Major crypto news sites
        'CoinDesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
        'CoinTelegraph': 'https://cointelegraph.com/rss',
        'Bitcoin.com': 'https://news.bitcoin.com/feed/',
        'Bitcoinist': 'https://bitcoinist.com/feed/',
        'CryptoSlate': 'https://cryptoslate.com/feed/',
        'The Daily Hodl': 'https://dailyhodl.com/feed/',
        'U.Today': 'https://u.today/rss',
        'BeInCrypto': 'https://beincrypto.com/feed/',
        'CryptoPotato': 'https://cryptopotato.com/feed/',
        'CoinGape': 'https://coingape.com/feed/',
        'NewsBTC': 'https://www.newsbtc.com/feed/',
        'AMBCrypto': 'https://ambcrypto.com/feed/',
        'Crypto Briefing': 'https://cryptobriefing.com/feed/',
        'The Block': 'https://www.theblockcrypto.com/rss.xml',
        'Decrypt': 'https://decrypt.co/feed',
        'CryptoGlobe': 'https://www.cryptoglobe.com/latest/feed/',
        'Blockonomi': 'https://blockonomi.com/feed/',
        'CoinJournal': 'https://coinjournal.net/feed/',
        'CryptoNews Australia': 'https://cryptonews.com.au/feed/',
        'Crypto Daily': 'https://cryptodaily.co.uk/feed',
        'InsideBitcoins': 'https://insidebitcoins.com/feed',
        'Live Bitcoin News': 'https://www.livebitcoinnews.com/feed/',
        'CoinSpeaker': 'https://www.coinspeaker.com/feed/',
        'Finance Magnates': 'https://www.financemagnates.com/cryptocurrency/feed/',
        'ZyCrypto': 'https://zycrypto.com/feed/'
    },
    'web_scraping': {
        'CoinMarketCap News': {
            'url': 'https://coinmarketcap.com/headlines/news/',
            'container_selector': 'article, div[class*="article"], a[href*="/headlines/news/"]',
            'title_selector': 'h3, h2, p[class*="title"]',
            'link_selector': 'a[href*="/headlines/news/"]',
            'time_selector': 'span[class*="time"], time',
            'base_url': 'https://coinmarketcap.com',
            'use_selenium': True,
            'cloudflare': True
        },
        'CoinGecko News': {
            'url': 'https://www.coingecko.com/en/news',
            'container_selector': 'article, div[class*="news-item"]',
            'title_selector': 'h2, h3, a[class*="title"]',
            'link_selector': 'a[href*="/en/news/"]',
            'time_selector': 'time, span[class*="date"]',
            'base_url': 'https://www.coingecko.com',
            'use_selenium': True,
            'wait_for': 'article'
        },
        'CryptoCompare': {
            'url': 'https://www.cryptocompare.com/news/list/latest/',
            'container_selector': 'div.news-item, article',
            'title_selector': 'h3, a.article-title',
            'link_selector': 'a[href*="/news/"]',
            'time_selector': 'time, span.date',
            'base_url': 'https://www.cryptocompare.com',
            'use_selenium': False
        }
    }
}


class CryptoNewsScraper:
    def __init__(self):
        self.news_data = []
        self.selenium_driver = None

    def get_selenium_driver(self):
        """Initialize and return a Selenium WebDriver instance"""
        if not self.selenium_driver:
            options = Options()
            options.add_argument("--headless")
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument(
                '--disable-blink-features=AutomationControlled')
            options.add_experimental_option(
                "excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--window-size=1920,1080')
            options.add_argument(
                'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            try:
                self.selenium_driver = webdriver.Chrome(options=options)
                # Execute script to remove webdriver property
                self.selenium_driver.execute_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            except Exception as e:
                logging.error(f"Failed to initialize Chrome driver: {e}")
                logging.info(
                    "Make sure you have Chrome and ChromeDriver installed")
                return None

        return self.selenium_driver

    def close_selenium(self):
        """Close Selenium driver"""
        if self.selenium_driver:
            self.selenium_driver.quit()
            self.selenium_driver = None

    def get_soup(self, url, use_selenium=False):
        """Get BeautifulSoup object from URL with enhanced headers and error handling"""
        try:
            if use_selenium:
                driver = self.get_selenium_driver()
                if not driver:
                    return None

                driver.get(url)
                # Wait for content to load with a more general condition
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                except:
                    pass

                # Scroll to load more content
                driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(3)

                soup = BeautifulSoup(driver.page_source, 'html.parser')
            else:
                # Enhanced headers to avoid 403 errors
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0',
                    'Referer': 'https://www.google.com/'
                }

                # Create a session for better connection handling
                session = requests.Session()
                session.headers.update(headers)

                # Add retry logic
                for attempt in range(3):
                    try:
                        response = session.get(
                            url, timeout=15, allow_redirects=True)
                        response.raise_for_status()
                        break
                    except requests.exceptions.HTTPError as e:
                        if e.response.status_code == 403:
                            logging.warning(
                                f"403 error for {url}, trying with different user agent...")
                            # Try with a different user agent
                            user_agents = [
                                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
                                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                            ]
                            session.headers['User-Agent'] = user_agents[attempt %
                                                                        len(user_agents)]
                            if attempt == 2:  # Last attempt
                                raise
                            time.sleep(2)  # Wait before retry
                        else:
                            raise

                soup = BeautifulSoup(response.text, 'html.parser')

            return soup

        except Exception as e:
            logging.error(f"Error fetching {url}: {e}")
            return None

    def scrape_rss_feeds(self):
        """Scrape news from RSS feeds"""
        logging.info("Scraping RSS feeds...")

        for source, feed_url in CRYPTO_SOURCES['rss_feeds'].items():
            try:
                logging.info(f"Fetching RSS feed from {source}...")
                feed = feedparser.parse(feed_url)

                if not feed.entries:
                    logging.warning(f"No entries found in {source} RSS feed")
                    continue

                articles_added = 0
                for entry in feed.entries[:15]:  # Get latest 15 articles
                    try:
                        # Extract publication date
                        published = entry.get(
                            'published', entry.get('updated', ''))
                        if published:
                            try:
                                # Parse the date
                                pub_date = datetime.strptime(
                                    published, '%a, %d %b %Y %H:%M:%S %z')
                                published = pub_date.isoformat()
                            except:
                                published = published

                        # Clean summary
                        summary = entry.get('summary', '')
                        if summary:
                            # Remove HTML tags
                            soup = BeautifulSoup(summary, 'html.parser')
                            summary = soup.get_text(
                            )[:200] + '...' if len(soup.get_text()) > 200 else soup.get_text()

                        article = {
                            'title': entry.get('title', 'No title'),
                            'link': entry.get('link', ''),
                            'source': source,
                            'sourceUrl': feed_url,
                            'timestamp': published,
                            'excerpt': summary,
                            'categories': self.determine_categories(entry.get('title', '') + ' ' + summary),
                            'tags': self.extract_tags(entry.get('title', '') + ' ' + summary)
                        }

                        self.news_data.append(article)
                        articles_added += 1

                    except Exception as e:
                        logging.error(
                            f"Error processing entry from {source}: {e}")

                logging.info(
                    f"✓ Added {articles_added} articles from {source} RSS")

            except Exception as e:
                logging.error(f"Error scraping RSS feed for {source}: {e}")

    def scrape_websites(self):
        """Scrape news directly from websites using updated selectors"""
        logging.info("Scraping websites directly...")

        for source, config in CRYPTO_SOURCES['web_scraping'].items():
            try:
                logging.info(f"Scraping {source} website...")
                soup = self.get_soup(
                    config['url'], config.get('use_selenium', False))
                if not soup:
                    continue

                # Try multiple possible selectors for articles
                articles = []

                # First try the configured selector
                if config.get('container_selector'):
                    articles = soup.select(config['container_selector'])

                # If no articles found, try common selectors
                if not articles:
                    common_selectors = [
                        'article',
                        'div[class*="article"]',
                        'div[class*="news"]',
                        'div[class*="post"]',
                        'div[class*="card"]',
                        'div[class*="item"]'
                    ]
                    for selector in common_selectors:
                        articles = soup.select(selector)
                        if articles:
                            logging.info(
                                f"Found articles using selector: {selector}")
                            break

                if not articles:
                    logging.warning(f"No articles found on {source}")
                    continue

                articles_added = 0
                for article in articles[:10]:
                    try:
                        # Extract title
                        title = None
                        # Try configured selector first
                        if config.get('title_selector'):
                            title_elem = article.select_one(
                                config['title_selector'])
                            if title_elem:
                                title = title_elem.get_text(strip=True)

                        # If no title found, try common selectors
                        if not title:
                            for selector in ['h1', 'h2', 'h3', 'h4', 'a[class*="title"]', 'a']:
                                title_elem = article.select_one(selector)
                                if title_elem:
                                    title = title_elem.get_text(strip=True)
                                    # Ensure it's a real title
                                    if title and len(title) > 10:
                                        break

                        if not title or len(title) < 10:
                            continue

                        # Extract link
                        link = None
                        link_elem = article.select_one('a[href]')
                        if link_elem:
                            link = link_elem.get('href', '')
                            # Make absolute URL
                            if link and not link.startswith('http'):
                                link = urljoin(config.get(
                                    'base_url', config['url']), link)

                        if not link:
                            continue

                        # Extract time
                        time_text = 'Recently'
                        time_elem = article.select_one(
                            'time, span[class*="date"], span[class*="time"]')
                        if time_elem:
                            time_text = time_elem.get_text(strip=True)

                        # Extract excerpt
                        excerpt = ''
                        for selector in ['p', 'div[class*="excerpt"]', 'div[class*="summary"]']:
                            excerpt_elem = article.select_one(selector)
                            if excerpt_elem:
                                excerpt = excerpt_elem.get_text(strip=True)[
                                    :200]
                                break

                        article_data = {
                            'title': title,
                            'link': link,
                            'source': source,
                            'sourceUrl': config['url'],
                            'timestamp': datetime.now().isoformat(),
                            'excerpt': excerpt,
                            'categories': self.determine_categories(title),
                            'tags': self.extract_tags(title + ' ' + excerpt)
                        }

                        self.news_data.append(article_data)
                        articles_added += 1

                    except Exception as e:
                        logging.error(
                            f"Error parsing article from {source}: {e}")

                logging.info(
                    f"✓ Added {articles_added} articles from {source} website")

            except Exception as e:
                logging.error(f"Error scraping website for {source}: {e}")

    def determine_categories(self, text):
        """Determine article categories based on content"""
        text_lower = text.lower()
        categories = []

        category_keywords = {
            'bitcoin': ['bitcoin', 'btc', 'satoshi', 'lightning network'],
            'ethereum': ['ethereum', 'eth', 'vitalik', 'smart contract', 'erc-20'],
            'defi': ['defi', 'decentralized finance', 'yield', 'liquidity', 'dex', 'amm'],
            'nft': ['nft', 'non-fungible', 'opensea', 'digital art', 'collectible'],
            'analysis': ['analysis', 'technical', 'chart', 'prediction', 'forecast']
        }

        for category, keywords in category_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                categories.append(category)

        if not categories:
            categories.append('crypto')

        return categories

    def extract_tags(self, text):
        """Extract relevant crypto tags from text"""
        text_lower = text.lower()
        tags = []

        crypto_keywords = {
            'Bitcoin': ['bitcoin', 'btc', 'satoshi', 'lightning network'],
            'Ethereum': ['ethereum', 'eth', 'vitalik', 'smart contract'],
            'DeFi': ['defi', 'yield', 'liquidity', 'uniswap', 'aave'],
            'NFT': ['nft', 'opensea', 'bored ape', 'cryptopunk'],
            'Trading': ['trading', 'price', 'market', 'bullish', 'bearish'],
            'Blockchain': ['blockchain', 'crypto', 'ledger'],
            'Altcoin': ['altcoin', 'token', 'binance', 'cardano', 'solana'],
            'Web3': ['web3', 'dapp', 'metaverse'],
            'Mining': ['mining', 'hashrate', 'proof of work'],
            'Regulation': ['regulation', 'sec', 'legal', 'government'],
            'Stablecoin': ['stablecoin', 'usdt', 'usdc', 'tether'],
            'Exchange': ['exchange', 'binance', 'coinbase', 'kraken'],
            'AI': ['ai', 'artificial intelligence', 'chatgpt', 'machine learning'],
            'Layer2': ['layer 2', 'l2', 'polygon', 'arbitrum', 'optimism']
        }

        for tag, keywords in crypto_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(tag)

        return list(set(tags))[:5]  # Return max 5 unique tags

    def scrape_all(self):
        """Run all scraping methods"""
        logging.info("Starting crypto news aggregation...")

        # Scrape RSS feeds first (more reliable)
        self.scrape_rss_feeds()

        # Then scrape websites
        self.scrape_websites()

        # Close Selenium driver
        self.close_selenium()

        # Remove duplicates based on title
        unique_news = []
        seen_titles = set()

        for article in self.news_data:
            # Normalize title for comparison
            normalized_title = article['title'].lower().strip()
            if normalized_title not in seen_titles and len(normalized_title) > 10:
                seen_titles.add(normalized_title)
                unique_news.append(article)

        self.news_data = unique_news

        # Sort by timestamp (most recent first)
        self.news_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        logging.info(
            f"✓ Total unique articles collected: {len(self.news_data)}")

        return self.news_data

    def save_to_hugo_format(self, output_dir='../data'):
        """Save data in Hugo-compatible format"""
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Categorize articles
        hugo_data = {
            'latest': self.news_data[:20],
            'featured': [a for a in self.news_data if any(cat in ['bitcoin', 'ethereum'] for cat in a.get('categories', []))][:5],
            'bitcoin': [a for a in self.news_data if 'bitcoin' in a.get('categories', [])][:10],
            'ethereum': [a for a in self.news_data if 'ethereum' in a.get('categories', [])][:10],
            'defi': [a for a in self.news_data if 'defi' in a.get('categories', [])][:10],
            'nft': [a for a in self.news_data if 'nft' in a.get('categories', [])][:10],
            'all': self.news_data,
            'last_updated': datetime.now().isoformat()
        }

        # Save to JSON file
        output_path = os.path.join(output_dir, 'aggregated_news.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(hugo_data, f, ensure_ascii=False, indent=2)

        logging.info(f"✓ Data saved to {output_path}")


def main():
    """Main function to run the scraper"""
    scraper = CryptoNewsScraper()

    # Scrape all sources
    news_data = scraper.scrape_all()

    if news_data:
        # Save in Hugo format
        scraper.save_to_hugo_format()

        # Print sample results
        print("\n--- Sample Results ---")
        for i, article in enumerate(news_data[:5], 1):
            print(f"\n{i}. {article['title']}")
            print(f"   Source: {article['source']}")
            print(f"   Link: {article['link']}")
            print(f"   Categories: {', '.join(article.get('categories', []))}")
            print(f"   Tags: {', '.join(article.get('tags', []))}")
    else:
        print("\nNo news data collected. Please check the logs for errors.")


if __name__ == '__main__':
    main()
