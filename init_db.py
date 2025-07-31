#!/usr/bin/env python3
"""
Database initialization script for BlockWire News
Run this after setting up PostgreSQL
"""

from crypto_news_scraper import SimpleCryptoRSSFeedScraper
from models import User, Article, NewsItem, PriceData, SiteSettings
from app import app, db
import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def init_database():
    """Initialize the database with tables and default data"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created")

        # Check if already initialized
        if User.query.first():
            print("Database already contains data. Skipping initialization.")
            return

        # Create default admin user
        print("\nCreating default admin user...")
        admin = User(
            username='admin',
            email='admin@blockwirenews.com',
            is_admin=True
        )
        admin.set_password('changeme123')  # CHANGE THIS!
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin user created (username: admin, password: changeme123)")
        print("  ⚠️  IMPORTANT: Change the admin password after first login!")

        # Create sample article
        print("\nCreating sample article...")
        article = Article(
            title='Welcome to BlockWire News',
            slug='welcome-to-blockwire-news',
            content='''Welcome to BlockWire News, your premier destination for cryptocurrency news and analysis.

This platform aggregates the latest news from leading cryptocurrency sources and provides a space for expert analysis and commentary.

Features include:
- Real-time cryptocurrency price tracking
- Aggregated news from multiple sources
- User-generated articles and analysis
- Admin dashboard for content management

Get started by exploring the latest news or creating your own account to contribute articles!''',
            summary='Welcome to BlockWire News - Your source for cryptocurrency news and analysis.',
            author_id=admin.id,
            published=True,
            published_at=datetime.utcnow()
        )
        db.session.add(article)
        db.session.commit()
        print("✓ Sample article created")

        # Initialize site settings
        print("\nInitializing site settings...")
        default_settings = [
            ('site_name', 'BlockWire News', 'Site name displayed in header'),
            ('site_description', 'Your premier source for cryptocurrency news and analysis',
             'Site meta description'),
            ('articles_per_page', '10', 'Number of articles per page'),
            ('news_per_page', '15', 'Number of news items per page'),
            ('enable_registration', 'true', 'Allow new user registration'),
            ('require_email_verification', 'false',
             'Require email verification for new users'),
            ('auto_publish_articles', 'false',
             'Automatically publish new articles'),
        ]

        for key, value, description in default_settings:
            SiteSettings.set(key, value, description)
        print("✓ Site settings initialized")

        # Fetch initial news
        print("\nFetching initial news articles...")
        try:
            scraper = SimpleCryptoRSSFeedScraper()
            articles = scraper.scrape_all()

            for article_data in articles:
                news_item = NewsItem(
                    external_id=article_data['id'],
                    title=article_data['title'],
                    url=article_data['url'],
                    summary=article_data.get('summary', ''),
                    source=article_data.get('source', 'Unknown'),
                    published_date=datetime.fromisoformat(
                        article_data.get('published', datetime.now().isoformat()))
                )
                db.session.add(news_item)

            db.session.commit()
            print(f"✓ {len(articles)} news articles imported")
        except Exception as e:
            print(f"⚠️  Could not fetch initial news: {e}")

        # Fetch initial price data
        print("\nFetching initial price data...")
        try:
            import requests
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': 'bitcoin,ethereum,binancecoin,ripple,cardano,solana,polkadot,dogecoin',
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true'
            }
            response = requests.get(url, params=params, verify=False)
            data = response.json()

            crypto_names = {
                'bitcoin': 'BTC',
                'ethereum': 'ETH',
                'binancecoin': 'BNB',
                'ripple': 'XRP',
                'cardano': 'ADA',
                'solana': 'SOL',
                'polkadot': 'DOT',
                'dogecoin': 'DOGE'
            }

            for crypto_id, info in data.items():
                price_data = PriceData(
                    symbol=crypto_names.get(crypto_id, crypto_id).upper(),
                    name=crypto_names.get(crypto_id, crypto_id),
                    price_usd=info.get('usd', 0),
                    change_24h=info.get('usd_24h_change', 0),
                    market_cap=info.get('usd_market_cap', 0),
                    volume_24h=info.get('usd_24h_vol', 0)
                )
                db.session.add(price_data)

            db.session.commit()
            print(f"✓ Price data for {len(data)} cryptocurrencies imported")
        except Exception as e:
            print(f"⚠️  Could not fetch initial prices: {e}")

        print("\n" + "="*50)
        print("✅ Database initialization complete!")
        print("="*50)
        print("\nNext steps:")
        print("1. Start the application: python app_enhanced.py")
        print("2. Login with admin/changeme123")
        print("3. Change the admin password immediately")
        print("4. Configure site settings in the admin panel")


if __name__ == '__main__':
    # Check for database URL
    db_url = os.environ.get('DATABASE_URL', 'postgresql://localhost/blockwire')

    print("BlockWire News - Database Initialization")
    print("="*50)
    print(f"Database URL: {db_url}")
    print()

    response = input("This will create all database tables. Continue? (y/n): ")
    if response.lower() != 'y':
        print("Initialization cancelled.")
        sys.exit(0)

    init_database()
