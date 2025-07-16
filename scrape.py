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

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Cryptocurrency news sources with their RSS feeds and web scraping configs
CRYPTO_SOURCES = {
    'rss_feeds': {
        'CoinDesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
        'CoinTelegraph': 'https://cointelegraph.com/rss',
        'CryptoSlate': 'https://cryptoslate.com/feed/',
        'The Block': 'https://www.theblock.co/rss.xml',
        'Decrypt': 'https://decrypt.co/feed',
        'Bitcoin Magazine': 'https://bitcoinmagazine.com/feed',
        'CryptoNews': 'https://cryptonews.com/news/feed/',
        'NewsBTC': 'https://www.newsbtc.com/feed/',
        'Bitcoinist': 'https://bitcoinist.com/feed/',
        'CryptoPotato': 'https://cryptopotato.com/feed/'
    },
    'web_scraping': {
        'CoinDesk': {
            'url': 'https://www.coindesk.com/livewire/',
            'article_selector': 'div.article-card',
            'title_selector': 'h3',
            'link_selector': 'a',
            'time_selector': 'time',
            'use_selenium': True
        },
        'CoinTelegraph': {
            'url': 'https://cointelegraph.com/tags/bitcoin',
            'article_selector': 'article.post-card',
            'title_selector': 'h2.post-card__title',
            'link_selector': 'a.post-card__title-link',
            'time_selector': 'time.post-card__date',
            'use_selenium': True
        },
        'CryptoSlate': {
            'url': 'https://cryptoslate.com/news/',
            'article_selector': 'article.post',
            'title_selector': 'h2.title',
            'link_selector': 'a',
            'time_selector': 'span.date',
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
            options.add_argument('--window-size=1920,1080')
            options.add_argument(
                'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            try:
                self.selenium_driver = webdriver.Chrome(options=options)
            except Exception as e:
                logging.error(f"Failed to initialize Chrome driver: {e}")
                return None

        return self.selenium_driver

    def close_selenium(self):
        """Close Selenium driver"""
        if self.selenium_driver:
            self.selenium_driver.quit()
            self.selenium_driver = None

    def get_soup(self, url, use_selenium=False):
        """Get BeautifulSoup object from URL"""
        try:
            if use_selenium:
                driver = self.get_selenium_driver()
                if not driver:
                    return None

                driver.get(url)
                # Wait for content to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "article"))
                )
                # Scroll to load more content
                driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                soup = BeautifulSoup(driver.page_source, 'html.parser')
            else:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
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
                feed = feedparser.parse(feed_url)

                for entry in feed.entries[:10]:  # Get latest 10 articles
                    article = {
                        'source': source,
                        'title': entry.get('title', 'No title'),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'summary': entry.get('summary', '')[:200] + '...' if entry.get('summary') else '',
                        'tags': self.extract_tags(entry.get('title', '') + ' ' + entry.get('summary', '')),
                        'scrape_time': datetime.now().isoformat()
                    }
                    self.news_data.append(article)

                logging.info(
                    f"✓ Scraped {len(feed.entries[:10])} articles from {source} RSS")

            except Exception as e:
                logging.error(f"Error scraping RSS feed for {source}: {e}")

    def scrape_websites(self):
        """Scrape news directly from websites"""
        logging.info("Scraping websites...")

        for source, config in CRYPTO_SOURCES['web_scraping'].items():
            try:
                soup = self.get_soup(
                    config['url'], config.get('use_selenium', False))
                if not soup:
                    continue

                articles = soup.select(config['article_selector'])[:10]

                for article in articles:
                    try:
                        # Extract title
                        title_elem = article.select_one(
                            config['title_selector'])
                        title = title_elem.get_text(
                            strip=True) if title_elem else 'No title'

                        # Extract link
                        link_elem = article.select_one(config['link_selector'])
                        if link_elem:
                            link = link_elem.get('href', '')
                            if link and not link.startswith('http'):
                                link = f"https://{source.lower().replace(' ', '')}.com{link}"
                        else:
                            link = ''

                        # Extract time
                        time_elem = article.select_one(
                            config.get('time_selector', 'time'))
                        published = time_elem.get_text(
                            strip=True) if time_elem else 'Unknown'

                        article_data = {
                            'source': source,
                            'title': title,
                            'link': link,
                            'published': published,
                            'summary': '',
                            'tags': self.extract_tags(title),
                            'scrape_time': datetime.now().isoformat()
                        }

                        self.news_data.append(article_data)

                    except Exception as e:
                        logging.error(
                            f"Error parsing article from {source}: {e}")

                logging.info(
                    f"✓ Scraped {len(articles)} articles from {source} website")

            except Exception as e:
                logging.error(f"Error scraping website for {source}: {e}")

    def extract_tags(self, text):
        """Extract relevant crypto tags from text"""
        text = text.lower()
        tags = []

        crypto_keywords = {
            'bitcoin': ['bitcoin', 'btc', 'satoshi'],
            'ethereum': ['ethereum', 'eth', 'vitalik'],
            'defi': ['defi', 'decentralized finance', 'yield', 'liquidity'],
            'nft': ['nft', 'non-fungible', 'opensea', 'digital art'],
            'blockchain': ['blockchain', 'distributed ledger', 'consensus'],
            'regulation': ['regulation', 'sec', 'legal', 'compliance'],
            'trading': ['trading', 'exchange', 'market', 'price'],
            'mining': ['mining', 'miner', 'hashrate', 'proof of work'],
            'web3': ['web3', 'decentralized web', 'dapp'],
            'altcoin': ['altcoin', 'alt', 'token'],
            'stablecoin': ['stablecoin', 'usdt', 'usdc', 'dai'],
            'metaverse': ['metaverse', 'virtual world', 'digital realm']
        }

        for tag, keywords in crypto_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(tag)

        return tags[:5]  # Return max 5 tags

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
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                unique_news.append(article)

        self.news_data = unique_news

        # Sort by scrape time (most recent first)
        self.news_data.sort(key=lambda x: x['scrape_time'], reverse=True)

        logging.info(
            f"✓ Total unique articles collected: {len(self.news_data)}")

        return self.news_data

    def save_to_json(self, filename='crypto_news.json'):
        """Save scraped data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.news_data, f, ensure_ascii=False, indent=2)
        logging.info(f"✓ Data saved to {filename}")

    def save_to_html(self, filename='crypto_news.html'):
        """Generate an HTML file with the news"""
        html_template = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Crypto News Aggregator</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .article { background: white; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .source { color: #007bff; font-weight: bold; }
                .title { font-size: 18px; margin: 10px 0; }
                .link { color: #28a745; text-decoration: none; }
                .tags { margin-top: 10px; }
                .tag { background: #e9ecef; padding: 5px 10px; border-radius: 15px; margin-right: 5px; font-size: 12px; }
                .time { color: #666; font-size: 14px; }
            </style>
        </head>
        <body>
            <h1>Latest Cryptocurrency News</h1>
            <p>Last updated: {update_time}</p>
            {articles}
        </body>
        </html>
        '''

        articles_html = ''
        for article in self.news_data[:50]:  # Show top 50 articles
            tags_html = ''.join(
                [f'<span class="tag">{tag}</span>' for tag in article['tags']])
            articles_html += f'''
            <div class="article">
                <span class="source">{article['source']}</span> • <span class="time">{article['published']}</span>
                <h3 class="title">{article['title']}</h3>
                <a class="link" href="{article['link']}" target="_blank">Read full article →</a>
                <div class="tags">{tags_html}</div>
            </div>
            '''

        html_content = html_template.format(
            update_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            articles=articles_html
        )

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logging.info(f"✓ HTML file generated: {filename}")


def main():
    """Main function to run the scraper"""
    scraper = CryptoNewsScraper()

    # Scrape all sources
    news_data = scraper.scrape_all()

    # Save results
    scraper.save_to_json()
    scraper.save_to_html()

    # Print sample results
    print("\n--- Sample Results ---")
    for article in news_data[:5]:
        print(f"\nSource: {article['source']}")
        print(f"Title: {article['title']}")
        print(f"Link: {article['link']}")
        print(f"Tags: {', '.join(article['tags'])}")
        print("-" * 50)


if __name__ == '__main__':
    main()
