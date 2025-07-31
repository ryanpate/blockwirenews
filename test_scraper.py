#!/usr/bin/env python3
"""
Test script to debug the crypto news scraper
"""

import feedparser
import requests
import json
from datetime import datetime

def test_internet_connection():
    """Test basic internet connectivity"""
    print("1. Testing internet connection...")
    try:
        response = requests.get("https://www.google.com", timeout=5)
        print("   ✓ Internet connection OK")
        return True
    except Exception as e:
        print(f"   ✗ Internet connection failed: {e}")
        return False

def test_single_feed(feed_url, name):
    """Test a single RSS feed"""
    print(f"\n2. Testing {name} feed...")
    print(f"   URL: {feed_url}")
    
    try:
        # Test direct HTTP request first
        response = requests.get(feed_url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        print(f"   HTTP Status: {response.status_code}")
        
        # Parse with feedparser
        feed = feedparser.parse(feed_url)
        
        if feed.bozo:
            print(f"   ⚠ Feed parsing warning: {feed.bozo_exception}")
        
        if 'entries' in feed and feed.entries:
            print(f"   ✓ Found {len(feed.entries)} articles")
            
            # Show first article as example
            if feed.entries:
                entry = feed.entries[0]
                print(f"\n   First article:")
                print(f"   - Title: {entry.get('title', 'No title')[:60]}...")
                print(f"   - Link: {entry.get('link', 'No link')}")
                
                # Check for summary/description
                has_summary = hasattr(entry, 'summary') or hasattr(entry, 'description')
                print(f"   - Has summary: {'Yes' if has_summary else 'No'}")
                
                # Check for date
                has_date = hasattr(entry, 'published_parsed') or hasattr(entry, 'updated_parsed')
                print(f"   - Has date: {'Yes' if has_date else 'No'}")
        else:
            print(f"   ✗ No entries found in feed")
            
    except Exception as e:
        print(f"   ✗ Error: {e}")

def test_alternative_feeds():
    """Test alternative RSS feeds"""
    print("\n3. Testing alternative RSS feeds...")
    
    alternative_feeds = {
        'CoinTelegraph': 'https://cointelegraph.com/rss',
        'CoinDesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
        'Crypto Slate': 'https://cryptoslate.com/feed/',
        'The Block': 'https://www.theblock.co/rss.xml',
        'Crypto News': 'https://cryptonews.com/news/rss/',
        'NewsBTC': 'https://www.newsbtc.com/feed/',
        'Bitcoinist': 'https://bitcoinist.com/feed/',
        'U.Today': 'https://u.today/rss',
        'DailyCoin': 'https://dailycoin.com/feed/',
        'CryptoPotato': 'https://cryptopotato.com/feed/'
    }
    
    working_feeds = []
    
    for name, url in alternative_feeds.items():
        try:
            print(f"\n   Testing {name}...")
            feed = feedparser.parse(url)
            
            if 'entries' in feed and len(feed.entries) > 0:
                print(f"   ✓ {name}: {len(feed.entries)} articles found")
                working_feeds.append((name, url))
            else:
                print(f"   ✗ {name}: No articles found")
                
        except Exception as e:
            print(f"   ✗ {name}: Error - {e}")
    
    print(f"\n   Summary: {len(working_feeds)} working feeds found")
    return working_feeds

def test_coingecko_api():
    """Test CoinGecko API for price data"""
    print("\n4. Testing CoinGecko API...")
    
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': 'bitcoin,ethereum',
        'vs_currencies': 'usd',
        'include_24hr_change': 'true'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"   HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✓ Price data received:")
            for coin, info in data.items():
                print(f"     - {coin}: ${info['usd']:,.2f} ({info['usd_24h_change']:.2f}%)")
        else:
            print(f"   ✗ API error: {response.text}")
            
    except Exception as e:
        print(f"   ✗ Error: {e}")

def create_test_json():
    """Create a test JSON file with sample data"""
    print("\n5. Creating test JSON file...")
    
    sample_data = {
        'last_updated': datetime.now().isoformat(),
        'article_count': 5,
        'articles': [
            {
                'id': 'test1',
                'title': 'Bitcoin Surges Past $100,000 as Institutional Adoption Accelerates',
                'url': 'https://example.com/bitcoin-100k',
                'summary': 'Bitcoin reached a historic milestone today, breaking through the $100,000 barrier as major corporations announce Bitcoin treasury strategies...',
                'source': 'Crypto Test News',
                'published': datetime.now().isoformat(),
                'scraped_at': datetime.now().isoformat()
            },
            {
                'id': 'test2',
                'title': 'Ethereum 3.0 Roadmap Unveiled with Revolutionary Scaling Solutions',
                'url': 'https://example.com/eth-3-0',
                'summary': 'The Ethereum Foundation revealed ambitious plans for Ethereum 3.0, promising transaction speeds of over 100,000 TPS...',
                'source': 'Blockchain Daily',
                'published': datetime.now().isoformat(),
                'scraped_at': datetime.now().isoformat()
            },
            {
                'id': 'test3',
                'title': 'Major Banks Launch Cryptocurrency Trading Services for Retail Clients',
                'url': 'https://example.com/banks-crypto',
                'summary': 'JPMorgan, Bank of America, and Wells Fargo simultaneously announced the launch of cryptocurrency trading services...',
                'source': 'Financial Times Crypto',
                'published': datetime.now().isoformat(),
                'scraped_at': datetime.now().isoformat()
            },
            {
                'id': 'test4',
                'title': 'DeFi Total Value Locked Reaches $500 Billion Milestone',
                'url': 'https://example.com/defi-tvl',
                'summary': 'Decentralized Finance protocols have reached a combined total value locked of $500 billion, marking exponential growth...',
                'source': 'DeFi Pulse',
                'published': datetime.now().isoformat(),
                'scraped_at': datetime.now().isoformat()
            },
            {
                'id': 'test5',
                'title': 'New Cryptocurrency Regulations Provide Clear Framework for Innovation',
                'url': 'https://example.com/crypto-regulations',
                'summary': 'Regulators announce comprehensive cryptocurrency framework that balances innovation with consumer protection...',
                'source': 'Regulatory News',
                'published': datetime.now().isoformat(),
                'scraped_at': datetime.now().isoformat()
            }
        ]
    }
    
    with open('crypto_news_rss.json', 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    print("   ✓ Created crypto_news_rss.json with 5 sample articles")

if __name__ == "__main__":
    print("Crypto News Scraper Test Suite")
    print("=" * 50)
    
    # Run tests
    if test_internet_connection():
        # Test main feed
        test_single_feed(
            'https://www.coindesk.com/arc/outboundfeeds/rss/',
            'CoinDesk'
        )
        
        # Test alternative feeds
        working_feeds = test_alternative_feeds()
        
        # Test price API
        test_coingecko_api()
    
    # Create test data regardless
    create_test_json()
    
    print("\n" + "=" * 50)
    print("Test complete!")
    print("\nRecommendations:")
    print("1. If feeds aren't working, use the test JSON file to proceed")
    print("2. Some feeds may require different parsing strategies")
    print("3. Consider using news APIs with authentication for better reliability")
    print("4. The sample data will let you test the website functionality")