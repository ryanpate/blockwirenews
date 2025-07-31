import requests
from bs4 import BeautifulSoup
import json
import datetime
import time
from typing import List, Dict
import hashlib
import feedparser
import ssl
import urllib3

# Fix SSL certificate issue on macOS
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CryptoNewsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.articles = []

    def generate_id(self, url: str) -> str:
        """Generate unique ID for article based on URL"""
        return hashlib.md5(url.encode()).hexdigest()[:8]

    def clean_html(self, text: str) -> str:
        """Remove HTML tags from text"""
        return BeautifulSoup(text, 'html.parser').get_text().strip()

    def scrape_rss_feed(self, feed_url: str, source_name: str, limit: int = 10) -> List[Dict]:
        """Parse RSS feed and extract articles"""
        articles = []
        try:
            print(f"Fetching RSS feed from {source_name}...")
            feed = feedparser.parse(feed_url)

            if feed.bozo:
                print(f"Warning: Feed parsing issues for {source_name}")

            for entry in feed.entries[:limit]:
                try:
                    # Extract article data
                    title = entry.get('title', 'No title')
                    link = entry.get('link', '')

                    # Get summary/description
                    summary = ''
                    if hasattr(entry, 'summary'):
                        summary = self.clean_html(entry.summary)
                    elif hasattr(entry, 'description'):
                        summary = self.clean_html(entry.description)

                    # Truncate summary to reasonable length
                    if len(summary) > 200:
                        summary = summary[:197] + '...'

                    # Get publication date
                    published = datetime.datetime.now().isoformat()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime.datetime(
                            *entry.published_parsed[:6]).isoformat()
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published = datetime.datetime(
                            *entry.updated_parsed[:6]).isoformat()

                    article = {
                        'id': self.generate_id(link),
                        'title': title,
                        'url': link,
                        'summary': summary if summary else title,
                        'source': source_name,
                        'published': published,
                        'scraped_at': datetime.datetime.now().isoformat()
                    }
                    articles.append(article)

                except Exception as e:
                    print(f"Error parsing entry from {source_name}: {e}")
                    continue

            print(
                f"Successfully scraped {len(articles)} articles from {source_name}")

        except Exception as e:
            print(f"Error fetching RSS feed from {source_name}: {e}")

        return articles

    def scrape_cryptopanic_api(self) -> List[Dict]:
        """Fetch news from CryptoPanic API (no auth required for public posts)"""
        articles = []
        try:
            print("Fetching from CryptoPanic API...")
            url = "https://cryptopanic.com/api/v1/posts/?auth_token=YOUR_TOKEN&public=true"
            # Note: CryptoPanic works without auth token for public posts
            url = "https://cryptopanic.com/api/v1/posts/?public=true&limit=10"

            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()

                for post in data.get('results', [])[:10]:
                    article = {
                        'id': self.generate_id(post.get('url', '')),
                        'title': post.get('title', 'No title'),
                        'url': post.get('url', ''),
                        # CryptoPanic doesn't provide summaries
                        'summary': post.get('title', '')[:200],
                        'source': post.get('source', {}).get('title', 'CryptoPanic'),
                        'published': post.get('published_at', datetime.datetime.now().isoformat()),
                        'scraped_at': datetime.datetime.now().isoformat()
                    }
                    articles.append(article)

                print(
                    f"Successfully scraped {len(articles)} articles from CryptoPanic")
            else:
                print(
                    f"CryptoPanic API returned status code: {response.status_code}")

        except Exception as e:
            print(f"Error fetching from CryptoPanic API: {e}")

        return articles

    def scrape_newsapi(self) -> List[Dict]:
        """Fetch crypto news from NewsAPI (requires free API key)"""
        articles = []
        try:
            # Note: Get free API key from https://newsapi.org/
            api_key = "YOUR_NEWSAPI_KEY"  # Replace with actual key
            url = f"https://newsapi.org/v2/everything?q=cryptocurrency+OR+bitcoin+OR+ethereum&sortBy=publishedAt&language=en&apiKey={api_key}"

            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()

                for item in data.get('articles', [])[:10]:
                    article = {
                        'id': self.generate_id(item.get('url', '')),
                        'title': item.get('title', 'No title'),
                        'url': item.get('url', ''),
                        'summary': item.get('description', '')[:200] if item.get('description') else item.get('title', ''),
                        'source': item.get('source', {}).get('name', 'News'),
                        'published': item.get('publishedAt', datetime.datetime.now().isoformat()),
                        'scraped_at': datetime.datetime.now().isoformat()
                    }
                    articles.append(article)

                print(
                    f"Successfully scraped {len(articles)} articles from NewsAPI")
            else:
                print(f"NewsAPI returned status code: {response.status_code}")

        except Exception as e:
            print(f"Error fetching from NewsAPI: {e}")

        return articles

    def scrape_all(self) -> List[Dict]:
        """Scrape all configured news sources"""
        print("Starting cryptocurrency news scraping...")
        print("=" * 50)

        # RSS Feeds that work reliably
        rss_feeds = {
            'CoinDesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
            'Cointelegraph': 'https://cointelegraph.com/rss',
            'Bitcoin.com': 'https://news.bitcoin.com/feed/',
            'Decrypt': 'https://decrypt.co/feed',
            'CryptoSlate': 'https://cryptoslate.com/feed/',
            'Bitcoin Magazine': 'https://bitcoinmagazine.com/feed',
            'CoinJournal': 'https://coinjournal.net/news/feed/',
            'Crypto News': 'https://crypto.news/feed/',
            'BeInCrypto': 'https://beincrypto.com/feed/',
            'Crypto Briefing': 'https://cryptobriefing.com/feed/'
        }

        # Scrape RSS feeds
        for source, feed_url in rss_feeds.items():
            articles = self.scrape_rss_feed(feed_url, source, limit=5)
            self.articles.extend(articles)
            time.sleep(0.5)  # Be respectful to servers

        # Try CryptoPanic API (works without auth)
        self.articles.extend(self.scrape_cryptopanic_api())

        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        for article in self.articles:
            if article['url'] and article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)

        # Sort by published time (newest first)
        unique_articles.sort(key=lambda x: x.get(
            'published', ''), reverse=True)

        print("=" * 50)
        print(f"Total unique articles scraped: {len(unique_articles)}")

        return unique_articles

    def save_to_json(self, filename: str = 'crypto_news.json'):
        """Save scraped articles to JSON file"""
        articles = self.scrape_all()

        data = {
            'last_updated': datetime.datetime.now().isoformat(),
            'article_count': len(articles),
            'articles': articles
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\nSaved {len(articles)} articles to {filename}")
        return filename

# Simplified version that only uses RSS feeds (most reliable)


class SimpleCryptoRSSFeedScraper:
    def __init__(self):
        # Only include feeds that are known to work
        self.feeds = {
            'CoinDesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
            'Cointelegraph': 'https://cointelegraph.com/rss',
            'Bitcoin.com': 'https://news.bitcoin.com/feed/',
            'Decrypt': 'https://decrypt.co/feed',
            'CryptoSlate': 'https://cryptoslate.com/feed/'
        }
        self.articles = []

    def generate_id(self, url: str) -> str:
        """Generate unique ID for article based on URL"""
        return hashlib.md5(url.encode()).hexdigest()[:8]

    def parse_rss_feed(self, feed_url: str, source_name: str) -> List[Dict]:
        """Parse RSS feed and extract articles"""
        articles = []
        try:
            print(f"Fetching {source_name}...")
            feed = feedparser.parse(feed_url)

            # Check if feed has entries
            if not feed.entries:
                print(f"  No entries found in {source_name} feed")
                return articles

            for entry in feed.entries[:5]:  # Get top 5 articles
                try:
                    title = entry.get('title', 'No title')
                    link = entry.get('link', '')

                    # Get summary
                    summary = ''
                    if hasattr(entry, 'summary'):
                        summary = BeautifulSoup(
                            entry.summary, 'html.parser').text.strip()
                    elif hasattr(entry, 'description'):
                        summary = BeautifulSoup(
                            entry.description, 'html.parser').text.strip()

                    # Limit summary length
                    if len(summary) > 200:
                        summary = summary[:197] + '...'

                    # Get date
                    published = datetime.datetime.now().isoformat()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime.datetime(
                            *entry.published_parsed[:6]).isoformat()

                    article = {
                        'id': self.generate_id(link),
                        'title': title,
                        'url': link,
                        'summary': summary if summary else title[:200],
                        'source': source_name,
                        'published': published,
                        'scraped_at': datetime.datetime.now().isoformat()
                    }
                    articles.append(article)

                except Exception as e:
                    print(f"  Error parsing entry: {e}")
                    continue

            print(f"  Found {len(articles)} articles")

        except Exception as e:
            print(f"  Error: {e}")

        return articles

    def scrape_all(self) -> List[Dict]:
        """Scrape all RSS feeds"""
        print("\nStarting RSS feed scraping...")
        print("-" * 40)

        for source, feed_url in self.feeds.items():
            articles = self.parse_rss_feed(feed_url, source)
            self.articles.extend(articles)
            time.sleep(0.5)  # Be respectful

        # Remove duplicates
        seen_urls = set()
        unique_articles = []
        for article in self.articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)

        # Sort by date
        unique_articles.sort(key=lambda x: x.get(
            'published', ''), reverse=True)

        print("-" * 40)
        print(f"Total articles found: {len(unique_articles)}\n")

        return unique_articles

    def save_to_json(self, filename: str = 'crypto_news_rss.json'):
        """Save scraped articles to JSON file"""
        articles = self.scrape_all()

        if not articles:
            print("WARNING: No articles were scraped!")
            print("This might be due to network issues or feed changes.")
            print("\nCreating sample data for testing...")

            # Create sample data for testing
            articles = [
                {
                    'id': 'sample1',
                    'title': 'Bitcoin Reaches New Heights in 2025',
                    'url': 'https://example.com/bitcoin-news',
                    'summary': 'Bitcoin continues its bullish trend as institutional adoption grows...',
                    'source': 'Sample News',
                    'published': datetime.datetime.now().isoformat(),
                    'scraped_at': datetime.datetime.now().isoformat()
                },
                {
                    'id': 'sample2',
                    'title': 'Ethereum 3.0 Development Update',
                    'url': 'https://example.com/ethereum-news',
                    'summary': 'The Ethereum foundation announces major upgrades coming to the network...',
                    'source': 'Sample News',
                    'published': datetime.datetime.now().isoformat(),
                    'scraped_at': datetime.datetime.now().isoformat()
                }
            ]

        data = {
            'last_updated': datetime.datetime.now().isoformat(),
            'article_count': len(articles),
            'articles': articles
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(articles)} articles to {filename}")
        return filename


if __name__ == "__main__":
    # Fix SSL issues on macOS
    import ssl
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

    # Suppress SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # First, make sure feedparser is installed
    try:
        import feedparser
    except ImportError:
        print("ERROR: feedparser not installed!")
        print("Please run: pip install feedparser")
        exit(1)

    # Use the simple RSS scraper (most reliable)
    print("Crypto News Scraper v2.0")
    print("========================\n")

    scraper = SimpleCryptoRSSFeedScraper()
    scraper.save_to_json()

    # Test reading the file
    print("\nTesting JSON file...")
    try:
        with open('crypto_news_rss.json', 'r') as f:
            data = json.load(f)
            print(f"Successfully loaded {data['article_count']} articles")
            if data['articles']:
                print(f"\nFirst article: {data['articles'][0]['title']}")
    except Exception as e:
        print(f"Error reading JSON file: {e}")
