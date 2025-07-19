#!/usr/bin/env python3
"""
Cryptocurrency News Scraper for Hugo
Scrapes news from popular crypto news site RSS feeds and saves to Hugo data format
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import time
import hashlib
from urllib.parse import urlparse
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class CryptoNewsScraper:
    def __init__(self, hugo_data_dir='.. data'):
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/91.0.4472.124 Safari/537.36'
            )
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.hugo_data_dir = hugo_data_dir
        self.news_file = os.path.join(hugo_data_dir, 'aggregated_news.json')
        self.existing_articles = self.load_existing_articles()

        # Ensure data directory exists
        os.makedirs(hugo_data_dir, exist_ok=True)

    def load_existing_articles(self):
        """Load existing articles to avoid duplicates."""
        if os.path.exists(self.news_file):
            try:
                with open(self.news_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    existing = set()
                    for category_articles in data.values():
                        if isinstance(category_articles, list):
                            for article in category_articles:
                                if 'id' in article:
                                    existing.add(article['id'])
                    return existing
            except Exception as e:
                logging.error(f"Error loading existing articles: {e}")
                return set()
        return set()

    def generate_article_id(self, title, url):
        """Generate unique ID for an article."""
        content = f"{title}{url}"
        return hashlib.md5(content.encode()).hexdigest()

    def determine_categories(self, title, summary):
        """Determine article categories based on content"""
        text = f"{title} {summary}".lower()
        categories = []

        if any(word in text for word in ['bitcoin', 'btc', 'satoshi', 'lightning']):
            categories.append('bitcoin')
        if any(word in text for word in ['ethereum', 'eth', 'vitalik', 'smart contract']):
            categories.append('ethereum')
        if any(word in text for word in ['defi', 'yield', 'liquidity', 'amm', 'dex']):
            categories.append('defi')
        if any(word in text for word in ['nft', 'opensea', 'collectible', 'non-fungible']):
            categories.append('nft')
        if any(word in text for word in ['analysis', 'technical', 'chart', 'prediction']):
            categories.append('analysis')

        if not categories:
            categories.append('crypto')

        return categories

    def extract_tags(self, title, summary):
        """Extract relevant tags from content"""
        text = f"{title} {summary}".lower()
        tags = []

        tag_keywords = {
            'Bitcoin': ['bitcoin', 'btc'],
            'Ethereum': ['ethereum', 'eth'],
            'DeFi': ['defi', 'yield', 'liquidity'],
            'NFT': ['nft', 'opensea'],
            'Trading': ['trading', 'price', 'market'],
            'Regulation': ['regulation', 'sec', 'legal'],
            'Analysis': ['analysis', 'technical', 'chart']
        }

        for tag, keywords in tag_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(tag)

        return tags[:5]  # Max 5 tags

    def clean_summary(self, summary):
        """Clean and truncate summary text"""
        # Remove HTML tags
        soup = BeautifulSoup(summary, 'html.parser')
        clean_text = soup.get_text()
        # Truncate to 200 chars
        if len(clean_text) > 200:
            clean_text = clean_text[:197] + '...'
        return clean_text.strip()

    def fetch_rss(self, feed_url, source_name, limit=10):
        """Fetch items from an RSS feed in Hugo format."""
        articles = []
        try:
            resp = self.session.get(feed_url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'xml')
            items = soup.find_all('item', limit=limit)

            for item in items:
                title = item.title.text.strip() if item.title else ''
                link = item.link.text.strip() if item.link else ''

                if not title or not link:
                    continue

                summary = ''
                if item.description:
                    summary = self.clean_summary(item.description.text)

                # Try to get publication date
                pub_date = item.pubDate.text if item.pubDate else datetime.now().isoformat()

                article_id = self.generate_article_id(title, link)
                if article_id in self.existing_articles:
                    continue

                # Format for Hugo
                article = {
                    'id': article_id,
                    'title': title,
                    'link': link,
                    'source': source_name,
                    'sourceUrl': feed_url,
                    'timestamp': pub_date,
                    'excerpt': summary,
                    'categories': self.determine_categories(title, summary),
                    'tags': self.extract_tags(title, summary)
                }

                articles.append(article)

            logging.info(
                f"Fetched {len(articles)} new articles from {source_name}")

        except Exception as e:
            logging.error(f"Error fetching RSS from {source_name}: {e}")

        return articles

    def scrape_all_sources(self):
        """Scrape all configured RSS sources."""
        all_articles = []

        # RSS sources configuration
        rss_sources = [
            ('CoinDesk', 'https://www.coindesk.com/arc/outboundfeeds/rss/'),
            ('CoinTelegraph', 'https://cointelegraph.com/rss'),
            ('CryptoNews', 'https://cryptonews.com/news/feed/'),
            ('Bitcoin.com', 'https://news.bitcoin.com/feed/'),
            ('Bitcoinist', 'https://bitcoinist.com/feed/'),
            ('CryptoSlate', 'https://cryptoslate.com/feed/'),
            ('The Daily Hodl', 'https://dailyhodl.com/feed/'),
            ('BeInCrypto', 'https://beincrypto.com/feed/'),
            ('NewsBTC', 'https://www.newsbtc.com/feed/'),
            ('CryptoPotato', 'https://cryptopotato.com/feed/')
        ]

        for source_name, feed_url in rss_sources:
            articles = self.fetch_rss(feed_url, source_name)
            all_articles.extend(articles)
            time.sleep(1)  # Be polite

        # Sort by timestamp (newest first)
        all_articles.sort(key=lambda x: x['timestamp'], reverse=True)
        return all_articles

    def save_to_hugo_format(self, new_articles):
        """Save articles in Hugo data format."""
        # Load existing data
        if os.path.exists(self.news_file):
            try:
                with open(self.news_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except:
                existing_data = {}
        else:
            existing_data = {}

        # Merge new articles with existing ones
        all_articles = new_articles
        if 'all' in existing_data and isinstance(existing_data['all'], list):
            # Add existing articles that aren't duplicates
            existing_ids = {a['id'] for a in new_articles}
            for article in existing_data['all']:
                if article.get('id') not in existing_ids:
                    all_articles.append(article)

        # Sort all articles by timestamp
        all_articles.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        # Limit total articles to prevent file from growing too large
        all_articles = all_articles[:500]

        # Categorize articles for Hugo
        hugo_data = {
            'latest': all_articles[:20],
            'featured': [a for a in all_articles if any(cat in ['bitcoin', 'ethereum'] for cat in a.get('categories', []))][:5],
            'bitcoin': [a for a in all_articles if 'bitcoin' in a.get('categories', [])][:10],
            'ethereum': [a for a in all_articles if 'ethereum' in a.get('categories', [])][:10],
            'defi': [a for a in all_articles if 'defi' in a.get('categories', [])][:10],
            'nft': [a for a in all_articles if 'nft' in a.get('categories', [])][:10],
            'analysis': [a for a in all_articles if 'analysis' in a.get('categories', [])][:10],
            'all': all_articles,
            'last_updated': datetime.now().isoformat()
        }

        # Save to JSON file
        with open(self.news_file, 'w', encoding='utf-8') as f:
            json.dump(hugo_data, f, ensure_ascii=False, indent=2)

        logging.info(
            f"Saved {len(new_articles)} new articles to {self.news_file}")

        # Update existing articles set
        for article in new_articles:
            self.existing_articles.add(article['id'])

    def run(self):
        """Main execution method."""
        try:
            logging.info("Starting crypto news scraping...")
            new_articles = self.scrape_all_sources()

            if new_articles:
                self.save_to_hugo_format(new_articles)
                logging.info(
                    f"Successfully scraped {len(new_articles)} new articles")

                # Print summary
                print(f"\n✓ Scraped {len(new_articles)} new articles")
                print(f"✓ Data saved to {self.news_file}")
                print("\nSample articles:")
                for article in new_articles[:3]:
                    print(f"- {article['title']} ({article['source']})")
            else:
                logging.info("No new articles found")

        except Exception as e:
            logging.error(f"Fatal error: {e}")
            raise


if __name__ == "__main__":
    # Determine the correct path to Hugo data directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    hugo_data_dir = os.path.join(script_dir, '..', 'data')

    scraper = CryptoNewsScraper(hugo_data_dir=hugo_data_dir)
    scraper.run()
