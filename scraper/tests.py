from celery import shared_task
from bs4 import BeautifulSoup
import requests
import feedparser
from datetime import datetime
from django.utils.text import slugify
from news.models import Article, Source, Category
import logging

logger = logging.getLogger(__name__)


@shared_task
def scrape_coindesk():
    """Scrape CoinDesk RSS feed"""
    try:
        source, _ = Source.objects.get_or_create(
            name='CoinDesk',
            defaults={'url': 'https://www.coindesk.com'}
        )

        feed = feedparser.parse(
            'https://www.coindesk.com/arc/outboundfeeds/rss/')
        category, _ = Category.objects.get_or_create(
            name='Bitcoin News',
            defaults={'slug': 'bitcoin-news'}
        )

        for entry in feed.entries[:10]:  # Get last 10 articles
            if not Article.objects.filter(source_url=entry.link).exists():
                article = Article.objects.create(
                    title=entry.title,
                    slug=slugify(entry.title)[:290],
                    content=entry.summary,
                    excerpt=entry.summary[:400],
                    source=source,
                    source_url=entry.link,
                    article_type='aggregated',
                    category=category,
                    published_date=datetime.now()
                )
                logger.info(f"Created article: {article.title}")

    except Exception as e:
        logger.error(f"Error scraping CoinDesk: {str(e)}")


@shared_task
def scrape_cointelegraph():
    """Scrape CoinTelegraph"""
    try:
        source, _ = Source.objects.get_or_create(
            name='CoinTelegraph',
            defaults={'url': 'https://cointelegraph.com'}
        )

        response = requests.get('https://cointelegraph.com/rss')
        feed = feedparser.parse(response.content)

        category, _ = Category.objects.get_or_create(
            name='Cryptocurrency News',
            defaults={'slug': 'cryptocurrency-news'}
        )

        for entry in feed.entries[:10]:
            if not Article.objects.filter(source_url=entry.link).exists():
                article = Article.objects.create(
                    title=entry.title,
                    slug=slugify(entry.title)[:290],
                    content=entry.description,
                    excerpt=entry.description[:400],
                    source=source,
                    source_url=entry.link,
                    article_type='aggregated',
                    category=category,
                    published_date=datetime.now()
                )
                logger.info(f"Created article: {article.title}")

    except Exception as e:
        logger.error(f"Error scraping CoinTelegraph: {str(e)}")


@shared_task
def update_crypto_prices():
    """Update cryptocurrency prices from CoinGecko API"""
    from ticker.models import Cryptocurrency, PriceHistory

    try:
        # Top cryptocurrencies to track
        coins = ['bitcoin', 'ethereum', 'binancecoin', 'cardano',
                 'solana', 'ripple', 'polkadot', 'dogecoin']

        for coin_id in coins:
            response = requests.get(
                f'https://api.coingecko.com/api/v3/simple/price',
                params={
                    'ids': coin_id,
                    'vs_currencies': 'usd',
                    'include_market_cap': 'true',
                    'include_24hr_vol': 'true',
                    'include_24hr_change': 'true'
                }
            )

            if response.status_code == 200:
                data = response.json()[coin_id]

                crypto, created = Cryptocurrency.objects.update_or_create(
                    symbol=coin_id.upper()[:10],
                    defaults={
                        'name': coin_id.title(),
                        'current_price': data['usd'],
                        'market_cap': data.get('usd_market_cap', 0),
                        'volume_24h': data.get('usd_24h_vol', 0),
                        'percent_change_24h': data.get('usd_24h_change', 0)
                    }
                )

                # Store price history
                PriceHistory.objects.create(
                    cryptocurrency=crypto,
                    price=data['usd']
                )

    except Exception as e:
        logger.error(f"Error updating crypto prices: {str(e)}")


@shared_task
def scrape_all_sources():
    """Run all scrapers"""
    scrape_coindesk()
    scrape_cointelegraph()
    update_crypto_prices()
