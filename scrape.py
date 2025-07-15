#!/usr/bin/env python3
"""
Cryptocurrency News Aggregator
Scrapes news from popular crypto news sources and saves to JSON
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import time
import hashlib
from typing import List, Dict
import feedparser
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CryptoNewsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.articles = []
        self.seen_urls = set()
        
    def scrape_coindesk_rss(self) -> List[Dict]:
        """Scrape CoinDesk RSS feed"""
        try:
            feed = feedparser.parse('https://www.coindesk.com/arc/outboundfeeds/rss/')
            articles = []
            
            for entry in feed.entries[:20]:  # Get latest 20 articles
                if entry.link not in self.seen_urls:
                    article = {
                        'title': entry.title,
                        'url': entry.link,
                        'source': 'CoinDesk',
                        'publishedAt': self._parse_date(entry.published),
                        'description': BeautifulSoup(entry.summary, 'html.parser').get_text()[:200],
                        'category': 'News'
                    }
                    articles.append(article)
                    self.seen_urls.add(entry.link)
                    
            logger.info(f"Scraped {len(articles)} articles from CoinDesk")
            return articles
            
        except Exception as e:
            logger.error(f"Error scraping CoinDesk: {e}")
            return []
    
    def scrape_cointelegraph_rss(self) -> List[Dict]:
        """Scrape Cointelegraph RSS feed"""
        try:
            feed = feedparser.parse('https://cointelegraph.com/rss')
            articles = []
            
            for entry in feed.entries[:20]:
                if entry.link not in self.seen_urls:
                    article = {
                        'title': entry.title,
                        'url': entry.link,
                        'source': 'Cointelegraph',
                        'publishedAt': self._parse_date(entry.published),
                        'description': BeautifulSoup(entry.summary, 'html.parser').get_text()[:200],
                        'category': 'News'
                    }
                    articles.append(article)
                    self.seen_urls.add(entry.link)
                    
            logger.info(f"Scraped {len(articles)} articles from Cointelegraph")
            return articles
            
        except Exception as e:
            logger.error(f"Error scraping Cointelegraph: {e}")
            return []
    
    def scrape_cryptonews_api(self) -> List[Dict]:
        """Scrape from CryptoNews API (if available)"""
        try:
            # This is a placeholder - you would need to sign up for a crypto news API
            # Examples: CryptoPanic, CryptoCompare, etc.
            api_url = "https://cryptonews-api.com/api/v1/category?section=general&items=20&token=YOUR_API_TOKEN"
            
            # For now, return empty list
            logger.info("CryptoNews API scraping not configured")
            return []
            
        except Exception as e:
            logger.error(f"Error scraping CryptoNews API: {e}")
            return []
    
    def scrape_bitcoin_magazine(self) -> List[Dict]:
        """Scrape Bitcoin Magazine"""
        try:
            url = "https://bitcoinmagazine.com/.rss/full/"
            feed = feedparser.parse(url)
            articles = []
            
            for entry in feed.entries[:15]:
                if entry.link not in self.seen_urls:
                    article = {
                        'title': entry.title,
                        'url': entry.link,
                        'source': 'Bitcoin Magazine',
                        'publishedAt': self._parse_date(entry.published),
                        'description': BeautifulSoup(entry.summary, 'html.parser').get_text()[:200],
                        'category': 'Bitcoin'
                    }
                    articles.append(article)
                    self.seen_urls.add(entry.link)
                    
            logger.info(f"Scraped {len(articles)} articles from Bitcoin Magazine")
            return articles
            
        except Exception as e:
            logger.error(f"Error scraping Bitcoin Magazine: {e}")
            return []
    
    def scrape_the_block(self) -> List[Dict]:
        """Scrape The Block (simplified version)"""
        try:
            # The Block requires more complex scraping or API access
            # This is a simplified example
            url = "https://www.theblock.co/"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                articles = []
                
                # This selector would need to be updated based on their current HTML structure
                # This is just an example
                logger.info("The Block scraping requires API access or updated selectors")
                return []
            
        except Exception as e:
            logger.error(f"Error scraping The Block: {e}")
            return []
    
    def _parse_date(self, date_string: str) -> str:
        """Parse various date formats to ISO format"""
        try:
            # Try parsing with feedparser's date parser
            parsed = feedparser._parse_date(date_string)
            if parsed:
                dt = datetime(*parsed[:6])
                return dt.isoformat()
            else:
                return datetime.now(timezone.utc).isoformat()
        except:
            return datetime.now(timezone.utc).isoformat()
    
    def aggregate_news(self) -> None:
        """Aggregate news from all sources"""
        # Use ThreadPoolExecutor for concurrent scraping
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.scrape_coindesk_rss): 'CoinDesk',
                executor.submit(self.scrape_cointelegraph_rss): 'Cointelegraph',
                executor.submit(self.scrape_bitcoin_magazine): 'Bitcoin Magazine',
                executor.submit(self.scrape_cryptonews_api): 'CryptoNews API',
                executor.submit(self.scrape_the_block): 'The Block'
            }
            
            for future in as_completed(futures):
                source = futures[future]
                try:
                    articles = future.result()
                    self.articles.extend(articles)
                except Exception as e:
                    logger.error(f"Error getting results from {source}: {e}")
        
        # Sort articles by publication date (newest first)
        self.articles.sort(key=lambda x: x['publishedAt'], reverse=True)
        
        # Remove duplicates based on title similarity
        self._remove_duplicates()
        
        logger.info(f"Total articles aggregated: {len(self.articles)}")
    
    def _remove_duplicates(self) -> None:
        """Remove duplicate articles based on title similarity"""
        unique_articles = []
        seen_titles = set()
        
        for article in self.articles:
            # Create a normalized title for comparison
            normalized_title = article['title'].lower().strip()
            title_hash = hashlib.md5(normalized_title.encode()).hexdigest()[:10]
            
            if title_hash not in seen_titles:
                unique_articles.append(article)
                seen_titles.add(title_hash)
        
        self.articles = unique_articles
    
    def save_to_json(self, filename: str = 'data/aggregated-news.json') -> None:
        """Save aggregated news to JSON file"""
        output = {
            'lastUpdated': datetime.now(timezone.utc).isoformat(),
            'articleCount': len(self.articles),
            'articles': self.articles[:100]  # Limit to 100 most recent articles
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(self.articles)} articles to {filename}")
    
    def categorize_articles(self) -> None:
        """Add categories to articles based on keywords"""
        categories = {
            'Bitcoin': ['bitcoin', 'btc', 'satoshi', 'lightning network'],
            'Ethereum': ['ethereum', 'eth', 'vitalik', 'smart contract'],
            'DeFi': ['defi', 'yield', 'liquidity', 'amm', 'dex', 'lending'],
            'NFT': ['nft', 'non-fungible', 'opensea', 'collection'],
            'Regulation': ['regulation', 'sec', 'government', 'legal', 'law'],
            'Trading': ['trading', 'price', 'market', 'bull', 'bear', 'analysis'],
            'Technology': ['blockchain', 'protocol', 'development', 'upgrade']
        }
        
        for article in self.articles:
            if 'category' not in article or article['category'] == 'News':
                title_lower = article['title'].lower()
                desc_lower = article.get('description', '').lower()
                combined_text = title_lower + ' ' + desc_lower
                
                for category, keywords in categories.items():
                    if any(keyword in combined_text for keyword in keywords):
                        article['category'] = category
                        break

def main():
    """Main execution function"""
    logger.info("Starting crypto news aggregation...")
    
    scraper = CryptoNewsScraper()
    scraper.aggregate_news()
    scraper.categorize_articles()
    scraper.save_to_json()
    
    logger.info("News aggregation completed!")

if __name__ == "__main__":
    main()